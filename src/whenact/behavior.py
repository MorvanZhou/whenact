import typing as tp
from dataclasses import dataclass, field

from whenact.types import WhenFnType, ActFnType

_BEHAVIOR_NAME_COUNT = 0


def _reset_behavior_name():
    global _BEHAVIOR_NAME_COUNT
    _BEHAVIOR_NAME_COUNT = 0


def _get_behavior_name():
    global _BEHAVIOR_NAME_COUNT
    name = f"b{_BEHAVIOR_NAME_COUNT}"
    _BEHAVIOR_NAME_COUNT += 1
    return name


@dataclass
class Behavior:
    when: tp.Sequence[WhenFnType]
    act: tp.Sequence[ActFnType]
    name: str = field(default_factory=_get_behavior_name)

    def __post_init__(self):
        if self.name is None:
            self.name = _get_behavior_name()
        if isinstance(self.when, tuple):
            self.when = list(self.when)
        if isinstance(self.act, tuple):
            self.act = list(self.act)
        if not isinstance(self.when, list):
            raise TypeError("when must be list type")
        if not isinstance(self.act, list):
            raise TypeError("act must be list type")
        if len(self.when) == 0:
            raise ValueError("when is empty")
        if len(self.act) == 0:
            raise ValueError("act is empty")
        for wa in self.when + self.act:
            if not callable(wa):
                raise TypeError("when and action must be a list of function type")
