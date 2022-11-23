import typing as tp
from dataclasses import dataclass, field


@dataclass
class FunctionSummary:
    function_name: str
    output: tp.Any

    def __repr__(self):
        return f"""function '{self.function_name}' returns {self.output}"""


@dataclass
class HistorySummary:
    behavior_name: str
    behavior_summary: tp.List[FunctionSummary] = field(default_factory=list)

    def __repr__(self):
        return f"{self.behavior_name}: {' > '.join([s.function_name for s in self.behavior_summary])}"

    def __str__(self):
        return self.__repr__()


@dataclass
class PipelineHistory:
    outputs: tp.List[tp.Any] = field(default_factory=list)
    summary: tp.List[HistorySummary] = field(default_factory=list)

    @property
    def acted(self) -> bool:
        """
        if pipeline has behaved any action, then acted is True, False otherwise.

        Returns:
            bool: True/False
        """
        return len(self.outputs) > 0

    @property
    def last_output(self):
        if len(self.outputs) == 0:
            return None
        return self.outputs[-1]
