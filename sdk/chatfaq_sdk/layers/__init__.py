from logging import getLogger
from typing import Dict, List
from uuid import uuid4

from pydantic import BaseModel

logger = getLogger(__name__)


class Layer:
    """
    Representation of all the future stack's layers. Implementing a new layer should inherit form this
    """

    _type = None
    _streaming = False

    def __init__(self, allow_feedback=True, state={}):
        self.allow_feedback = allow_feedback
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
                r["meta"]["allow_feedback"] = self.allow_feedback
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
        super().__init__(allow_feedback=False)
        self.tag = tag

    async def build_payloads(self, ctx, data):
        payload = {"payload": self.tag}
        yield [payload], True


class StarRating(Layer):
    """
    A message layer that includes a star rating.
    """
    _type = "star_rating"

    def __init__(
        self,
        content: str,
        num_stars: int,
        explanation: str = None,
        *args,
        **kwargs,
    ):
        """
        :param content: The content of the message.
        :param num_stars: The maximum number of stars. For example: 5
        :param explanation: An optional explanation to explain the rating. For example: "1 is negative, 5 is positive"
        """
        super().__init__(*args, **kwargs)
        self.content = content
        self.num_stars = num_stars
        self.explanation = explanation

    async def build_payloads(self, ctx, data):
        payload = {
            "payload": {
                "content": self.content,
                "num_stars": self.num_stars,
                "explanation": self.explanation,
            }
        }
        yield [payload], True


class TextFeedback(Layer):
    """
    A message layer that includes a feedback text box.
    """
    _type = "text_feedback"

    def __init__(
        self,
        content: str,
        hint: str = None,
        *args,
        **kwargs,
    ):
        """
        :param content: The content of the message.
        :param hint: An optional hint to explain what to put in the text box. For example: "Please provide your feedback here"
        """
        super().__init__(*args, **kwargs)
        self.content = content
        self.hint = hint

    async def build_payloads(self, ctx, data):
        payload = {
            "payload": {
                "content": self.content,
                "hint": self.hint,
            }
        }
        yield [payload], True