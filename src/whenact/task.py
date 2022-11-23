import typing
from dataclasses import dataclass, field

from whenact.types import WhenFnType, ActFnType

_TASK_NAME_COUNT = 0


def _reset_task_name():
    global _TASK_NAME_COUNT
    _TASK_NAME_COUNT = 0


def _get_task_name():
    global _TASK_NAME_COUNT
    name = f"p{_TASK_NAME_COUNT}"
    _TASK_NAME_COUNT += 1
    return name


@dataclass
class Task:
    when: typing.Sequence[WhenFnType]
    action: typing.Sequence[ActFnType]
    name: str = field(default_factory=_get_task_name)

    def __post_init__(self):
        if self.name is None:
            self.name = _get_task_name()
        if isinstance(self.when, tuple):
            self.when = list(self.when)
        if isinstance(self.action, tuple):
            self.action = list(self.action)
        if not isinstance(self.when, list):
            raise TypeError("when must be list type")
        if not isinstance(self.action, list):
            raise TypeError("action must be list type")
        for wa in self.when + self.action:
            if not callable(wa):
                raise TypeError("when and action must be a list of function type")
