fsm_def = {
    "states": [{
            "events": [
                "say_hello"
            ],
            "initial": True,
            "name": "hello"
        }, {
            "events": [
                "create_answer"
            ],
            "name": "answering"
        }, {
            "events": [
                "create_goodbye_answer"
            ],
            "name": "goodbye"
        }
    ],
    "transitions": [{
            "dest": "answering",
            "source": "hello",
            "trigger": "give_answer"
        }, {
            "dest": "answering",
            "source": "answering",
            "trigger": "give_answer",
            "unless": [
                "is_saying_goodbye"
            ]
        }, {
            "conditions": [
                "is_saying_goodbye"
            ],
            "dest": "goodbye",
            "source": "hello",
            "trigger": "say_goodbye"
        }, {
            "conditions": [
                "is_saying_goodbye"
            ],
            "dest": "goodbye",
            "source": "answering",
            "trigger": "say_goodbye"
        }
    ]
}
