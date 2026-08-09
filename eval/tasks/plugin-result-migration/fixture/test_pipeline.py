import unittest

import plugins  # noqa: F401  (registers everything)
from core import compat
from core.pipeline import run_pipeline


class TestPipeline(unittest.TestCase):
    def test_single_step(self):
        self.assertEqual(run_pipeline(["upper"], "abc"), "ABC")

    def test_chained_steps(self):
        self.assertEqual(run_pipeline(["upper", "reverse"], "abc"), "CBA")

    def test_slugify_is_registered(self):
        self.assertEqual(run_pipeline(["slugify"], "Hello Big World"), "hello-big-world")

    def test_legacy_adapter_returns_raw_value(self):
        self.assertEqual(compat.legacy_run("upper", "abc"), "ABC")

    def test_pipeline_reports_a_failing_step_without_raising(self):
        outcome = run_pipeline(["upper", "explode"], "say boom")
        self.assertFalse(outcome.ok)
        self.assertEqual(outcome.error_step, "explode")
