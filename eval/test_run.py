#!/usr/bin/env python3
"""Stdlib regression tests for the eval runner and effort sweep."""
from __future__ import annotations

import contextlib
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

EVAL_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(EVAL_DIR))
import effort_sweep  # noqa: E402
import run as eval_run  # noqa: E402


def record(**overrides) -> dict:
    base = {
        "solved": False,
        "run_valid": True,
        "error": None,
        "grade_detail": "",
        "num_turns": 1,
        "input_tokens": 100,
        "output_tokens": 20,
        "output_chars": 80,
        "created_file_count": 0,
        "workflow_artifact_count": 0,
        "workflow_artifact_budget": 0,
        "cost_usd": 0.25,
        "agent_ms": 1000,
        "models": ["claude-opus-5"],
        "requested_model": "claude-opus-5",
        "requested_effort": "high",
        "task": "task-a",
        "variant": "default",
        "run": 0,
    }
    base.update(overrides)
    return base


def cli_result(**overrides) -> dict:
    """Build the minimum current Claude Code terminal ResultMessage."""
    base = {
        "type": "result",
        "subtype": "success",
        "is_error": False,
        "session_id": "eval-test-session",
        "num_turns": 1,
        "usage": {},
        "result": "done",
    }
    base.update(overrides)
    return base


class RequestedSettingsTests(unittest.TestCase):
    def test_cli_value_wins_over_environment(self):
        with patch.dict(os.environ, {"CK_EVAL_MODEL": "claude-opus-4-8"}):
            self.assertEqual(
                eval_run.resolve_requested_setting(
                    "claude-opus-5", "CK_EVAL_MODEL"
                ),
                "claude-opus-5",
            )

    def test_environment_is_fallback(self):
        with patch.dict(os.environ, {"CK_EVAL_EFFORT": " medium "}):
            self.assertEqual(
                eval_run.resolve_requested_setting(None, "CK_EVAL_EFFORT"),
                "medium",
            )

    def test_run_trial_records_requested_model_and_effort(self):
        with tempfile.TemporaryDirectory() as tmp:
            task_dir = Path(tmp)
            (task_dir / "fixture").mkdir()
            task = {
                "_dir": task_dir,
                "grade": {},
                "workflow_artifact_budget": 0,
            }
            grade_result = SimpleNamespace(
                solved=False, returncode=1, detail="expected failure"
            )
            with patch.object(eval_run.grader, "grade", return_value=grade_result):
                result = eval_run.run_trial(
                    task, {"claude_args": []}, "mock-noop", 1, False,
                    requested_model="claude-opus-5",
                    requested_effort="high",
                )
        self.assertEqual(result["requested_model"], "claude-opus-5")
        self.assertEqual(result["requested_effort"], "high")

    def test_run_trial_counts_new_workflow_artifacts(self):
        with tempfile.TemporaryDirectory() as tmp:
            task_dir = Path(tmp)
            (task_dir / "fixture").mkdir()
            task = {
                "_dir": task_dir,
                "grade": {},
                "workflow_artifact_budget": 0,
            }
            grade_result = SimpleNamespace(
                solved=True, returncode=0, detail=""
            )

            def create_plan(_task, _variant, workdir, *_args, **_kwargs):
                plan = workdir / "plans" / "unneeded" / "plan.md"
                plan.parent.mkdir(parents=True)
                plan.write_text("plan", encoding="utf-8")
                return {}

            with patch.object(
                eval_run, "_invoke_claude", side_effect=create_plan
            ), patch.object(
                eval_run.grader, "grade", return_value=grade_result
            ):
                result = eval_run.run_trial(
                    task, {"claude_args": []}, "claude", 1, False
                )

        self.assertEqual(result["created_file_count"], 1)
        self.assertEqual(result["workflow_artifact_count"], 1)
        self.assertFalse(result["run_valid"])
        self.assertIn("workflow artifact budget exceeded", result["error"])

    def test_run_trial_counts_root_summary_and_docs_report(self):
        with tempfile.TemporaryDirectory() as tmp:
            task_dir = Path(tmp)
            (task_dir / "fixture").mkdir()
            task = {
                "_dir": task_dir,
                "grade": {},
                "workflow_artifact_budget": 0,
            }
            grade_result = SimpleNamespace(solved=True, returncode=0, detail="")

            def create_reports(_task, _variant, workdir, *_args, **_kwargs):
                (workdir / "IMPLEMENTATION_SUMMARY.md").write_text(
                    "summary", encoding="utf-8"
                )
                report = workdir / "docs" / "report.md"
                report.parent.mkdir()
                report.write_text("report", encoding="utf-8")
                return {}

            with patch.object(
                eval_run, "_invoke_claude", side_effect=create_reports
            ), patch.object(
                eval_run.grader, "grade", return_value=grade_result
            ):
                result = eval_run.run_trial(
                    task, {"claude_args": []}, "claude", 1, False
                )

        self.assertFalse(result["run_valid"])
        self.assertEqual(result["workflow_artifact_count"], 2)
        self.assertEqual(
            result["workflow_artifacts"],
            ["IMPLEMENTATION_SUMMARY.md", "docs/report.md"],
        )

    def test_run_trial_rejects_and_restores_visible_test_tampering(self):
        with tempfile.TemporaryDirectory() as tmp:
            task_dir = Path(tmp)
            fixture = task_dir / "fixture"
            fixture.mkdir()
            original = b"raise AssertionError('real grader test')\n"
            (fixture / "test_calc.py").write_bytes(original)
            task = {
                "_dir": task_dir,
                "grade": {},
                "workflow_artifact_budget": 0,
            }

            def tamper(_task, _variant, workdir, *_args, **_kwargs):
                (workdir / "test_calc.py").write_text(
                    "# fake passing test\n", encoding="utf-8"
                )
                return {}

            def grade_restored(workdir, _grade):
                self.assertEqual((workdir / "test_calc.py").read_bytes(), original)
                return SimpleNamespace(solved=True, returncode=0, detail="")

            with patch.object(
                eval_run, "_invoke_claude", side_effect=tamper
            ), patch.object(
                eval_run.grader, "grade", side_effect=grade_restored
            ):
                result = eval_run.run_trial(
                    task, {"claude_args": []}, "claude", 1, False
                )

        self.assertFalse(result["run_valid"])
        self.assertEqual(result["protected_file_violations"], ["test_calc.py"])
        self.assertIn("protected grader file modified", result["error"])

    def test_full_kit_variant_is_staged_inside_fixture(self):
        with tempfile.TemporaryDirectory() as tmp:
            task_dir = Path(tmp)
            (task_dir / "fixture").mkdir()
            task = {"_dir": task_dir, "grade": {}}

            def inspect_staging(_task, _variant, workdir, *_args, **_kwargs):
                self.assertTrue((workdir / ".claude" / "settings.json").is_file())
                return {}

            with patch.object(
                eval_run, "_invoke_claude", side_effect=inspect_staging
            ), patch.object(
                eval_run.grader,
                "grade",
                return_value=SimpleNamespace(
                    solved=False, returncode=1, detail="expected failure"
                ),
            ):
                result = eval_run.run_trial(
                    task, {"claude_args": [], "stage_kit": True},
                    "claude", 1, False
                )

        self.assertTrue(result["run_valid"])

    def test_shipped_variants_load_only_isolated_project_settings(self):
        for name in ("baseline", "full-kit"):
            with self.subTest(variant=name):
                self.assertEqual(
                    eval_run.load_variant(name)["claude_args"],
                    ["--setting-sources", "project"],
                )

    def test_discount_refactor_hidden_test_rejects_behavior_only_patch(self):
        task = eval_run.load_task("discount-refactor")
        with tempfile.TemporaryDirectory() as tmp:
            workdir = Path(tmp) / "work"
            shutil.copytree(task["_dir"] / "fixture", workdir)
            (workdir / "pricing.py").write_text(
                """def final_price(price, customer_type):
    if customer_type == "regular":
        return price
    elif customer_type == "member":
        return price * 0.9
    elif customer_type == "vip":
        return price * 0.8
    elif customer_type == "staff":
        return price * 0.5
    raise ValueError(f"unknown customer type: {customer_type}")
""",
                encoding="utf-8",
            )
            visible = subprocess.run(
                [sys.executable, "-m", "unittest", "test_pricing.py"],
                cwd=workdir, capture_output=True, text=True,
            )
            self.assertEqual(visible.returncode, 0, visible.stderr)
            for src in (task["_dir"] / "tests").rglob("*"):
                if src.is_file():
                    shutil.copy2(src, workdir / src.relative_to(task["_dir"] / "tests"))
            graded = eval_run.grader.grade(workdir, task["grade"])

        self.assertFalse(graded.solved)


class ModelPinTests(unittest.TestCase):
    def test_fixed_model_requires_exact_model_usage_key(self):
        self.assertIsNone(
            eval_run.model_pin_error("claude-opus-5", ["claude-opus-5"])
        )
        self.assertIn(
            "modelUsage reported",
            eval_run.model_pin_error(
                "claude-opus-5", ["claude-opus-4-8"]
            ),
        )

    def test_fixed_model_rejects_mixed_model_usage(self):
        error = eval_run.model_pin_error(
            "claude-opus-5", ["claude-opus-5", "claude-haiku-4-5"]
        )
        self.assertIn("also reported", error)
        self.assertIn("claude-haiku-4-5", error)

    def test_alias_matches_family_but_missing_usage_fails(self):
        self.assertEqual(
            eval_run.matching_models("opus", ["claude-opus-5"]),
            ["claude-opus-5"],
        )
        self.assertIn(
            "omitted modelUsage",
            eval_run.model_pin_error("opus", []),
        )
        self.assertIn(
            "also reported",
            eval_run.model_pin_error(
                "opus", ["claude-opus-5", "claude-haiku-4-5"]
            ),
        )

    def test_invoke_claude_appends_cli_pin_and_verifies_model_usage(self):
        payload = cli_result(
            modelUsage={"claude-opus-5": {}},
            usage={"input_tokens": 10, "output_tokens": 5},
        )
        completed = subprocess.CompletedProcess(
            args=[], returncode=0, stdout=json.dumps(payload), stderr=""
        )
        variant = {
            "claude_args": ["--model", "claude-opus-4-8", "--effort", "low"]
        }
        with patch.object(eval_run.subprocess, "run", return_value=completed) as run:
            result = eval_run._invoke_claude(
                {"prompt": "fix it"}, variant, Path("/tmp"), 10, False,
                requested_model="claude-opus-5",
                requested_effort="high",
            )

        command = run.call_args.args[0]
        self.assertGreater(
            max(i for i, value in enumerate(command) if value == "claude-opus-5"),
            max(i for i, value in enumerate(command) if value == "claude-opus-4-8"),
        )
        self.assertEqual(command[command.index("--max-turns") - 1], "high")
        self.assertTrue(result["model_pin_ok"])
        self.assertEqual(result["output_chars"], 4)
        self.assertIsNone(result["error"])

    def test_invoke_claude_uses_canonical_models_and_whole_tree_tokens(self):
        payload = cli_result(
            modelUsage={
                "provider/deployment-a": {
                    "canonicalModel": "claude-opus-5",
                    "inputTokens": 100,
                    "outputTokens": 20,
                },
                "provider/deployment-b": {
                    "canonicalModel": "claude-opus-5",
                    "inputTokens": 50,
                    "outputTokens": 10,
                },
            },
            usage={"input_tokens": 1, "output_tokens": 1},
        )
        completed = subprocess.CompletedProcess(
            args=[], returncode=0, stdout=json.dumps(payload), stderr=""
        )
        with patch.object(eval_run.subprocess, "run", return_value=completed):
            result = eval_run._invoke_claude(
                {"prompt": "fix it"}, {"claude_args": []}, Path("/tmp"),
                10, False, requested_model="claude-opus-5"
            )

        self.assertEqual(result["models"], ["claude-opus-5"])
        self.assertEqual(
            result["raw_models"],
            ["provider/deployment-a", "provider/deployment-b"],
        )
        self.assertEqual(result["input_tokens"], 150)
        self.assertEqual(result["output_tokens"], 30)
        self.assertTrue(result["model_pin_ok"])
        self.assertIsNone(result["error"])

    def test_invoke_claude_marks_mismatched_live_model_invalid(self):
        payload = cli_result(modelUsage={"claude-opus-4-8": {}})
        completed = subprocess.CompletedProcess(
            args=[], returncode=0, stdout=json.dumps(payload), stderr=""
        )
        with patch.object(eval_run.subprocess, "run", return_value=completed):
            result = eval_run._invoke_claude(
                {"prompt": "fix it"}, {"claude_args": []}, Path("/tmp"),
                10, False, requested_model="claude-opus-5"
            )
        self.assertFalse(result["model_pin_ok"])
        self.assertIn("claude-opus-4-8", result["error"])

    def test_invoke_claude_rejects_missing_model_usage_when_pinned(self):
        completed = subprocess.CompletedProcess(
            args=[], returncode=0, stdout=json.dumps(cli_result()),
            stderr=""
        )
        with patch.object(eval_run.subprocess, "run", return_value=completed):
            result = eval_run._invoke_claude(
                {"prompt": "fix it"}, {"claude_args": []}, Path("/tmp"),
                10, False, requested_model="claude-opus-5"
            )
        self.assertFalse(result["model_pin_ok"])
        self.assertIn("omitted modelUsage", result["error"])

    def test_invoke_claude_rejects_nonzero_exit_without_stderr(self):
        payload = cli_result(modelUsage={"claude-opus-5": {}})
        completed = subprocess.CompletedProcess(
            args=[], returncode=2, stdout=json.dumps(payload), stderr=""
        )
        with patch.object(eval_run.subprocess, "run", return_value=completed):
            result = eval_run._invoke_claude(
                {"prompt": "fix it"}, {"claude_args": []}, Path("/tmp"),
                10, False, requested_model="claude-opus-5"
            )
        self.assertIn("CLI exited with status 2", result["error"])

    def test_invoke_claude_rejects_json_error_flag(self):
        payload = cli_result(
            is_error=True, modelUsage={"claude-opus-5": {}}
        )
        completed = subprocess.CompletedProcess(
            args=[], returncode=0, stdout=json.dumps(payload), stderr=""
        )
        with patch.object(eval_run.subprocess, "run", return_value=completed):
            result = eval_run._invoke_claude(
                {"prompt": "fix it"}, {"claude_args": []}, Path("/tmp"),
                10, False, requested_model="claude-opus-5"
            )
        self.assertIn("is_error=true", result["error"])

    def test_invoke_claude_rejects_structured_sdk_errors(self):
        payload = cli_result(
            errors=["rate limit exhausted"],
            api_error_status=429,
            modelUsage={"claude-opus-5": {}},
        )
        completed = subprocess.CompletedProcess(
            args=[], returncode=0, stdout=json.dumps(payload), stderr=""
        )
        with patch.object(eval_run.subprocess, "run", return_value=completed):
            result = eval_run._invoke_claude(
                {"prompt": "fix it"}, {"claude_args": []}, Path("/tmp"),
                10, False, requested_model="claude-opus-5"
            )
        self.assertIn("rate limit exhausted", result["error"])
        self.assertIn("API error status=429", result["error"])

    def test_invoke_claude_rejects_empty_invalid_or_incomplete_results(self):
        cases = {
            "empty": "",
            "not-json": "not json",
            "unrelated-json": json.dumps({"hello": "world"}),
            "success-without-result": json.dumps(
                cli_result(result=None)
            ),
        }
        for name, stdout in cases.items():
            with self.subTest(case=name):
                completed = subprocess.CompletedProcess(
                    args=[], returncode=0, stdout=stdout, stderr=""
                )
                with patch.object(
                    eval_run.subprocess, "run", return_value=completed
                ):
                    result = eval_run._invoke_claude(
                        {"prompt": "fix it"}, {"claude_args": []}, Path("/tmp"),
                        10, False,
                    )
                self.assertIsNotNone(result["error"])
                self.assertIn("ResultMessage", result["error"])

    def test_invoke_claude_rejects_noncompletion_terminal_reasons(self):
        for terminal_reason in (
            "max_turns", "api_error", "aborted_streaming", "aborted_tools"
        ):
            with self.subTest(terminal_reason=terminal_reason):
                payload = cli_result(terminal_reason=terminal_reason)
                completed = subprocess.CompletedProcess(
                    args=[], returncode=0, stdout=json.dumps(payload), stderr=""
                )
                with patch.object(
                    eval_run.subprocess, "run", return_value=completed
                ):
                    result = eval_run._invoke_claude(
                        {"prompt": "fix it"}, {"claude_args": []}, Path("/tmp"),
                        10, False,
                    )
                self.assertIn(f"terminal_reason={terminal_reason}", result["error"])

    def test_invoke_claude_rejects_refusal_and_discards_partial_output(self):
        payload = cli_result(
            stop_reason="refusal", result="partial refused output"
        )
        completed = subprocess.CompletedProcess(
            args=[], returncode=0, stdout=json.dumps(payload), stderr=""
        )
        with patch.object(eval_run.subprocess, "run", return_value=completed):
            result = eval_run._invoke_claude(
                {"prompt": "fix it"}, {"claude_args": []}, Path("/tmp"),
                10, False,
            )
        self.assertIn("stop_reason=refusal", result["error"])


class SuiteValidityTests(unittest.TestCase):
    def test_mock_oracle_failure_is_invalid(self):
        valid, issues = eval_run.assess_suite([record(solved=False)], "mock")
        self.assertFalse(valid)
        self.assertIn("oracle did not solve", issues[0])

    def test_mock_noop_accidental_solve_is_invalid(self):
        valid, issues = eval_run.assess_suite(
            [record(solved=True)], "mock-noop"
        )
        self.assertFalse(valid)
        self.assertIn("no-op unexpectedly solved", issues[0])

    def test_live_unsolved_task_is_valid_but_model_error_is_not(self):
        valid, _ = eval_run.assess_suite([record(solved=False)], "claude")
        self.assertTrue(valid)
        valid, issues = eval_run.assess_suite(
            [record(run_valid=False, error="requested model mismatch")],
            "claude",
        )
        self.assertFalse(valid)
        self.assertIn("requested model mismatch", issues[0])

    def test_run_suite_returns_false_for_broken_mock(self):
        with tempfile.TemporaryDirectory() as tmp:
            out_file = Path(tmp) / "mock.ndjson"
            with patch.object(eval_run, "load_task", return_value={}), \
                 patch.object(eval_run, "run_trial", return_value=record(solved=False)), \
                 contextlib.redirect_stdout(io.StringIO()):
                valid = eval_run.run_suite(
                    ["task-a"], [None], 1, "mock", 1, False, out_file
                )
        self.assertFalse(valid)

    def test_run_suite_returns_false_for_noop_that_solves(self):
        with tempfile.TemporaryDirectory() as tmp:
            out_file = Path(tmp) / "noop.ndjson"
            with patch.object(eval_run, "load_task", return_value={}), \
                 patch.object(eval_run, "run_trial", return_value=record(solved=True)), \
                 contextlib.redirect_stdout(io.StringIO()):
                valid = eval_run.run_suite(
                    ["task-a"], [None], 1, "mock-noop", 1, False, out_file
                )
        self.assertFalse(valid)

    def test_main_propagates_run_suite_failure(self):
        with patch.object(sys, "argv", ["run.py", "--all", "--mock"]), \
             patch.object(eval_run, "all_task_ids", return_value=["task-a"]), \
             patch.object(eval_run, "run_suite", return_value=False), \
             patch.dict(os.environ, {"CK_EVAL_MODEL": "", "CK_EVAL_EFFORT": ""}), \
             contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(eval_run.main(), 1)

    def test_mock_modes_are_mutually_exclusive(self):
        with patch.object(
            sys, "argv", ["run.py", "--all", "--mock", "--mock-noop"]
        ), self.assertRaises(SystemExit) as raised, \
             contextlib.redirect_stderr(io.StringIO()):
            eval_run.main()
        self.assertEqual(raised.exception.code, 2)

    def test_grader_rejects_failed_setup_even_when_test_would_pass(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = eval_run.grader.grade(
                Path(tmp),
                {
                    "setup": [[sys.executable, "-c", "raise SystemExit(7)"]],
                    "test_cmd": [sys.executable, "-c", "raise SystemExit(0)"],
                },
            )
        self.assertFalse(result.solved)
        self.assertEqual(result.returncode, 7)
        self.assertIn("setup failed with exit 7", result.detail)


class EffortSweepTests(unittest.TestCase):
    def test_summary_reports_solve_rate_turns_tokens_cost_and_latency(self):
        summary = effort_sweep.summarize_records(
            "high",
            [record(solved=True, num_turns=2, input_tokens=100,
                    output_tokens=20, cost_usd=1.0, agent_ms=1000),
             record(solved=False, num_turns=4, input_tokens=300,
                    output_tokens=60, cost_usd=3.0, agent_ms=3000)],
            "claude-opus-5",
        )
        self.assertEqual(summary["solve_rate"], 0.5)
        self.assertEqual(summary["mean_turns"], 3.0)
        self.assertEqual(summary["mean_input_tokens"], 200.0)
        self.assertEqual(summary["mean_output_tokens"], 40.0)
        self.assertEqual(summary["mean_output_chars"], 80.0)
        self.assertEqual(summary["mean_workflow_artifacts"], 0.0)
        self.assertEqual(summary["mean_cost_usd"], 2.0)
        self.assertEqual(summary["mean_latency_ms"], 2000.0)

    def test_summary_does_not_count_invalid_live_run_as_solved(self):
        summary = effort_sweep.summarize_records(
            "high", [record(solved=True, run_valid=False)], "claude-opus-5"
        )
        self.assertEqual(summary["solved"], 0)

    def test_sweep_rejects_model_change_between_efforts(self):
        summaries = [
            {"effort": "low", "matching_models": ["claude-opus-5"],
             "actual_models": ["claude-opus-5"]},
            {"effort": "high", "matching_models": ["claude-opus-5-v2"],
             "actual_models": ["claude-opus-5-v2"]},
        ]
        self.assertIn(
            "actual model changed",
            effort_sweep.model_consistency_error(
                summaries, "opus"
            ),
        )

    def test_default_effort_list_is_low_medium_high(self):
        self.assertEqual(
            effort_sweep.parse_efforts("low,medium,high"),
            ["low", "medium", "high"],
        )


if __name__ == "__main__":
    unittest.main()
