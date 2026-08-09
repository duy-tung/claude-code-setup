# Agent Teams Guide

ClaudeKit's `/ck:team` command coordinates named Claude Code teammates for independent research, review, debugging, and implementation workstreams.

Canonical runtime documentation: https://code.claude.com/docs/en/agent-teams

## Compatibility

- Claude Code `2.1.178+` provides the implicit Agent Teams lifecycle used by this guide.
- ClaudeKit's runtime baseline requires Claude Code `2.1.219+`.
- Agent Teams are experimental, disabled by default, and can depend on
  account/runtime availability.

Check and update Claude Code before using the command:

```text
claude --version
claude update
```

Opt in for one Claude invocation from a POSIX shell (macOS, Linux, WSL, or Git
Bash):

```bash
CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1 claude
```

Only add the flag to Claude Code settings if you intentionally want Agent Teams
enabled for every session that loads that settings file:

```json
{
  "env": {
    "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1"
  }
}
```

Restart the session after changing persistent settings.

## Quick Start

```text
/ck:team research "Compare queue backends for this service"
/ck:team review "Review PR #142"
/ck:team debug "WebSocket closes after the first message"
/ck:team cook plans/dashboard/plan.md --devs 3
```

The enabled session already has an implicit team. `/ck:team` spawns named background teammates directly, coordinates tasks and messages, requests shutdown from each teammate, and lets Claude Code clean up session resources automatically.

## When Teams Help

Use Agent Teams when workstreams are independent and benefit from peer communication:

- research from distinct angles
- review across correctness, security, performance, and tests
- debugging with competing hypotheses
- cross-layer implementation with exclusive file ownership

Prefer a single session or ordinary subagent for:

- one focused or routine task
- sequential steps with many dependencies
- multiple edits to the same files
- cost-sensitive work where teammates would duplicate context

## Templates

### Research

```text
/ck:team research "Evaluate authentication providers" --researchers 3
```

The lead gives each researcher a different question, then synthesizes their reports. Research teammates can read the same files safely because they do not write implementation code.

### Review

```text
/ck:team review "src/auth and its tests" --reviewers 3
```

Each reviewer receives a distinct focus and returns concrete file/line evidence. The lead deduplicates findings without imposing a finding quota.

### Debug

```text
/ck:team debug "checkout intermittently returns 409" --debuggers 3
```

Each debugger tests one hypothesis with predicted evidence. Keep the checkout read-only until the evidence identifies a root cause, then handle the fix as a separate, owned implementation task.

### Cook

```text
/ck:team cook plans/dashboard/plan.md --devs 3
```

The lead partitions implementation by exclusive writable paths, coordinates dependencies, and verifies the combined result after writers finish. Use `--delegate` when the lead should only coordinate and synthesize.

## Shared Checkout and File Ownership

All teammates share the same checkout. A teammate's edits are immediately visible to every other teammate.

Before parallel implementation, assign exclusive ownership:

```text
api-dev:
  writable: src/api/dashboard/**, src/models/dashboard.ts

ui-dev:
  writable: src/components/dashboard/**, src/pages/dashboard.tsx

integrator:
  writable: package.json, lockfile, shared schemas, generated indexes
```

Operating rules:

1. Never give two active writers the same file.
2. Sequence work that cannot be partitioned safely.
3. Stop and message the lead before touching an unassigned path.
4. Assign shared manifests, schemas, lockfiles, and generated files to one integrator.
5. Do not stage, discard, or commit another teammate's changes.
6. Run combined verification after all implementation slices finish.

## Models and Effort

Models are selected per teammate. Mixed-model teams are supported:

```text
Use Sonnet for two focused reviewers and Opus for the integration reviewer.
```

A custom agent definition can supply its own model, or the lead can set a model for an individual spawn. Do not force every teammate onto Opus.

Teammates inherit the lead's effort level by default. Model and effort are independent controls; evaluate them separately for quality, latency, and cost.

## Tasks and Dependencies

The shared task list uses three primary states:

```text
pending -> in_progress -> completed
```

Tasks can block other tasks. When a prerequisite completes, Claude Code makes its dependents available automatically.

Every implementation task should include:

- a bounded deliverable
- acceptance criteria
- exclusive writable paths
- read-only context
- dependencies
- focused verification
- completion report format

## Direct Messaging

Use stable teammate names and send a separate direct message to each intended recipient.

Good message:

```text
To ui-dev: API field `widgets` changed to `items` in src/api/dashboard.ts:88.
Update only your owned UI files and reply with affected call sites.
```

Messages arrive automatically. Task completion and idle events also notify the lead, so fixed-interval polling is unnecessary. Use the task list only when state is unclear.

## Display Modes

- **In-process:** use `Shift+Down` to cycle through teammates, `Enter` to inspect, `Escape` to interrupt, and `Ctrl+T` for the task list.
- **Split panes:** requires a supported tmux or iTerm2 setup.

Force in-process mode in settings:

```json
{
  "teammateMode": "in-process"
}
```

Or for one session:

```text
claude --teammate-mode in-process
```

## Lifecycle

### Start

The lead spawns named background agents directly. No explicit team setup step exists.

### Monitor

React to inbound messages, task-completion events, and teammate-idle events. Reassign blocked work or message its owner directly.

### Finish

1. Reconcile completed and unfinished tasks.
2. Send a shutdown request to each active teammate by name.
3. Wait for acknowledgements or report in-flight work.
4. End the workflow; cleanup is automatic.

Do not edit or remove Claude Code's runtime team/task state manually.

## Cost Control

Every teammate has a separate context window, so token use grows with team size and duration.

- Start with two or three teammates.
- Add only genuinely independent workstreams.
- Keep spawn prompts focused.
- Use lower-cost models where evals preserve quality.
- Avoid duplicate research and repeated verification.
- Shut down teammates after their follow-up work is complete.

## Known Limitations

- `/resume` and `/rewind` do not restore in-process teammates. After resuming,
  spawn replacement teammates instead of messaging stale names.
- Task status can lag when a teammate finishes without marking its task complete.
  Check the work, then update or reassign the task deliberately.
- Shutdown can be slow because a teammate finishes its current request or tool
  call before stopping.
- A session has one team, teams cannot be nested, and the original lead cannot be
  replaced.
- Split-pane mode requires a supported tmux or iTerm2 setup; in-process mode is
  the portable default.

## Troubleshooting

### A Named Teammate Does Not Start

1. Confirm `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` is visible to the running session.
2. Confirm `claude --version` is at least 2.1.219 for this kit.
3. Restart after settings changes.
4. Check account/runtime Agent Teams availability.

### Parallel Edits Collide

1. Stop one writer.
2. Select one authoritative owner for the overlapping file.
3. Reconcile the file through normal version-control review.
4. Re-scope remaining tasks to exclusive paths or execute them sequentially.

### Task State Is Stale

Message the owner directly, inspect the shared task list once, and reassign if the teammate stopped before updating status.

### Shutdown Takes Time

A teammate may finish an in-flight operation before acknowledging shutdown. Wait or report the unfinished operation; cleanup remains managed by Claude Code.

## Source of Truth

Runtime details belong in:

- `.claude/skills/team/SKILL.md`
- `.claude/skills/team/references/agent-teams-official-docs.md`

This guide explains usage. When these files disagree, update them together against the canonical Claude Code documentation rather than preserving multiple historical behaviors.
