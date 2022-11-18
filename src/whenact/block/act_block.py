from functools import wraps

from whenact.context import PipelineContext


def act(func):
    func._type = "act"

    @wraps(func)
    def wrapper(context: PipelineContext, *args, **kwargs):
        res = func(context, *args, **kwargs)
        context.set_pipeline_output(res)
        return res

    return wrapper
