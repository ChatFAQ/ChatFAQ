from asgiref.sync import sync_to_async

from riddler.apps.broker.models.rpc import RPCResponse


class RPCResponseLayer:
    """
    It is used to manage the communication between 2 different processes: the RPC consumer and a Bot Consumer/View
    """

    @staticmethod
    async def poll(conversation_id: str):  # TODO: return types
        """
        Is is used by the Bot Consumer/View that is waiting for the RPC result to come from the RPCConsumer
        Parameters
        ----------
        conversation_id: str
            The current conversation ID

        Returns
        -------
        dict
            Result from the remote call

        """
        result = None
        while result is None:
            result = await sync_to_async(RPCResponse.objects.filter(ctx__conversation_id=conversation_id).first)()
        await sync_to_async(result.delete)()
        return result.payload
