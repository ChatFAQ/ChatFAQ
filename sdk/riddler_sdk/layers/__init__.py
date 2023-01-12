class Layer:
    """
    Representation of all the future stack's layers. Implementing a new layer should inherit form this
    """
    _type = None

    def to_json(self):
        """
        Used to represent the layer as a dictionary which will be sent through the WS to Riddler
        :return:
            dict
                A json compatible dict
        """
        raise NotImplementedError


class Text(Layer):
    """
    Simplest layer representing raw text
    """

    _type = "text"

    def __init__(self, payload):
        self.payload = payload

    def to_json(self):
        return [{
            "type": self._type,
            "payload": self.payload
        }]
