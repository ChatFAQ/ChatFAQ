from __future__ import annotations

from typing import List, Tuple, Union

from django.db import models
from typefit import typefit

from back.common.models import ChangesMixin

from ...common.abs.bot_consumers import BotConsumer
from ...utils.logging_formatters import TIMESTAMP_FORMAT
from .lib import FSM, State, Transition


class FSMDefinition(ChangesMixin):
    # TODO: Model 'definitions' inside DB ???
    name = models.CharField(null=True, unique=True, max_length=255)
    definition = models.JSONField(null=True)
    initial_state_values = models.JSONField(null=True)

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
        cls, name, definition, overwrite
    ) -> Tuple[Union[FSMDefinition, None], bool, str]:
        for item in cls.objects.all():
            if item.definition == definition and item.name == name:
                return item, False, ""
        if not overwrite and cls.objects.filter(name=name).first():
            return (
                None,
                False,
                f"Trying to create a new FSM definition with a conflicting name: {name} which already exists",
            )
        elif overwrite:
            cls.objects.filter(name=name).delete()

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
    conversation = models.ForeignKey("broker.Conversation", on_delete=models.CASCADE)
    current_state = models.JSONField(default=dict)
    fsm_def: FSMDefinition = models.ForeignKey(FSMDefinition, on_delete=models.CASCADE)

    @classmethod
    def update_or_create(cls, fsm: FSM):
        instance = cls.objects.filter(conversation=fsm.ctx.conversation).first()
        if instance:
            instance.current_state = fsm.current_state._asdict()
        else:
            instance = cls(
                conversation=fsm.ctx.conversation,
                current_state=fsm.current_state._asdict(),
                fsm_def=fsm.ctx.fsm_def,
            )
        instance.save()

    @classmethod
    def build_fsm(cls, ctx: BotConsumer) -> FSM:
        instance: CachedFSM = cls.objects.filter(conversation=ctx.conversation).first()
        if instance:
            return instance.fsm_def.build_fsm(
                ctx, typefit(State, instance.current_state)
            )

        return None

    @classmethod
    def get_conv_updated_date(cls, ctx: BotConsumer):
        instance = cls.objects.filter(conversation=ctx.conversation).first()
        if instance:
            instance.updated_date.strftime(TIMESTAMP_FORMAT)
