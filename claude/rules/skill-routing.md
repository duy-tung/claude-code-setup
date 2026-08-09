# Skill Routing

Claude Code already lists every skill with its description, so this file does not repeat
what a description says. It carries the two things a description cannot: **escalation
chains** and **disambiguation between skills that sound alike**.

Workflow scale — when to work inline versus reach for a plan or a specialist — is defined
in `./.claude/rules/model-calibration.md` §2. Pick the smallest workflow that delivers and
verifies the outcome. The chains below are escalation paths, not mandatory pipelines.

## Escalation chains

```
Development   /ck:plan → /ck:cook → [test if needed] → [review if risk warrants] → [ship when requested]
Bugfix        [scout if broad] → /ck:debug → /ck:fix → [expanded test/review if risk warrants]
```

| User intent | Suggested start |
|---|---|
| Small, well-specified feature or edit | Work inline: inspect → edit → targeted check |
| Multi-component feature needing a durable handoff | `/ck:plan` then `/ck:cook` |
| "execute this plan" | `/ck:cook <plan-path>` |
| "quick implementation" | `/ck:cook --fast` |
| Small bug with a local reproduction | Diagnose and fix inline, then rerun that reproduction |
| Broad or unclear bug | `/ck:fix` (scout/debug only as needed) |
| "CI is failing", "tests broken" | `/ck:fix --auto` |
| "understand how X works" | Inspect directly; `/ck:scout` only when the surface is broad |
| "why is X happening" | `/ck:debug` |
| "explore options for X" | `/ck:brainstorm`; offer `/ck:plan` only after a decision |
| "what am I missing", "map my blind spots" | `/ck:brainstorm --blindspots` |

## Disambiguation

Pick one skill per distinct intent. These pairs overlap in wording but not in job:

| Sounds similar | Use this when |
|---|---|
| `/ck:scout` vs `/ck:repomix` | scout = find specific files, symbols, callers. repomix = pack a whole repo for onboarding or an LLM dump |
| `/ck:git` vs `/ck:ship` | git = stage, commit, push, open a PR. ship = the full branch → merge → test → review → PR pipeline |
| `/ck:preview --diagram` vs `/ck:tech-graph` | preview = fast visual for self-review. tech-graph = publish-grade SVG/PNG output |
| `/ck:docs` vs `/ck:find-skills` | docs = write or sync project documentation. find-skills = discover which skill does a thing |
| `/ck:security` vs `/ck:code-review` | security = STRIDE/OWASP audit with optional auto-fix. code-review = correctness and quality of a bounded diff |
| `/ck:loop` vs `/ck:autoresearch` | loop = run the bounded iteration. autoresearch = router explaining which family member fits |

## After implementation

Inspect the final diff and reuse the verification evidence you already have — see
`model-calibration.md` §4. Then consider, only when it applies:

- `/ck:code-review` — broad, unfamiliar, security-sensitive, data-changing, or
  concurrency-heavy changes
- `/ck:ship` — only when the user wants the release/PR pipeline
- `/ck:journal` — only for a durable decision, incident, or lesson worth preserving
- `/ck:worktree` — when branch isolation is useful for sizeable shared-codebase work
