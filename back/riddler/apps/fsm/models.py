from typing import List

from django.db import models
from django_better_admin_arrayfield.models.fields import ArrayField
from typefit import typefit

from riddler.common.models import ChangesMixin

from .lib import Machine, MachineContext, State, Transition


class FiniteStateMachine(ChangesMixin):
    # TODO: Model 'definitions' inside DB ???
    name = models.CharField(null=True, unique=True, max_length=255)
    definition = models.JSONField(null=True)
    funcs = ArrayField(models.TextField(), default=list)

    def build_machine(self, ctx: MachineContext, current_state: State = None):
        m = Machine(
            ctx=ctx,
            states=self.states,
            transitions=self.transitions,
            current_state=current_state,
        )
        self.declare_ctx_functions(ctx)
        return m

    def declare_ctx_functions(self, ctx: MachineContext):
        for f in self.funcs:
            loc = {}
            exec(f, globals(), loc)
            setattr(ctx, list(loc.keys())[0], list(loc.values())[0].__get__(ctx))

    @property
    def states(self) -> List[State]:
        return typefit(List[State], self.definition.get("states", []))

    @property
    def transitions(self) -> List[Transition]:
        return typefit(List[Transition], self.definition.get("transitions", []))


class CachedMachine(ChangesMixin):
    conversation_id = models.CharField(unique=True, max_length=255)
    current_state = models.JSONField(default=dict)
    fsm = models.ForeignKey(FiniteStateMachine, on_delete=models.CASCADE)

    @classmethod
    def update_or_create(cls, m: Machine):
        instance = cls.objects.filter(conversation_id=m.ctx.conversation_id).first()
        if instance:
            instance.current_state = m.current_state._asdict()
        else:
            fsm = FiniteStateMachine.objects.get(name=m.ctx.fsm_name)
            instance = cls(
                conversation_id=m.ctx.conversation_id,
                current_state=m.current_state._asdict(),
                fsm=fsm,
            )
        instance.save()

    @classmethod
    def build_cached_fsm(cls, ctx: MachineContext):
        instance = cls.objects.filter(conversation_id=ctx.conversation_id).first()
        if instance:
            return instance.fsm.build_machine(
                ctx, typefit(State, instance.current_state)
            )

        return None
