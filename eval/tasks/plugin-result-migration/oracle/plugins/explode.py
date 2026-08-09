from core.base import Plugin, Result
from core.registry import register


@register("explode")
class ExplodePlugin(Plugin):
    def run(self, payload):
        if "boom" in str(payload).lower():
            return Result.failure("payload contained boom")
        return Result.success(payload)
