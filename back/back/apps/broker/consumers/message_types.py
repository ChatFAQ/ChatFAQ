from enum import Enum


class RPCMessageType(Enum):
    fsm_def = "fsm_def"
    rpc_request = "rpc_request"
    rpc_result = "rpc_result"
    llm_request = "llm_request"
    llm_request_result = "llm_request_result"
    retriever_request = "retriever_request"
    retriever_request_result = "retriever_request_result"
    error = "error"


class ParseMessageType(Enum):
    register_parsers = "register_parsers"
    parser_result_ki = "parser_result_ki"
    parser_finished = "parser_finished"
    error = "error"


class RPCNodeType(Enum):
    action = "action"
    condition = "condition"
