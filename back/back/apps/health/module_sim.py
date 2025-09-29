import asyncio
import json
import logging
import random

import requests
import websockets
from channels.db import database_sync_to_async
from django.conf import settings

from back.apps.broker.models.message import Conversation
from back.apps.health.models import Event
from back.config.storage_backends import select_private_storage

logger = logging.getLogger(__name__)

HANDSHAKE_TIMEOUT = 10.0
FILE_PROCESSING_TIMEOUT = 900.0  # 15 minutes
USER_ID = "2b84e03d-cb1e-48db-b79c-7c41372b98a3"  # Random UUID for the health check simulation
STORAGE = select_private_storage()
DEFAULT_FSM_DEF = "lefebvre_fsm"


async def _receive_json_message(websocket, timeout=10.0, timeout_message=None):
    """
    Helper method to receive a JSON message from the websocket.
    (Moved from ModuleSimulationBase)
    """
    message_text = ""
    try:
        message_text = await asyncio.wait_for(websocket.recv(), timeout)
        msg = json.loads(message_text)
        print(f"Received message: {msg}")
        return msg
    except asyncio.TimeoutError:
        if timeout_message:
            raise asyncio.TimeoutError(
                timeout_message + ". Last message: " + message_text
            )
        else:
            raise asyncio.TimeoutError(
                "Timeout waiting for message from server. Last message: " + message_text
            )
    except json.JSONDecodeError:
        raise ValueError(
            "Invalid JSON response from server. Last message: " + message_text
        )


async def _wait_for_initial_messages(websocket, num_messages=3):
    """
    Waits for initial messages, throwing an error if any indicate a problem.
    (Moved from ModuleSimulationBase)
    """
    for _ in range(num_messages):
        response = await _receive_json_message(websocket, timeout=HANDSHAKE_TIMEOUT)
        if response.get("status") == 400:
            raise ValueError(
                f"Error in initial message from WS: {response.get('payload')}"
            )


async def _run_single_module_simulation(
    module_number: int,
    module_name: str,
    file_name: str,
    conversation_id: int,
    fsm_def: str | None = None,
    state_overwrite: str | None = None,
):
    """
    Runs a file generation simulation for a single module.
    """
    # Use default values if not provided
    fsm_def = fsm_def or DEFAULT_FSM_DEF
    state_overwrite = state_overwrite  # Can be None

    auth_token = settings.BACKEND_TOKEN
    internal_ws_url = settings.INTERNAL_WS_URL
    if not auth_token:
        logger.error(f"[Module {module_number}] BACKEND_TOKEN is not set.")
        return False, "BACKEND_TOKEN is not set in settings"
    if not internal_ws_url:
        logger.error(f"[Module {module_number}] INTERNAL_WS_URL is not set.")
        return False, "INTERNAL_WS_URL is not set in settings"

    # Check base file exists
    base_file_name = f"health_check_files/{file_name}"
    logger.debug(
        f"[Module {module_number}] Checking existence of base file: {base_file_name}"
    )
    # Assume storage interaction is okay in async context for now
    file_exists = STORAGE.exists(base_file_name)

    if not file_exists:
        message = f"Base file '{base_file_name}' not found in storage for Module {module_number} simulation. Please upload a test file to the project S3 bucket in the health_check_files folder."
        logger.error(f"[Module {module_number}] {message}")
        return False, message

    logger.info(f"[Module {module_number}] Base file found. Generating presigned URL.")

    query_params = ""

    if auth_token:
        query_params = f"?token={auth_token}"
        if state_overwrite:
            query_params += f"&state_overwrite={state_overwrite}"
    elif state_overwrite:
        query_params = f"?state_overwrite={state_overwrite}"

    # Add metadata to query params, ensuring proper joining with '&' or '?'
    metadata_param = f'metadata={{"module":"{module_name}"}}'
    if query_params:
        query_params += f"&{metadata_param}"
    else:
        query_params = f"?{metadata_param}"

    uri = (
        internal_ws_url
        + "/back/ws/broker/"
        + str(conversation_id)
        + "/"
        + fsm_def
        + "/"
        + f"{USER_ID}/"
        + query_params
    )
    logger.info(f"[Module {module_number}] Connecting to WebSocket: {uri}")
    try:
        async with websockets.connect(uri, close_timeout=300) as websocket:
            logger.info(
                f"[Module {module_number}] WebSocket connected. Waiting for initial messages."
            )
            await _wait_for_initial_messages(websocket)
            logger.info(
                f"[Module {module_number}] Initial messages received. Sending file payload."
            )

            # Build and send the message payload.
            message = {
                "sender": {"type": "human", "platform": "WS", "id": USER_ID},
                "stack": [
                    {
                        "type": "file_uploaded",
                        "payload": {
                            "files": [
                                {
                                    "name": base_file_name.split("/")[
                                        -1
                                    ],  # just send the file name
                                    "s3_path": base_file_name,
                                }
                            ]
                        },
                    }
                ],
                "stack_id": "0",
                "stack_group_id": "0",
                "last": True,
            }
            await websocket.send(json.dumps(message))
            logger.info(
                f"[Module {module_number}] File payload sent. Waiting for responses."
            )

            # Process responses after sending the message.
            first_response = await _receive_json_message(
                websocket, timeout=HANDSHAKE_TIMEOUT
            )
            if first_response.get("status") == 400:
                error_payload = first_response.get("payload")
                logger.error(
                    f"[Module {module_number}] Error in initial response from WS: {error_payload}"
                )
                return False, f"Error in initial response from WS: {error_payload}"

            logger.info(
                f"[Module {module_number}] Initial response OK. Waiting for file processing response (timeout={FILE_PROCESSING_TIMEOUT}s)."
            )
            new_file_response = await _receive_json_message(
                websocket,
                timeout=FILE_PROCESSING_TIMEOUT,
                timeout_message="Timeout waiting for file processing",
            )
            logger.info(f"[Module {module_number}] File processing response received.")

            new_file_url = (
                new_file_response.get("stack", [{}])[0]
                .get("payload", {})
                .get("document_result", {})
                .get("file_url", "")
            )

            # Try to download the newly created file
            if new_file_url:
                logger.info(
                    f"[Module {module_number}] Received new file URL: {new_file_url}. Attempting download."
                )
                try:
                    response = requests.get(new_file_url, timeout=10)
                    response.raise_for_status()  # Raise an exception for 4XX/5XX responses
                    logger.info(
                        f"[Module {module_number}] Successfully downloaded generated file."
                    )
                    # Successfully downloaded the file
                except requests.exceptions.RequestException as e:
                    logger.error(
                        f"[Module {module_number}] Failed to download generated file: {e}. Response: {new_file_response}"
                    )
                    return (
                        False,
                        f"Failed to download the generated file: {str(e)}. Full response: {str(new_file_response)}",
                    )
            else:
                logger.error(
                    f"[Module {module_number}] No file URL provided in response: {new_file_response}"
                )
                return (
                    False,
                    "No file URL was provided in the response. Full response: "
                    + str(new_file_response),
                )

            logger.info(f"[Module {module_number}] Simulation completed successfully.")
            # Wait for the last message to be received
            last = False
            while not last:
                response = await _receive_json_message(
                    websocket, timeout=HANDSHAKE_TIMEOUT
                )
                if response.get("last"):
                    last = True
            return True, f"Module {module_number} simulation completed successfully."
    except websockets.exceptions.ConnectionClosedError as e:
        logger.error(
            f"[Module {module_number}] WebSocket connection closed unexpectedly: {e.code} {e.reason}"
        )
        return False, f"WebSocket connection closed unexpectedly: {e.code} {e.reason}"
    except asyncio.TimeoutError as e:
        logger.error(
            f"[Module {module_number}] Timeout occurred during WebSocket communication: {e}"
        )
        return False, f"Timeout occurred during WebSocket communication: {e}"
    except Exception as e:
        logger.exception(
            f"[Module {module_number}] Unexpected error during WebSocket communication."
        )  # Use logger.exception to include stack trace
        # Catch specific configuration errors if possible, otherwise generic
        if isinstance(e, (ValueError, ConnectionRefusedError)):
            return False, f"Configuration or Connection Error: {type(e).__name__} - {e}"
        return (
            False,
            f"An unexpected error occurred during WebSocket communication: {type(e).__name__} - {e}",
        )


async def run_module_simulation(
    module_number: int,
    module_name: str,
    file_name: str,
    fsm_def: str | None = None,
    state_overwrite: str | None = None,
):
    """
    Procrastinate task to run a module simulation and record the result.
    """
    event_type = f"module_{module_number}_simulation"
    conversation_id = int(random.random() * 1000000000)
    logger.info(f"[Task {event_type}] Starting simulation.")
    success = False
    message = "Task started but did not complete simulation logic."  # Default message
    try:
        success, message = await _run_single_module_simulation(
            module_number=module_number,
            module_name=module_name,
            file_name=file_name,
            conversation_id=conversation_id,
            fsm_def=fsm_def,
            state_overwrite=state_overwrite,
        )
        logger.info(f"[Task {event_type}] Simulation finished. Success: {success}")

    except Exception as e:
        success = False
        message = (
            f"Task failed unexpectedly during simulation: {type(e).__name__} - {e}"
        )
        logger.exception(f"[Task {event_type}] Exception during simulation run.")

    try:
        # Delete the conversation to not leave any traces of the simulation
        await delete_conversation(conversation_id)
    except Exception as e:
        logger.exception(f"[Task {event_type}] Exception during conversation deletion.")

    finally:
        await database_sync_to_async(Event.objects.create)(
            event_type=event_type,
            is_success=success,
            data={"message": message},
        )
        logger.info(f"[Task {event_type}] Recorded event. Success: {success}")


async def delete_conversation(conversation_id: int):
    """Synchronous function to delete a conversation by platform ID.
    We need to delete the conversation to not leave any traces of the simulation.
    """
    conv_to_delete = await database_sync_to_async(
        Conversation.objects.filter(platform_conversation_id=str(conversation_id)).first
    )()
    if conv_to_delete:
        logger.info(f"Deleting conversation with platform_id {conversation_id}")
        await database_sync_to_async(conv_to_delete.delete)()
        logger.info(f"Deleted conversation {conversation_id}")
    else:
        logger.warning(
            f"Conversation with platform_id {conversation_id} not found for deletion."
        )
