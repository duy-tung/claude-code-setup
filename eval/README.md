# Eval harness (maintainer-only)

A local-first, dependency-free (Python stdlib) harness for measuring whether a
change to the **Claude Code setup** (skills / hooks / agents / rules) actually
makes Claude Code *do real tasks better* — before merging the change.

> Not shipped to end users. Lives at repo root (outside `claude/`) so it never
> installs into a user's `.claude/`. Rationale + the research behind this design:
> [`docs/research/eval-claude-code-setup.md`](../docs/research/eval-claude-code-setup.md).

## The two tiers

| Tier | Cost | What it does | Command |
|---|---|---|---|
| **Tier 0 — Static** | ~$0, <5s | Runs the skill validators and stdlib eval-runner regression tests | `npm run eval:static` |
| **Tier 1 — Task suite** | depends on model | Runs golden SWE tasks through `claude -p`, grades by **running real tests**, repeats N× for variance, A/B compares two setups | `npm run eval` |

## How Tier 1 works

For each golden task in `tasks/<id>/`:

1. Copy `fixture/` (a pinned repo state with a failing test) into a throwaway dir.
2. Stage variant-owned project state, then run Claude Code headless:
   `claude -p "<prompt>" --output-format json …`. The `full-kit` variant copies
   this branch's `claude/` profile to `.claude/` inside the throwaway fixture;
   `baseline` loads user settings only.
3. **Grade by execution:** run the task's `test_cmd`; exit 0 ⇒ *solved*. The test
   file is authored so it passes only when the bug is fixed / feature implemented
   **and** nothing regresses (SWE-bench's `FAIL_TO_PASS` + `PASS_TO_PASS`, folded
   into one signal).
4. Repeat `--runs N` times (agents are stochastic). Metrics captured per run:
   `solved`, `num_turns`, `cost_usd`, `agent_ms`, `subtype`, requested
   model/effort, whole-tree input/output tokens, visible-output length, created
   workflow-artifact count, and canonical models reported by Claude Code.

Two variants ⇒ a **paired A/B**: per-task McNemar exact p-value + bootstrap CI on
the solve-rate difference, with a plain-language verdict.

## Verify the harness without a live CLI

The scaffold is self-testing — no `claude` auth needed:

```bash
npm run eval:mock        # apply each task's oracle ("perfect agent") → ALL must solve
python3 eval/run.py --all --mock-noop   # do nothing ("useless agent") → ALL must fail
```

If mock solves everything and mock-noop solves nothing, the fixtures + graders
are wired correctly. Either command exits non-zero when that invariant breaks.

## Real A/B run (in a Claude Code environment)

```bash
# Does the kit help vs a bare Claude Code?
python3 eval/run.py --all --variant-a baseline --variant-b full-kit --runs 5 \
  --model claude-opus-5 --effort high
```

- Variants live in `variants/*.json`. `claude_args` are passed through to Claude;
  `stage_kit: true` installs this checkout's `claude/` directory as the isolated
  fixture's `.claude/`. An A/B should isolate one variable. `${REPO_ROOT}` in a
  variant's args resolves to the repository path. Both shipped variants load only
  the isolated fixture's `project` setting source: baseline has no `.claude/`,
  while full-kit receives the staged profile. Personal user rules, skills, hooks,
  and settings therefore cannot leak into either side; authentication discovery is
  independent of `--setting-sources`.
- **Gotcha:** do NOT put `--bare` in a variant. In headless mode `--bare` skips auth discovery and every run returns `"Not logged in"` → a false `0/N` (floor effect), not a real result.
- **Headroom matters:** to measure a behavioral rule, the task's base solve-rate must be strictly between 0 and 1. If plain Claude already solves a task every time (ceiling) or never (floor), the A/B shows `Δ=0` for the wrong reason. Pick/author tasks where the baseline genuinely fails some of the time.
- Env: `CK_EVAL_CMD` (default `claude`, e.g. `"ccs glm"`),
  `CK_EVAL_CLAUDE_ARGS` (default `--permission-mode bypassPermissions`),
  `CK_EVAL_TIMEOUT_SEC` (default 180).
- **Pin the model + effort** so every A/B run uses the same settings. CLI flags
  override environment fallbacks:
  ```bash
  python3 eval/run.py --all --model claude-opus-5 --effort high

  # Equivalent fallbacks for repeated commands:
  export CK_EVAL_MODEL=claude-opus-5
  export CK_EVAL_EFFORT=high
  ```
  Effort levels are not comparable across model generations, so measure cost,
  latency, and quality on this suite rather than carrying an effort choice
  forward from another model.
  Each live record stores the requested model/effort and `modelUsage`. Canonical
  model IDs are used when a provider-specific map key differs. A pinned run is
  intentionally strict-single-model: a missing requested model or any additional
  canonical model invalidates the run and makes the suite exit non-zero. This
  detects fallback and accidental delegation in the small calibration suite. Omit
  the pin only for a purpose-built mixed-model team experiment.

Results stream to `results/eval-<ts>.ndjson` (git-ignored).

## What the suite has measured

Recorded so we do not re-derive it. Claude Opus 5 at `high` effort, `baseline`
(no kit) versus `full-kit`, 36 valid pairs across 11 tasks.

**Solve rate cannot separate the variants.** Every task, every run, both arms:
36/36. Three task designs were tried specifically to break this — intricate
single-file logic, stateful dispatch semantics, and an eleven-file contract
migration at 25 turns per run. All three came back tied. On execution-graded,
fully-specified Python, the model clears the work with or without the kit, so
solve rate is the wrong instrument here.

**The kit's cost penalty depends on task size, and the split is clean.**

| Task size | n | cost Δ range | median |
|---|---|---|---|
| trivial (≤6 turns) | 6 | +94% … +117% | +104% |
| substantive (>6 turns) | 4 | +43% … +76% | +54% |

The ranges do not overlap, and the relationship strengthens when the single
25-turn task is removed (r = -0.79 versus -0.47 with it), so it is not an
artifact of one leverage point. A pooled median of "+96%" is really the trivial
tasks talking.

Cache accounting explains the mechanism: the kit adds roughly 12,700 tokens of
one-time cache *creation* per session, against cache *reads* an order of
magnitude larger. The preamble is cached and amortised, not re-sent per turn, so
its relative cost falls as a task runs longer.

**Output length separates on substantive tasks only.** Across the two large
tasks the kit was shorter in 6/6 pairs, median -23% (sign test p = 0.031). Pooled
across all sizes it is 19/30, p = 0.20 — not established. An earlier read of the
same data via means suggested -24% overall; a paired test does not support that,
which is why the runner uses a sign test.

**Turn count favours the kit but is not established.** Median -14% to -17%
depending on the subset, p between 0.001 and 0.125. Files touched and unrequested
artifacts are identical in both arms, at zero, on every task measured.

## Sweep effort

Start at `high`, then measure lower settings for cost/latency and reserve
`xhigh`/`max` for capability-sensitive tasks. The helper runs one fixed model at
each effort, verifies that the same actual model was reported, and prints solve
rate, behavior compliance, mean turns, input/output tokens, visible output length,
workflow artifacts, cost, and latency:

```bash
python3 eval/effort_sweep.py --all --variant full-kit --model claude-opus-5 \
  --efforts low,medium,high --runs 5

# Add xhigh/max only when the selected tasks have headroom and justify the spend.
```

The sweep reports measurements; it does not declare one effort globally best.

## Measuring a candidate rule (eval-driven, before shipping)

Test a behavioral rule BEFORE adding it to `claude/rules/`:

1. Put the rule text in `candidates/<name>.md` (NOT shipped to users).
2. Add a variant that appends it: `--append-system-prompt-file ${REPO_ROOT}/eval/candidates/<name>.md`.
3. **Headroom probe** — characterise a task with the baseline alone:
   ```bash
   python3 eval/run.py --task <id> --variant-a baseline --runs 8
   ```
   Only tasks with `0 < solve_rate < 1` can reveal a rule's effect (ceiling/floor cannot).
4. A/B on a task that has headroom:
   ```bash
   python3 eval/run.py --task <id> --variant-a baseline --variant-b with-<name> --runs 8
   ```
5. Ship the rule (move into `claude/rules/`) ONLY if the paired verdict is a real improvement.

> `string-utils-multi` is a ceiling (base Claude solves it 8/8). `calc-engine` (multi-file
> expression evaluator) and the harder tasks are headroom candidates — probe each first.

## Adding a task

```
tasks/<id>/
  task.json     { id, prompt, workflow_artifact_budget, workflow_artifact_exempt_paths?, protected_paths?, grade:{ test_cmd, fail_to_pass[], pass_to_pass[], timeout_sec } }
  fixture/      starting repo state the agent sees and edits
  tests/        OPTIONAL hidden grading tests — copied into the workdir ONLY at
                grade time, so the agent never sees them (SWE-bench style). Use
                this to remove test hill-climbing and create real headroom.
  oracle/       reference solution (files copied over fixture in --mock) — proves solvability
```

Keep tasks small, deterministic, and stdlib-only (the samples use `python3 -m unittest`).
Visible `test_*.py`/`*_test.py` files are hashed, restored before grading, and
invalidate a run if the agent changes them. Add non-test grader contracts such as
a known-good parser to `protected_paths`.
Do not tell the agent to plan, delegate, self-review, or rerun checks in the task
prompt unless that behavior is the variable being tested; let the kit prompt cause
those actions so the eval can detect regressions in calibration.
Set `workflow_artifact_budget: 0` on small tasks that should not create plan or
journal files. Created Markdown outside the staged `.claude/` profile, files under
`plans/`, `reports/`, or `docs/journals/`, and named report/summary artifacts count
toward the budget. A budget breach sets `behavior_ok: false` and records the reason
in `behavior_issues`, but it does not change `solved`, `run_valid`, solve-rate, or
the suite exit status. `run_valid` is reserved for harness/infrastructure failures,
model-pin violations, and protected grader-file tampering.

If Markdown is the requested task deliverable, exempt only its expected relative
path (or a shell-style glob) so unrelated plan/report files are still measured:

```json
"workflow_artifact_exempt_paths": ["README.md", "docs/deliverable-*.md"]
```

The normal suite summary and effort sweep report behavior compliance separately
from solve-rate, alongside the mean workflow-artifact count.
For larger/representative suites, see SWE-smith / terminal-bench patterns in the research doc.

## Files

- `run.py` — Tier 1 orchestrator + A/B stats
- `effort_sweep.py` — fixed-model effort comparison (solve rate/cost/latency)
- `test_run.py` — stdlib tests for pin verification and harness exit semantics
- `grader.py` — execution grader (run tests → pass/fail)
- `stats.py` — pass^k, McNemar exact, bootstrap CI (stdlib only)
- `tier0_static.py` — Tier 0 wrapper around the surviving validators
- `variants/`, `tasks/`, `results/`
