"""Adapter kept for external callers that predate the plugin API."""
from core import registry


def legacy_run(name, payload):
    """Return the plugin's raw value; raise on failure.

    External callers depend on this exact shape. It must not start returning
    Result objects.
    """
    return registry.get(name).run(payload)
