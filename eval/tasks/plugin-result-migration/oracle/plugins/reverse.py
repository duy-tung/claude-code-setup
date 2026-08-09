from core.base import Plugin, Result
from core.registry import register


@register("reverse")
class ReversePlugin(Plugin):
    def run(self, payload):
        return Result.success(str(payload)[::-1])
