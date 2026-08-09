---
name: ck:code-review
description: "Review code with proportional evidence and reachable-risk analysis. Use for pending diffs, PRs, commits, or explicit codebase and security audits."
user-invocable: true
when_to_use: "Invoke to review pending changes, a PR or commit, or to run an explicit broad codebase/pre-landing audit."
category: utilities
keywords: [review, quality, verification, reliability]
argument-hint: "[#PR | COMMIT | --pending | codebase [parallel]]"
metadata:
  author: claudekit
  version: "2.0.0"
---

# Code Review

Review production risk with evidence. Small diffs receive one focused pass; broad,
security-sensitive, migration, and pre-landing scopes may add independent scouting,
checklists, and durable evidence.

## Input Modes

| Input | Mode | Review target |
|---|---|---|
| `#123` or PR URL | PR | Full PR diff from `gh pr diff` |
| `abc1234` (7+ hex chars) | Commit | One commit from `git show` |
| `--pending` | Pending | Staged and unstaged changes |
| No args with recent context | Default | The change already in context |
| `codebase` | Codebase | Explicit full-codebase scan |
| `codebase parallel` | Codebase+ | Explicit multi-reviewer codebase audit |

Use `references/input-mode-resolution.md` for parsing details. With no arguments,
reuse an unambiguous recent change; otherwise inspect pending changes. Ask the user
only when multiple plausible targets would materially change the review or no target
can be discovered.

## Scale Gate

- **Small/single-file diff:** resolve the diff, read direct callers/tests only as
  needed, review it once, and return findings inline. Skip separate spec stages,
  scout/subagent pipelines, full scans, report files, and duplicate test runs.
- **Standard diff:** review the complete bounded diff and trace affected contracts or
  data flow with targeted searches. Add an independent reviewer only for a distinct
  difficult lens.
- **Broad/high-risk:** use the matching expanded workflow for security, public
  contracts, migrations, release/pre-landing, or explicit codebase audits.

Three changed files alone do not make a change broad. Parallelize only independent
review scopes, with no more than three ordinary concurrent workers.

## Direct Diff Review

1. **Resolve scope.** Capture the requested behavior/spec and the exact diff.
2. **Read once for compliance and quality.** In one pass, check requested behavior,
   unjustified scope, correctness, reachable edge cases, contracts, error paths,
   performance, and relevant trust boundaries.
3. **Trace selectively.** Use direct `rg`, file reads, or caller/test inspection only
   where the diff leaves a material risk question.
4. **Reuse fresh evidence.** Accept recent tests, reproduction, lint, typecheck, or
   build output that matches the unchanged diff. Run the narrowest missing check;
   re-run only after relevant edits, when evidence is stale, or when risk requires an
   independent confirmation.
5. **Report all supported findings, then rank severity.** Do not hide discovery by
   filtering for only critical findings in the initial pass.

For plan/spec work, use `references/spec-compliance-review.md` as a lens inside this
pass. A separate stage is justified only for a broad contractual change where
independent evidence improves reliability.

## Review Lenses

| Lens | Questions |
|---|---|
| Behavior | Does the diff implement the request and important boundary/error cases? |
| Regression | Which reachable callers or stored states can break? |
| Contract | Are exported types, API/schema/config behavior, timing, and compatibility intentional? |
| Reliability | Are errors, cleanup, retries, concurrency, and state mutation safe? |
| Performance | Is there reachable unbounded work, N+1 I/O, or a hot-path regression? |
| Security | Are authn/authz, untrusted input, secrets/PII, and output boundaries protected? |
| Evidence | Does fresh verification actually cover the claimed behavior? |

Use YAGNI, KISS, and DRY as design lenses, not reasons to report preference-only
style issues.

## Findings Format

Return findings first, ordered by severity. Each finding needs:

- severity and concise title;
- tight file/line location;
- a concrete reachable scenario and impact;
- the smallest practical fix or missing verification.

Use Critical, High, Medium, and Low based on impact and reachability. No findings is a
valid result. Do not invent numeric confidence, coverage, or quality scores. Mark a
material claim verified, inferred, or unknown when that distinction helps the landing
decision.

For small reviews, follow findings with only a short scope/evidence note. Create a
durable report artifact only when requested or when an explicit broad audit needs one.

## Conditional Edge-Case Scouting

Use `references/edge-case-scouting.md` or `/ck:scout` only when the dependency graph,
async/state flow, or blast radius cannot be established efficiently from the diff and
targeted search. A routine local change does not require a scout report before review.

## Expanded Broad and Security Workflows

These explicit workflows retain stricter gates:

- **Pre-landing, `/ck:ship`, or checklist request:** load
  `references/checklist-workflow.md` and applicable files under
  `references/checklists/`. Preserve the critical blocking pass, informational pass,
  and required verification evidence.
- **Security audit:** apply all relevant trust-boundary/domain checklists; unsupported
  or unverified high-impact surfaces remain a blocker or stated evidence gap.
- **Full codebase:** use `references/codebase-scan-workflow.md` only for the explicit
  `codebase` input.
- **Parallel codebase audit:** use `references/parallel-review-workflow.md`; split
  independent domains across at most three ordinary reviewers unless the user
  explicitly authorizes a larger team.
- **Broad public-contract or migration review:** independent spec/domain review and
  adversarial verification may be warranted before landing.

`repomix`, full-repository scans, and review artifacts belong to these broad workflows,
not ordinary diff review.

## Conditional Task Pipeline

Use `references/task-management-reviews.md` only when broad independent scopes or
high-risk fix/review cycles need durable coordination. The conceptual chain is:

```text
conditional scout -> review scopes -> fix blockers -> verify affected evidence
```

Do not create this chain for a small change or simply because several files changed.
If Task tools are unavailable, keep the same evidence boundaries in a short inline
plan. Re-review only the affected diff after fixes; stop after three unresolved fix
cycles and ask for the material decision.

## Verification Before Claims

Completion and landing claims require relevant evidence, but “fresh” does not mean
duplicating an unchanged command. Follow
`references/verification-before-completion.md` to identify, run or reuse, read, and
record the check that actually proves the behavior. Critical findings block landing
until fixed and the affected evidence passes.

## Receiving or Requesting Review

For external feedback, use:

```text
READ -> UNDERSTAND -> VERIFY -> EVALUATE -> RESPOND -> IMPLEMENT
```

See `references/code-review-reception.md`. Ask about unclear feedback only when its
interpretation changes the code or risk materially.

When an independent review is explicitly useful, use
`references/requesting-code-review.md` with a bounded diff, requested behavior, base
and head SHA, and existing verification evidence. Do not dispatch a reviewer merely
to confirm a fresh passing local review.

## Reference Map

| Need | Reference |
|---|---|
| Input parsing | `references/input-mode-resolution.md` |
| Spec lens | `references/spec-compliance-review.md` |
| Feedback handling | `references/code-review-reception.md` |
| Independent review | `references/requesting-code-review.md` |
| Verification evidence | `references/verification-before-completion.md` |
| Conditional scouting | `references/edge-case-scouting.md` |
| Pre-landing/security checklists | `references/checklist-workflow.md` |
| Broad task coordination | `references/task-management-reviews.md` |
| Full-codebase scan | `references/codebase-scan-workflow.md` |
| Parallel codebase audit | `references/parallel-review-workflow.md` |

## Workflow Position

**Typically follows:** `/ck:cook` or `/ck:fix` when an independent review is useful.

**Typically precedes:** `/ck:ship` for changes whose landing policy requires review.

**Related:** `/ck:scout` and `/ck:test`, both conditional on missing context or evidence.
