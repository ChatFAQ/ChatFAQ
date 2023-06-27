from django.db import models
from back.common.models import ChangesMixin
from django.utils import timezone

class RPCConsumerRoundRobinQueue(ChangesMixin):
    """
    RPCConsumerRoundRobinQueue: This table is used to keep track of the round robin queue of the RPC consumers.
    This is used to distribute the RPC messages between the RPC consumers from the Bot Consumers.
    """
    rpc_group_name = models.CharField(max_length=255, unique=True)
    fsm_id = models.CharField(max_length=255)

    @classmethod
    def get_next_rpc_consumer_group_name(cls, fsm_id):
        """
        This method implements the Round Robin.
        """
        rpc_consumer = cls.objects.filter(fsm_id=fsm_id).order_by("updated_date").first()
        rpc_consumer.updated_date = timezone.now()
        rpc_consumer.save()
        return rpc_consumer.rpc_group_name

    @classmethod
    def add(cls, rpc_group_name, fsm_id):
        """
        This method is used to add a new RPC consumer to the round robin queue.
        """
        cls.objects.create(rpc_group_name=rpc_group_name, fsm_id=fsm_id)

    @classmethod
    def remove(cls, rpc_group_name):
        """
        This method is used to remove a RPC consumer from the round robin queue.
        """
        cls.objects.filter(rpc_group_name=rpc_group_name).delete()

    @classmethod
    def clear(cls):
        """
        This method is used to clear the Round Robin queue (used when booting up the server).
        """
        cls.objects.all().delete()
