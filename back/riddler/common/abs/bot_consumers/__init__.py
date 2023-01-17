from abc import ABC
from logging import getLogger

from riddler.apps.broker.serializers.message import BotMessageSerializer
from riddler.apps.fsm.lib import FSMContext, FSM
from riddler.utils.custom_channels import CustomAsyncConsumer

logger = getLogger(__name__)


class BotConsumer(CustomAsyncConsumer, FSMContext, ABC):
    serializer_class = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.serializer_class is None or not issubclass(self.serializer_class, BotMessageSerializer):
            raise Exception("serializer_class should not be None on any BotConsumer and should implement "
                            "ToMMLSerializer methods")

        self.fsm: FSM = None

    @staticmethod
    def create_group_name(conversation_id):
        return f"bot_{conversation_id}"

    def get_group_name(self):
        return self.create_group_name(self.conversation_id)

    async def rpc_response(self, data: dict):
        self.fsm.rpc_result_future.set_result(data["payload"])

    async def disconnect(self, code=None):
        logger.debug(f"Disconnecting from conversation ({self.conversation_id}) (CODE: {code})")
        # Leave room group
        await self.channel_layer.group_discard(self.get_group_name(), self.channel_name)
