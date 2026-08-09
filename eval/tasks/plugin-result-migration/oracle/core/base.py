"""Plugin base class and the Result value type."""


class Result:
    """Outcome of a plugin run."""

    __slots__ = ("ok", "value", "error", "error_step")

    def __init__(self, ok, value=None, error=None, error_step=None):
        self.ok = ok
        self.value = value
        self.error = error
        self.error_step = error_step

    @classmethod
    def success(cls, value):
        return cls(True, value=value)

    @classmethod
    def failure(cls, error, error_step=None):
        return cls(False, error=str(error), error_step=error_step)

    def __repr__(self):
        return (f"Result(ok={self.ok!r}, value={self.value!r}, "
                f"error={self.error!r}, error_step={self.error_step!r})")


class Plugin:
    name = "plugin"

    def run(self, payload):
        raise NotImplementedError
