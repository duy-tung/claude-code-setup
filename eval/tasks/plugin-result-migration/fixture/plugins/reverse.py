from core.base import Plugin
from core.registry import register


@register("reverse")
class ReversePlugin(Plugin):
    def run(self, payload):
        return str(payload)[::-1]
