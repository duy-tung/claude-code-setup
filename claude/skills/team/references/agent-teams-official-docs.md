# Agent Teams -- Canonical Runtime Semantics

> Canonical source: https://code.claude.com/docs/en/agent-teams
> Compatibility baseline: Claude Code 2.1.178+ implicit teams
> Claude Opus 5 baseline: Claude Code 2.1.219+
> Reviewed: 2026-08-09

This reference records only the runtime contracts CK depends on. Re-check the canonical source when Claude Code changes Agent Teams.

## Overview

Agent Teams coordinate multiple Claude Code sessions through one lead, named teammates, a shared task list, and direct inter-agent messaging. Each teammate has an independent context window and receives project context plus its spawn prompt; it does not receive the lead's conversation history.

Use teams when independent workstreams need to exchange findings or coordinate. Prefer a single session or ordinary subagent for sequential work, same-file edits, or routine tasks where coordination cost exceeds the benefit.

## Enablement and Version

Agent Teams remain experimental. Enable them in the shell or project/user settings:

```json
{
  "env": {
    "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1"
  }
}
```

Check the runtime before diagnosing team behavior:

```text
claude --version
```

CK targets Claude Code 2.1.219 or newer so the same installation also supports Claude Opus 5. Account and runtime policy can still make Agent Teams unavailable after the flag is set.

## Implicit Lifecycle

Every enabled session has one implicit, session-scoped team. Spawn named teammates directly with `Agent`; there is no setup call before the first spawn.

At completion, request shutdown from every active teammate. Claude Code owns the session team lifecycle and resource cleanup. Do not hand-edit runtime team/task directories.

## Architecture

| Component | Responsibility |
|-----------|----------------|
| Lead | Decomposes work, assigns tasks, resolves ownership, and synthesizes results |
| Named teammate | Runs an independent Claude Code context and performs one bounded workstream |
| Shared task list | Tracks ownership, dependencies, and task state |
| Direct messaging | Delivers messages between specifically named participants |

Task dependency changes are automatic: completing a blocker makes dependent tasks claimable.

## Spawn Contract

```text
Agent(
  subagent_type: "researcher",
  name: "api-researcher",
  description: "research API constraints",
  prompt: "bounded task, deliverable, constraints, file ownership, context",
  model: "sonnet",
  run_in_background: true
)
```

- `name` makes the background agent addressable as a teammate.
- `run_in_background: true` allows concurrent work.
- `model` is optional and may differ by teammate. A referenced agent definition can also provide its model.
- Mixed-model teams are supported. Select models according to task difficulty, quality evals, latency, and cost.
- Teammates inherit the lead's effort level by default. Model selection and effort are separate controls.
- A custom agent's instruction body and supported restrictions apply when that agent type is used as a teammate.

## Shared Checkout

Teammates operate in the same checkout. Parallel writers therefore need exclusive file ownership:

- Put explicit file or directory boundaries in each implementation task.
- Give shared manifests, schemas, generated indexes, and lockfiles to one integrator.
- Make tasks sequential when ownership cannot be separated safely.
- Stop and reassign before editing when an unexpected overlap appears.
- Read-only research and review can overlap freely.

Agent Teams coordinate collaborators; they do not provide per-teammate filesystem isolation.

## Task Surface

| Tool | Purpose |
|------|---------|
| `TaskCreate` | Create a bounded item with acceptance criteria and ownership |
| `TaskUpdate` | Assign, claim, block, complete, or reassign work |
| `TaskGet` | Read full details and dependency relationships |
| `TaskList` | Read compact team progress |

Task states are `pending`, `in_progress`, and `completed`. Claiming is synchronized so two teammates do not claim the same task simultaneously.

## Direct Messaging and Shutdown

- Address a teammate by its stable name.
- Send one direct message to each intended recipient.
- Messages arrive automatically; recipients do not need an inbox polling loop.
- An idle teammate can resume when it receives another direct instruction.
- Send a shutdown request separately to each active teammate at the end.
- A teammate can finish a critical operation before approving shutdown; report delays rather than deleting state.

## Hooks and Progress

Agent Teams expose task-completion and teammate-idle lifecycle events. Use them for reactive progress handling:

1. Spawn independent teammates and create their tasks.
2. React to completion/idle events and inbound messages.
3. Use `TaskList` only to reconcile unclear state or recover after missed events.
4. Do not poll on a fixed timer.

Hooks can enforce task-quality gates, but routine tasks should not accumulate redundant verification passes.

## Context, Models, and Permissions

Each teammate loads project instructions, available skills, and configured tool integrations, then receives the lead's spawn prompt. Include task-specific constraints and deliverables in that prompt because the lead's conversation is not copied.

Teammates start with the lead's permission settings. Keep per-teammate prompts free of secrets because prompts and tool activity can be retained in logs or session state.

## Cost Guidance

Token use grows with the number and lifetime of active teammates. Keep teams small, scope prompts tightly, shut down completed teammates, and use lower-cost models when evals show that quality holds. A team is usually not cost-effective for one focused or sequential task.

## Known Constraints

- Experimental availability can vary by account/runtime.
- Teammates share the checkout, so same-file parallel writes are unsafe.
- Each teammate has its own context and does not inherit lead conversation history.
- Task state can lag if a teammate fails to update its task.
- Shutdown may wait for an in-flight response or tool call.
- The lead remains responsible for ownership, synthesis, and incomplete work.
