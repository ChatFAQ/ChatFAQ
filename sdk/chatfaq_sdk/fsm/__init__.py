from __future__ import annotations

from typing import TYPE_CHECKING, Callable, List

if TYPE_CHECKING:
    from chatfaq_sdk import ChatFAQSDK


class FSMDefinition:
    """
    Representation of the entire FSM, this class will generate the DSM Definition sent to the ChatFAQ's back-end server
    and will do all the validation of the states/transitions and will register all the RPCs
    """

    def __init__(
        self,
        states: List[State] = [],
        transitions: List[Transition] = []
    ):
        """

        Parameters
        ----------
        states: list of State
            All the states conforming the FSM
        transitions: list of Transition
            All the transitions conforming the FSM
        """
        self.states = states
        self.transitions = transitions

    def register_rpcs(self, chatfaq_sdk: ChatFAQSDK):
        for state in self.states:
            for rpc in state.events:
                chatfaq_sdk.rpc(rpc.__name__)(rpc)

        for transition in self.transitions:
            for rpc in transition.conditions:
                chatfaq_sdk.rpc(rpc.__name__)(rpc)
            for rpc in transition.unless:
                chatfaq_sdk.rpc(rpc.__name__)(rpc)

    def to_dict_repr(self):
        return {
            "states": [item.to_dict_repr() for item in self.states],
            "transitions": [item.to_dict_repr() for item in self.transitions],
        }


class State:
    """
    The state of the FSM
    """

    def __init__(self, name: str, events: List[Callable] = [], initial: bool = False):
        """

        Parameters
        ----------
        name: str
            Descriptive name of the state
        events: list of function
            List of functions they need to be called when entering this state
        initial: bool
            If initial = True then this state will be the first entering when initializing the FSM

        """
        self.initial = initial
        self.name = name
        self.events = events

    def to_dict_repr(self):
        return {
            "initial": self.initial,
            "name": self.name,
            "events": [f.__name__ for f in self.events],
        }


class Transition:
    """
    The transition between 2 states of the FSM
    """

    def __init__(
        self,
        dest: State,
        source: State = None,
        conditions: List[Callable] = [],
        unless: List[Callable] = [],
    ):
        """

        Parameters
        ----------
        dest: State
            Mandatory, the target state if all the conditions/unless pass
        source: State
            The state where the FSM is coming from in order to execute his transition, in case 'source' is not set then
            the 'dest' state on this transition would be considered 'ubiquitous state', meaning it can be accesses from
            any other state
        conditions: function
            The functions that has to pass in order to satisfy the transition
        unless: function
            The functions that doesn't have to pass in order to satisfy the transition
        """
        self.source = source
        self.dest = dest
        self.conditions = conditions
        self.unless = unless

    def to_dict_repr(self):
        json = {
            "dest": self.dest.name,
            "unless": [f.__name__ for f in self.unless],
            "conditions": [f.__name__ for f in self.conditions],
        }
        if self.source:
            json["source"] = self.source.name
        return json
