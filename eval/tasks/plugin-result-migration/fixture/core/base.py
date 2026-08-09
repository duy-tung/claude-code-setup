"""Plugin base class and the Result value type."""


class Result:
    """Outcome of a plugin run. Currently unused by the plugins."""

    __slots__ = ("ok", "value", "error")

    def __init__(self, ok, value=None, error=None):
        self.ok = ok
        self.value = value
        self.error = error

    @classmethod
    def success(cls, value):
        return cls(True, value=value)

    @classmethod
    def failure(cls, error):
        return cls(False, error=str(error))

    def __repr__(self):
        return f"Result(ok={self.ok!r}, value={self.value!r}, error={self.error!r})"


class Plugin:
    name = "plugin"

    def run(self, payload):
        raise NotImplementedError
