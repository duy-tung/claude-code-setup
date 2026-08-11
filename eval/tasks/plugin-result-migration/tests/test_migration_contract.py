"""Hidden contract for the Result migration.

These checks are deliberately discovery-driven: they walk the live registry
rather than naming plugins, so a module that was never migrated fails here even
though every visible test still passes.
"""
import unittest

import plugins  # noqa: F401  (registers everything)
from core import compat, registry
from core.base import Plugin, Result
from core.pipeline import run_pipeline


class TestEveryRegisteredPluginMigrated(unittest.TestCase):
    def test_registry_is_not_empty(self):
        self.assertGreaterEqual(len(registry.names()), 5)

    def test_every_registered_plugin_returns_a_result(self):
        unmigrated = []
        for name in registry.names():
            outcome = registry.get(name).run("sample text")
            if not isinstance(outcome, Result):
                unmigrated.append(f"{name} -> {type(outcome).__name__}")
        self.assertEqual(unmigrated, [], f"plugins still returning raw values: {unmigrated}")

    def test_successful_plugin_result_carries_the_value(self):
        outcome = registry.get("upper").run("abc")
        self.assertTrue(outcome.ok)
        self.assertEqual(outcome.value, "ABC")
        self.assertIsNone(outcome.error)


class TestPipelineSemantics(unittest.TestCase):
    def test_threads_unwrapped_values_between_steps(self):
        self.assertEqual(run_pipeline(["upper", "reverse", "double"], "ab"), "BABA")

    def test_short_circuits_on_failure_and_names_the_step(self):
        calls = []

        class Recorder(Plugin):
            def run(self, payload):
                calls.append(payload)
                return Result.success(payload)

        registry.register_by_name("recorder", Recorder)
        outcome = run_pipeline(["upper", "explode", "recorder"], "say boom")
        self.assertFalse(outcome.ok)
        self.assertEqual(outcome.error_step, "explode")
        self.assertEqual(calls, [], "steps after the failure must not run")

    def test_converts_a_raising_plugin_into_a_failure_result(self):
        class Detonator(Plugin):
            def run(self, payload):
                raise RuntimeError("third-party plugin blew up")

        registry.register_by_name("detonator", Detonator)
        outcome = run_pipeline(["detonator"], "anything")
        self.assertFalse(outcome.ok)
        self.assertEqual(outcome.error_step, "detonator")
        self.assertIn("blew up", outcome.error)


class TestLegacyAdapterUnchanged(unittest.TestCase):
    """The migration must not leak Result objects to external callers."""

    def test_returns_the_raw_value_not_a_result(self):
        value = compat.legacy_run("slugify", "Hello Big World")
        self.assertNotIsInstance(value, Result)
        self.assertEqual(value, "hello-big-world")

    def test_raises_on_plugin_failure(self):
        with self.assertRaises(RuntimeError):
            compat.legacy_run("explode", "say boom")


if __name__ == "__main__":
    unittest.main()
