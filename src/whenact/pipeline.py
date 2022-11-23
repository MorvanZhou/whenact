import typing
from collections import OrderedDict
from dataclasses import dataclass, field

from whenact.context import PipelineContext, BaseContext
from whenact.task import Task
from whenact.types import WhenFnType, ActFnType


@dataclass
class FunctionSummary:
    function_name: str
    output: typing.Any

    def __repr__(self):
        return f"""function '{self.function_name}' returns {self.output}"""


@dataclass
class HistorySummary:
    policy_name: str
    policy_summary: typing.List[FunctionSummary] = field(default_factory=list)

    def __repr__(self):
        return f"{self.policy_name}: {' > '.join([s.function_name for s in self.policy_summary])}"

    def __str__(self):
        return self.__repr__()


@dataclass
class PipelineHistory:
    outputs: typing.List[typing.Any] = field(default_factory=list)
    summary: typing.List[HistorySummary] = field(default_factory=list)

    @property
    def acted(self) -> bool:
        return len(self.outputs) > 0

    @property
    def last_output(self):
        if len(self.outputs) == 0:
            return None
        return self.outputs[-1]


class Pipeline:
    def __init__(self, pipe_list: typing.Optional[typing.Sequence[Task]] = None):
        self.data: typing.OrderedDict[str, Task] = OrderedDict()
        if pipe_list is not None:
            for p in pipe_list:
                self.add_task(p)

    def add(
            self,
            when: typing.Union[WhenFnType, typing.Sequence[WhenFnType]],
            action: typing.Union[ActFnType, typing.Sequence[ActFnType]],
            name: typing.Optional[str] = None
    ):
        if not isinstance(when, (tuple, list)):
            when = [when]
        if not isinstance(action, (tuple, list)):
            action = [action]
        self.add_task(Task(when=when, action=action, name=name))

    def add_task(self, policy: Task):
        if policy.name in self.data:
            raise ValueError(f"name={policy.name} is exist in pipeline, please use new one")
        self.data[policy.name] = policy

    def remove_task(self, name: str):
        del self.data[name]

    def run(self, context: typing.Optional[BaseContext] = None, auto_break: bool = True):
        p_ctx = PipelineContext(base_ctx=context)
        hist = PipelineHistory()
        for name, policy in self.data.items():
            keep = True
            ps = []
            hist.summary.append(HistorySummary(
                policy_name=name,
                policy_summary=ps
            ))
            for w in policy.when:
                keep = w(p_ctx)
                ps.append(
                    FunctionSummary(function_name=w.__name__, output=keep))
                if not keep:
                    break
            if keep:
                for a in policy.action:
                    o = a(p_ctx)
                    ps.append(
                        FunctionSummary(function_name=a.__name__, output=o)
                    )
                    hist.outputs.append(o)
                if auto_break:
                    return hist
        return hist

    def __getitem__(self, item) -> Task:
        if isinstance(item, int):
            return list(self.data.values())[item]
        return self.data[item]

    def __str__(self):
        return "\n".join(self.view())

    def view(self):
        res = []
        for name, p in self.data.items():
            res.append(f"{name}: "
                       f"[{' > '.join([a.__name__ for a in p.when])}] "
                       f"> [{' > '.join([a.__name__ for a in p.action])}]")
        return res


def create_pipeline(config: typing.Sequence[typing.Sequence[ActFnType]]) -> Pipeline:
    p = Pipeline()
    for policy in config:
        when = []
        action = []
        to_action = False
        for wa in policy:
            try:
                t = getattr(wa, "_type")
            except AttributeError as e:
                raise ValueError(f"when or act function must be decorated: {e}")
            if t == "when" and not to_action:
                when.append(wa)
            elif t == "act":
                to_action = True
                action.append(wa)
            else:
                raise TypeError("[when] function must be set before [act] function")
        p.add_task(Task(when=when, action=action))
    return p
