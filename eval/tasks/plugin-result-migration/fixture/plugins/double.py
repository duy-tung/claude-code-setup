from core.base import Plugin
from core.registry import register


@register("double")
class DoublePlugin(Plugin):
    def run(self, payload):
        return str(payload) * 2
