import json
import logging
from django.db import transaction

from asgiref.sync import async_to_sync
from rest_framework.response import Response
from rest_framework.views import APIView

from riddler.apps.broker.models.message import Message
from riddler.apps.broker.serializers.message import BasicMessageSerializer, ToMMLSerializer
from riddler.apps.fsm.lib import FSMContext
from riddler.apps.fsm.models import CachedFSM, FSMDefinition
from riddler.utils.logging_formatters import TIMESTAMP_FORMAT

logger = logging.getLogger(__name__)


class BotView(APIView, FSMContext):
    """
    Abstract class all views representing an HTTP bot should inherit from,
    it takes care of the initialization and management of the fsm and
    the persistence of the sending/receiving MMLs into the database
    """
    serializer_class: ToMMLSerializer = BasicMessageSerializer

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fsm = None

    def gather_platform_config(self, request):
        raise NotImplemented("Implement a method that gathers the fsm name")

    def gather_conversation_id(self, mml: Message):
        raise NotImplemented("Implement a method that gathers the conversation id")

    def resolve_fsm(self):
        """
        It will try to get a cached FSM from a provided name or create a new one in case
        there is no one yet (when is a brand-new conversation_id)
        Returns
        -------
        bool
            Whether or not it was able to create (new) or retrieve (cached) a FSM.
            If returns False most likely it is going be because a wrongly provided FSM name
        """
        self.fsm = CachedFSM.build_fsm(self)
        if not self.fsm:
            if self.platform_config is None:
                return False
            logger.debug(
                f"Starting new conversation ({self.conversation_id}), creating new FSM"
            )
            self.fsm = self.platform_config.fsm_def.build_fsm(self)
            async_to_sync(self.fsm.start)()
        else:
            logger.debug(
                f"Continuing conversation ({self.conversation_id}), reusing cached conversation's FSM ({CachedFSM.get_conv_updated_date(self)})"
            )
            async_to_sync(self.fsm.next_state)()
        return True

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid():
            self.send_response(json.dumps(serializer.errors))
        else:
            mml = serializer.to_mml()
            self.set_conversation_id(self.gather_conversation_id(mml.conversation))
            self.set_platform_config(self.gather_platform_config(request))

            with transaction.atomic():
                self.resolve_fsm()
            return Response({"ok": "POST request processed"})

    @staticmethod
    def send_response(*args, **kargs):
        raise NotImplemented(
            "Implement the 'send_response' method to your specific platform"
        )
