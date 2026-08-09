from core.base import Plugin
from core.registry import register


@register("explode")
class ExplodePlugin(Plugin):
    def run(self, payload):
        if "boom" in str(payload).lower():
            raise ValueError("payload contained boom")
        return payload
