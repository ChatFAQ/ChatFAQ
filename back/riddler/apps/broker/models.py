from enum import Enum

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from riddler.common.models import ChangesMixin


class Satisfaction(Enum):
    positive = "positive"
    negative = "negative"
    neutral = "neutral"


class AgentType(Enum):
    human = "human"
    bot = "bot"


class Message(ChangesMixin):
    """
    ivar str prev: The id of the previous MML, typically to which this one answers. Thanks to this we can reconstruct the whole conversation in order.
    ivar JSONField transmitter: The type of agent (human/bot) that generated this message.
        str first_name: The first name of the sending agent
        str last_name: The last name of the sending agent
        str type: Its type: bot or human
    ivar JSONField receiver: The agent to which this message is intended. Is this property ****required? Could it be the transmitter is entirely unknown to whom is communicating?
    ivar str conversation: A unique identifier that groups all the messages sent within the same context.
    ivar str send_time: The moment at which this message was sent.
    ivar float confidence: How certain the bot is about its answer (required when transmitter = bot)
    ivar float threshold: The minimal confidence the user would accept from the bot (required when transmitter = human)
    ivar JSONField meta: any extra info out of the bot domain the agen considers to put in
    ivar JSONField payload: contains the payload of the answer or question of the agent, it needs to have at least one item but it could contain an indefinite number of them.
        str text: Plain text
        str html: HTML that should be interpreted
        str image: Image content
        JSONField quick_replies: A list of CTAs. If this field is present it needs to contain at least 1 item. It is assumed that if it only contains an **id** it would mean is a response (a choose quick_replied) of a previous MML, being this id the same as the choose CTA
            str text: The text to display on the CTA button
            str id: an identifier to use later on as a reference in the response
            JSONField meta: any extra info out of the bot domain the agen considers to put in
        str response_id: In case the response is an indexed item on a database (as such the answer of a FAQ)
        str satisfaction: For the user to express its satisfaction to the given bot’s answer
    """

    prev = models.ForeignKey("self", null=True, unique=True, on_delete=models.SET_NULL)
    transmitter = models.JSONField()
    receiver = models.JSONField(null=True)
    conversation = models.CharField(max_length=255)
    send_time = models.DateTimeField()
    confidence = models.FloatField(
        null=True,
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
    )
    threshold = models.FloatField(
        null=True,
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
    )
    meta = models.JSONField(null=True)
    payload = models.JSONField(null=True)

    def cycle_fsm(self):
        pass
