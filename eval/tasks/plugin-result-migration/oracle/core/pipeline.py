"""Run a sequence of plugins over a payload."""
from core import registry
from core.base import Result


def run_pipeline(steps, payload):
    """Thread the unwrapped value through each step.

    Returns the final raw value on success. On the first failing step, returns
    that failure Result tagged with the step name and skips the remaining steps.
    A plugin that raises is converted rather than propagated, so a third-party
    plugin that never migrated cannot take the pipeline down.
    """
    current = payload
    for step in steps:
        try:
            outcome = registry.get(step).run(current)
        except Exception as exc:  # noqa: BLE001 - deliberate boundary
            return Result.failure(exc, error_step=step)
        if not isinstance(outcome, Result):
            outcome = Result.success(outcome)
        if not outcome.ok:
            outcome.error_step = outcome.error_step or step
            return outcome
        current = outcome.value
    return current
