#!/usr/bin/env python3
"""Run one pinned Claude model across effort levels and compare efficiency.

This is a maintainer-only live eval helper. It deliberately does not select a
"best" effort globally: it reports solve rate, turns, token use, cost, and
latency so a maintainer can choose an effort for the workload being measured.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

EVAL_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(EVAL_DIR))
import run as eval_run  # noqa: E402


def _mean(values: list[float | int | None]) -> float | None:
    numeric = [value for value in values if isinstance(value, (int, float))]
    return sum(numeric) / len(numeric) if numeric else None


def load_records(path: Path) -> list[dict]:
    records = []
    with path.open(encoding="utf-8") as fh:
        for line in fh:
            if line.strip():
                records.append(json.loads(line))
    return records


def summarize_records(effort: str, records: list[dict],
                      requested_model: str) -> dict:
    solved = sum(bool(record.get("solved") and record.get("run_valid", True))
                 for record in records)
    actual_models = sorted({model for record in records
                            for model in (record.get("models") or [])})
    return {
        "effort": effort,
        "trials": len(records),
        "solved": solved,
        "solve_rate": solved / len(records) if records else 0.0,
        "mean_turns": _mean([record.get("num_turns") for record in records]),
        "mean_input_tokens": _mean(
            [record.get("input_tokens") for record in records]
        ),
        "mean_output_tokens": _mean(
            [record.get("output_tokens") for record in records]
        ),
        "mean_output_chars": _mean(
            [record.get("output_chars") for record in records]
        ),
        "mean_workflow_artifacts": _mean(
            [record.get("workflow_artifact_count") for record in records]
        ),
        "mean_cost_usd": _mean([record.get("cost_usd") for record in records]),
        "mean_latency_ms": _mean([record.get("agent_ms") for record in records]),
        "actual_models": actual_models,
        "matching_models": eval_run.matching_models(requested_model, actual_models),
    }


def model_consistency_error(summaries: list[dict],
                            requested_model: str) -> str | None:
    """Require every effort to prove the same requested model actually ran."""
    signatures = []
    for summary in summaries:
        matches = tuple(summary["matching_models"])
        if not matches:
            actual = ", ".join(summary["actual_models"]) or "missing modelUsage"
            return (f"effort {summary['effort']} did not run requested model "
                    f"{requested_model!r}: {actual}")
        signatures.append(matches)
    if len(set(signatures)) > 1:
        detail = "; ".join(
            f"{summary['effort']}={','.join(summary['matching_models'])}"
            for summary in summaries
        )
        return f"actual model changed during effort sweep: {detail}"
    return None


def _format_number(value: float | None, digits: int = 3) -> str:
    return "n/a" if value is None else f"{value:.{digits}f}"


def print_report(summaries: list[dict], requested_model: str) -> None:
    print("\n=== Effort Sweep Summary ===")
    print(f"Pinned model: {requested_model}")
    print("\nEffort  Solved  Rate   Turns  Input tok  Output tok  Chars  Artifacts  Cost      Latency  Actual model(s)")
    print("------  ------  -----  -----  ---------  ----------  -----  ---------  --------  -------  ---------------")
    for summary in summaries:
        solved = f"{summary['solved']}/{summary['trials']}"
        rate = f"{summary['solve_rate']:.2f}"
        turns = _format_number(summary["mean_turns"], 1)
        input_tokens = _format_number(summary["mean_input_tokens"], 0)
        output_tokens = _format_number(summary["mean_output_tokens"], 0)
        output_chars = _format_number(summary["mean_output_chars"], 0)
        artifacts = _format_number(summary["mean_workflow_artifacts"], 1)
        cost = _format_number(summary["mean_cost_usd"])
        latency = (_format_number(summary["mean_latency_ms"] / 1000, 2) + "s"
                   if summary["mean_latency_ms"] is not None else "n/a")
        models = ",".join(summary["actual_models"]) or "unknown"
        print(f"{summary['effort']:<6}  {solved:<6}  {rate:<5}  "
              f"{turns:<5}  {input_tokens:<9}  {output_tokens:<10}  "
              f"{output_chars:<5}  {artifacts:<9}  ${cost:<7}  "
              f"{latency:<7}  {models}")


def parse_efforts(raw: str) -> list[str]:
    efforts = []
    for value in raw.split(","):
        effort = value.strip()
        if not effort:
            continue
        if effort not in eval_run.EFFORT_LEVELS:
            raise ValueError(
                f"invalid effort {effort!r}; choose from "
                f"{', '.join(eval_run.EFFORT_LEVELS)}"
            )
        if effort not in efforts:
            efforts.append(effort)
    if not efforts:
        raise ValueError("provide at least one effort level")
    return efforts


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="Compare one pinned model across Claude effort levels"
    )
    ap.add_argument("--task", action="append", help="task id (repeatable)")
    ap.add_argument("--all", action="store_true", help="run every task")
    ap.add_argument("--variant", help="variant json name")
    ap.add_argument("--model", help="fixed model ID (fallback: CK_EVAL_MODEL)")
    ap.add_argument("--efforts", default="low,medium,high",
                    help="comma-separated levels (default: low,medium,high)")
    ap.add_argument("--runs", type=int, default=3)
    ap.add_argument("--max-turns", type=int, default=30)
    ap.add_argument("--out-dir", help="directory for per-effort NDJSON files")
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args(argv)

    requested_model = eval_run.resolve_requested_setting(args.model, "CK_EVAL_MODEL")
    if not requested_model:
        ap.error("--model (or CK_EVAL_MODEL) is required for a comparable sweep")
    try:
        efforts = parse_efforts(args.efforts)
    except ValueError as exc:
        ap.error(str(exc))

    task_ids = args.task or (eval_run.all_task_ids() if args.all else [])
    if not task_ids:
        ap.error("specify --all or --task <id>")
    if args.runs < 1:
        ap.error("--runs must be at least 1")

    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
    out_dir = (Path(args.out_dir) if args.out_dir else
               eval_run.RESULTS_DIR / f"effort-sweep-{ts}")
    out_dir.mkdir(parents=True, exist_ok=True)

    summaries = []
    all_valid = True
    for effort in efforts:
        out_file = out_dir / f"{effort}.ndjson"
        print(f"\n=== Effort {effort} ===")
        valid = eval_run.run_suite(
            task_ids, [args.variant], args.runs, "claude", args.max_turns,
            args.verbose, out_file,
            requested_model=requested_model,
            requested_effort=effort,
        )
        records = load_records(out_file)
        summaries.append(summarize_records(effort, records, requested_model))
        all_valid = all_valid and valid

    print_report(summaries, requested_model)
    consistency_error = model_consistency_error(summaries, requested_model)
    if consistency_error:
        print(f"\n[X] {consistency_error}")
        all_valid = False
    else:
        print("\n[OK] Same requested model verified at every effort level")
    print(f"Results directory: {out_dir}")
    return 0 if all_valid else 1


if __name__ == "__main__":
    sys.exit(main())
