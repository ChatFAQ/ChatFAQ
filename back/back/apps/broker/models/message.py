from logging import getLogger
from enum import Enum

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Q
from django.contrib.postgres.fields import ArrayField

from back.common.models import ChangesMixin

logger = getLogger(__name__)


class Satisfaction(Enum):
    positive = "positive"
    negative = "negative"
    neutral = "neutral"


class AgentType(Enum):
    human = "human"
    bot = "bot"


class StackPayloadType(Enum):
    text = "text"
    lm_generated_text = "lm_generated_text"
    html = "html"
    image = "image"
    satisfaction = "satisfaction"
    quick_replies = "quick_replies"


class AdminReviewValue(Enum):
    positive = "positive"
    negative = "negative"
    alternative = "alternative"


class Conversation(ChangesMixin):
    """
    Table that holds the conversation information, all messages that belong to the same conversation will have the same conversation_id
    """

    platform_conversation_id = models.CharField(max_length=255, unique=True)
    name = models.CharField(max_length=255, null=True, blank=True)

    def get_first_msg(self):
        return Message.objects.filter(
            prev__isnull=True,
            conversation=self,
        ).first()

    def get_mml_chain(self, as_conv_format=False):
        from back.apps.broker.serializers.messages import MessageSerializer  # TODO: CI
        first_message = self.get_first_msg()

        if not first_message:
            return []
        chain = first_message.get_chain()

        if as_conv_format:
            return self.get_formatted_conversation(chain)

        return [MessageSerializer(m).data for m in chain]

    def get_last_mml(self):
        return (
            Message.objects.filter(conversation=self).order_by("-created_date").first()
        )

    def get_formatted_conversation(self, chain):
        '''
        Returns a list of messages in the format of the conversation LLMs.
        '''
        messages = []
        human_messages_ids = []

        bot_content = ""
        for m in chain[1:]:  # skip predefined message
            if m.sender['type'] == 'human':
                if bot_content != "":  # when human message, add bot message before
                    messages.append({'role': 'assistant', 'content': bot_content})
                    bot_content = ""

                messages.append({'role': 'user', 'content': m.stack[0]['payload']})
                human_messages_ids.append(m.id)
            elif m.sender['type'] == 'bot':
                bot_content += m.stack[0]['payload']['model_response']

        if bot_content != "":  # last message
            messages.append({'role': 'assistant', 'content': bot_content})

        return messages, human_messages_ids

    def group_by_stack(self, chain):
        '''
        returns the chain but with the bot messages stack[0].payload of the same stack_id concatenated.
        '''
        from back.apps.broker.serializers import MessageSerializer

        def _stack_el(m):
            el = m['stack']
            while type(el) is list:
                el = el[0]
            return el

        grouped_chain = []
        for m in chain:
            m = MessageSerializer(m).data
            first_stack_el = _stack_el(m)

            if m['sender']['type'] == 'human':
                grouped_chain.append(m)
            elif m['sender']['type'] == 'bot' and first_stack_el['type'] == StackPayloadType.text.value:
                grouped_chain.append(m)
            elif m['sender']['type'] == 'bot' and first_stack_el['type'] == StackPayloadType.lm_generated_text.value:
                if len(grouped_chain) > 0 and grouped_chain[-1]['sender']['type'] == 'bot' and \
                    grouped_chain[-1]['stack'][0]['type'] == StackPayloadType.lm_generated_text.value and \
                    grouped_chain[-1]['stack_id'] == m['stack_id']:
                    grouped_chain[-1]['stack'][0]['payload']['model_response'] += first_stack_el['payload'][
                        'model_response']
                else:
                    grouped_chain.append(m)

                if m['last']:
                    grouped_chain[-1]['last'] = m['last']
                    grouped_chain[-1]['id'] = m['id']
                    grouped_chain[-1]['stack'][0]['payload']['references'] = first_stack_el['payload']['references']
        return grouped_chain

    @classmethod
    def conversations_from_sender(cls, sender_id):
        conversations = (
            cls.objects.filter(
                Q(message__sender__id=sender_id) | Q(message__receiver__id=sender_id)
            )
            .distinct()
            .order_by("-created_date")
        )

        return list(conversations.all())

    def conversation_to_text(self):
        text = ""
        msgs = self.get_mml_chain()

        for msg in msgs:
            text = f"{text}{Message._to_text(msg['stack'], msg['send_time'], msg['sender'])}\n"

        return text

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if not self.name:
            self.name = self.created_date.strftime("%Y-%m-%d_%H-%M-%S")
            super().save(update_fields=["name"])


class Message(ChangesMixin):
    """
    The representation of the MML as a Django model

    Attributes
    ----------
    prev: str
        The id of the previous MML, typically to which this one answers. Thanks to this we can reconstruct the whole
         conversation in order.
    sender: JSONField
        The type of agent (human/bot) that generated this message.
        * first_name str:
            The first name of the sending agent
        * last_name str:
            The last name of the sending agent
        * type str:
            Its type: bot or human
    receiver: JSONField
        The agent to which this message is intended. Is this property ****required? Could it be the sender is
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
        How certain the bot is about its answer (required when sender = bot)
    threshold: float
        The minimal confidence the user would accept from the bot (required when sender = human)
    meta: JSONField
        any extra info out of the bot domain the agen considers to put in
    stack: list
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
    stack_id: str
        The id of the stack to which this message belongs to. This is used to group stacks
    last: bool
        Whether this message is the last one of the stack_id
    """

    conversation = models.ForeignKey("Conversation", on_delete=models.CASCADE)
    prev = models.OneToOneField("self", null=True, on_delete=models.SET_NULL)
    sender = models.JSONField()
    receiver = models.JSONField(null=True)
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
    stack = models.JSONField(null=True)
    stack_id = models.CharField(max_length=255, null=True)
    last = models.BooleanField(default=False)

    def cycle_fsm(self):
        pass

    def get_chain(self):
        next_msg = self
        chain = []
        while next_msg and next_msg not in chain:
            chain.append(next_msg)
            next_msg = Message.objects.filter(prev=next_msg).first()
        return chain

    def to_text(self):
        return self._to_text(self.stack, self.send_time.strftime('[%Y-%m-%d %H:%M:%S]'), self.sender)

    @staticmethod
    def _to_text(stack, send_time, sender):
        stack_text = ""
        for layer in stack:
            if layer["type"] == StackPayloadType.text.value:
                stack_text += layer["payload"] + "\n"
            elif layer["type"] == StackPayloadType.lm_generated_text.value:
                if layer["payload"]["model_response"]:
                    stack_text += layer["payload"]["model_response"]
            else:
                logger.error(f"Unknown stack payload type to export as csv: {layer['type']}")

        return f"{send_time} {sender['type']}: {stack_text}"

    def save(self, *args, **kwargs):
        if not self.prev: # avoid setting prev to itself if model is being updated
            self.prev = self.conversation.get_last_mml()
        super(Message, self).save(*args, **kwargs)


class UserFeedback(ChangesMixin):
    VALUE_CHOICES = (
        ("positive", "Positive"),
        ("negative", "Negative"),
    )
    message = models.OneToOneField(
        Message, null=True, unique=True, on_delete=models.SET_NULL
    )
    value = models.CharField(max_length=255, choices=VALUE_CHOICES)

    feedback_selection = ArrayField(models.TextField(), null=True, blank=True)
    feedback_comment = models.TextField(null=True, blank=True)


class AdminReview(ChangesMixin):
    VALUE_CHOICES = (
        (0, 0),
        (1, 1),
        (2, 2),
        (3, 3),
        (4, 4),
    )
    REVIEW_TYPES = (
        ("alternative_answer", "Alternative Answer"),
        ("review", "Review"),
    )
    message = models.OneToOneField(
        Message, null=True, unique=True, on_delete=models.SET_NULL
    )
    ki_review_data = models.JSONField(null=True, blank=True, default=list)
    gen_review_msg = models.TextField(null=True, blank=True)
    gen_review_val = models.IntegerField(null=True, choices=VALUE_CHOICES)
    gen_review_type = models.CharField(null=True, blank=True, max_length=255, choices=REVIEW_TYPES)
