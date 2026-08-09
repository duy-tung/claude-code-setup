# Agent Teams -- Controls and Task Management

> Source: https://code.claude.com/docs/en/agent-teams
> Baseline: Claude Code 2.1.178+ implicit teams; CK requires 2.1.219+

## Display Modes

- **In-process:** teammates share one terminal UI. Use `Shift+Down` to cycle through the lead and teammates, `Enter` to inspect a teammate, `Escape` to interrupt the active turn, and `Ctrl+T` to toggle the task list.
- **Split panes:** each teammate has a pane. This requires a supported tmux or iTerm2 setup.

The default `auto` mode uses panes when an eligible pane environment is already active and otherwise uses in-process mode.

```json
{
  "teammateMode": "in-process"
}
```

Per-session override:

```text
claude --teammate-mode in-process
```

## Start and Stop

With `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`, the session's team exists implicitly. Start work by spawning named background agents directly.

At the end:

1. Confirm all tasks are completed, reassigned, or explicitly reported unfinished.
2. Send a shutdown request to each active teammate by name.
3. Wait for acknowledgements or report any teammate still finishing an in-flight operation.
4. End the workflow; Claude Code performs session-team cleanup automatically.

## Model and Effort Controls

- Use the agent definition's model or provide `model` on an individual spawn.
- Different teammates can use different models in the same team.
- Omit a model override when the agent definition/runtime default is appropriate.
- Teammates inherit the lead's effort level by default.
- Keep model and effort decisions independent: a cheap model can still receive high effort, and an expensive model can use lower effort for a narrow task.

Do not pin every teammate to Opus. For example, a focused research pass may use Sonnet while a difficult integration review uses Opus.

## Plan Approval

Require teammate plan approval only when the change is complex, risky, or hard to reverse:

```text
Spawn an architect teammate for the authentication refactor and require plan approval before edits.
```

The teammate remains read-only until the lead accepts the plan. If rejected, the teammate revises it using the lead's concrete feedback. Avoid adding this gate to routine, well-scoped work.

## Delegate Mode

Delegate mode keeps the lead focused on decomposition, task ownership, direct messages, dependency handling, and synthesis. The lead does not implement code. Give shared-file integration to one explicitly named integrator teammate.

## Task Assignment

Task flow: `pending` -> `in_progress` -> `completed`.

- **Lead-assigned:** set the owner explicitly when special expertise or file ownership matters.
- **Self-claimed:** an idle teammate takes an unassigned, unblocked task.
- **Dependent:** a task remains blocked until all prerequisites complete.

Include these fields in every implementation task:

- concrete deliverable and acceptance criteria
- exclusive file or directory ownership
- inputs and dependencies
- expected verification and report format

## Shared Checkout Controls

All teammates see the same files immediately.

1. Partition parallel writers by non-overlapping files or directories.
2. Reserve shared manifests, schemas, generated files, and lockfiles for one owner.
3. If ownership overlaps, pause one task and reassign or sequence the edits.
4. Never rely on later reconciliation to make concurrent overwrites safe.
5. Run combined verification only after all writers have finished their assigned slices.

## Direct Teammate Interaction

- Address a teammate by stable name, not runtime ID.
- Send one direct message per intended recipient.
- Put the requested action, relevant evidence, and any deadline/blocker in the message.
- An idle teammate resumes when messaged.
- Teammate-to-lead and peer messages arrive automatically.

## Event-Driven Monitoring

Prefer event-driven coordination:

1. Spawn independent work in the background.
2. React to task-completion events, idle events, and inbound messages.
3. Reconcile with `TaskList` when state is unclear or an event may have been missed.
4. Reassign blocked work or message its owner directly.

Fixed-interval polling wastes turns and tokens; do not use it as the normal monitoring loop.
