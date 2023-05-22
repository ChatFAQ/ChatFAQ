from typing import List, NamedTuple, Text

from .models import AgentType, Satisfaction


class QuickReply(NamedTuple):
    id: Text
    text: Text = None
    meta: Text = None


class Agent(NamedTuple):
    type: AgentType
    platform: Text = None
    first_name: Text = None
    last_name: Text = None


class Payload(NamedTuple):
    text: Text = None
    html: Text = None
    image: Text = None
    response_id: Text = None
    satisfaction: Satisfaction = None
    meta: dict = {}
    quick_replies: List[QuickReply] = []


class Message(NamedTuple):
    conversation: Text
    sender: Agent
    payload: List[Payload]
    send_time: int
    confidence: float = 1
    threshold: float = 0
    meta: dict = {}
