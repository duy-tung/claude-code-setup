"""Stdlib tests for the context analyzer defaults."""

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "context_analyzer.py"
SPEC = importlib.util.spec_from_file_location("context_analyzer", SCRIPT)
CONTEXT_ANALYZER = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(CONTEXT_ANALYZER)


class Opus5ContextDefaultsTests(unittest.TestCase):
    def test_uses_one_million_token_window_and_explicit_heuristics(self):
        result = CONTEXT_ANALYZER.analyze_context(
            [{"role": "user", "content": "hello"}]
        )
        self.assertEqual(result.token_limit, 1_000_000)
        self.assertEqual(result.warning_utilization, 0.80)
        self.assertEqual(result.critical_utilization, 0.90)

    def test_budget_uses_configured_capacity_thresholds(self):
        result = CONTEXT_ANALYZER.calculate_budget(
            100, 100, 100, 100,
            warning_utilization=0.75,
            critical_utilization=0.95,
        )
        # 400 input tokens + 15% response buffer = 460 total.
        self.assertEqual(result["warning_threshold"], 345)
        self.assertEqual(result["critical_threshold"], 437)

    def test_cli_rejects_reversed_thresholds(self):
        with tempfile.TemporaryDirectory() as tmp:
            context_file = Path(tmp) / "context.json"
            context_file.write_text(json.dumps({"messages": []}), encoding="utf-8")
            completed = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "analyze",
                    str(context_file),
                    "--warning-threshold",
                    "0.95",
                    "--critical-threshold",
                    "0.80",
                ],
                capture_output=True,
                text=True,
                timeout=10,
            )
        self.assertEqual(completed.returncode, 2)
        self.assertIn("0 < warning < critical <= 1", completed.stderr)


if __name__ == "__main__":
    unittest.main()
