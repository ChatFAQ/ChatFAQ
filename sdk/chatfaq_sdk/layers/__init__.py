from logging import getLogger
from typing import List
from uuid import uuid4

logger = getLogger(__name__)


class Layer:
    """
    Representation of all the future stack's layers. Implementing a new layer should inherit form this
    """

    _type = None
    _streaming = False

    def __init__(self, state={}):
        self.state = state
        self.stack_id = str(uuid4())

    async def build_payloads(self, ctx, data) -> tuple[List[dict], bool]:
        """
        Used to represent the layer as a dictionary which will be sent through the WS to the ChatFAQ's back-end server
        It is cached since there are layers as such as the LMGeneratedText which are computationally expensive
        :return:
            dict
                A json compatible dict
            bool
                If it is the last stack's layer or there are more stacks
        """
        raise NotImplementedError

    async def result(self, ctx, data, fsm_def_name: str = None) -> List[dict]:
        repr_gen = self.build_payloads(ctx, data)
        async for _repr, last_chunk in repr_gen:
            for r in _repr:
                r["type"] = self._type
                r["streaming"] = self._streaming
                r["meta"] = {}
                r["state"] = self.state
                if fsm_def_name:
                    r["fsm_definition"] = fsm_def_name
            yield [_repr, self.stack_id, last_chunk]


class Message(Layer):
    """
    A flexible message layer that can include text, references, tool calls, and other metadata.
    """

    _type = "message"

    def __init__(
        self,
        content,
        references={},
        tool_calls=[],
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.content = content
        self.references = references
        self.tool_calls = tool_calls

    async def build_payloads(self, ctx, data):
        payload = {
            "payload": {
                "content": self.content,
                "references": self.references,
                "tool_calls": self.tool_calls,
            }
        }
        yield [payload], True


class FileUpload(Layer):
    """
    A message layer that includes a file upload request.
    """
    _type = "file_upload"

    def __init__(
        self,
        content,
        file_extensions=[],
        max_size=0,
        *args,
        **kwargs,
    ):
        """
        :param file_extensions: A list of file extensions to request. For example: ["pdf", "xml"]
        :param max_size: The maximum size of the file to request in bytes. For example: 50 * 1024 * 1024 (50MB)
        """
        super().__init__(*args, **kwargs)
        self.content = content
        self.file_extensions = file_extensions
        self.max_size = max_size

    async def build_payloads(self, ctx, data):
        _payload = {
            "content": self.content,
            "files": {
                file_extension: {
                    "max_size": self.max_size,
                }
                for file_extension in self.file_extensions
            },
        }

        yield [{"payload": _payload}], True


class FileDownload(Layer):
    """
    A message layer that includes a file download.
    """
    _type = "file_download"

    def __init__(
            self,
            content: str,
            file_name: str,
            file_url: str,
            *args,
            **kwargs,
    ):
        """
        :param file_name: The name of the file. For example: "report.pdf"
        :param file_url: The URL of the file where the user can download it or visualize it. For example: "https://example.com/report.pdf"
        """
        super().__init__(*args, **kwargs)
        self.content = content
        self.file_name = file_name
        self.file_url = file_url

    async def build_payloads(self, ctx, data):
        payload = {
            "payload": {
                    "content": self.content,
                    "name": self.file_name,
                    "url": self.file_url,
            }
        }
        yield [payload], True


class StreamingMessage(Layer):
    _type = "message_chunk"
    _streaming = True

    def __init__(
        self,
        generator,
        references={},
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.generator = generator
        self.references = references

    async def build_payloads(self, ctx, data):
        async for chunk in self.generator:
            last_chunk = chunk.get("last_chunk", False)
            tool_calls = chunk.get("tool_calls", [])
            if last_chunk:  # now we send the references only in the final message
                payload = {
                    "payload": {
                        "content": chunk.get("content"),
                        "references": self.references,
                        "tool_calls": tool_calls,
                    }
                }
                yield (
                    [payload],
                    last_chunk,
                )
                break

            else:
                yield (
                    [
                        {
                            "payload": {
                                "content": chunk.get("content"),
                                "tool_calls": tool_calls,
                            }
                        }
                    ],
                    last_chunk,
                )


class GTMTag(Layer):
    _type = "gtm_tag"

    def __init__(self, tag):
        super().__init__()
        self.tag = tag

    async def build_payloads(self, ctx, data):
        payload = {"payload": self.tag}
        yield [payload], True


class UserFeedback(Layer):
    """
    An abstract class to inherit from for feedback layers representing common feedback elements.
    """

    def __init__(
        self,
        hint: str = None,
        merge_to_prev: bool = False,
        full_conversation: bool = False,
        *args,
        **kwargs,
    ):
        """
        :param hint: A text to explain the rating. For example: "Please rate the service"
        :param merge_to_prev: It controls whether the feedback should be merged (UI wise) with the previous message (default: False)
        :param full_conversation: Feedback reference always the last not feedback message from the bot, but they could reference to the whole conversation (default: False)
        """
        super().__init__(*args, **kwargs)
        self.hint = hint
        self.merge_to_prev = merge_to_prev
        self.full_conversation = full_conversation

    def _build_payloads(self):
        return {
            "hint": self.hint,
            "merge_to_prev": self.merge_to_prev,
            "full_conversation": self.full_conversation,
        }


class StarRating(UserFeedback):
    """
    A message layer that includes a star rating.
    """
    _type = "star_rating"

    def __init__(
        self,
        num_stars: int,
        placeholder: str,
        *args,
        **kwargs,
    ):
        """
        :param num_stars: The maximum number of stars. For example: 5
        """
        super().__init__(*args, **kwargs, merge_to_prev=False)
        self.placeholder = placeholder
        self.num_stars = num_stars

    async def build_payloads(self, ctx, data):
        payload = {
            "payload": {
                **self._build_payloads(),
                "num_stars": self.num_stars,
            }
        }
        yield [payload], True


class ThumbsRating(UserFeedback):
    """
    A message layer that includes a thumbs rating.
    """
    _type = "thumbs_rating"

    def __init__(
        self,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs, merge_to_prev=True)

    async def build_payloads(self, ctx, data):
        payload = {
            "payload": {
                **self._build_payloads(),
            }
        }
        yield [payload], True


class TextFeedback(UserFeedback):
    """
    A message layer that includes a feedback text box.
    """
    _type = "text_feedback"

    def __init__(
        self,
        placeholder: str,
        *args,
        **kwargs,
    ):
        """
        :param placeholder: The placeholder text inside the text box. For example: "Please provide your feedback here"
        """
        super().__init__(*args, **kwargs, merge_to_prev=False)
        self.placeholder = placeholder

    async def build_payloads(self, ctx, data):
        payload = {
            "payload": {
                **self._build_payloads(),
                "placeholder": self.placeholder,
            }
        }
        yield [payload], True


class CloseConversation(Layer):
    """
    A message layer that includes a close conversation request.
    """
    _type = "close_conversation"

    async def build_payloads(self, ctx, data):
        yield [{"payload": {}}], True


class ToolUse(Layer):
    """
    A message layer that includes a tool use request.
    """
    _type = "tool_use"

    def __init__(self, name: str = None, id: str = None, args: dict = None):
        super().__init__()
        self.id = id
        self.name = name
        self.args = args

    async def build_payloads(self, ctx, data):
        payload = {
            "payload": {
                "id": self.id,
                "name": self.name,
                "args": self.args,
            }
        }
        yield [payload], True

class ToolResult(Layer):
    """
    A message layer that includes a tool result.
    """
    _type = "tool_result"

    def __init__(self, id: str = None, name: str = None, result: dict = None):
        super().__init__()
        self.id = id
        self.name = name
        self.tool_result = result

    async def build_payloads(self, ctx, data):
        payload = {
            "payload": {
                "id": self.id,
                "name": self.name,
                "result": self.tool_result,
            }
        }
        yield [payload], True
