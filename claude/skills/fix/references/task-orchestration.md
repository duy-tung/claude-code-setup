# Task Orchestration

Use native Claude Tasks when they improve multi-phase visibility, handoff, or
coordination. They are optional execution aids, not prerequisites for fixing.

`TaskCreate`, `TaskUpdate`, `TaskGet`, and `TaskList` may be unavailable outside the
CLI. If so, use a lightweight inline checklist or `TodoWrite`; the workflow remains
fully functional.

## When to Track

| Work | Tracking |
|------|----------|
| Quick/local | None; scout, diagnose, edit, and check inline |
| Straightforward standard | Inline checklist if useful |
| Multi-phase/multi-owner standard | Small task graph |
| Deep/high-risk | Durable phases, dependencies, owners, and approval points |
| Independent issues | One owner/tree per issue plus integration verification |

Activate `ck:project-management` only when an existing tracked plan needs hydration
or sync-back, or when cross-session program management has real value.

## Minimal Standard Graph

```text
investigate -> implement -> verify -> finalize
```

Combine scout and diagnosis when one owner performs both. Add a separate review
task only for broad, difficult, or high-risk changes.

Example:

```text
T1 = TaskCreate(subject="Investigate root cause")
T2 = TaskCreate(subject="Implement fix", addBlockedBy=[T1])
T3 = TaskCreate(subject="Verify affected behavior", addBlockedBy=[T2])
T4 = TaskCreate(subject="Finalize", addBlockedBy=[T3])
```

## Deep Graph

Represent only necessary phases:

```text
investigate/research -> choose approach -> implement
  -> proportional evidence bundle -> independent review/approval -> finalize
```

Research, design notes, machine-readable artifacts, and review are appropriate
when risk, CI/release gates, or handoff consumes them. Do not create empty phases
solely to match a fixed template.

## Independent Issues

Assign separate owners only when issues do not share mutable files or critical
context. Each owner follows `reproduce -> diagnose -> fix -> targeted verify`.
Afterwards, run one integration check across the combined diff. Limit ordinary
fan-out to three workers.

## Rules

- One in-progress task per owner unless the tool requires otherwise.
- Mark status promptly enough to unblock dependent work.
- Keep ownership and dependencies explicit for shared surfaces.
- Do not delegate the integrated diagnosis or final compatibility decision to
  disconnected workers.
- Questions are for material scope, contract, authority, or regression choices,
  not routine task transitions.
