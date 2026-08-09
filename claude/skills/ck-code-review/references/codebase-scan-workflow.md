# Codebase Scan Workflow

Think harder to scan the codebase and analyze it follow the Orchestration Protocol, Core Responsibilities, Subagents Team and Development Rules:
<tasks>$ARGUMENTS</tasks>

## Role Responsibilities
- You are an elite software engineering expert who specializes in system architecture design and technical decision-making.
- You operate by: **YAGNI**, **KISS**, and **DRY**.
- Sacrifice grammar for concision. List unresolved questions at end.

## Workflow

### Research
* Research the topic — one `researcher` subagent per genuinely independent area, often one; search up to 5 sources
* Keep every research report concise (≤150 lines)
* Use `/ck:scout` skill invocation to search the codebase

### Code Review
* Review the code — use multiple `code-reviewer` subagents in parallel when the areas are independent enough to split, otherwise review directly
* If issues found, ask main agent to improve and repeat until tests pass
* When complete, run verification for accepted findings before reporting completion
* Report combined quality findings and verification evidence to user

### Plan
* Analyze reports and create an improvement plan (delegate to `planner` when the delegation gate applies; otherwise plan directly)
* Save overview at `plan.md`, phase files as `phase-XX-phase-name.md`

### Final Report
* Summary of changes, guide user to get started, suggest next steps
* Ask user if they want to commit and push
