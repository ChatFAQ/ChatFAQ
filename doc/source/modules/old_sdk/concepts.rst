Concepts
==================

Concepts
------------------


.. role:: underline

- :underline:`FSMDefinition`: Is the full description of a Finite State Machine.

An FSM (Finite State Machine) definition consists of two types of blocks: States and Transitions.

- :underline:`States`: A state in an FSM is a node that represents a specific condition. When a node is reached, its associated **events** are triggered. These events are executed on the demand of the ChatFAQ back-end server as Remote Procedure Calls (RPC).

- :underline:`Transitions`: Transitions define the **conditions** needed to move from one state to another. These conditions are executed on the demand of the ChatFAQ back-end server as Remote Procedure Calls (RPC).

Both **events** and **conditions** are functionality that is executed on demand by the ChatFAQ back-end server as RPCs. An RPC is a function that is executed remotely, and its results are returned to the caller.

Example
------------------

.. module:: examples

Inside :ref:`examples/__init__.py <SDK Usage Example>`, you can find a simple working example of the usage of the SDK.

Let's walk through it step by step.

The diagram below describes the FSM definition used in this example and implemented in :ref:`examples/fsm_def.py <fsm_def>`.

.. image:: ../../_static/images/simple_fsm.png

States
------------------


Instantiate the **State** class for creating a new state in the SDK:

- Give it a **name**.


- If is the initial state, set **initial** to `True`.


- Pass a list of **events** that should be trigger when it is entered.

.. literalinclude:: ../../../../sdk/examples/fsm_def.py
   :language: python
   :lines: 4,30-41


In this example, the FSM definition is composed of 3 states: **Greeting**, **Answering**, **Goodbye**.

The Greeting state is the initial state (represented as green in the image), all FSM definitions should have one and only one initial state.

All our 3 states have one event to trigger once entered:

- **Greeting** is going to trigger `send_greeting`, which returns a stack of 2 layers of text: the first layer is saying hello and the second layer is asking our human how is it going.


- **Answering** is going to trigger `send_answer`, which also returns a stack of 2 layers of text: the first layer is replying a customized answer (by appending a random number) to the last message, the second layer is inviting the human to keep asking questions


- **Goodbye** is going to trigger `send_goodbye`, which returns a stack of 1 layer of text simply effusively saying goodbye


.. literalinclude:: ../../../../sdk/examples/fsm_def.py
   :language: python
   :lines: 1,3,5,7-29

Transitions
------------------


We have already defined our states, but we also need to define how to go from one to another; in other words, we have to define the transitions between them.

Instantiate the **Transition** class for creating a new transition in the SDK:

- pass the **source** state from which this transition is possible (or do not pass it if this transition is possible from any state, AKA *ubiquitous transitions*)


- pass the **dest** state, indicating the state on which this transition lands


- declare the list of **conditions** that need to pass in order to the transition to happen


- declare the list of **unless** that need NOT pass in order to the transition to happen


.. literalinclude:: ../../../../sdk/examples/fsm_def.py
   :language: python
   :lines: 4,42-53


In this example, we have 3 transitions:

- *any_to_goodbye*: it is a ubiquitous transition (as there is no **source** passed to), it does not matter where we are at, if the user says "goodbye", then we will pass to the Goodbye state.


- *greeting_to_answer*: represents the move from Greetings to Answer, which will always happens as long as we are not saying goodbye


- *answer_to_answer*: represents the move from Answer to itself, which will always happens as long as we are not saying goodbye

FSM Definition
------------------


The last step is to glue everything together.

In order to orchestrate all of the states and their transitions instantiate the **FSMDefinition** class.

- pass the **states**, order won't matter.


- pass the **transitions**, order matters: if 2 transitions returns same scores, then the first one on the list will be the winner.


.. literalinclude:: ../../../../sdk/examples/fsm_def.py
   :language: python
   :lines: 4,53-57


Connection
------------------


The only thing left after defining your FSM is to communicate it to ChatFAQ back-end server and remain listening as an RPC server (for executing your previously declared events and conditions on demand).

We do so by instantiating the class ChatFAQSDK and passing to the constructor 5 parameters:

- *chatfaq_host*: the address of our ChatFAQ back-end server


- *user_email*: the email of ChatFAQ back-end admin user


- *user_password*:  the password of ChatFAQ back-end admin user


- *fsm_name*: the name of our new FSM Definition if we are providing `fsm_def`, or the name/ID of an already existing FSM Definition on the remote server if `fsm_def` is not provided


- *fsm_def* (optional): an instance of FSMDefinition

You should make sure the used user belongs to the *RPC* group; you can set that from the admin site of ChatFAQ back-end server.

Then we call our ChatFAQSDK instance's `connect` method, and we are done.


.. literalinclude:: ../../../../sdk/examples/__init__.py
   :language: python
