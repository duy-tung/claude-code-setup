from core.base import Plugin, Result
from core.registry import register


@register("upper")
class UpperPlugin(Plugin):
    def run(self, payload):
        return Result.success(str(payload).upper())
