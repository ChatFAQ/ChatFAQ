# Riddler SDK

This SDK assists you on 2 main tasks:

- Creating FSM Definitions on a Riddler server


- Hosting RPCs (Remote Procedure Calls) to serve when a session's FSM connected to a Riddler server reach the call.

## Installation

Go inside ./back directory and install project dependencies:

`poetry install`


## Build the docs

go inside the `doc` directory and run:

```
poetry run make html
```


## Quick start

### Concepts

- <ins>FSMDefinition</ins>: Is the full description of a Finite State Machine.

An FSM definition is composed out of 2 types of blocks: States & Transitions:

- <ins>States</ins>: defines the nodes of an FSM, when a node is reached its __events__ will be triggered.

- <ins>Transitions</ins>: define the __conditions__ needed to transit from one state to the other.

Both __events__ and __conditions__ are functionality that will be executed on demand of the Riddler Server. They are known as RPC (Remote Procedure Calls)


### Example

Inside [examples/\_\_init\_\_.py](examples/__init__.py) you can find a simple working example of the usage of the SDK.

Let's walk through it step by step.

The diagram below describe the FSM definition used in this exampled and implemented in [examples/fsm_def.py](examples/fsm_def.py).

![Simple FSM Definition](./doc/source/images/simple_fsm.png?raw=true "Simple FSM Definition")

### States

Instantiate the __State__ class for creating a new state in the SDK:

- give it a __name__


- set __initial__ to `True` in case is the initial state


- pass a list of __events__ it should trigger once it's entered.

```python
from riddler_sdk.fsm import State

greeting_state = State(
    name="Greeting",
    events=[send_greeting],
    initial=True
)

answering_state = State(
    name="Answering",
    events=[send_answer],
)

goodbye_state = State(
    name="Goodbye",
    events=[send_goodbye],
)

...
```


In this example the FSM definition is composed of 3 states: __Greeting__, __Answering__, __Goodbye__.

the Greeting state is the initial state (represented as green in the image), all FSM definitions should have one and only one initial state.

All our 3 states have one event to trigger once entered:

- __Greeting__ is going to trigger `send_greeting` which return a stack of 2 layers of text: the first layer is saying hello and the second layer is asking our human how is it going.


- __Answering__ is going to trigger `send_answer` which also returns a stack of 2 layers of text: the first layer is replying a customized answer (by appending a random number) to the last message, the second layer is inviting the human to keep asking questions


- __Goodbye__ is going to trigger `send_goodbye` which returns a stack of 1 layer of text simply effusively saying goodbye

```python
import random

from riddler_sdk.conditions import Result
from riddler_sdk.layers import Text

def is_saying_goodbye(ctx: dict):
    if ctx["last_mml"]["stacks"][0][0]["payload"] == "goodbye":
        return Result(1)
    return Result(0)


def send_greeting(ctx: dict):
    yield Text("Hello!")
    yield Text("How are you?")


def send_answer(ctx: dict):
    last_payload = ctx['last_mml']['stacks'][0][0]['payload']
    yield Text(f'My answer to your message: "{last_payload}" is: {random.randint(0, 999)}')
    yield Text(f'Tell me more')


def send_goodbye(ctx: dict):
    yield Text("Byeeeeeeee!")
```

### Transitions

We have already defined our states, but we also need to defined how to go from one to another, in other words, we have to define the transitions between them.

Instantiate the __Transition__ class for creating a new transition in the SDK:

- pass the __source__ state from which this transition could happen (or do not pass it in case this transition can occur from any state, AKA _ubiquitous transitions_)


- pass the __dest__ state indicating on which state this transition lands


- declare the list of __conditions__ that need to pass in order to the transition to happen


- declare the list of __unless__ that need NOT pass in order to the transition to happen
```python
from riddler_sdk.fsm import Transition

any_to_goodbye = Transition(
    dest=goodbye_state,
    conditions=[is_saying_goodbye]
)

greeting_to_answer = Transition(
    source=greeting_state,
    dest=answering_state,
    unless=[is_saying_goodbye],
)
answer_to_answer = Transition(
    source=answering_state,
    dest=answering_state,
    unless=[is_saying_goodbye]
)
```


In this example we have 3 transitions:
- any_to_goodbye: it is a ubiquitous transitions (as there is no __source__ passed to), it does not matter where we are at, if the user says "goodbye" then we will pass to the Goodbye state.


- greeting_to_answer: represents the move from Greetings to Answer, which will always happens as long as we are not saying goodbye


- answer_to_answer: represents the move from Answer to itself, which will always happens as long as we are not saying goodbye

### FSM Definition

The final step consist on gluing everything together.

Instantiate the __FSMDefinition__ class for orchestrating all the states and its transitions.

- pass the __states__, order won't matter


- pass the __transitions__, order matters: if 2 transitions returns same scores then the first one on the list will be the winner.
```python
from riddler_sdk.fsm import FSMDefinition

fsm_def = FSMDefinition(
    states=[greeting_state, answering_state, goodbye_state],
    transitions=[greeting_to_answer, any_to_goodbye, answer_to_answer],
)
```

### Connexion

The only thing left after defining your FSM is to communicate it to Riddler Server and remain listening as an RPC server (for executing your previously declared events & conditions on demand)

We do so by instantiating the class RiddlerSDK and passing to the constructor 3 parameters:

- riddler_host: the address of our Riddler Server


- fsm_name: the name of our new FSM Definition if we are providing `fsm_def` or the name/ID of an already existing FSM Definition on the remote server if not `fsm_def` is provided


- fsm_def (optional): an instance of FSMDefinition

Then we call our RiddlerSDK instance's `connect` method, and we are done.
```python
from riddler_sdk import RiddlerSDK

sdk = RiddlerSDK("ws://localhost:8000/", "simple_fsm", fsm_def)
sdk.connect()
```
