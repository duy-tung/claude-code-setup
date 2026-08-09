---
name: ck:team
description: "Orchestrate Agent Teams for parallel multi-session collaboration. Use for research, implementation, review, and debug workflows requiring independent teammates."
user-invocable: true
when_to_use: "Invoke for coordinated multi-session agent teamwork."
category: dev-tools
keywords: [agents, parallel, multi-session, collaboration]
argument-hint: "<template> <context> [--devs|--researchers|--reviewers N] [--delegate]"
metadata:
  author: claudekit
  version: "3.1.0"
---

# Agent Teams - CK-Native Orchestration

Coordinate named Claude Code teammates through one implicit, session-scoped team. Each teammate has its own context window, loads project context, shares the current checkout and task list, and can message other teammates directly.

## Requirements

- Claude Code `2.1.219` or newer for Claude Opus 5 support. Implicit teams require `2.1.178` or newer.
- Agent Teams are experimental and disabled by default. Opt in for one POSIX-shell invocation with `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1 claude`; use `settings.json` only for intentional persistent enablement.
- Agent Teams availability can still depend on account and runtime support.

Claude Code creates the implicit team automatically. There is no explicit setup or teardown tool. Spawn named background teammates directly. When work ends, shut down each teammate; Claude Code owns team-resource cleanup.

## Usage

```text
/ck:team <template> <context> [flags]
```

Templates: `research`, `cook`, `review`, `debug`.

Flags:

- `--devs N`, `--researchers N`, `--reviewers N`, `--debuggers N`: team size
- `--plan-approval` / `--no-plan-approval`: teammate plan gate; default on for `cook`
- `--delegate`: lead coordinates and synthesizes without editing code

## Execution Invariants

1. Start by spawning a named teammate with `Agent`. If named Agent Teams behavior is unavailable, stop and explain the enablement/version requirement. Do not silently fall back to ordinary subagents.
2. Spawn independent work concurrently with `run_in_background: true`.
3. Treat the checkout as shared. Assign non-overlapping file ownership before any parallel edits. Read-only overlap is fine; write overlap is not.
4. If two tasks need the same file, make them sequential, reassign the shared file to the lead, or collapse them into one teammate task.
5. Models are per teammate. Honor the selected agent definition's model or set a model per spawn; mixed-model teams are supported. Teammates inherit the lead's effort level by default.
6. Send one direct message per teammate name.
7. Use task events and automatic message delivery for progress. Check `TaskList` only when state is unclear; do not poll on a timer.
8. Request shutdown from every active teammate when complete. There is no explicit team cleanup call.

## Agent Tool

```text
Agent(
  subagent_type: "researcher" | "general-purpose" | "code-reviewer" | "debugger" | "tester" | ...,
  name: "stable-teammate-name",
  description: "short task summary",
  prompt: "full instructions + CK Context Block",
  model: "sonnet",             # Optional per-teammate override
  run_in_background: true
)
```

Omit `model` to use the agent definition/runtime default. Do not force every teammate onto Opus. `Agent` is the current tool name; keep legacy `Task` compatibility only in hooks or parsers that read older transcripts.

## Shared Task and Messaging Surface

| Tool | Purpose |
|------|---------|
| `TaskCreate` | Create a work item with acceptance criteria and file ownership |
| `TaskUpdate` | Assign, claim, block, or complete a task |
| `TaskGet` | Read full task details and dependencies |
| `TaskList` | Inspect compact team task state |
| `SendMessage` | Direct message or shutdown request to one named teammate |

Task dependencies unblock automatically. Teammate messages and idle/completion events arrive automatically; the lead does not need to poll for them.

## CK Context Block

Append this block to every teammate prompt:

```text
CK Context:
- Work dir: {CK_PROJECT_ROOT or CWD}
- Naming: {CK_NAME_PATTERN or "YYMMDD-HHMM"}
- Shared checkout: yes; edit only files assigned to this teammate
- Commits: conventional (feat:, fix:, docs:, refactor:, test:, chore:)
- Refer to teammates by name, not agent ID

Include only when applicable:
- Reports: {explicit report path when this teammate owns a persistent report}
- Active plan: {CK_ACTIVE_PLAN when this workflow executes a durable plan}
```

Do not add placeholder `plans/` or `reports/` paths to a task that does not use
those artifacts.

## Template: Research

For `/ck:team research <topic> [--researchers N]`:

1. Derive independent research angles; default `N=3`.
2. Create one task per angle with a focused question and report path.
3. Spawn named `researcher` teammates concurrently. Choose models per task cost and difficulty.
4. Let teammates challenge findings through direct messages when useful.
5. Read the reports and synthesize one concise summary with evidence, recommendations, and unresolved questions.
6. Send a shutdown request to each teammate individually.
7. Report the summary path and number of reports generated.

## Template: Cook

For `/ck:team cook <plan-path-or-description> [--devs N]`:

1. Read the plan, or use one planner teammate when a plan is genuinely needed.
2. Split implementation into independent groups with exclusive file ownership. Record ownership in every task description.
3. Create developer tasks plus dependent verification work. Avoid parallel writes to shared manifests, schemas, generated indexes, and lockfiles; give those to one integrator.
4. Spawn named developer teammates concurrently in the shared checkout.
5. If plan approval is enabled, require it only for risky or complex implementation tasks.
6. Monitor task events. Start verification after its dependencies complete.
7. Integrate shared-file changes sequentially, then run the smallest relevant test, type, lint, or build bundle for the combined result.
8. Evaluate documentation impact and update docs only when behavior or public contracts changed.
9. Send a shutdown request to each teammate individually and report implementation plus verification results.

## Template: Review

For `/ck:team review <scope> [--reviewers N]`:

1. Derive independent focuses such as correctness, security, performance, and test coverage.
2. Create one read-only task per focus and spawn named reviewers concurrently.
3. Ask reviewers for concrete file/line evidence and actionable findings; do not force a finding quota.
4. Synthesize, deduplicate, and prioritize the findings.
5. Send a shutdown request to each teammate individually and report the result.

## Template: Debug

For `/ck:team debug <issue> [--debuggers N]`:

1. Generate independently testable hypotheses with distinct predicted evidence.
2. Create one task per hypothesis and spawn named debugger teammates concurrently.
3. Keep code changes read-only until evidence identifies a root cause. Use direct peer messages for challenges or contradictory evidence.
4. Synthesize the evidence chain, rejected hypotheses, root cause, and recommended fix.
5. Send a shutdown request to each teammate individually and report the result.

## Delegate Mode

With `--delegate`, the lead only decomposes work, assigns tasks, messages teammates, resolves ownership, and synthesizes results. The lead does not edit files or run the implementation itself. Assign any shared-file integration to one named integrator teammate.

## When to Use Agent Teams

| Scenario | Prefer |
|----------|--------|
| Focused or sequential task | Single session or subagent |
| Same-file implementation | Single owner, sequential work |
| Independent research/review angles | Agent Team |
| Competing debug hypotheses | Agent Team |
| Cross-layer work with disjoint files | Agent Team |
| Tight token budget | Single session or lower-cost subagents |

Agent Teams multiply token use by the number and lifetime of active teammates. Keep teams small, keep prompts focused, and choose lower-cost teammate models where evals show sufficient quality.

## Recovery and Shutdown

1. Redirect a teammate with a direct message.
2. Reassign a stuck task or spawn a named replacement.
3. Resolve file-ownership conflicts before further edits.
4. On abort, send a shutdown request to every active teammate and report unfinished tasks.

Do not delete team directories manually. Session-scoped team setup and cleanup are managed by Claude Code.

## References

- [`references/agent-teams-official-docs.md`](references/agent-teams-official-docs.md): canonical runtime semantics
- [`references/agent-teams-controls-and-modes.md`](references/agent-teams-controls-and-modes.md): controls and task management
- [`references/agent-teams-examples-and-best-practices.md`](references/agent-teams-examples-and-best-practices.md): examples and operating patterns
- `.claude/rules/team-coordination-rules.md`: teammate behavior rules
