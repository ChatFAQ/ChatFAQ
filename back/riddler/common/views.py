import json
import os

from asgiref.sync import async_to_sync
from rest_framework.response import Response
from rest_framework.views import APIView

from riddler.apps.broker.models import Message
from riddler.apps.broker.serializers import BasicMessageSerializer, ToMMLSerializer
from riddler.apps.fsm.lib import MachineContext
from riddler.apps.fsm.models import CachedMachine, FiniteStateMachine
import logging

from riddler.utils.logging_formatters import TIMESTAMP_FORMAT

logger = logging.getLogger(__name__)


class BotView(APIView, MachineContext):
    serializer_class: ToMMLSerializer = BasicMessageSerializer

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.machine = None

    def gather_fsm_name(self, data):
        raise NotImplemented("Implement a method that gathers the fsm name")

    def gather_conversation_id(self, mml: Message):
        raise NotImplemented("Implement a method that gathers the conversation id")

    def resolve_machine(self, request):
        self.machine = CachedMachine.build_cached_fsm(self)
        if not self.machine:
            if self.fsm_name is None:
                return False
            logger.debug(f"Starting new conversation ({self.conversation_id}), creating new FSM")
            fsm = FiniteStateMachine.objects.get(name=self.fsm_name)
            self.machine = fsm.build_machine(self)
            async_to_sync(self.machine.start)()
        else:
            logger.debug(f"Continuing conversation ({self.conversation_id}), reusing cached conversation's FSM ({self.machine.cachedmachine_set.first().updated_date.strftime(TIMESTAMP_FORMAT)})")
            async_to_sync(self.machine.next_state)()
        return True

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid():
            self.send_response(json.dumps(serializer.errors))
        else:
            mml = serializer.to_mml()
            self.set_conversation_id(self.gather_conversation_id(mml.conversation))
            self.set_fsm_name(self.gather_fsm_name(request.data))

            self.resolve_machine(request, mml)
            return Response({"ok": "POST request processed"})

    @staticmethod
    def send_response(*args, **kargs):
        raise NotImplemented(
            "Implement the 'send_response' method to your specific platform"
        )
