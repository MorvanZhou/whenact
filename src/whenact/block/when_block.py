from functools import wraps

from whenact.context import PipelineContext


def when(func):
    func._type = "when"

    @wraps(func)
    def wrapper(context: PipelineContext, *args, **kwargs):
        res = func(context, *args, **kwargs)
        if not isinstance(res, bool):
            raise TypeError(f"{func.__name__} should return a boolean")
        return res

    return wrapper
