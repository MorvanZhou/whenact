import typing as tp

from whenact import block
from whenact.context import BaseContext
from whenact.history import PipelineHistory
from whenact.pipeline import Pipeline
from whenact.types import WhenFnType, ActFnType

PIPE = Pipeline()


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
    PIPE.add(when=when, act=act, name=name)


def remove(name: str):
    PIPE.remove_decision(name)


def clear():
    PIPE.clear()


def run(context: BaseContext, auto_break: bool = True) -> PipelineHistory:
    return PIPE.run(context, auto_break)
