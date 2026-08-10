#!/usr/bin/env python3
"""
Tier 1 — Execution-graded task-suite runner with A/B support.

For each golden task it copies a pinned fixture into a throwaway working dir,
lets a Claude Code variant act on it (headless `claude -p --output-format json`),
then grades by running the task's real tests. Repeats N times per (task, variant)
to handle agent stochasticity, and compares two variants with a paired test.

This is the harness scaffold — it is verifiable WITHOUT a live `claude` CLI via
--mock (apply the task's oracle = "perfect agent") and --mock-noop (do nothing =
"useless agent"), which prove fixture + oracle + grader are wired correctly.

Usage:
  python3 eval/run.py --all                                  # run every task, default variant
  python3 eval/run.py --task fix-off-by-one --runs 5
  python3 eval/run.py --all --model claude-opus-5 --effort high
  python3 eval/run.py --all --variant-a baseline --variant-b full-kit --runs 5
  python3 eval/run.py --all --mock                           # apply oracle (no claude needed)
  python3 eval/run.py --all --mock-noop                      # sanity: tasks must FAIL

Env:
  CK_EVAL_CMD           AI CLI to spawn (default "claude"; e.g. "ccs glm")
  CK_EVAL_CLAUDE_ARGS   extra args appended to the claude invocation
                        (default "--permission-mode bypassPermissions")
  CK_EVAL_MODEL         fallback for --model, e.g. "claude-opus-5"
  CK_EVAL_EFFORT        fallback for --effort, e.g. "high"
  CK_EVAL_TIMEOUT_SEC   per-run agent timeout (default 180)

The summary prints "model(s) actually run" (from the result JSON's modelUsage).
When a model is pinned, missing or mismatched modelUsage invalidates the live run.
"""
from __future__ import annotations

import argparse
import fnmatch
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path

EVAL_DIR = Path(__file__).resolve().parent
REPO_ROOT = EVAL_DIR.parent
TASKS_DIR = EVAL_DIR / "tasks"
VARIANTS_DIR = EVAL_DIR / "variants"
RESULTS_DIR = EVAL_DIR / "results"

sys.path.insert(0, str(EVAL_DIR))
import grader  # noqa: E402
import stats  # noqa: E402

DEFAULT_CLAUDE_ARGS = ["--permission-mode", "bypassPermissions"]
JSON_OBJ_RE = re.compile(r"\{.*\}", re.DOTALL)
EFFORT_LEVELS = ("low", "medium", "high", "xhigh", "max")
RESULT_SUBTYPES = {
    "success",
    "error_during_execution",
    "error_max_turns",
    "error_max_budget_usd",
    "error_max_structured_output_retries",
}
# Share of total output tokens below which a non-requested model reads as
# Claude Code's own bookkeeping rather than a fallback doing the task.
AUXILIARY_OUTPUT_SHARE_MAX = 0.10
# What each arm spends to reach the same outcome. Solve rate saturates on this
# task class, so these are the metrics that can still separate two variants.
EFFICIENCY_METRICS = (
    ("num_turns", "turns", "{:.2f}"),
    ("modified_file_count", "files touched", "{:.2f}"),
    ("output_chars", "output chars", "{:.0f}"),
    ("cache_creation_tokens", "cache created", "{:.0f}"),
    ("cache_read_tokens", "cache read", "{:.0f}"),
    ("cost_usd", "cost $", "{:.3f}"),
    ("agent_ms", "latency ms", "{:.0f}"),
)
WORKFLOW_ARTIFACT_NAME_RE = re.compile(
    r"(?:^|[-_])(plan|report|summary|journal)(?:[-_][^.]*)?\.(?:md|txt|json|ya?ml)$",
    re.I,
)


# ── Task / variant loading ───────────────────────────────────────────────────

def load_task(task_id: str) -> dict:
    task_path = TASKS_DIR / task_id / "task.json"
    task = json.loads(task_path.read_text(encoding="utf-8"))
    task["_dir"] = TASKS_DIR / task_id
    task.setdefault("id", task_id)
    return task


def all_task_ids() -> list[str]:
    return sorted(p.name for p in TASKS_DIR.iterdir()
                  if (p / "task.json").exists())


def load_variant(name: str | None) -> dict:
    if name is None:
        return {"label": "default", "claude_args": []}
    variant = json.loads((VARIANTS_DIR / f"{name}.json").read_text(encoding="utf-8"))
    variant.setdefault("label", name)
    variant.setdefault("claude_args", [])
    return variant


# ── A single trial ───────────────────────────────────────────────────────────

def _extract_result_json(stdout: str) -> dict:
    try:
        return json.loads(stdout)
    except json.JSONDecodeError:
        match = JSON_OBJ_RE.search(stdout)
        if match:
            try:
                return json.loads(match.group(0))
            except json.JSONDecodeError:
                pass
    return {}


def resolve_requested_setting(cli_value: str | None, env_name: str) -> str | None:
    """Resolve a CLI setting with an environment fallback (CLI wins)."""
    value = cli_value if cli_value is not None else os.environ.get(env_name)
    if value is None:
        return None
    value = value.strip()
    return value or None


def result_message_error(data: dict) -> str | None:
    """Validate the minimum current Claude Code terminal-result contract."""
    if not data:
        return "CLI produced no parseable ResultMessage JSON"
    if data.get("type") != "result":
        return f"CLI JSON is not a ResultMessage (type={data.get('type')!r})"
    if data.get("subtype") not in RESULT_SUBTYPES:
        return (
            "CLI ResultMessage has unknown or missing subtype: "
            f"{data.get('subtype')!r}"
        )
    if not isinstance(data.get("is_error"), bool):
        return "CLI ResultMessage omitted boolean is_error"
    session_id = data.get("session_id")
    if not isinstance(session_id, str) or not session_id.strip():
        return "CLI ResultMessage omitted session_id"
    num_turns = data.get("num_turns")
    if (not isinstance(num_turns, int) or isinstance(num_turns, bool)
            or num_turns < 0):
        return "CLI ResultMessage omitted non-negative integer num_turns"
    if not isinstance(data.get("usage"), dict):
        return "CLI ResultMessage omitted usage"
    if data.get("subtype") == "success" and not isinstance(data.get("result"), str):
        return "CLI success ResultMessage omitted string result"
    return None


def matching_models(requested_model: str, actual_models: list[str]) -> list[str]:
    """Return modelUsage keys that satisfy a fixed ID or Claude Code alias pin."""
    requested = requested_model.strip().lower()
    actual = sorted({str(model) for model in actual_models})
    if requested in {"opus", "sonnet", "haiku"}:
        family = re.compile(rf"(?:^|[-_/]){re.escape(requested)}(?:[-_/]|$)", re.I)
        return [model for model in actual if family.search(model)]
    return [model for model in actual if model.lower() == requested]


def _split_by_work(requested_model: str,
                   model_output_tokens: dict) -> tuple[dict, dict, int]:
    """Partition modelUsage into requested vs other, with their output totals."""
    actual = {
        str(model): (tokens if isinstance(tokens, (int, float))
                     and not isinstance(tokens, bool) else 0)
        for model, tokens in (model_output_tokens or {}).items()
    }
    matched = set(matching_models(requested_model, list(actual)))
    requested = {m: t for m, t in actual.items() if m in matched}
    other = {m: t for m, t in actual.items() if m not in matched}
    return requested, other, sum(actual.values())


def auxiliary_models(requested_model: str | None,
                     model_output_tokens: dict) -> list[str]:
    """Non-requested models tolerated as Claude Code's own bookkeeping."""
    if not requested_model:
        return []
    _, other, total = _split_by_work(requested_model, model_output_tokens)
    if not other or total <= 0:
        return []
    return sorted(m for m, t in other.items()
                  if t / total <= AUXILIARY_OUTPUT_SHARE_MAX)


def model_pin_error(requested_model: str | None,
                    model_output_tokens: dict) -> str | None:
    """Explain why modelUsage does not prove the requested model did the work.

    Presence alone is the wrong test. Claude Code runs a small auxiliary model
    for its own bookkeeping — summaries, titles — alongside the model doing the
    task, so a strict "no other model may appear" rule invalidates every run of
    an un-pinned arm. That is precisely the arm an A/B needs, and invalid runs
    count as unsolved, so the strict rule manufactures a false effect.

    Judge by work share instead: a model that produced a negligible slice of the
    output is bookkeeping; one that produced a material slice is a fallback or a
    stray delegation, which is what this check exists to catch.
    """
    if not requested_model:
        return None
    requested, other, total = _split_by_work(requested_model, model_output_tokens)
    if not (requested or other):
        return (f"requested model {requested_model!r}, but live result omitted "
                "modelUsage")
    if not requested:
        return (f"requested model {requested_model!r}, but modelUsage reported "
                f"{', '.join(sorted(other))}")
    if not other:
        return None
    if total <= 0:
        # Nothing to judge share by; stay strict rather than silently passing.
        return (f"requested model {requested_model!r}, but modelUsage also "
                f"reported {', '.join(sorted(other))} with no token attribution")
    working = sorted(m for m, t in other.items()
                     if t / total > AUXILIARY_OUTPUT_SHARE_MAX)
    if working:
        detail = ", ".join(f"{m} ({other[m] / total:.0%} of output)" for m in working)
        return (f"requested model {requested_model!r}, but {detail} did a "
                "material share of the work")
    return None


def is_workflow_artifact(
    relative_path: str,
    exempt_paths: list[str] | None = None,
) -> bool:
    """Identify unrequested workflow prose, honoring task deliverable exemptions."""
    normalized = relative_path.replace("\\", "/")
    if normalized.startswith(".claude/"):
        return False
    if any(
        fnmatch.fnmatchcase(normalized, pattern.replace("\\", "/"))
        for pattern in (exempt_paths or [])
    ):
        return False
    lowered = normalized.lower()
    if lowered.endswith(".md"):
        return True
    if lowered.startswith(("plans/", "reports/", "docs/journals/")):
        return True
    return bool(WORKFLOW_ARTIFACT_NAME_RE.search(Path(normalized).name))


def run_trial(task: dict, variant: dict, mode: str, max_turns: int,
              verbose: bool, requested_model: str | None = None,
              requested_effort: str | None = None) -> dict:
    """mode ∈ {'claude', 'mock', 'mock-noop'}. Returns a metrics record."""
    fixture = task["_dir"] / "fixture"
    metrics = {"subtype": None, "num_turns": None,
               "cost_usd": None, "agent_ms": None, "error": None,
               "output_chars": None, "created_file_count": 0,
               "modified_files": [], "modified_file_count": 0,
               "cache_creation_tokens": None, "cache_read_tokens": None,
               "workflow_artifact_count": 0,
               "workflow_artifacts": [],
               "workflow_artifact_budget": task.get("workflow_artifact_budget"),
               "behavior_ok": True, "behavior_issues": [],
               "protected_file_violations": [],
               "models": [], "raw_models": [], "model_output_tokens": {},
               "auxiliary_models": [], "model_pin_ok": None,
               "requested_model": requested_model,
               "requested_effort": requested_effort}

    with tempfile.TemporaryDirectory(prefix="ckeval-") as tmp:
        workdir = Path(tmp) / "work"
        shutil.copytree(fixture, workdir)
        fixture_files = {
            path.relative_to(workdir).as_posix()
            for path in workdir.rglob("*") if path.is_file()
        }
        protected_paths = {
            path for path in fixture_files
            if Path(path).name.startswith("test_")
            or Path(path).name.endswith("_test.py")
        }
        protected_paths.update(task.get("protected_paths", []))
        protected_contents = {
            path: (workdir / path).read_bytes()
            for path in protected_paths
            if (workdir / path).is_file()
        }

        if variant.get("stage_kit"):
            # The repository stores the installable project profile in `claude/`.
            # Stage it as `.claude/` inside the isolated fixture so this variant
            # exercises the current branch rather than the caller's project cwd.
            shutil.copytree(
                REPO_ROOT / "claude",
                workdir / ".claude",
                ignore=shutil.ignore_patterns(
                    "__pycache__", "*.pyc", ".DS_Store", ".logs"
                ),
            )

        # Digest, not just names: scope discipline is about which files the
        # agent decided to touch, and a rename-free edit is invisible to a
        # name-only snapshot.
        baseline_digests = {
            path.relative_to(workdir).as_posix(): path.read_bytes()
            for path in workdir.rglob("*") if path.is_file()
        }
        baseline_files = set(baseline_digests)
        # Monotonic, to match the clock subprocess.run's timeout uses. Wall clock
        # keeps ticking while a machine sleeps, which fabricated a two-hour
        # "latency" for a run that the timeout never saw as overdue.
        start = time.monotonic()

        if mode == "mock":
            oracle = task["_dir"] / "oracle"
            for src in oracle.rglob("*"):
                if src.is_file():
                    dst = workdir / src.relative_to(oracle)
                    dst.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(src, dst)
            metrics["subtype"] = "mock-oracle"
        elif mode == "mock-noop":
            metrics["subtype"] = "mock-noop"
        else:
            metrics.update(_invoke_claude(
                task, variant, workdir, max_turns, verbose,
                requested_model=requested_model,
                requested_effort=requested_effort,
            ))

        metrics["agent_ms"] = int((time.monotonic() - start) * 1000)
        current_files = {
            path.relative_to(workdir).as_posix()
            for path in workdir.rglob("*") if path.is_file()
        }
        created_files = current_files - baseline_files
        metrics["created_file_count"] = len(created_files)

        # Files the agent edited or deleted, ignoring the staged kit itself.
        touched = []
        for relative_path, before in baseline_digests.items():
            if relative_path.startswith(".claude/"):
                continue
            target = workdir / relative_path
            after = target.read_bytes() if target.is_file() else None
            if after != before:
                touched.append(relative_path)
        metrics["modified_files"] = sorted(touched)
        metrics["modified_file_count"] = len(touched)
        metrics["workflow_artifacts"] = sorted(
            path for path in created_files
            if is_workflow_artifact(
                path, task.get("workflow_artifact_exempt_paths")
            )
        )
        metrics["workflow_artifact_count"] = len(metrics["workflow_artifacts"])
        artifact_budget = metrics["workflow_artifact_budget"]
        if (mode == "claude" and isinstance(artifact_budget, int)
                and metrics["workflow_artifact_count"] > artifact_budget):
            artifact_issue = (
                "workflow artifact budget exceeded: "
                f"{metrics['workflow_artifact_count']} > {artifact_budget}"
            )
            metrics["behavior_issues"].append(artifact_issue)
            metrics["behavior_ok"] = False

        # Visible tests give the agent useful feedback but remain part of the
        # grader contract. Detect edits/deletions, restore pristine bytes, and
        # invalidate the run so test tampering cannot manufacture a solve.
        protected_violations = []
        for relative_path, expected in protected_contents.items():
            protected_path = workdir / relative_path
            try:
                current = (
                    protected_path.read_bytes()
                    if protected_path.is_file() and not protected_path.is_symlink()
                    else None
                )
            except OSError:
                current = None
            if current == expected:
                continue

            protected_violations.append(relative_path)
            if protected_path.is_symlink() or protected_path.is_file():
                protected_path.unlink()
            elif protected_path.exists():
                shutil.rmtree(protected_path)
            protected_path.parent.mkdir(parents=True, exist_ok=True)
            protected_path.write_bytes(expected)

        if protected_violations:
            metrics["protected_file_violations"] = sorted(protected_violations)
            protected_error = (
                "protected grader file modified: "
                + ", ".join(sorted(protected_violations))
            )
            metrics["error"] = "; ".join(
                error for error in (metrics.get("error"), protected_error) if error
            )

        # Hidden tests (SWE-bench style): a task's tests/ dir is NOT in the
        # fixture the agent sees — copy it in only now, at grade time, so the
        # agent cannot hill-climb the grading tests.
        hidden = task["_dir"] / "tests"
        if hidden.is_dir():
            for src in hidden.rglob("*"):
                if src.is_file():
                    dst = workdir / src.relative_to(hidden)
                    dst.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(src, dst)

        grade_res = grader.grade(workdir, task["grade"])

    run_valid = not metrics.get("error")
    return {"solved": grade_res.solved, "grade_rc": grade_res.returncode,
            "grade_detail": grade_res.detail, "run_valid": run_valid,
            **metrics}


def _invoke_claude(task: dict, variant: dict, workdir: Path,
                   max_turns: int, verbose: bool,
                   requested_model: str | None = None,
                   requested_effort: str | None = None) -> dict:
    base = shlex.split(os.environ.get("CK_EVAL_CMD", "claude"))
    extra = shlex.split(os.environ["CK_EVAL_CLAUDE_ARGS"]) \
        if os.environ.get("CK_EVAL_CLAUDE_ARGS") else list(DEFAULT_CLAUDE_ARGS)
    timeout = int(os.environ.get("CK_EVAL_TIMEOUT_SEC", "180"))

    variant_args = [a.replace("${REPO_ROOT}", str(REPO_ROOT))
                    for a in variant.get("claude_args", [])]
    # Pin model / reasoning effort for reproducible runs (recorded + verified below).
    model_args = []
    if requested_model:
        model_args += ["--model", requested_model]
    if requested_effort:
        model_args += ["--effort", requested_effort]
    cmd = (base + ["-p", task["prompt"], "--output-format", "json"]
           + extra + variant_args + model_args
           + ["--max-turns", str(max_turns)])
    if verbose:
        print(f"       $ {' '.join(shlex.quote(c) for c in cmd)}")

    try:
        proc = subprocess.run(cmd, cwd=workdir, capture_output=True,
                              text=True, timeout=timeout)
    except FileNotFoundError:
        return {"models": [], "model_pin_ok": False if requested_model else None,
                "error": f"CLI not found: {base[0]} "
                         "(set CK_EVAL_CMD or use --mock to test the harness)"}
    except subprocess.TimeoutExpired:
        return {"subtype": "timeout", "models": [],
                "model_pin_ok": False if requested_model else None,
                "error": f"agent timeout after {timeout}s"}

    data = _extract_result_json(proc.stdout)
    if not isinstance(data, dict):
        data = {}
    usage = data.get("usage") or {}
    if not isinstance(usage, dict):
        usage = {}
    raw_model_usage = data.get("modelUsage") or data.get("model_usage") or {}
    model_usage = raw_model_usage if isinstance(raw_model_usage, dict) else {}
    result_text = data.get("result")
    raw_models = sorted(model_usage.keys())
    model_output = {}
    for raw_model, details in model_usage.items():
        canonical = (str(details.get("canonicalModel") or raw_model)
                     if isinstance(details, dict) else str(raw_model))
        tokens = details.get("outputTokens") if isinstance(details, dict) else None
        if not isinstance(tokens, (int, float)) or isinstance(tokens, bool):
            tokens = 0
        model_output[canonical] = model_output.get(canonical, 0) + tokens
    models = sorted(model_output)
    pin_error = model_pin_error(requested_model, model_output)
    process_errors = []
    schema_error = result_message_error(data)
    if schema_error:
        process_errors.append(schema_error)
    data_error = data.get("error")
    if data_error:
        process_errors.append(str(data_error)[:200])
    raw_errors = data.get("errors")
    if isinstance(raw_errors, list):
        process_errors.extend(str(error)[:200] for error in raw_errors if error)
    api_error_status = data.get("api_error_status")
    if api_error_status:
        process_errors.append(f"CLI API error status={api_error_status}")
    if proc.returncode != 0:
        detail = proc.stderr.strip() or (
            str(data.get("result", "")).strip() if data else ""
        )
        message = f"CLI exited with status {proc.returncode}"
        if detail:
            message += f": {detail[:200]}"
        process_errors.append(message)
    if data.get("is_error") is True:
        process_errors.append("CLI result marked is_error=true")
    subtype = data.get("subtype")
    if subtype in RESULT_SUBTYPES and subtype != "success":
        process_errors.append(f"CLI result subtype={subtype}")
    if data.get("stop_reason") == "refusal":
        process_errors.append("CLI result stop_reason=refusal; partial output discarded")
    terminal_reason = data.get("terminal_reason")
    if terminal_reason is not None and terminal_reason != "completed":
        process_errors.append(
            f"CLI result terminal_reason={terminal_reason}; turn did not complete"
        )
    errors = list(dict.fromkeys(
        error for error in (*process_errors, pin_error) if error
    ))

    def whole_tree_tokens(field: str, fallback_field: str):
        values = [
            details.get(field)
            for details in model_usage.values()
            if isinstance(details, dict)
            and isinstance(details.get(field), (int, float))
            and not isinstance(details.get(field), bool)
        ]
        return sum(values) if values else usage.get(fallback_field)

    return {
        "subtype": data.get("subtype") or "invalid-result",
        "num_turns": data.get("num_turns"),
        "cost_usd": data.get("total_cost_usd"),
        "input_tokens": whole_tree_tokens("inputTokens", "input_tokens"),
        "output_tokens": whole_tree_tokens("outputTokens", "output_tokens"),
        # A variant that loads a large fixed preamble pays for it once as cache
        # creation and at a tenth of the rate on every later turn. Without both
        # numbers, an input-token total cannot say whether an expensive arm is
        # expensive per session or per turn.
        "cache_creation_tokens": whole_tree_tokens(
            "cacheCreationInputTokens", "cache_creation_input_tokens"),
        "cache_read_tokens": whole_tree_tokens(
            "cacheReadInputTokens", "cache_read_input_tokens"),
        "output_chars": len(result_text) if isinstance(result_text, str) else None,
        "models": models,  # canonical model IDs for pin verification
        "raw_models": raw_models,  # provider/runtime keys from modelUsage
        "model_output_tokens": model_output,
        "auxiliary_models": auxiliary_models(requested_model, model_output),
        "model_pin_ok": pin_error is None if requested_model else None,
        "error": "; ".join(errors) or None,
    }


# ── Orchestration ────────────────────────────────────────────────────────────

def _mean(xs: list) -> float | None:
    xs = [x for x in xs if isinstance(x, (int, float))]
    return sum(xs) / len(xs) if xs else None


def run_suite(task_ids: list[str], variant_names: list[str | None],
              runs: int, mode: str, max_turns: int, verbose: bool,
              out_file: Path, requested_model: str | None = None,
              requested_effort: str | None = None) -> bool:
    variants = [load_variant(n) for n in variant_names]
    records: list[dict] = []
    # results[variant_label][task_id] = [solved bool per run]
    results: dict[str, dict[str, list[bool]]] = {v["label"]: {} for v in variants}

    out_file.parent.mkdir(parents=True, exist_ok=True)
    fh = out_file.open("w", encoding="utf-8")

    for task_id in task_ids:
        task = load_task(task_id)
        for variant in variants:
            solved_runs: list[bool] = []
            for i in range(runs):
                rec = run_trial(
                    task, variant, mode, max_turns, verbose,
                    requested_model=requested_model,
                    requested_effort=requested_effort,
                )
                rec.update({"task": task_id, "variant": variant["label"],
                            "run": i, "mode": mode})
                records.append(rec)
                counted_solved = rec["solved"] and rec["run_valid"]
                solved_runs.append(counted_solved)
                fh.write(json.dumps(rec) + "\n")
                if not rec["run_valid"]:
                    icon = "[X] "
                elif mode == "mock-noop":
                    icon = "[OK]" if not rec["solved"] else "[X] "
                else:
                    icon = "[OK]" if rec["solved"] else "[--]"
                note_parts = [rec.get("error") or rec.get("grade_detail") or ""]
                if not rec.get("behavior_ok", True):
                    note_parts.append(
                        "behavior: " + "; ".join(rec.get("behavior_issues") or [])
                    )
                note = "; ".join(part for part in note_parts if part)
                print(f"{icon} {task_id} / {variant['label']} "
                      f"run {i + 1}/{runs} ({rec['agent_ms']}ms) {note}".rstrip())
            results[variant["label"]][task_id] = solved_runs

    fh.close()
    ok = _print_summary(results, records, variants, task_ids, runs, out_file, mode)
    return ok


def assess_suite(records: list[dict], mode: str) -> tuple[bool, list[str]]:
    """Apply mode-aware harness validity rules without grading live solve-rate."""
    issues: list[str] = []
    if not records:
        return False, ["suite produced no records"]

    for rec in records:
        run_number = rec.get("run", 0) + 1
        label = (f"{rec.get('task', '?')} / {rec.get('variant', '?')} "
                 f"run {run_number}")
        if not rec.get("run_valid", not rec.get("error")):
            issues.append(f"{label}: {rec.get('error') or 'invalid run'}")
        elif mode == "mock" and not rec.get("solved"):
            issues.append(f"{label}: oracle did not solve task")
        elif mode == "mock-noop" and rec.get("solved"):
            issues.append(f"{label}: no-op unexpectedly solved task")
    return not issues, issues


def _print_summary(results, records, variants, task_ids, runs, out_file,
                   mode: str) -> bool:
    print("\n" + "=" * 64)
    print(f"Summary  (runs={runs} per task/variant, mode-aware)\n")

    for variant in variants:
        label = variant["label"]
        per_task = results[label]
        total_solved = sum(sum(s) for s in per_task.values())
        total_runs = sum(len(s) for s in per_task.values())
        v_recs = [r for r in records if r["variant"] == label]
        requested_models = sorted({r["requested_model"] for r in v_recs
                                   if r.get("requested_model")})
        requested_efforts = sorted({r["requested_effort"] for r in v_recs
                                    if r.get("requested_effort")})
        behavior_ok = sum(r.get("behavior_ok", True) for r in v_recs)
        print(f"• {label}: solved {total_solved}/{total_runs}  "
              f"(mean turns={_fmt(_mean([r['num_turns'] for r in v_recs]))}, "
              f"cost=${_fmt(_mean([r['cost_usd'] for r in v_recs]))}, "
              f"agent_ms={_fmt(_mean([r['agent_ms'] for r in v_recs]))}, "
              f"output_chars={_fmt(_mean([r['output_chars'] for r in v_recs]))}, "
              f"behavior_ok={behavior_ok}/{len(v_recs)}, "
              f"workflow_artifacts="
              f"{_fmt(_mean([r['workflow_artifact_count'] for r in v_recs]))})")
        models = sorted({m for r in v_recs for m in (r.get("models") or [])})
        print(f"    requested model: {', '.join(requested_models) if requested_models else 'un-pinned'}")
        print(f"    requested effort: {', '.join(requested_efforts) if requested_efforts else 'default'}")
        print(f"    model(s) actually run: {', '.join(models) if models else 'unknown (mock or no modelUsage)'}")
        aux = sorted({m for r in v_recs for m in (r.get("auxiliary_models") or [])})
        if aux:
            print(f"    tolerated as auxiliary (<{AUXILIARY_OUTPUT_SHARE_MAX:.0%} of output): {', '.join(aux)}")
        for task_id in task_ids:
            s = per_task[task_id]
            print(f"    - {task_id}: {sum(s)}/{len(s)} "
                  f"(solve_rate={stats.solve_rate(s):.2f}, pass^{len(s)}={stats.pass_hat_k(s):.0f})")
        for rec in v_recs:
            if rec.get("behavior_ok", True):
                continue
            for issue in rec.get("behavior_issues") or ["unspecified behavior issue"]:
                print(
                    f"    ! behavior {rec['task']} run {rec['run'] + 1}: {issue}"
                )

    # Paired A/B comparison (only when exactly two variants).
    #
    # An invalid run is counted as unsolved, so comparing across invalid records
    # manufactures an effect out of discarded data: an arm whose runs were all
    # invalidated reads as 0% solved and the other arm looks perfect. Pair on
    # validity first and refuse a verdict when there is nothing valid to compare.
    if len(variants) == 2:
        a, b = variants[0]["label"], variants[1]["label"]
        valid = {(r["variant"], r["task"], r["run"]): r.get("run_valid", True)
                 for r in records}
        diffs, bb, cc, dropped = [], 0, 0, 0
        for task_id in task_ids:
            sa, sb = results[a][task_id], results[b][task_id]
            for i, (x, y) in enumerate(zip(sa, sb)):
                if not (valid.get((a, task_id, i), True)
                        and valid.get((b, task_id, i), True)):
                    dropped += 1
                    continue
                diffs.append(int(y) - int(x))
                if x and not y:
                    bb += 1
                if y and not x:
                    cc += 1

        print(f"\nPaired A/B  ({b} − {a}):")
        if dropped:
            print(f"    dropped {dropped} pair(s): one or both runs were invalid")
        if not diffs:
            print("    Verdict: NOT COMPUTED — no valid paired runs remain.")
            print("    Fix the harness validation errors below and re-run; the "
                  "solve counts above treat every invalid run as unsolved.")
        else:
            point, lo, hi = stats.bootstrap_diff_ci(diffs)
            p = stats.mcnemar_exact(bb, cc)
            print(f"    pairs compared = {len(diffs)}")
            print(f"    Δ solve-rate = {point:+.3f}  (95% CI [{lo:+.3f}, {hi:+.3f}])")
            print(f"    McNemar exact p = {p:.4f}  (discordant: {a}-only={bb}, {b}-only={cc})")
            verdict = ("B significantly better" if cc > bb and p < 0.05 else
                       "A significantly better" if bb > cc and p < 0.05 else
                       "no significant difference")
            print(f"    Verdict: {verdict}")

    # Efficiency comparison.
    #
    # Solve rate cannot separate these variants: a capable model clears this
    # task class in both arms, so the interesting question is what each arm
    # SPENDS to get there. Restricted to pairs where both arms are valid and
    # both solved — comparing effort across different outcomes compares nothing.
    if len(variants) == 2:
        a, b = variants[0]["label"], variants[1]["label"]
        indexed = {(r["variant"], r["task"], r["run"]): r for r in records}
        comparable = []
        for task_id in task_ids:
            for i in range(runs):
                ra, rb = indexed.get((a, task_id, i)), indexed.get((b, task_id, i))
                if not (ra and rb):
                    continue
                if not (ra.get("run_valid", True) and rb.get("run_valid", True)):
                    continue
                if not (ra.get("solved") and rb.get("solved")):
                    continue
                comparable.append((task_id, ra, rb))

        print(f"\nEfficiency  ({b} − {a}), pairs where both arms solved: {len(comparable)}")
        if not comparable:
            print("    NOT COMPUTED — no pair had a valid solve on both sides.")
        else:
            # "lower" is reported over non-tied pairs, which is what the sign
            # test actually uses. Printing it over all pairs would understate a
            # real effect whenever a metric ties often, as integer turn counts do.
            header = (f"    {'metric':<14}{a[:9]:>10}{b[:9]:>10}"
                      f"{'med Δ':>10}{'med Δ%':>9}{'lower':>10}{'ties':>6}{'sign p':>9}")
            print(header)
            for field, label, fmt in EFFICIENCY_METRICS:
                va = [(ra.get(field) or 0) for _, ra, _ in comparable]
                vb = [(rb.get(field) or 0) for _, _, rb in comparable]
                diffs = [y - x for x, y in zip(va, vb)]
                rel = [((y - x) / x * 100) for x, y in zip(va, vb) if x]
                lower, higher, p = stats.sign_test(diffs)
                ties = len(diffs) - lower - higher
                print(f"    {label:<14}{fmt.format(_mean(va) or 0):>10}"
                      f"{fmt.format(_mean(vb) or 0):>10}"
                      f"{stats.median(diffs):>+10.2f}"
                      f"{stats.median(rel):>+8.0f}%"
                      f"{f'{lower}/{lower + higher}':>10}{ties:>6}{p:>9.4f}")

            if len(task_ids) > 1:
                print("    per task (median Δ% — negative favours "
                      f"{b}):")
                for task_id in task_ids:
                    rows = [(ra, rb) for t, ra, rb in comparable if t == task_id]
                    if not rows:
                        continue
                    cells = []
                    for field, label, _ in EFFICIENCY_METRICS:
                        rel = [((rb.get(field) or 0) - (ra.get(field) or 0))
                               / (ra.get(field) or 1) * 100 for ra, rb in rows]
                        cells.append(f"{label}={stats.median(rel):+.0f}%")
                    print(f"      {task_id:<26} n={len(rows)}  " + "  ".join(cells))

    print(f"\nResults → {out_file}")
    ok, issues = assess_suite(records, mode)
    if issues:
        print("\nHarness validation failed:")
        for issue in issues:
            print(f"    - {issue}")
    return ok


def _fmt(x) -> str:
    return "n/a" if x is None else f"{x:.2f}"


def main() -> int:
    ap = argparse.ArgumentParser(description="Tier 1 execution-graded eval runner")
    ap.add_argument("--task", action="append", help="task id (repeatable)")
    ap.add_argument("--all", action="store_true", help="run every task")
    ap.add_argument("--variant-a", help="variant json name (eval/variants/<name>.json)")
    ap.add_argument("--variant-b", help="second variant for paired A/B")
    ap.add_argument("--model", help="pin model (overrides CK_EVAL_MODEL)")
    ap.add_argument("--effort", choices=EFFORT_LEVELS,
                    help="pin reasoning effort (overrides CK_EVAL_EFFORT)")
    ap.add_argument("--runs", type=int, default=3)
    ap.add_argument("--max-turns", type=int, default=30)
    mode_group = ap.add_mutually_exclusive_group()
    mode_group.add_argument(
        "--mock", action="store_true",
        help="apply oracle instead of calling claude",
    )
    mode_group.add_argument(
        "--mock-noop", action="store_true",
        help="do nothing (tasks must fail)",
    )
    ap.add_argument("--out", help="results ndjson path")
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args()

    requested_model = resolve_requested_setting(args.model, "CK_EVAL_MODEL")
    requested_effort = resolve_requested_setting(args.effort, "CK_EVAL_EFFORT")
    if requested_effort and requested_effort not in EFFORT_LEVELS:
        ap.error(f"invalid effort {requested_effort!r}; choose from {', '.join(EFFORT_LEVELS)}")

    task_ids = args.task or (all_task_ids() if args.all else [])
    if not task_ids:
        ap.error("specify --all or --task <id>")

    mode = "mock" if args.mock else "mock-noop" if args.mock_noop else "claude"
    variant_names: list[str | None] = [args.variant_a]
    if args.variant_b:
        variant_names.append(args.variant_b)

    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
    out_file = Path(args.out) if args.out else RESULTS_DIR / f"eval-{ts}.ndjson"

    print(f"=== Tier 1: Task Suite ===  mode={mode}  tasks={task_ids}\n")
    ok = run_suite(
        task_ids, variant_names, args.runs, mode, args.max_turns,
        args.verbose, out_file,
        requested_model=requested_model,
        requested_effort=requested_effort,
    )

    # In mock mode the suite is a self-test: every task MUST be solved by its
    # oracle, and (with --mock-noop) MUST NOT be solved with no edits.
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
