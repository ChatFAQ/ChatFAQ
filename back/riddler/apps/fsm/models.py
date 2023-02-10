from __future__ import annotations

from typing import List, Tuple, Union

from django.db import models
from typefit import typefit

from riddler.common.models import ChangesMixin

from ...common.abs.bot_consumers import BotConsumer
from ...utils.logging_formatters import TIMESTAMP_FORMAT
from .lib import FSM, State, Transition


class FSMDefinition(ChangesMixin):
    # TODO: Model 'definitions' inside DB ???
    name = models.CharField(null=True, unique=True, max_length=255)
    definition = models.JSONField(null=True)

    def build_fsm(self, ctx: BotConsumer, current_state: State = None) -> FSM:
        m = FSM(
            ctx=ctx,
            states=self.states,
            transitions=self.transitions,
            current_state=current_state,
        )
        return m

    @property
    def states(self) -> List[State]:
        return typefit(List[State], self.definition.get("states", []))

    @property
    def transitions(self) -> List[Transition]:
        return typefit(List[Transition], self.definition.get("transitions", []))

    @classmethod
    def get_or_create_from_definition(
        cls, name, definition
    ) -> Tuple[Union[FSMDefinition, None], bool, str]:
        for item in cls.objects.all():
            if item.definition == definition:
                return item, False, ""
        if cls.objects.filter(name=name).first():
            return (
                None,
                False,
                f"Trying to create a new FSM definition with a conflicting name: {name} which already exists",
            )
        fsm = cls(
            name=name,
            definition=definition,
        )
        fsm.save()
        return fsm, True, ""

    @classmethod
    def get_by_id_or_name(cls, id_or_name: str) -> Union[FSMDefinition, None]:
        if id_or_name is None:
            return
        if id_or_name.isnumeric():
            fsm = cls.objects.filter(pk=id_or_name).first()
            if fsm:
                return fsm
        else:
            fsm = cls.objects.filter(name=id_or_name).first()
            if fsm:
                return fsm


class CachedFSM(ChangesMixin):
    conversation_id = models.CharField(unique=True, max_length=255)
    current_state = models.JSONField(default=dict)
    fsm_def: FSMDefinition = models.ForeignKey(FSMDefinition, on_delete=models.CASCADE)

    @classmethod
    def update_or_create(cls, fsm: FSM):
        instance = cls.objects.filter(conversation_id=fsm.ctx.conversation_id).first()
        if instance:
            instance.current_state = fsm.current_state._asdict()
        else:
            instance = cls(
                conversation_id=fsm.ctx.conversation_id,
                current_state=fsm.current_state._asdict(),
                fsm_def=fsm.ctx.fsm_def,
            )
        instance.save()

    @classmethod
    def build_fsm(cls, ctx: BotConsumer) -> FSM:
        instance: CachedFSM = cls.objects.filter(
            conversation_id=ctx.conversation_id
        ).first()
        if instance:
            return instance.fsm_def.build_fsm(
                ctx, typefit(State, instance.current_state)
            )

        return None

    @classmethod
    def get_conv_updated_date(cls, ctx: BotConsumer):
        instance = cls.objects.filter(conversation_id=ctx.conversation_id).first()
        if instance:
            instance.updated_date.strftime(TIMESTAMP_FORMAT)
