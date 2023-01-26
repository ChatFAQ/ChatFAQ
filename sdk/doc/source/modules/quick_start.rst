Quick Start
==================

Concepts
------------------


.. role:: underline

- :underline:`FSMDefinition`: Is the full description of a Finite State Machine.

An FSM definition is composed out of 2 types of blocks: States & Transitions:

- :underline:`States`: defines the nodes of an FSM, when a node is reached its **events** will be triggered.

- :underline:`Transitions`: define the **conditions** needed to transit from one state to the other.

Both **events** and **conditions** are functionality that will be executed on demand of the Riddler Server. They are known as RPC (Remote Procedure Calls)


Example
------------------

.. module:: examples

Inside :ref:`examples/__init__.py <init_example>` you can find a simple working example of the usage of the SDK.

Let's walk through it step by step.

The diagram below describe the FSM definition used in this exampled and implemented in :ref:`examples/fsm_def.py <fsm_def>`.

.. image:: ../_static/images/simple_fsm.png

States
------------------


Instantiate the **State** class for creating a new state in the SDK:

- give it a **name**


- set **initial** to `True` in case is the initial state


- pass a list of **events** it should trigger once it's entered.

.. literalinclude:: ../../../../sdk/examples/fsm_def.py
   :language: python
   :lines: 4,30-41


In this example the FSM definition is composed of 3 states: **Greeting**, **Answering**, **Goodbye**.

the Greeting state is the initial state (represented as green in the image), all FSM definitions should have one and only one initial state.

All our 3 states have one event to trigger once entered:

- **Greeting** is going to trigger `send_greeting` which return a stack of 2 layers of text: the first layer is saying hello and the second layer is asking our human how is it going.


- **Answering** is going to trigger `send_answer` which also returns a stack of 2 layers of text: the first layer is replying a customized answer (by appending a random number) to the last message, the second layer is inviting the human to keep asking questions


- **Goodbye** is going to trigger `send_goodbye` which returns a stack of 1 layer of text simply effusively saying goodbye


.. literalinclude:: ../../../../sdk/examples/fsm_def.py
   :language: python
   :lines: 1,3,5,7-29

Transitions
------------------


We have already defined our states, but we also need to defined how to go from one to another, in other words, we have to define the transitions between them.

Instantiate the **Transition** class for creating a new transition in the SDK:

- pass the **source** state from which this transition could happen (or do not pass it in case this transition can occur from any state, AKA *ubiquitous transitions*)


- pass the **dest** state indicating on which state this transition lands


- declare the list of **conditions** that need to pass in order to the transition to happen


- declare the list of **unless** that need NOT pass in order to the transition to happen


.. literalinclude:: ../../../../sdk/examples/fsm_def.py
   :language: python
   :lines: 4,42-53


In this example we have 3 transitions:

- *any_to_goodbye*: it is a ubiquitous transitions (as there is no **source** passed to), it does not matter where we are at, if the user says "goodbye" then we will pass to the Goodbye state.


- *greeting_to_answer*: represents the move from Greetings to Answer, which will always happens as long as we are not saying goodbye


- *answer_to_answer*: represents the move from Answer to itself, which will always happens as long as we are not saying goodbye

FSM Definition
------------------


The final step consist on gluing everything together.

Instantiate the **FSMDefinition** class for orchestrating all the states and its transitions.

- pass the **states**, order won't matter


- pass the **transitions**, order matters: if 2 transitions returns same scores then the first one on the list will be the winner.


.. literalinclude:: ../../../../sdk/examples/fsm_def.py
   :language: python
   :lines: 4,53-57


Connection
------------------


The only thing left after defining your FSM is to communicate it to Riddler Server and remain listening as an RPC server (for executing your previously declared events & conditions on demand)

We do so by instantiating the class RiddlerSDK and passing to the constructor 5 parameters:

- *riddler_host*: the address of our Riddler Server


- *user_email*: the email of an Riddler's admin user


- *user_password*:  the password of an Riddler's admin user


- *fsm_name*: the name of our new FSM Definition if we are providing `fsm_def` or the name/ID of an already existing FSM Definition on the remote server if not `fsm_def` is provided


- *fsm_def* (optional): an instance of FSMDefinition

Then we call our RiddlerSDK instance's `connect` method, and we are done.


.. literalinclude:: ../../../../sdk/examples/__init__.py
   :language: python
