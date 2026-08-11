from core.base import Plugin
from core.registry import register


@register("upper")
class UpperPlugin(Plugin):
    def run(self, payload):
        return str(payload).upper()
