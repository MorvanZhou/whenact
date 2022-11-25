import typing as tp
from collections import OrderedDict

from whenact import block
from whenact.context import PipelineContext, BaseContext
from whenact.decision import Decision
from whenact.history import PipelineHistory
from whenact.types import WhenFnType, ActFnType


class DecisionFlow:
    def __init__(self, decisions: tp.Optional[tp.Sequence[Decision]] = None):
        self.data: tp.OrderedDict[str, Decision] = OrderedDict()
        if decisions is not None:
            for d in decisions:
                self.add_decision(d)

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
        when = [block.when_decorator.when(f) for f in when]
        act = [block.act_decorator.act(f) for f in act]
        self.add_decision(Decision(when=when, act=act, name=name))

    def add_decision(self, decision: Decision):
        if decision.name in self.data:
            raise ValueError(f"name={decision.name} is exist, please use new name")
        self.data[decision.name] = decision

    def remove_decision(self, name: str):
        del self.data[name]

    def run(self, context: tp.Optional[BaseContext] = None, auto_break: bool = True):
        p_ctx = PipelineContext(base_ctx=context)
        hist = PipelineHistory()
        for decision in self.data.values():
            hist.add_decision(decision.name)
            keep = True
            for w in decision.when:
                keep = w(p_ctx)
                hist.add_when_result(fn=w, output=keep)
                if not keep:
                    break
            if keep:
                for a in decision.act:
                    o = a(p_ctx)
                    hist.add_act_result(fn=a, output=o)
                if auto_break:
                    return hist
        return hist

    def clear(self):
        self.data.clear()

    def __getitem__(self, item) -> Decision:
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


def create_flow(config: tp.Sequence[tp.Sequence[ActFnType]]) -> DecisionFlow:
    p = DecisionFlow()
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
        p.add_decision(Decision(when=when, act=action))
    return p
