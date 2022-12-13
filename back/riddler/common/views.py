import json
import os

from asgiref.sync import async_to_sync
from rest_framework.response import Response
from rest_framework.views import APIView

from api.broker.serializers import BasicMessageSerializer, ToMMLSerializer
from api.fsm.lib import MachineContext
from api.fsm.models import CachedMachine, FiniteStateMachine


class BotView(APIView, MachineContext):
    serializer_class: ToMMLSerializer = BasicMessageSerializer

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.machine = None

    def get_fsm_name(self, data):
        raise NotImplemented("Implement a method that gathers the fsm name")

    def resolve_machine(self, request, mml):
        self.machine = CachedMachine.build_cached_fsm(self)
        if not self.machine:
            fsm_name = self.get_fsm_name(request.data)
            if fsm_name is None:
                return False
            self.set_fsm_name(fsm_name)
            fsm = FiniteStateMachine.objects.get(name=self.get_fsm_name(request.data))
            self.machine = fsm.build_machine(self)
            async_to_sync(self.machine.start)()
        else:
            async_to_sync(self.machine.next_state)()
        return True

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid():
            self.send_response(json.dumps(serializer.errors))
        else:
            mml = serializer.to_mml()
            self.set_conversation_id(mml.conversation)

            self.resolve_machine(request, mml)
            return Response({"ok": "POST request processed"})

    @staticmethod
    def send_response(*args, **kargs):
        raise NotImplemented(
            "Implement the 'send_response' method to your specific platform"
        )
