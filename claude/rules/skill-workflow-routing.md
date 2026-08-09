# Skill Workflow Routing

Choose the smallest workflow that can deliver and verify the requested outcome. Skill
sequences below are escalation paths, not mandatory pipelines.

## Scale First

- **Small and clear:** inspect the relevant files, edit inline, run one targeted check,
  inspect the diff, and report the outcome. Do not create a plan, journal, report, or
  subagent chain.
- **Multi-step:** keep a short inline checklist and activate only the stages that own a
  meaningful deliverable.
- **Large, risky, or explicitly parallel:** use planning and specialist skills with
  bounded scopes, then broaden verification or review in proportion to risk.

## Core Development Workflow

For large or durable work, a typical escalation path is:

```
/ck:plan → /ck:cook → [test if needed] → [review if risk warrants] → [ship when requested]
```

| User Intent | Suggested Start |
|-------------|----------------|
| Small, well-specified feature or edit | Work inline: inspect → edit → targeted check |
| Multi-component feature needing a durable handoff | `/ck:plan` then `/ck:cook` |
| "execute this plan" | `/ck:cook <plan-path>` |
| "quick implementation" | `/ck:cook --fast` |

## Bugfix Workflow

For a broad or unclear failure, a typical escalation path is:

```
[scout if broad] → /ck:debug → /ck:fix → [expanded test/review if risk warrants]
```

| User Intent | Suggested Start |
|-------------|----------------|
| Small bug with a local reproduction | Diagnose and fix inline, then rerun that reproduction |
| Broad or unclear bug | `/ck:fix` (scout/debug only as needed) |
| "CI is failing", "tests broken" | `/ck:fix --auto` |
| "investigate why X happens" | `/ck:debug`; add `/ck:scout` only for a broad search |

## Investigation Workflow

Activate only the investigation stage that matches the request; do not append a plan
unless the user asks for one or the result needs a durable implementation handoff.

| User Intent | Suggested Start |
|-------------|----------------|
| "understand how X works" | Inspect directly; use `/ck:scout` only when the surface is broad |
| "why is X happening" | `/ck:debug` |
| "explore options for X" | `/ck:brainstorm`; offer `/ck:plan` only after a decision |
| "what am I missing", "map my blind spots / unknowns" | `/ck:brainstorm --blindspots` |

## Post-Implementation Checklist

After implementation, inspect the final diff and reuse fresh verification evidence.
Then consider:

- `/ck:code-review` — broad, unfamiliar, security-sensitive, data-changing, or
  concurrency-heavy changes
- `/ck:ship` — only when the user wants the release/PR pipeline
- `/ck:journal` — only for a durable decision, incident, or lesson worth preserving

## Setup Skills

For sizeable shared-codebase work, consider:

- `/ck:worktree` — when branch isolation is useful
- `/ck:scout` — when relevant files cannot be found with a focused direct search
