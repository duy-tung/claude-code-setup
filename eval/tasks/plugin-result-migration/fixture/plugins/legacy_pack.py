"""Older plugin bundle. Registered imperatively, not via the decorator."""
from core.base import Plugin
from core.registry import register_by_name


class SlugifyPlugin(Plugin):
    def run(self, payload):
        return "-".join(str(payload).lower().split())


register_by_name("slugify", SlugifyPlugin)
