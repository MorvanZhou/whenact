import typing as tp
from collections import OrderedDict

from whenact.behavior import Behavior
from whenact.context import PipelineContext, BaseContext
from whenact.history import PipelineHistory, HistorySummary, FunctionSummary
from whenact.types import WhenFnType, ActFnType


class Pipeline:
    def __init__(self, pipe_list: tp.Optional[tp.Sequence[Behavior]] = None):
        self.data: tp.OrderedDict[str, Behavior] = OrderedDict()
        if pipe_list is not None:
            for p in pipe_list:
                self.add_behavior(p)

    def add(
            self,
            when: tp.Union[WhenFnType, tp.Sequence[WhenFnType]],
            act: tp.Union[ActFnType, tp.Sequence[ActFnType]],
            name: tp.Optional[str] = None
    ):
        if not isinstance(when, (tuple, list)):
            when = [when]
        if not isinstance(act, (tuple, list)):
            act = [act]
        self.add_behavior(Behavior(when=when, act=act, name=name))

    def add_behavior(self, task: Behavior):
        if task.name in self.data:
            raise ValueError(f"name={task.name} is exist in pipeline, please use new one")
        self.data[task.name] = task

    def remove_behavior(self, name: str):
        del self.data[name]

    def run(self, context: tp.Optional[BaseContext] = None, auto_break: bool = True):
        p_ctx = PipelineContext(base_ctx=context)
        hist = PipelineHistory()
        for name, task in self.data.items():
            keep = True
            ps = []
            hist.summary.append(HistorySummary(
                behavior_name=name,
                behavior_summary=ps
            ))
            for w in task.when:
                keep = w(p_ctx)
                ps.append(
                    FunctionSummary(function_name=w.__name__, output=keep))
                if not keep:
                    break
            if keep:
                for a in task.act:
                    o = a(p_ctx)
                    ps.append(
                        FunctionSummary(function_name=a.__name__, output=o)
                    )
                    hist.outputs.append(o)
                if auto_break:
                    return hist
        return hist

    def __getitem__(self, item) -> Behavior:
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
                       f"> [{' > '.join([a.__name__ for a in p.act])}]")
        return res


def create_pipeline(config: tp.Sequence[tp.Sequence[ActFnType]]) -> Pipeline:
    p = Pipeline()
    for task in config:
        when = []
        action = []
        to_action = False
        for wa in task:
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
        p.add_behavior(Behavior(when=when, act=action))
    return p
