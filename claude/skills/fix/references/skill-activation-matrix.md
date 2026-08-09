# Skill Activation Matrix

Activate a skill, agent, or artifact only when it reduces uncertainty or execution
time enough to justify its coordination cost.

## Core Work

| Need | Default | Escalate when |
|------|---------|---------------|
| Locate a deterministic local failure | Direct search/read | Use `ck:scout` or focused Explore workers for a broad or unfamiliar surface |
| Diagnose an obvious cause | Inspect inline and rerun repro | Use `ck:debug` for non-trivial traces; use structured reasoning for stubborn competing hypotheses |
| Track work | Inline checklist or no artifact | Use Tasks for multi-phase coordination, handoff, or independent issue trees |
| Verify | Run one proportional evidence bundle inline | Parallelize long independent checks; use a tester for a distinct testing problem |
| Review | Inspect final diff inline | Use an independent reviewer for broad, difficult, or high-risk changes |
| Finalize | Concise evidence-backed report | Sync an existing plan, update public docs, or journal a durable lesson only when relevant |

## Conditional Skills and Workers

| Skill/worker | Use when |
|--------------|----------|
| `ck:brainstorm` | Deep work has multiple materially different valid approaches |
| `ck:context-engineering` | The defect involves AI/LLM context, prompts, memory, or agent behavior |
| vision/browser tooling | Visual behavior or browser interaction is part of the acceptance criteria |
| `researcher` | Versioned external documentation, advisories, or provider behavior affects the fix |
| `planner` | A complex multi-owner or multi-session change needs a durable execution graph |
| `general-purpose` | Two or more independent issues can be owned without overlapping edits |
| `git-manager` | Commit/publish work is authorized and delegation is useful |
| `docs-manager` | Public behavior or operating instructions changed substantially |

## Workflow Map

| Workflow | Typical activation |
|----------|--------------------|
| Quick | Direct targeted scout, diagnosis, edit, checks, and diff review |
| Standard | Direct work plus only the focused tools/tasks needed by uncertainty or coordination |
| Deep | Durable tasks/artifacts, research, and independent review as justified by risk |
| Parallel | Separate issue owners plus one integration owner/check |

## Questions and Evidence

Infer mode by default. Ask only for a material scope, contract, authority, or
regression-acceptance decision that cannot be discovered locally. Report evidence
as `verified`, `inferred`, or `unknown`, never as a numeric confidence threshold.
