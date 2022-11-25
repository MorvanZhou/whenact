import typing as tp

from whenact import block
from whenact.context import BaseContext
from whenact.decisionflow import DecisionFlow
from whenact.history import PipelineHistory
from whenact.types import WhenFnType, ActFnType

FLOW = DecisionFlow()


def add(
        when: tp.Union[WhenFnType, tp.Sequence[WhenFnType]],
        act: tp.Union[ActFnType, tp.Sequence[ActFnType]],
        name: tp.Optional[str] = None,
):
    if not isinstance(when, (tuple, list)):
        when = [when]
    if not isinstance(act, (tuple, list)):
        act = [act]
    when = [block.when_decorator.when(f) for f in when]
    act = [block.act_decorator.act(f) for f in act]
    FLOW.add(when=when, act=act, name=name)


def remove(name: str):
    FLOW.remove_decision(name)


def clear():
    FLOW.clear()


def run(context: BaseContext, auto_break: bool = True) -> PipelineHistory:
    return FLOW.run(context, auto_break)
