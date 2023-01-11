from typing import List

from django.db import models
from django_better_admin_arrayfield.models.fields import ArrayField
from typefit import typefit

from riddler.common.models import ChangesMixin

from .lib import FSM, FSMContext, State, Transition
from ...utils.logging_formatters import TIMESTAMP_FORMAT


class FSMDefinition(ChangesMixin):
    # TODO: Model 'definitions' inside DB ???
    name = models.CharField(null=True, unique=True, max_length=255)
    definition = models.JSONField(null=True)

    def build_fsm(self, ctx: FSMContext, current_state: State = None) -> FSM:
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
                fsm_def=fsm.ctx.platform_config.fsm_def,
            )
        instance.save()

    @classmethod
    def build_fsm(cls, ctx: FSMContext) -> FSM:
        instance: CachedFSM = cls.objects.filter(conversation_id=ctx.conversation_id).first()
        if instance:
            return instance.fsm_def.build_fsm(
                ctx, typefit(State, instance.current_state)
            )

        return None

    @classmethod
    def get_conv_updated_date(cls, ctx: FSMContext):
        instance = cls.objects.filter(conversation_id=ctx.conversation_id).first()
        if instance:
            instance.updated_date.strftime(TIMESTAMP_FORMAT)
