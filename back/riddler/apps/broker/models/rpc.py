from django.db import models

from riddler.common.models import ChangesMixin


class RPCResponse(ChangesMixin):
    """
    This model represent the communication layer between the RPC consumer and the Bot Consumer/View
    Attributes
    ----------
    ctx: str
        The conversation ctx to which the RPC is giving a result, this json has to have a "conversation_id" key just so
        the Bot Consumer/View knows how to fetch the data from the RPCResponseLayer
    payload: str
        The RPC response payload
    """
    ctx = models.JSONField(default=dict)
    payload = models.JSONField(default=dict)
