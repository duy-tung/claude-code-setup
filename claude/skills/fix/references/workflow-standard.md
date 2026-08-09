# Standard Workflow

Use this workflow for a moderate fix with a confirmed but multi-file root cause,
or when a quick investigation uncovers meaningful uncertainty.

## Tracking

Use a small task list only when it improves visibility or coordinates independent
work. A typical sequence is `investigate → implement → verify → finalize`;
do not create separate tasks for every tool or report.

## 1. Scout and Diagnose

1. Capture the smallest reproducible failure and expected behavior.
2. Map the symptom, direct call chain, related tests, and recent relevant changes.
3. Form explicit hypotheses and test the cheapest discriminating evidence first.
4. Trace the confirmed chain back to the root cause and identify the demonstrated
   blast radius.

Inspect directly first. Use `ck:debug`, focused exploration workers, or structured
reasoning only when the uncertainty warrants their coordination cost. See
`diagnosis-protocol.md`.

## 2. Implement

- Fix the confirmed root cause with a minimal, cohesive diff.
- Follow existing patterns and preserve contracts unless a contract change is
  intentional and authorized.
- If the implementation surface differs materially from the diagnosis, record the
  new evidence and reassess scope before continuing.

## 3. Proportional Evidence Bundle

Collect one bundle that contains:

1. the original repro rerun and before/after result;
2. focused regression coverage;
3. checks for affected modules and demonstrated dependents;
4. applicable lint, type, or build checks at the narrowest meaningful scope;
5. final-diff inspection for contract and side-effect risk.

Broaden to repository-wide checks only for shared contracts or a repository-wide
blast radius. Parallelize long independent checks only when it saves real time.
Add an independent reviewer when the diff is broad, hard to reason about, or high
risk; otherwise review inline.

If a check fails, return to diagnosis. Repair an obvious in-scope regression; ask
the user only when resolution needs a material scope, contract, authority, or
regression-acceptance decision. Stop and question the architecture after three
failed fix attempts.

## 4. Finalize

Report outcome, root cause, changed files, evidence, and unresolved risks using
`verified`, `inferred`, and `unknown`. Sync an existing plan when relevant, update
docs only for changed public behavior or operations, and journal only a durable
lesson. Ask before commit/push/deploy unless already authorized.

For UI work, include the smallest useful visual/browser check. For AI/LLM code,
consider `ck:context-engineering` when context behavior is part of the defect.
