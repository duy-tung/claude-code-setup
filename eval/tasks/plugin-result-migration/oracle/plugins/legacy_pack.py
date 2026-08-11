"""Older plugin bundle. Registered imperatively, not via the decorator."""
from core.base import Plugin, Result
from core.registry import register_by_name


class SlugifyPlugin(Plugin):
    def run(self, payload):
        return Result.success("-".join(str(payload).lower().split()))


register_by_name("slugify", SlugifyPlugin)
