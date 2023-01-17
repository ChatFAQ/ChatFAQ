from enum import Enum


class MessageType(Enum):
    fsm_def = "fsm_def"
    rpc_request = "rpc_request"
    rpc_result = "rpc_result"
    error = "error"
