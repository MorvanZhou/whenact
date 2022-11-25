import typing as tp
from dataclasses import dataclass, field

from whenact.context import PipelineContext


@dataclass
class FnResult:
    name: str
    output: tp.Any = None

    def __repr__(self):
        return f"""function '{self.name}' returns {self.output}"""


@dataclass
class DecisionResult:
    name: str
    when_results: tp.List[FnResult] = field(default_factory=list)
    act_results: tp.List[FnResult] = field(default_factory=list)

    def __repr__(self):
        return f"{self.name}: {' > '.join([s.name for s in self.when_results + self.act_results])}"

    def __str__(self):
        return self.__repr__()


@dataclass
class PipelineHistory:
    outputs: tp.List[tp.Any] = field(default_factory=list)
    summary: tp.List[DecisionResult] = field(default_factory=list)
    acted: bool = False  # if flow has behaved any action, then acted is True, otherwise False.
    __dict: dict = field(default_factory=dict, init=False)

    def add_when_result(self, fn: tp.Callable[[PipelineContext], bool], output: bool):
        s = self.summary[-1]
        s.when_results.append(
            FnResult(
                name=fn.__name__,
                output=output
            )
        )
        self.__dict[s.name]["when"][fn.__name__] = output

    def add_act_result(self, fn: tp.Callable, output: tp.Any):
        s = self.summary[-1]
        s.act_results.append(
            FnResult(
                name=fn.__name__,
                output=output,
            )
        )
        self.outputs.append(output)
        if not self.acted:
            self.acted = True
        self.__dict[s.name]["act"][fn.__name__] = output

    def add_decision(self, name):
        self.summary.append(DecisionResult(name=name))
        self.__dict[name] = {"when": {}, "act": {}}

    @property
    def last_output(self):
        if len(self.outputs) == 0:
            return None
        return self.outputs[-1]

    @property
    def first_output(self):
        if len(self.outputs) == 0:
            return None
        return self.outputs[0]

    def get_decision(
            self,
            decision: str,
    ) -> dict:
        return self.__dict[decision]
