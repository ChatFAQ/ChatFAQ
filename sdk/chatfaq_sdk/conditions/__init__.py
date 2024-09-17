class Condition:
    """
    Instances of this class should be always returned by the conditions of the FSM's transitions
    """

    def __init__(self, score: float, data: dict = {}):
        """

        Parameters
        ----------
        score: float
            The confidence of the transition, this scalar will be used by the FSM to determine at the end of the
            executiron of all the possible transitions which one should be the right one
        data: dict
            This data is passed from the transition result to the resulting state
            this is usually helpful when the transition compute something expensive, and we don't want to recompute
            again in the state
        """

        self.score = score
        self.data = data

    async def result(self, *args, fsm_def_name: str = None):
        yield [{"score": self.score, "data": self.data}, 0, True]
