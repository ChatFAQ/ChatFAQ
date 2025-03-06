import asyncio
import json
import os
import random
import uuid
from typing import Mapping, Sequence

import requests
import websockets
from django.conf import settings
from django.core.files.storage import default_storage
from health_check.cache.backends import CacheBackend
from health_check.contrib.psutil.backends import MemoryUsage
from health_check.db.backends import DatabaseBackend

from .base import DjangoHealthCheckWrapper, HealthCheck, Outcome, Status


def disp_window(window: Mapping[str, int]) -> str:
    """
    Returns a friendly text for a time window (aka the kwargs of a timedelta)

    Parameters
    ----------
    window
        Window to be displayed
    """

    items = []

    for key, value in window.items():
        if value == 0:
            continue

        if value == 1:
            key = key.rstrip("s")

        items.append(f"{value} {key}")

    return " ".join(items)


def disp_stats(stats: Mapping[str, int]) -> str:
    """
    All the checks relying on the logs use the same pattern of checking how
    many success/failures happened. This is an utility to transform these
    stats into a readable text.

    Parameters
    ----------
    stats
        A dictionary with "success", "failure" and "total" as keys
    """

    success_str, failure_str, total_str = "", "", ""

    if success := stats["success"]:
        plural = "es" if success != 1 else ""
        success_str = f"{success} success{plural}"

    if failure := stats["failure"]:
        plural = "s" if failure != 1 else ""
        failure_str = f"{failure} failure{plural}"

    if total := stats["total"]:
        total_str = f"out of {total}"
    else:
        total_str = "no events"

    part_1 = ", ".join([x for x in [success_str, failure_str] if x])

    return " ".join([x for x in [part_1, total_str] if x]).capitalize()


class Database(DjangoHealthCheckWrapper):
    """
    Checks that the default database can be reached, read and write
    """

    base_class = DatabaseBackend

    def get_resolving_actions(self, outcome: Outcome) -> str:
        return """# __CODE__ &mdash; Database cannot be reached

This checks verifies if the database is reachable by inserting and deleting a
row in a test table.

## Possible causes

- There could be a network issue that prevents to access the database
- The data could be inconsistent or the disk full
- The database server could be overloaded

## Possible solutions

- Check the network connectivity
- Check the disk space
- Check the database server logs
- Check the database server status
"""

    def suggest_reboot(self, outcome: Outcome) -> Sequence[str]:
        return ["database"]

    def get_name(self) -> str:
        return "Database"


class RamUsage(DjangoHealthCheckWrapper):
    """
    Checks that we don't use too much RAM
    """

    base_class = MemoryUsage

    def get_name(self) -> str:
        return "RAM Usage"

    def get_resolving_actions(self, outcome: Outcome) -> str:
        return """# __CODE__ &mdash; RAM usage is too high

The memory usage in the container running the application is too high.

## Possible causes

- There is a memory leak in the application
- The application just needs more RAM

## Possible solutions

- Short term, restart the container
- Long term, identify if this issue comes from a leak (in which case you can
  fix the leak) or if the application just needs more RAM (in which case you
  can increase the RAM allocated to the container)
"""

    def suggest_reboot(self, outcome: Outcome) -> Sequence[str]:
        return ["api"]


class Cache(DjangoHealthCheckWrapper):
    """
    Validates cache accessibility. Since the queue is also the cache, it will
    validate the queue as well (somehow).
    """

    base_class = CacheBackend

    def get_name(self) -> str:
        return "Cache"

    def get_resolving_actions(self, outcome: Outcome) -> str:
        return """# __CODE__ &mdash; Redis cache cannot be reached

This checks verifies if the cache is reachable by inserting and deleting an
entry in the cache.

## Possible causes

- There could be a network issue that prevents to access the cache
- The cache could be overloaded

## Possible solutions

- Check the network connectivity
- Check the cache server logs
- Check the cache server status
"""

    def suggest_reboot(self, outcome: Outcome) -> Sequence[str]:
        return ["redis"]


class ModuleSimulationBase(HealthCheck):
    """
    Base class for module simulation health checks.
    Provides common WebSocket communication and file processing methods.
    """
    
    # Configuration parameters that should be overridden by subclasses
    MODULE_NUMBER = None
    MODULE_NAME = None
    FILE_NAME = None
    FSM_DEF = "lefebvre_fsm"
    STATE_OVERWRITE = None
    HANDSHAKE_TIMEOUT = 10.0
    FILE_PROCESSING_TIMEOUT = 300.0
    USER_ID = "2b84e03d-cb1e-48db-b79c-7c41372b98a3" # Random UUID for the health check
    
    def get_name(self) -> str:
        if self.MODULE_NAME is None:
            raise NotImplementedError("Subclasses must define MODULE_NAME")
        return f"{self.MODULE_NAME} Simulation"
    
    async def _receive_json_message(self, websocket, timeout=10.0, timeout_message=None):
        """
        Helper method to receive a JSON message from the websocket.
        """
        message_text = ""
        try:
            message_text = await asyncio.wait_for(websocket.recv(), timeout)
            msg = json.loads(message_text)
            return msg
        except asyncio.TimeoutError:
            if timeout_message:
                raise asyncio.TimeoutError(timeout_message + ". Last message: " + message_text)
            else:
                raise asyncio.TimeoutError("Timeout waiting for message from server. Last message: " + message_text)
        except json.JSONDecodeError:
            raise ValueError("Invalid JSON response from server. Last message: " + message_text)
    
    async def _wait_for_initial_messages(self, websocket, num_messages=3):
        """
        Waits for initial messages, throwing an error if any indicate a problem.
        """
        for _ in range(num_messages):
            response = await self._receive_json_message(websocket, timeout=self.HANDSHAKE_TIMEOUT)
            if response.get("status") == 400:
                raise ValueError(f"Error in initial message from WS: {response.get('payload')}")
    
    async def _run_module(self, module_file_name, file_url, fsm_def=None, state_overwrite=None):
        """
        Runs a file generation simulation.
        """
        # Use default values if not provided
        fsm_def = fsm_def or self.FSM_DEF
        state_overwrite = state_overwrite or self.STATE_OVERWRITE
        
        conversation_id = int(random.random() * 1000000000)

        auth_token = settings.BACKEND_TOKEN
        internal_ws_url = settings.INTERNAL_WS_URL
        if not auth_token or not internal_ws_url:
            return False, "BACKEND_TOKEN or INTERNAL_WS_URL is not set"
        
        query_params = ""
        
        if auth_token:
            query_params = f"?token={auth_token}"
            if state_overwrite:
                query_params += f"&state_overwrite={state_overwrite}"
        elif state_overwrite:
            query_params = f"?state_overwrite={state_overwrite}"
            
        query_params += f'&metadata={{"module":"{self.MODULE_NAME}"}}'

        uri = (
            internal_ws_url
            + "/back/ws/broker/"
            + str(conversation_id)
            + "/"
            + fsm_def
            + "/"
            + f"{self.USER_ID}/" 
            + query_params
        )

        try:
            async with websockets.connect(uri, close_timeout=1000) as websocket:
                # Process the initial handshake responses.
                await self._wait_for_initial_messages(websocket)

                # Build and send the message payload.
                message = {
                    "sender": {
                        "type": "human",
                        "platform": "WS",
                        "id": self.USER_ID, 
                    },
                    "stack": [
                        {
                            "type": "file_uploaded",
                            "payload": {
                                        "name": module_file_name.split('/')[-1], # just send the file name
                                        "url": file_url,
                            }
                        }
                    ],
                    "stack_id": "0",
                    "stack_group_id": "0",
                    "last": True
                }
                await websocket.send(json.dumps(message))

                # Process responses after sending the message.
                first_response = await self._receive_json_message(websocket, timeout=self.HANDSHAKE_TIMEOUT)
                if first_response.get("status") == 400:
                    return False, f"Error in initial response from WS: {first_response.get('payload')}"

                new_file_response = await self._receive_json_message(websocket, timeout=self.FILE_PROCESSING_TIMEOUT, timeout_message="Timeout waiting for file processing") # Increase timeout for file processing, if it takes longer than 5 minutes then there may be an issue
                new_file_url = (
                    new_file_response.get("stack", [{}])[0]
                    .get("payload", {})
                    .get("url", "")
                )

                # Try to download the newly created file
                if new_file_url:
                    try:
                        response = requests.get(new_file_url, timeout=10)
                        response.raise_for_status()  # Raise an exception for 4XX/5XX responses
                        # Successfully downloaded the file
                    except requests.exceptions.RequestException as e:
                        return False, f"Failed to download the generated file: {str(e)}. Full response: {str(new_file_response)}"
                else:
                    return False, "No file URL was provided in the response. Full response: " + str(new_file_response)
            
                return True, "Everything is working correctly"
        except websockets.exceptions.ConnectionClosedError as e:
            return False, f"WebSocket connection closed unexpectedly: {e.code} {e.reason}"
        except Exception as e:
            return False, f"An unexpected error occurred: {type(e).__name__} - {e}"

    async def get_status(self) -> Outcome:
        """
        Performs the module simulation to determine system health.
        """
        try:
            if self.FILE_NAME is None:
                raise ValueError("Subclasses must define FILE_NAME")
            
            file_name = f'health_check_files/{self.FILE_NAME}'
            if default_storage.exists(file_name):
                file_url = default_storage.url(file_name)
                success, message = await self._run_module(file_name, file_url)
            else:
                success = False
                message = f"The base document to test module {self.MODULE_NUMBER} does not exist in the storage. Please upload the file {file_name} to the Digital Ocean bucket."
        except Exception as e:
            return Outcome(
                instance=self,
                status=Status.ERROR,
                message=f"Module {self.MODULE_NUMBER} failed: {e}",
            )
        
        if success:
            return Outcome(
                instance=self,
                status=Status.OK,
                message=f"Module {self.MODULE_NUMBER} successful",
            )
        else:
            return Outcome(
                instance=self,
                status=Status.ERROR,
                message=f"Module {self.MODULE_NUMBER} failed: {message}",
            )

    def get_resolving_actions(self, outcome: Outcome) -> str:
        return f"""# __CODE__ &mdash; {self.MODULE_NAME} failed

This check simulates a file generation with the chatbot via WebSocket to verify:
- The WebSocket server is reachable.
- The FSM works correctly.
- The FastAPI modules server is reachable.
- The file generation LLM is reachable.
- The file storage is reachable.
"""

    def suggest_reboot(self, outcome: Outcome) -> Sequence[str]:
        return []


class Module1Simulation(ModuleSimulationBase):
    """
    Simulates a file generation with module 1 of the chatbot to check if 
    WebSocket connection, message processing and file generation are working correctly.
    """
    MODULE_NUMBER = 1
    MODULE_NAME = "Info2ArticleXia"
    FILE_NAME = "module1.pdf"
    STATE_OVERWRITE = "M1"


class Module2Simulation(ModuleSimulationBase):
    """
    Simulates a file generation with module 2 of the chatbot to check if 
    WebSocket connection, message processing and file generation are working correctly.
    """
    MODULE_NUMBER = 2
    MODULE_NAME = "TopicsIndexGenXia"
    FILE_NAME = "module2.sgm"
    STATE_OVERWRITE = "M2"


class Module3Simulation(ModuleSimulationBase):
    """
    Simulates a file generation with module 3 of the chatbot to check if 
    WebSocket connection, message processing and file generation are working correctly.
    """
    MODULE_NUMBER = 3
    MODULE_NAME = "ColAgreeSumXia"
    FILE_NAME = "module3.xml"
    STATE_OVERWRITE = "M3"


class LLMQuestionSimulation(HealthCheck):
    """
    Simulates a LLM question with the chatbot to check if the WebSocket
    connection, message processing and LLM response generation are working correctly.
    """

    USER_ID = "2b84e03d-cb1e-48db-b79c-7c41372b98a3" # Random UUID for the health check

    def get_name(self) -> str:
        return "LLM Question Simulation"
    
    async def _receive_json_message(self, websocket, timeout=10.0, timeout_message=None):
        """
        Helper method to receive a JSON message from the websocket.
        """
        message_text = ""
        try:
            message_text = await asyncio.wait_for(websocket.recv(), timeout)
            msg = json.loads(message_text)
            print(f"Received message: {msg}")  # Log received message
            return msg
        except asyncio.TimeoutError:
            if timeout_message:
                raise asyncio.TimeoutError(timeout_message + ". Last message: " + message_text)
            else:
                raise asyncio.TimeoutError("Timeout waiting for message from server. Last message: " + message_text)
        except json.JSONDecodeError:
            raise ValueError("Invalid JSON response from server. Last message: " + message_text)
    
    async def _wait_for_initial_messages(self, websocket, num_messages=3):
        """
        Waits for three initial messages, throwing an error if any indicate a problem.
        """
        for _ in range(num_messages):
            response = await self._receive_json_message(websocket)
            if response.get("status") == 400:
                raise ValueError(f"Error in initial message from WS: {response.get('payload')}")
    
    async def _wait_for_llm_response(self, websocket):
        """
        Waits for LLM response chunks until the final chunk (with last_chunk=True)
        is received.
        """
        prev_response = None
        while True:
            response = await self._receive_json_message(websocket)
            if response.get("last", False):
                return prev_response # We return the previous response because the last one is empty
            prev_response = response

    async def _run_module(self, fsm_def="lefebvre_fsm"):
        """
        Runs an LLM question simulation.
        """
        conversation_id = int(random.random() * 1000000000)

        auth_token = settings.BACKEND_TOKEN
        internal_ws_url = settings.INTERNAL_WS_URL
        if not auth_token or not internal_ws_url:
            return False, "BACKEND_TOKEN or INTERNAL_WS_URL is not set"
        
        query_params = f"?token={auth_token}&state_overwrite=M3" if auth_token else ""
        query_params += '&metadata={"module":"ColAgreeSumXia"}'

        uri = (
            internal_ws_url
            + "/back/ws/broker/"
            + str(conversation_id)
            + "/"
            + fsm_def
            + "/"
            + f"{self.USER_ID}/"
            + query_params
        )

        try:
            async with websockets.connect(uri, close_timeout=1000) as websocket:
                # Process the initial handshake responses.
                await self._wait_for_initial_messages(websocket)
                print("Initial handshake successful.")  # Log handshake

                # Build and send the message payload.
                message = {
                    "sender": {
                        "type": "human",
                        "platform": "WS",
                        "id": self.USER_ID, 
                    },
                    "stack": [
                        {
                            "type": "message",
                            "payload": {
                                "content": "Qué tipos de documentos puedo subir?"
                            },
                        }
                    ],
                    "stack_id": "0",
                    "stack_group_id": "0",
                    "last": True
                }
                await websocket.send(json.dumps(message))
                print(f"Message sent: {message}")  # Log sent message

                # Process responses after sending the message.
                first_response = await self._receive_json_message(websocket)
                if first_response.get("status") == 400:
                    return False, f"Error in initial response from WS: {first_response.get('payload')}"
                print(f"First response received: {first_response}")  # Log first response

                llm_response = await self._wait_for_llm_response(websocket)
                response_content = (
                    llm_response.get("stack", [{}])[0]
                    .get("payload", {})
                    .get("content", "")
                )

                return True, f"LLM responded: {response_content}"
            
        except websockets.exceptions.ConnectionClosedError as e:
            print(f"WebSocket connection closed: {e.code} {e.reason}")  # Log WS close
            return False, f"WebSocket connection closed unexpectedly: {e.code} {e.reason}"
        except Exception as e:
            print(f"Unexpected error: {type(e).__name__} - {e}")  # Log other errors
            return False, f"An unexpected error occurred: {type(e).__name__} - {e}"

    async def get_status(self) -> Outcome:
        try:
            success, message = await self._run_module()
        except Exception as e:
            return Outcome(
                instance=self,
                status=Status.ERROR,
                message=f"LLM question simulation failed: {e}",
            )
        if success:
            return Outcome(
                instance=self,
                status=Status.OK,
                message=f"LLM question simulation successful. The message was: {message}",
            )
        else:
            return Outcome(
                instance=self,
                status=Status.ERROR,
                message=f"LLM question simulation failed: {message}",
            )

    def get_resolving_actions(self, outcome: Outcome) -> str:
        return """# __CODE__ &mdash; Module failed

This check simulates a LLM question with the chatbot via WebSocket to verify:
- The WebSocket server is reachable.
- The FSM works correctly.
- The FastAPI modules server is reachable.
- The LLM is reachable.
"""

    def suggest_reboot(self, outcome: Outcome) -> Sequence[str]:
        return []