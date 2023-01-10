import json
from logging import getLogger

from channels.generic.websocket import AsyncJsonWebsocketConsumer
from riddler.apps.broker.serializers.rpc import RPCResponseSerializer
from riddler.apps.fsm.serializers import FSMSerializer
from riddler.common.consumers import AbsBotConsumer
from riddler.utils import WSStatusCodes

logger = getLogger(__name__)


class RPCConsumer(AsyncJsonWebsocketConsumer):
    """
    The consumer in responsible for keeping the connection of the Remote Procedure Calls servers and associate it to a
    FSM definition. Any state/transition declared on the FSM unknown to the system will be considered a RCP and piped it
     to the corresponding connection.
    """
    serializer_class = FSMSerializer

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fsm_id = None

    @staticmethod
    def create_group_name(fsm_id):
        return f"rpc_{fsm_id}"

    def get_group_name(self):
        return self.create_group_name(self.fsm_id)

    async def connect(self):
        self.fsm_id = self.scope["url_route"]["kwargs"].get("fsm_id")
        if self.fsm_id is None:
            logger.debug("New RPC WS Connection without fsm_id, the fsm definition will have to be declared later on "
                         "with a 'set_fsm' command")
        await self.channel_layer.group_add(self.get_group_name(), self.channel_name)
        await self.accept()
        logger.debug(
            f"Starting new RPC WS connection (channel group: {self.get_group_name()})"
        )

    async def disconnect(self, close_code):
        logger.debug(f"Disconnecting from RPC consumer")
        # Leave room group
        await self.channel_layer.group_discard(self.conversation_id, self.channel_name)

    async def receive_json(self, content, **kwargs):
        serializer = RPCResponseSerializer(data=content)
        serializer.is_valid(raise_exception=True)
        data = {
            "type": "rpc_response",
            "status": WSStatusCodes.ok.value,
            "payload": serializer.data["payload"]
        }
        conversation_id = content["ctx"]["conversation_id"]
        await self.channel_layer.group_send(AbsBotConsumer.create_group_name(conversation_id), data)

    async def response(self, data: dict):
        if not WSStatusCodes.is_ok(data["status"]):
            await self.send(json.dumps(data))
        data = {
            **data["payload"],
            "status": data["status"]
        }
        await self.send(json.dumps(data))
