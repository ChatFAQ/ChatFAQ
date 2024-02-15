
PROMPT_TOO_LONG_ERROR = "It's not possible to process your request because the prompt is too long. Please open a new conversation and try again with a shorter prompt."
MODEL_NOT_FOUND_ERROR = "There was an error processing your request because the LLM was not found. Contact the administrator."
REQUEST_ERROR = "There was an error processing your request. Please try again or contact the administrator."

class PromptTooLongException(Exception):
    def __init__(self, message=PROMPT_TOO_LONG_ERROR):
        self.message = message
        super().__init__(self.message)

class ModelNotFoundException(Exception):
    def __init__(self, message=MODEL_NOT_FOUND_ERROR):
        self.message = message
        super().__init__(self.message)

class RequestException(Exception):
    def __init__(self, message=REQUEST_ERROR):
        self.message = message
        super().__init__(self.message)

    