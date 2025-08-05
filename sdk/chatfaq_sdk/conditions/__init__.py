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


    def __or__(self, other):
        return Condition(max(self.score, other.score), {**self.data, **other.data})

    def __and__(self, other):
        return Condition(min(self.score, other.score), {**self.data, **other.data})

    def __sub__(self, other):
        other_score = other.score if isinstance(other, Condition) else other
        return Condition(max(0, self.score - other_score), {**self.data, **other.data})

    def __add__(self, other):
        other_score = other.score if isinstance(other, Condition) else other
        return Condition(self.score + other_score, {**self.data, **other.data})

    def __eq__(self, other):
        if isinstance(other, Condition):
            return self.score == other.score and self.data == other.data
        return False

    def __repr__(self):
        return f"Condition(score={self.score}, data={self.data})"

    async def result(self, *args, fsm_def_name: str = None):
        yield [[{"score": self.score, "data": self.data}], 0, True]
