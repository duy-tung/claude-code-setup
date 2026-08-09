# Orchestration Protocol

## Delegation Context

When spawning a subagent via Agent, include only the context needed for its owned
deliverable:

1. **Work Context Path**: The git root of the PRIMARY files being worked on
2. **Files and boundaries**: Exact files to read or modify, plus acceptance evidence
3. **Plan reference**: Only when the task is executing an active plan phase
4. **Reports path**: Only when the worker explicitly owns a persistent report artifact

**Example:**
```
Agent prompt: "Fix parser bug.
Work context: /path/to/project-b
Files: src/parser.ts, tests/parser.test.ts
Acceptance: targeted parser test passes"
```

**Rule:** If CWD differs from work context, use the work context path. Do not invent a
`plans/` or `reports/` path for work that does not use those artifacts.

---

#### Delegation Threshold

Before applying either pattern below, decide whether to delegate at all. Spawn a
subagent only when the work is genuinely independent and parallelizable, or needs its
own context budget. Work finishable in a handful of tool calls stays inline — writing
the prompt, paying for the subagent's context, and reading its report back costs more
than doing it. Full criteria: `./.claude/rules/model-calibration.md` §3.

Start with one worker when one can finish the track. Keep ordinary fan-out to three or
fewer concurrent workers; use a larger Agent Team only for clearly partitioned work or
when the user requests it.

#### Sequential Chaining
Sequential dependencies are usually cheapest in the controller. Chain specialists only
when each stage is substantial enough to benefit from a separate context:

- **Research → design:** when an external decision must be resolved before architecture
- **Implementation → test analysis:** when the test surface or failures form their own sizeable task
- **Implementation → independent review:** only for broad or high-risk changes

Do not instantiate planning, simplification, testing, review, and documentation agents
as a default pipeline. Pass only the prior stage's decision and evidence to the next
stage, not its full transcript.

#### Parallel Execution
Spawn multiple subagents simultaneously for independent tasks:
- **Code + Tests + Docs**: When implementing separate, non-conflicting components
- **Multiple Feature Branches**: Different agents working on isolated features
- **Cross-platform Development**: iOS and Android specific implementations
- **Careful Coordination**: Ensure no file conflicts or shared resource contention
- **Merge Strategy**: Plan integration points before parallel execution begins
- **Don't Idle-Wait**: After delegating independent subtasks, keep working on other available work while subagents run — collect results when they return

Do not parallelize multiple workers over the same files. Agent Team teammates share the
same checkout unless the workflow explicitly creates separate worktrees.

---

## Subagent Status Protocol

Subagents MUST report one of these statuses when completing work:

| Status | Meaning | Controller Action |
|--------|---------|-------------------|
| **DONE** | Task completed successfully | Proceed to next step (review, next task) |
| **DONE_WITH_CONCERNS** | Completed but flagged doubts | Read concerns → address if correctness/scope issue → proceed if observational |
| **BLOCKED** | Cannot complete task | Assess blocker → provide context / break task / escalate to user |
| **NEEDS_CONTEXT** | Missing information to proceed | Provide missing context → re-dispatch |

### Handling Rules

- **Never** ignore BLOCKED or NEEDS_CONTEXT — something must change before retry
- **Never** force same approach after BLOCKED — try: more context → simpler task → more capable model → escalate
- **DONE_WITH_CONCERNS** about file growth or tech debt → note for future, proceed now
- **DONE_WITH_CONCERNS** about correctness → address before review
- If subagent fails 3+ times on same task → escalate to user, don't retry blindly

### Reporting Format

Subagents should end their response with:

```
**Status:** DONE | DONE_WITH_CONCERNS | BLOCKED | NEEDS_CONTEXT
**Summary:** [1-2 sentence summary]
**Concerns/Blockers:** [if applicable]
```

---

## Context Isolation Principle

**Subagents receive only the context they need.** Never pass full session history.

### Rules

1. **Craft prompts explicitly** — Provide task description, relevant file paths, acceptance criteria. Not "here's what we discussed."
2. **No session history** — Subagent gets fresh context. Summarize relevant decisions, don't replay conversation.
3. **Scope file references** — List specific files to read/modify. Not "look at the codebase."
4. **Include plan context** — If working from a plan, provide the specific phase text, not the entire plan.
5. **Preserve controller context** — Coordination work stays in main agent. Don't dump coordination details into subagent prompts.

### Prompt Template

```
Task: [specific task description]
Files to modify: [list]
Files to read for context: [list]
Acceptance criteria: [list]
Constraints: [any relevant constraints]
Plan reference: [phase file path if applicable]

Work context: [project path]
Reports: [only when this worker owns a report artifact]
```

### Anti-Patterns

| Bad | Good |
|-----|------|
| "Continue from where we left off" | "Implement X feature per spec in phase-02.md" |
| "Fix the issues we discussed" | "Fix null check in auth.ts:45, root cause: missing validation" |
| "Look at the codebase and figure out" | "Read src/api/routes.ts and add POST /users endpoint" |
| Passing 50+ lines of conversation | 5-line task summary with file paths |

---

## Agent Teams (Optional)

For multi-session parallel collaboration, activate the `/ck:team` skill.
Not part of the default orchestration workflow. See `.claude/skills/team/SKILL.md` for templates, decision criteria, and spawn instructions.
