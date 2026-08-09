# Agent Teams -- Examples and Best Practices

> Source: https://code.claude.com/docs/en/agent-teams
> Baseline: Claude Code 2.1.178+ implicit teams; CK requires 2.1.219+

## Parallel Code Review

```text
Review PR #142 with three named teammates:
- security-reviewer: auth, trust boundaries, and input handling
- performance-reviewer: latency, allocation, and query behavior
- test-reviewer: missing regression and failure-path coverage

Use Sonnet for the focused passes and Opus only for final synthesis if needed.
Each reviewer reports concrete file/line evidence. Send follow-up questions
directly to the relevant reviewer.
```

This is a good team task because all workstreams are read-only and independent.

## Competing Debug Hypotheses

```text
Users report that the app exits after one message. Spawn three named debugger
teammates, each with one distinct hypothesis and predicted evidence. Keep the
checkout read-only until evidence identifies a root cause. Ask each debugger to
send contradictions directly to the teammate whose hypothesis they challenge.
```

The lead synthesizes supported and rejected hypotheses without asking every teammate to repeat the same investigation.

## Parallel Feature Implementation

```text
Implement the dashboard with three named teammates in the shared checkout:
- api-dev owns src/api/** and src/models/dashboard.ts
- ui-dev owns src/components/dashboard/** and src/pages/dashboard.tsx
- integrator owns package manifests, generated indexes, and shared schemas

Do not start tester edits until developer tasks complete. If a task unexpectedly
needs another owner's file, stop and message the lead before editing it.
```

The safety mechanism is exclusive file ownership. Do not give two active teammates the same writable file.

## Spawn Prompt Pattern

Every teammate prompt should answer:

1. What bounded outcome is required?
2. What inputs and project context matter?
3. Which files may this teammate edit?
4. Which files are read-only or owned elsewhere?
5. What evidence or artifact should be returned?
6. What task state must be updated before completion?

Example:

```text
Implement request validation for the dashboard API.
Writable ownership: src/api/dashboard/**, src/models/dashboard.ts.
Read-only context: src/components/dashboard/**.
Do not edit package.json, lockfiles, schemas, or generated indexes; message the
lead if one must change. Run the focused API tests and report changed files,
test result, and unresolved risks. Mark your task completed when done.
```

## Model Selection

Use per-teammate models intentionally:

| Workstream | Starting point |
|------------|----------------|
| Narrow lookup or classification | Haiku or Sonnet |
| Focused research, test, or review | Sonnet |
| Difficult architecture, integration, or synthesis | Opus |

These are starting points, not mandates. Preserve a custom agent's declared model when it matches the task. Teammates inherit lead effort by default; sweep effort separately from model choice when measuring quality and cost.

## File Ownership

- Assign exclusive writable paths before spawning implementation teammates.
- Let research and review teammates read the same files concurrently.
- Give shared manifests, schemas, lockfiles, and generated outputs to one integrator.
- Sequence tasks that cannot be partitioned cleanly.
- Stop at the first unplanned overlap; do not hope the last writer wins safely.
- Include ownership in the shared task and spawn prompt so both lead and teammate see it.

## Messaging

- Use stable teammate names.
- Send one direct message to every intended recipient.
- Include evidence and the requested action, not only a status phrase.
- Let automatic delivery and task events drive progress.
- Reconcile with `TaskList` only when state is unclear.

Example direct update:

```text
To ui-dev: API response field `widgets` is now `items` in src/api/dashboard.ts:88.
Please update only your owned UI files and reply with the affected call sites.
```

## Task Sizing

- **Too small:** coordination overhead exceeds execution time.
- **Too large:** ownership becomes vague and feedback arrives too late.
- **Good:** one independent deliverable, clear ownership, bounded verification, and a concise report.

Start with two or three teammates. Add another only when a genuinely independent workstream exists.

## Monitoring and Synthesis

1. Spawn all independent tasks in the background.
2. React to completion, idle, and message events.
3. Redirect a teammate when its evidence shows the approach is wrong.
4. Deduplicate results at the lead; do not ask all teammates to produce identical summaries.
5. Shut down each teammate directly after its follow-up work is complete.

## Cost Control

Agent Teams multiply context and output costs. Keep prompts focused, choose lower-cost models where evals support them, avoid duplicate verification, and shut down finished teammates promptly. Use a single session for routine or sequential work.

## Troubleshooting

### Named Teammate Does Not Start

- Confirm `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` is visible to the session.
- Confirm `claude --version` is 2.1.219 or newer for this Opus 5 kit.
- Check account/runtime availability.
- Spawn a named background agent directly; no setup call precedes it.

### Parallel Edits Conflict

- Stop one writer immediately.
- Identify the authoritative owner for the overlapping file.
- Restore or reconcile the file through normal version-control review.
- Re-scope remaining tasks to exclusive paths or run them sequentially.

### Task State Lags

- Message the task owner directly for a status update.
- Inspect `TaskList` once to reconcile state.
- Reassign the task if the owner stopped before updating it.

### Shutdown Is Slow

A teammate may finish an in-flight operation before acknowledging shutdown. Wait for the acknowledgement or report the unfinished state; do not edit runtime state directories manually.
