import typing

from whenact.context import PipelineContext

WhenFnType = typing.Callable[[PipelineContext], bool]
ActFnType = typing.Callable[[PipelineContext], typing.Any]
