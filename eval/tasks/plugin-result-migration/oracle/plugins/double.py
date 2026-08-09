from core.base import Plugin, Result
from core.registry import register


@register("double")
class DoublePlugin(Plugin):
    def run(self, payload):
        return Result.success(str(payload) * 2)
