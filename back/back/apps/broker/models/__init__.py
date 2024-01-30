from django.db import models
from back.common.models import ChangesMixin
from django.utils import timezone


class ConsumerRoundRobinQueue(ChangesMixin):
    """
    RPCConsumerRoundRobinQueue: This table is used to keep track of the round robin queue of the RPC consumers.
    This is used to distribute the RPC messages between the RPC consumers from the Bot Consumers.
    """
    layer_group_name = models.CharField(max_length=255, unique=True)
    rr_group_key = models.CharField(max_length=255)

    @classmethod
    def get_next_consumer_group_name(cls, rr_group_key):
        """
        This method implements the Round Robin.
        """
        rpc_consumer = cls.objects.filter(rr_group_key=rr_group_key).order_by("updated_date").first()
        rpc_consumer.updated_date = timezone.now()
        rpc_consumer.save()
        return rpc_consumer.layer_group_name

    @classmethod
    def add(cls, layer_group_name, rr_group_key):
        """
        This method is used to add a new RPC consumer to the round robin queue.
        """
        cls.objects.create(layer_group_name=layer_group_name, rr_group_key=rr_group_key)

    @classmethod
    def remove(cls, layer_group_name):
        """
        This method is used to remove a RPC consumer from the round robin queue.
        """
        cls.objects.filter(layer_group_name=layer_group_name).delete()

    @classmethod
    def clear(cls):
        """
        This method is used to clear the Round Robin queue (used when booting up the server).
        """
        cls.objects.all().delete()


class RemoteSDKParsers(ChangesMixin):
    """
    This table is used to keep track of the parsers registered by the remote SDKs and the channel's group name to which
    the parsing request should be sent.
    """
    layer_group_name = models.CharField(max_length=255)
    parser_name = models.CharField(max_length=255)

    @classmethod
    def get_next_consumer_group_name(cls, parser_name):
        """
        This method is used to get the channel's group name to which the parsing request should be sent.
        """
        parser_consumer = cls.objects.filter(parser_name=parser_name).order_by("updated_date").first()
        if parser_consumer:
            parser_consumer.updated_date = timezone.now()
            parser_consumer.save()
            return parser_consumer.layer_group_name

    @classmethod
    def add(cls, layer_group_name, parser_name):
        """
        This method is used to add a new parser to the table.
        """
        cls.objects.create(layer_group_name=layer_group_name, parser_name=parser_name)

    @classmethod
    def remove(cls, layer_group_name):
        """
        This method is used to remove a parser from the table.
        """
        cls.objects.filter(layer_group_name=layer_group_name).delete()

    @classmethod
    def clear(cls):
        """
        This method is used to clear the table (used when booting up the server).
        """
        cls.objects.all().delete()

    def __str__(self):
        return self.parser_name
