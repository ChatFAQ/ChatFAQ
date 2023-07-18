from enum import Enum


class MessageType(Enum):
    fsm_def = "fsm_def"
    rpc_request = "rpc_request"
    rpc_result = "rpc_result"
    llm_request = "llm_request"
    llm_request_result = "llm_request_result"
    error = "error"


class RPCNodeType(Enum):
    action = "action"
    condition = "condition"
