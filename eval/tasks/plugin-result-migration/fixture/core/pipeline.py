"""Run a sequence of plugins over a payload."""
from core import registry


def run_pipeline(steps, payload):
    """Apply each named plugin in order, threading the value through."""
    current = payload
    for step in steps:
        current = registry.get(step).run(current)
    return current
