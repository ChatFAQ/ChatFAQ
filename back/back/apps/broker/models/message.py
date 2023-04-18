import itertools

from enum import Enum

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Q

from back.common.models import ChangesMixin


class Satisfaction(Enum):
    positive = "positive"
    negative = "negative"
    neutral = "neutral"


class AgentType(Enum):
    human = "human"
    bot = "bot"


class StackPayloadType(Enum):
    text = "text"
    html = "html"
    image = "image"
    satisfaction = "satisfaction"
    quick_replies = "quick_replies"


class Message(ChangesMixin):
    """
    The representation of the MML as a Django model

    Attributes
    ----------
    prev: str
        The id of the previous MML, typically to which this one answers. Thanks to this we can reconstruct the whole
         conversation in order.
    transmitter: JSONField
        The type of agent (human/bot) that generated this message.
        * first_name str:
            The first name of the sending agent
        * last_name str:
            The last name of the sending agent
        * type str:
            Its type: bot or human
    receiver: JSONField
        The agent to which this message is intended. Is this property ****required? Could it be the transmitter is
        entirely unknown to whom is communicating?
    conversation: str
        A unique identifier that groups all the messages sent within the same conversation.
         There is no Conversation model, instead, a conversation is represented by the group of
         messages that share the same 'conversation' value, and their order is determined by
         the 'prev' attribute.
    conversation_name: str
        A name that describes the conversation. Since a conversation is a virtual concept
         that does not have its own entity, this property is held by the first message in the
         conversation, which has 'prev' set to null.
    send_time: str
        The moment at which this message was sent.
    confidence: float
        How certain the bot is about its answer (required when transmitter = bot)
    threshold: float
        The minimal confidence the user would accept from the bot (required when transmitter = human)
    meta: JSONField
        any extra info out of the bot domain the agen considers to put in
    stacks: list
        contains the payload of the message itself.
        * text str:
            Plain text
        * html str:
            HTML that should be interpreted
        * image str:
            Image content
        * quick_replies JSONField:
            A list of CTAs. If this field is present it needs to contain at least 1 item. It is assumed that if it only contains an **id** it would mean is a response (a choose quick_replied) of a previous MML, being this id the same as the choose CTA
            * text str:
                The text to display on the CTA button
            * id str:
                an identifier to use later on as a reference in the response
            * meta JSONField:
                any extra info out of the bot domain the agen considers to put in
        * response_id str:
            In case the response is an indexed item on a database (as such the answer of a FAQ)
        * satisfaction str:
            For the user to express its satisfaction to the given bot’s answer
    """

    prev = models.ForeignKey("self", null=True, unique=True, on_delete=models.SET_NULL)
    transmitter = models.JSONField()
    receiver = models.JSONField(null=True)
    conversation = models.CharField(max_length=255)
    conversation_name = models.CharField(max_length=255, null=True)
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
    stacks = models.JSONField(null=True)

    def cycle_fsm(self):
        pass

    def get_chain(self, chain=None):
        chain = chain if chain else []
        # chain.append(MessageSerializer(self).data)
        chain.append(self)
        _next = Message.objects.filter(prev=self).first()
        if _next:
            return _next.get_chain(chain)
        return chain

    def to_text(self):
        stacks_text = '\n'.join([s["payload"] for s in itertools.chain(*self.stacks)])
        return f"{self.send_time.strftime('[%Y-%m-%d %H:%M:%S]')} {self.transmitter['type']}: {stacks_text}"

    @classmethod
    def get_first_msg(cls, conversation_id):
        return cls.objects.filter(
            prev__isnull=True,
            conversation=conversation_id,
        ).first()

    @classmethod
    def get_mml_chain(cls, conversation_id):
        from back.apps.broker.serializers.messages import MessageSerializer  # TODO: CI

        first_message = cls.get_first_msg(conversation_id)

        if not first_message:
            return []
        return [MessageSerializer(m).data for m in first_message.get_chain()]

    @classmethod
    def delete_conversation(cls, conversation_id):
        return cls.objects.filter(
            conversation=conversation_id,
        ).delete()

    @classmethod
    def delete_conversations(cls, conversation_ids):
        return cls.objects.filter(
            conversation__in=conversation_ids,
        ).delete()

    @classmethod
    def conversations_info(cls, transmitter__id):
        conversations = (
            cls.objects.filter(Q(transmitter__identifier=transmitter__id) | Q(receiver__identifier=transmitter__id))
            .values("conversation")
            .distinct()
            .all()
        )

        first_messages = cls.objects.values_list("conversation", "created_date").filter(
            prev__isnull=True,
            conversation__in=conversations,
        ).order_by("-created_date")

        return list(first_messages.all())

    @classmethod
    def conversation_to_text(cls, conversation_id):
        text = ""
        first_message = cls.get_first_msg(conversation_id)
        msgs = first_message.get_chain()

        for msg in msgs:
            text = f"{text}{msg.to_text()}\n"

        return text

    @classmethod
    def get_last_mml(cls, conversation_id):
        return cls.objects.filter(conversation=conversation_id).order_by("-created_date").first()

    def save(self, *args, **kwargs):
        self.prev = Message.get_last_mml(self.conversation)
        super(Message, self).save(*args, **kwargs)
