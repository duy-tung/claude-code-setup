"""Adapter kept for external callers that predate the plugin API."""
from core import registry
from core.base import Result


def legacy_run(name, payload):
    """Return the plugin's raw value; raise on failure.

    External callers depend on this exact shape, so the Result migration stops
    at this boundary: unwrap on success, raise on failure.
    """
    outcome = registry.get(name).run(payload)
    if not isinstance(outcome, Result):
        return outcome
    if not outcome.ok:
        raise RuntimeError(outcome.error)
    return outcome.value
