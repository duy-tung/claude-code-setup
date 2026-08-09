# Orchestration Protocol

**Whether** to delegate is decided in `./.claude/rules/model-calibration.md` §3. This file
covers only the mechanics once you have decided to.

## Subagent prompts

A subagent starts with fresh context and never sees the conversation. Give it the task,
not the history.

```
Task: [specific task description]
Files to modify: [list]
Files to read for context: [list]
Acceptance criteria: [list]
Constraints: [any relevant constraints]

Work context: [git root of the PRIMARY files being worked on]
Plan reference: [phase file path — only when executing an active plan phase]
Reports: [only when this worker owns a persistent report artifact]
```

If CWD differs from the work context, use the work context path. Do not invent a `plans/`
or `reports/` path for work that does not use those artifacts.

| Bad | Good |
|-----|------|
| "Continue from where we left off" | "Implement X feature per spec in phase-02.md" |
| "Fix the issues we discussed" | "Fix null check in auth.ts:45, root cause: missing validation" |
| "Look at the codebase and figure out" | "Read src/api/routes.ts and add POST /users endpoint" |
| Passing 50+ lines of conversation | 5-line task summary with file paths |

Pass the prior stage's decision and evidence to the next stage, not its full transcript.
Do not parallelize workers over the same files — Agent Team teammates share one checkout
unless the workflow explicitly creates worktrees. After delegating independent work, keep
working rather than idle-waiting.

## Status protocol

Subagents end their response with:

```
**Status:** DONE | DONE_WITH_CONCERNS | BLOCKED | NEEDS_CONTEXT
**Summary:** [1-2 sentences]
**Concerns/Blockers:** [if applicable]
```

| Status | Controller action |
|--------|-------------------|
| **DONE** | Proceed |
| **DONE_WITH_CONCERNS** | Address correctness or scope concerns; note observational ones and proceed |
| **BLOCKED** | Change something before retrying: more context → simpler task → escalate. Never repeat the same approach |
| **NEEDS_CONTEXT** | Supply what is missing, then re-dispatch |

After three failures on the same task, escalate to the user instead of retrying.

## Agent Teams

Multi-session parallel collaboration is opt-in and not part of the default workflow.
See `.claude/skills/team/SKILL.md`.
