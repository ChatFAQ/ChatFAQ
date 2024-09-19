from logging import getLogger
from typing import Dict, List

from pydantic import BaseModel
from uuid import uuid4

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

    def __init__(self, content, references={}, tool_calls=[], *args, **kwargs):
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


class StreamingMessage(Layer):
    _type = "message_chunk"
    _streaming = True

    def __init__(self, generator, references={}, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.generator = generator
        self.references = references

    async def build_payloads(self, ctx, data):
        async for chunk in self.generator:
            last_chunk = chunk.get("last_chunk", False)
            tool_calls = chunk.get("tool_calls", [])
            if last_chunk:  # now we send the references only in the final message
                yield (
                    [
                        {
                            "payload": {
                                "content": chunk.get("content"),
                                "references": self.references,
                                "tool_calls": tool_calls,
                            }
                        }
                    ],
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
