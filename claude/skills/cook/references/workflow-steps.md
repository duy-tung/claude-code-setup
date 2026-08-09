# Proportional Workflow Steps

All modes start with the scale gate in `../SKILL.md`. Later step descriptions do
not turn optional artifacts, subagents, or checkpoints into requirements for a
small, clear task.

**Native task-list fallback:** `TaskCreate`/`TaskUpdate`/`TaskGet`/`TaskList` are
CLI-only and unavailable in some clients. If they fail, use a lightweight inline
checklist only when progress tracking is useful. The workflow must not depend on
task-tool availability.

## Small, Clear Fast Lane

For a localized request with a known contract:

1. Inspect the relevant files, adjacent convention, and affected test.
2. State a one-line inline intent when useful.
3. Implement routine reversible details without a questionnaire or durable plan.
4. Run one coherent, proportional evidence bundle after the logical batch.
5. Review the diff inline and report the outcome and any evidence gap.

Stop here. Do not instantiate research, plan files, subagents, phase approvals,
workflow artifacts, project sync, docs, or journals unless they are directly
useful or explicitly requested.

## Step 0: Intent, Scale, and Setup

1. Parse flags and intent using `intent-detection.md`.
2. Scout just enough context to classify the task as small-clear, standard, or
   large/high-risk.
3. Route small-clear work to the fast lane above.
4. For standard/large work, select the lightest useful structured steps.
5. If a current plan path is supplied, validate its scope and reuse it.
6. Create Claude Tasks only when multiple dependent units benefit from durable
   tracking.

**Output:** `Step 0: [scale] / [mode] - [routing reason]`

## Step 1: Targeted Scout and Conditional Research

Inspect enough code to identify:

- affected files and nearby conventions;
- relevant tests and callers;
- public contracts at risk;
- unknowns that could materially change the implementation.

Use primary-source research or a researcher subagent only for novel,
version-sensitive, or independently answerable questions. Ordinary repository
discovery stays inline. Share findings when they change the approach or expose a
material user decision; phase completion does not require approval.

Mode guidance:

- `fast` and `code`: skip broad research; use the current code/plan evidence.
- `parallel`: at most two research workers, and no more than three concurrent
  ordinary workers total.
- `auto`, `interactive`, `proportional`, `no-test`: research only as uncertainty
  warrants.

**Output when useful:** `Step 1: Scout complete - [decision-relevant findings]`

## Step 2: Requirements and Planning

Infer routine reversible details from the request, code, and conventions. Ask a
question only when alternatives materially change observable behavior, contracts,
risk, cost, or external side effects.

For standard work, use a short inline plan unless a file improves coordination or
resumability. For large/high-risk work, capture:

- expected artifacts and acceptance criteria;
- scope boundary and non-negotiable constraints;
- touched contracts and rollback/safety concerns;
- phase dependencies and file ownership for parallel streams.

Create `plan.md` and phase files only when they will be used. In `code` mode,
reuse the supplied plan rather than recreating it. Request approval only for a
material plan choice, not because planning ended.

**Output when a durable plan is created:** `Step 2: Plan ready - [N] phases`

## Step 3: Implementation

### Before Editing

At the scope appropriate to the change:

1. Read the governing code standard or local instruction that actually applies.
2. Inspect adjacent patterns for imports, naming, error handling, and tests.
3. Reuse an existing helper when it preserves cohesion.
4. Confirm public interfaces that must remain stable.
5. For a durable plan, map each owned file to its acceptance criterion.

Do not read every repository guide or produce a conformance report for a local
change.

### While Editing

- Implement the smallest cohesive change that satisfies the request.
- Keep overlapping files sequential. Parallelize only independent workstreams
  with explicit ownership and a concurrent fanout of three or less.
- Check local syntax/import issues while editing, but run compile/typecheck at a
  coherent logical-batch boundary rather than after every file.
- If a durable plan is active, record only material deviations that affect scope,
  contracts, or later phases. Routine implementation details do not need an
  `implementation-notes.md` entry.
- Ask before a deviation only if it needs new authority or materially changes the
  accepted outcome; otherwise choose the conservative reversible option and
  report it if relevant.

### `--tdd` Behavior

When `--tdd` is active, use this cycle per cohesive behavior slice:

```text
Step 3.T: Add a failing or characterization test for the behavior
Step 3.I: Implement the smallest passing change
Step 3.V: Run the targeted tests plus the batch-level compile/typecheck
```

Do not write tests that merely lock in accidental implementation details.

### Conditional Simplify

For a live git diff, read thresholds from `.ck.json`
`simplify.threshold.{locDelta,fileCount,singleFileLoc}` (defaults: 400 / 8 / 200).
When a threshold is breached and the simplify gate is enabled, simplify inline or
delegate a worker scoped to the modified files. Compare the scoped diff before and
after. Skip when under threshold, `CK_SIMPLIFY_DISABLED=1`, or
`.ck.json` has `simplify.gate.enabled=false`.

**Output:** `Step 3: Implemented [cohesive scope] - [relevant files/checkpoint]`

Implementation completion is not a mandatory human gate. Pause only for a
material decision or high-risk external effect.

## Step 4: Proportional Verification

Build one coherent evidence bundle for the requested behavior and relevant
regression surface:

1. Targeted behavior tests (happy path, important edge/error cases).
2. Relevant caller/contract checks.
3. The narrowest meaningful lint/type/build command for the logical batch.
4. Broader suites only when shared contracts, breadth, or risk warrants them.

Run ordinary checks inline. Use a `tester` only when verification is long-running,
independent, difficult, or benefits from a separate environment/domain lens. Use
a `debugger` only for a specific failure whose diagnosis can be isolated. Never
weaken assertions, fake evidence, or hide a failing relevant check.

If a clearly in-scope reversible correction fixes a failure, make it and re-run
the affected evidence. Ask the user only when resolution changes scope/contracts,
needs new authority, or requires accepting a regression.

For `--no-test`, skip requested test execution and report the evidence gap; still
run non-test checks needed to show that changed code parses/builds when applicable.

**Output:** `Step 4: Verification [passed|blocked|partial] - [commands/evidence]`

Testing completion is not a mandatory approval gate.

## Step 5: Conditional Review and Artifact Gate

Review the final diff inline by default. Add one independent reviewer for broad,
difficult, high-risk, or ship-like work when a distinct lens provides useful
evidence. Check:

- acceptance criteria and requested scope;
- reachable regressions in touched callers;
- intentional versus accidental contract changes;
- consistency with the inspected local conventions;
- relevant verification gaps.

Report evidenced blockers and warnings directly. Do not use a numeric confidence
or review score, and do not add a verifier merely to verify another reviewer.

Follow `review-cycle.md` when a structured `--auto` workflow, large/high-risk
change, or finalize/commit/ship/push/PR/deploy action uses durable review artifacts.
Only then write the applicable artifact bundle and run:

```bash
node claude/hooks/workflow-artifact-gate.cjs --stage finalize --artifact-dir <artifact-dir>
```

For high-risk `--auto`, stop before the external finalize/commit/ship effect when
`risk-gate.autoStopRequired` is true and `humanApproved` is not true. This safety
gate does not imply approval stops after ordinary phases.

**Output:** `Step 5: Review [inline|independent|artifact-gated] - [decision]`

## Step 6: Conditional Finalize

Perform only the finalization artifacts the task actually needs:

1. If a durable plan/task set was used, reconcile completed work with its phase
   files and update plan status from actual evidence.
2. Update documentation only when public behavior, setup, or operating
   instructions changed.
3. Record a journal entry only for a noteworthy decision likely to help future
   work.
4. Check onboarding/env instructions only when the change introduces them.
5. Commit, push, PR, deploy, or ship only when authorized by the requested
   workflow, respecting any high-risk/artifact gate.

These actions may be inline. Delegate project management, docs, or git work only
when it has an independent bounded deliverable and adds value. Do not spawn a
three-agent finalization fanout by default.

When plan sync applies, use deterministic commands where available:

```bash
ck plan check <phase-id>
ck plan check <phase-id> --start
ck plan uncheck <phase-id>
```

If `ck` is unavailable, edit only the relevant status/checkbox fields while
preserving the plan structure. Report unresolved task-to-phase mappings.

**Output:** `Step 6: Finalized - [artifacts/actions actually completed]`

## Mode Summary

```text
small-clear:  intent/scale -> targeted inspect -> implement -> one evidence bundle -> report
proportional: scout -> short plan if useful -> implement -> verify -> conditional finalize
interactive:  proportional + user-requested checkpoints at material decisions
auto:         structured flow -> artifact gate when applicable -> stop on high risk
fast:         targeted scout -> inline plan -> implement -> targeted verify
parallel:     structured flow with <=3 independent workers -> integrate -> verify
no-test:      proportional flow -> record test gap -> relevant non-test checks
code:         validate current plan -> implement -> verify -> sync plan if used
```

## Workflow Rules

- Scale the process to the task; the small-clear fast lane takes precedence.
- Do not ask for human approval merely because a phase completed.
- Compile/typecheck cohesive batches, not every touched file independently.
- Testing, review, docs, project sync, journaling, and delegation are conditional
  activities chosen for evidence or artifact value.
- Keep concurrent ordinary subagent fanout at three or less and assign disjoint
  ownership in a shared checkout.
- Preserve artifact and human gates for structured auto/high-risk external
  actions that actually use them.
- Describe verified facts, inferences, and unknowns without numeric confidence.
