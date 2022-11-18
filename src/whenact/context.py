
class BaseContext:
    def __init__(self):
        self._cache_data = {}

    def __getitem__(self, item):
        return self._cache_data[item]

    def __setitem__(self, key, value):
        self._cache_data[key] = value
        self.__setattr__(key, value)

    def __delitem__(self, key):
        if key in self._cache_data:
            del self._cache_data[key]
            self.__delattr__(key)


class PipelineContext:
    def __init__(self, base_ctx: BaseContext):
        self._ctx = base_ctx
        self._pipeline_output = None

    def _set_pipeline_output(self, data):
        self._pipeline_output = data

    def __getattr__(self, item):
        try:
            return self._ctx.__getattribute__(item)
        except AttributeError:
            return self.__getattribute__(item)

    def __getitem__(self, item):
        return self._ctx.__getitem__(item)

    def __setitem__(self, key, value):
        self._ctx.__setitem__(key, value)

    @property
    def last_output(self):
        return self._pipeline_output