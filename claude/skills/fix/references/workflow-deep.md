# Deep Workflow

Use this workflow for complex, production-critical, security-sensitive, or
architectural failures. It may use durable tasks, research, design artifacts, and
independent review because the risk and handoff value justify them.

## Suggested Work Graph

Create only the phases the incident needs. A common graph is:

```text
investigate (scout + reproduce + diagnose)
  -> design (research/alternatives when needed)
  -> implement
  -> verify (repro + regression + blast radius)
  -> independent review / approval when risk requires it
  -> finalize
```

Parallelize bounded research or independent hypotheses when they do not duplicate
context. Keep one owner for the integrated diagnosis and shared implementation.

## 1. Establish the Evidence Chain

Capture the exact symptom, reproduction, expected behavior, relevant environment,
recent changes, call chain, shared contracts, and affected tests. Form competing
hypotheses and test the cheapest discriminating evidence. Trace the confirmed
chain from symptom to the original defect.

Use focused exploration workers, `ck:debug`, or structured reasoning when useful;
none is mandatory merely because this mode is named Deep. If three fix attempts
fail, stop and discuss whether the architecture or original assumptions are wrong.

## 2. Research and Choose an Approach

Research external behavior only when framework, provider, security, or versioned
contracts are relevant. Compare viable approaches against:

- ability to remove the root cause;
- compatibility and migration impact;
- data, security, performance, and rollback risk;
- verification cost and observable success criteria.

Ask the user only if the decision changes a public contract, intended scope,
destructive action, external authority, or acceptable regression. Otherwise choose
the conservative reversible option and record why.

Create a durable plan or design note when multiple owners, sessions, or risky
phases benefit from it. Do not generate artifacts solely to satisfy a template.

## 3. Implement

- Fix the root cause in cohesive, reviewable phases.
- Preserve contracts by default and surface intentional migrations explicitly.
- Reassess the diagnosis whenever implementation evidence expands the scope.
- Avoid unrelated cleanup that obscures causality or rollback.

## 4. Proportional Evidence Bundle

For deep work, the bundle usually includes:

1. exact pre-fix repro rerun with before/after evidence;
2. focused regression tests that distinguish the defect;
3. affected integration, contract, and dependent checks;
4. applicable type, lint, build, security, performance, or migration checks;
5. edge cases identified by the diagnosis;
6. final-diff and rollback inspection.

Run independent checks in parallel only when their duration makes that useful.
Write machine-readable workflow artifacts when a CI gate, release process, or
high-risk approval consumes them. Otherwise a concise evidence summary is enough.

## 5. Independent Review and Approval

Use one independent reviewer for broad, difficult, security-sensitive, data-risk,
or production-critical changes. Add domain/adversarial review only for a distinct
risk that the first review cannot cover. Findings and executable evidence approve
the change; numeric scores do not.

Pause for the user when a material contract/scope/authority choice remains or a
known regression would need acceptance. Repair clear in-scope reversible issues
without creating an unnecessary checkpoint.

## 6. Finalize

Report the root cause, evidence chain, implementation, fresh verification,
rollback notes, and unresolved risks using `verified`, `inferred`, or `unknown`.
Sync an existing plan and update public docs when relevant. Journal a durable
technical lesson only when it will help future work. Commit, push, or deploy only
with the required authority.

For frontend incidents, include project-native browser and visual checks. For
AI/LLM behavior, use `ck:context-engineering` when context or prompt mechanics are
part of the root cause.
