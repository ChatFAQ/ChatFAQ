import asyncio
import json
import logging
import random
from datetime import timedelta
from typing import Mapping, Sequence

import requests
import websockets
from channels.db import database_sync_to_async
from django.conf import settings
from django.core.cache import cache
from django.utils import timezone
from health_check.cache.backends import CacheBackend
from health_check.contrib.psutil.backends import MemoryUsage
from health_check.db.backends import DatabaseBackend

from back.config.storage_backends import select_private_storage

from .base import DjangoHealthCheckWrapper, HealthCheck, Outcome, Status
from .models import Event

# Get a logger instance
logger = logging.getLogger(__name__)

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
    Uses a cache-based lock to prevent concurrent runs.
    Triggers long simulations in the background to return status quickly.
    """
    
    # Configuration parameters that should be overridden by subclasses
    MODULE_NUMBER = None
    MODULE_NAME = None
    FILE_NAME = None
    FSM_DEF = "lefebvre_fsm"
    STATE_OVERWRITE = None
    HANDSHAKE_TIMEOUT = 10.0
    FILE_PROCESSING_TIMEOUT = 300.0 # 5 minutes
    USER_ID = "2b84e03d-cb1e-48db-b79c-7c41372b98a3" # Random UUID for the health check
    STORAGE = select_private_storage()
    # This is a heavy health check, results cached based on this window
    WINDOW = dict(hours=6)
    # Timeout for the cache lock (processing timeout + buffer)
    LOCK_TIMEOUT_SECONDS = FILE_PROCESSING_TIMEOUT + 120 # Increased buffer
    
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
            print("11111111111111")
            response = await self._receive_json_message(websocket, timeout=self.HANDSHAKE_TIMEOUT)
            print("22222222222222", response)
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
        if not auth_token:
             logger.error(f"[Module {self.MODULE_NUMBER}] BACKEND_TOKEN is not set.")
             return False, "BACKEND_TOKEN is not set in settings"
        if not internal_ws_url:
            logger.error(f"[Module {self.MODULE_NUMBER}] INTERNAL_WS_URL is not set.")
            return False, "INTERNAL_WS_URL is not set in settings"
        
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
        logger.info(f"[Module {self.MODULE_NUMBER}] Connecting to WebSocket: {uri}")
        try:
            async with websockets.connect(uri, close_timeout=1000) as websocket:
                logger.info(f"[Module {self.MODULE_NUMBER}] WebSocket connected. Waiting for initial messages.")
                await self._wait_for_initial_messages(websocket)
                logger.info(f"[Module {self.MODULE_NUMBER}] Initial messages received. Sending file payload.")

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
                logger.info(f"[Module {self.MODULE_NUMBER}] File payload sent. Waiting for responses.")

                # Process responses after sending the message.
                first_response = await self._receive_json_message(websocket, timeout=self.HANDSHAKE_TIMEOUT)
                if first_response.get("status") == 400:
                    error_payload = first_response.get('payload')
                    logger.error(f"[Module {self.MODULE_NUMBER}] Error in initial response from WS: {error_payload}")
                    return False, f"Error in initial response from WS: {error_payload}"

                logger.info(f"[Module {self.MODULE_NUMBER}] Initial response OK. Waiting for file processing response (timeout={self.FILE_PROCESSING_TIMEOUT}s).")
                new_file_response = await self._receive_json_message(websocket, timeout=self.FILE_PROCESSING_TIMEOUT, timeout_message="Timeout waiting for file processing") # Increase timeout for file processing, if it takes longer than 5 minutes then there may be an issue
                logger.info(f"[Module {self.MODULE_NUMBER}] File processing response received.")

                new_file_url = (
                    new_file_response.get("stack", [{}])[0]
                    .get("payload", {})
                    .get("url", "")
                )

                # Try to download the newly created file
                if new_file_url:
                    logger.info(f"[Module {self.MODULE_NUMBER}] Received new file URL: {new_file_url}. Attempting download.")
                    try:
                        response = requests.get(new_file_url, timeout=10)
                        response.raise_for_status()  # Raise an exception for 4XX/5XX responses
                        logger.info(f"[Module {self.MODULE_NUMBER}] Successfully downloaded generated file.")
                        # Successfully downloaded the file
                    except requests.exceptions.RequestException as e:
                        logger.error(f"[Module {self.MODULE_NUMBER}] Failed to download generated file: {e}. Response: {new_file_response}")
                        return False, f"Failed to download the generated file: {str(e)}. Full response: {str(new_file_response)}"
                else:
                    logger.error(f"[Module {self.MODULE_NUMBER}] No file URL provided in response: {new_file_response}")
                    return False, "No file URL was provided in the response. Full response: " + str(new_file_response)
            
                logger.info(f"[Module {self.MODULE_NUMBER}] Simulation completed successfully.")
                return True, f"Module {self.MODULE_NUMBER} simulation completed successfully."
        except websockets.exceptions.ConnectionClosedError as e:
            print("cccccccccccccccc")
            logger.error(f"[Module {self.MODULE_NUMBER}] WebSocket connection closed unexpectedly: {e.code} {e.reason}")
            return False, f"WebSocket connection closed unexpectedly: {e.code} {e.reason}"
        except asyncio.TimeoutError as e:
             print("bbbbbbbbbbbbbbbb")
             logger.error(f"[Module {self.MODULE_NUMBER}] Timeout occurred during WebSocket communication: {e}")
             return False, f"Timeout occurred during WebSocket communication: {e}"
        except Exception as e:
            print("aaaaaaaaaaaaaaaa")
            logger.exception(f"[Module {self.MODULE_NUMBER}] Unexpected error during WebSocket communication.") # Use logger.exception to include stack trace
            # Catch specific configuration errors if possible, otherwise generic
            if isinstance(e, (ValueError, ConnectionRefusedError)):
                 return False, f"Configuration or Connection Error: {type(e).__name__} - {e}"
            return False, f"An unexpected error occurred during WebSocket communication: {type(e).__name__} - {e}"

    async def get_status(self) -> Outcome:
        """
        Performs the module simulation health check.
        Returns status based on cached results or last known state.
        If no recent cached result exists and no other check is running,
        it acquires a lock and runs the simulation synchronously (blocking).
        """
        event_type = f"module_{self.MODULE_NUMBER}_simulation"
        lock_key = f"health_check_lock_{event_type}"
        now = timezone.now()
        cache_cutoff = now - timedelta(**self.WINDOW)

        logger.info(f"[Module {self.MODULE_NUMBER}] Running health check. Type: {event_type}")

        # --- Check for Cached Successful Run ---
        logger.debug(f"[Module {self.MODULE_NUMBER}] Checking for successful event since {cache_cutoff.isoformat()}")
        last_success_event = await database_sync_to_async(
            Event.objects.type(event_type)
            .filter(is_success=True, date_created__gt=cache_cutoff)
            .order_by('-date_created')
            .first,
            thread_sensitive=False
        )()

        if last_success_event:
            logger.info(f"[Module {self.MODULE_NUMBER}] Found recent successful event from {last_success_event.date_created.isoformat()}. Returning cached OK status.")
            return Outcome(
                instance=self,
                status=Status.OK,
                message=f"Module {self.MODULE_NUMBER} successful (cached result from {last_success_event.date_created.strftime('%H:%M:%S')})",
            )
        else:
             logger.info(f"[Module {self.MODULE_NUMBER}] No recent successful event found in cache window.")

        # --- Try to Acquire Lock ---
        logger.info(f"[Module {self.MODULE_NUMBER}] Attempting to acquire cache lock: {lock_key} (timeout: {self.LOCK_TIMEOUT_SECONDS}s)")
        acquired_lock = cache.add(lock_key, "running", timeout=self.LOCK_TIMEOUT_SECONDS)

        if acquired_lock:
            logger.info(f"[Module {self.MODULE_NUMBER}] Lock acquired: {lock_key}. Running live simulation check.")
            success = False
            message = ""
            status = Status.ERROR # Default to error unless success
            try:
                # --- Run the simulation directly ---
                if self.FILE_NAME is None:
                    logger.error(f"[Module {self.MODULE_NUMBER}] Internal configuration error: FILE_NAME is not defined.")
                    message = "Internal Error: FILE_NAME not defined for health check."
                    raise ValueError(message)

                base_file_name = f'health_check_files/{self.FILE_NAME}'
                logger.debug(f"[Module {self.MODULE_NUMBER}] Checking existence of base file: {base_file_name}")
                # Assume storage interaction is okay in async context for now
                file_exists = self.STORAGE.exists(base_file_name)

                if file_exists:
                    logger.info(f"[Module {self.MODULE_NUMBER}] Base file found. Generating presigned URL.")
                    # Assume storage interaction is okay in async context for now
                    file_url = self.STORAGE.generate_presigned_url_get(base_file_name)

                    logger.info(f"[Module {self.MODULE_NUMBER}] Running module simulation via _run_module.")
                    success, message = await self._run_module(base_file_name, file_url)
                    logger.info(f"[Module {self.MODULE_NUMBER}] Simulation run finished. Success: {success}, Message: {message}")
                else:
                    success = False
                    message = f"Base file '{base_file_name}' not found in storage for Module {self.MODULE_NUMBER} simulation."
                    logger.error(f"[Module {self.MODULE_NUMBER}] {message}")

                # Record the final result as an event
                logger.info(f"[Module {self.MODULE_NUMBER}] Recording simulation result event. Success: {success}")
                await database_sync_to_async(Event.objects.create, thread_sensitive=False)(
                    event_type=event_type,
                    is_success=success,
                    data={"message": message}
                )
                status = Status.OK if success else Status.ERROR

            except BaseException as e: # Catch BaseException to handle potential errors robustly
                success = False
                # Use existing message if available, otherwise format the exception
                if not message:
                     message = f"Module {self.MODULE_NUMBER} simulation check failed unexpectedly: {type(e).__name__} - {e}"
                logger.exception(f"[Module {self.MODULE_NUMBER}] Exception during live simulation run.")
                # Attempt to record the failure event
                try:
                    await database_sync_to_async(Event.objects.create, thread_sensitive=False)(
                        event_type=event_type,
                        is_success=False,
                        data={"error": message}
                    )
                except Exception as db_exc:
                    logger.error(f"[Module {self.MODULE_NUMBER}] Failed to record failure event after exception: {db_exc}")
                status = Status.ERROR # Ensure status is Error on exception

            finally:
                # Ensure the lock is released regardless of outcome
                logger.info(f"[Module {self.MODULE_NUMBER}] Releasing lock: {lock_key}")
                cache.delete(lock_key)
                logger.info(f"[Module {self.MODULE_NUMBER}] Live simulation run complete.")

            # Return the outcome of the live run
            return Outcome(
                instance=self,
                status=status,
                message=message,
            )

        else:
            # --- Lock Not Acquired: Return Last Known Status ---
            logger.warning(f"[Module {self.MODULE_NUMBER}] Lock NOT acquired ({lock_key}). Another check is likely running.")
            # Determine Last Completed Status (needed if lock not acquired)
            last_completed_event = await database_sync_to_async(
                Event.objects.type(event_type)
                .order_by('-date_created')
                .first,
                thread_sensitive=False
            )()

            if last_completed_event:
                status = Status.OK if last_completed_event.is_success else Status.ERROR
                last_message = last_completed_event.data.get('message', last_completed_event.data.get('error', 'No details available.'))
                logger.info(f"[Module {self.MODULE_NUMBER}] Returning status based on last completed event ({last_completed_event.date_created.isoformat()}). Status: {status}.")
                return Outcome(
                    instance=self,
                    status=status,
                    message=f"{last_message} (Result from {last_completed_event.date_created.strftime('%H:%M:%S')}; another check currently in progress)",
                )
            else:
                # Lock not acquired, and no prior completed state available
                logger.warning(f"[Module {self.MODULE_NUMBER}] Lock not acquired, and no prior completed state found. Returning WARNING status.")
                return Outcome(
                    instance=self,
                    status=Status.WARNING,
                    message=f"Module {self.MODULE_NUMBER} simulation check is already in progress, but no previous completed state is available.",
                )

    def get_resolving_actions(self, outcome: Outcome) -> str:
        return f"""# __CODE__ &mdash; {self.MODULE_NAME} failed

This check simulates a file generation with the chatbot via WebSocket to verify:
- The WebSocket server is reachable.
- The FSM works correctly.
- The FastAPI modules server is reachable.
- The file generation LLM is reachable.
- The file storage is reachable.

Note: Simulation runs in the background. Status reflects the last completed run.
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


class LLMCheck(HealthCheck):
    """
    Validates that the enabled LLM are working correctly.
    """

    # WINDOW = dict(minutes=2)
    WINDOW = dict(hours=1)

    def get_name(self) -> str:
        return "LLM Check"

    def get_status(self) -> Outcome:
        logger.info(f"[LLM Check] Running health check. Type: llm_call_complete")
        events = Event.objects.types(["llm_call_complete", "llm_call_start"]).within(**self.WINDOW)
        stats = events.stats()
        stats_str = disp_stats(stats)

        if stats["failure"]:
            errors = [e.data for e in events.filter(is_success=False)]
            return Outcome(
                instance=self,
                status=Status.ERROR,
                message=f"{stats_str} in the last {disp_window(self.WINDOW)}",
                extra={"errors": errors},
            )
        else:
            return Outcome(
                instance=self,
                status=Status.OK,
                message=f"{stats_str} in the last {disp_window(self.WINDOW)}",
            )

    def get_resolving_actions(self, outcome: Outcome) -> str:
        return """# __CODE__ &mdash; LLM failed

This check validates that the enabled LLM are working correctly.

## Possible causes

- The API key is invalid.
- The defined endpoint url is invalid.
- The model provider is down.
"""
    def suggest_reboot(self, outcome: Outcome) -> Sequence[str]:
        return []