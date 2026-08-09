# Parallel Exploration

Parallelism is an optimization for independent, substantial work. Quick fixes use
targeted search, diagnosis, and checks inline.

## Good Uses

- separate modules must be mapped independently;
- two or three competing hypotheses have distinct evidence sources;
- external research can proceed without blocking local reproduction;
- independent issue trees have non-overlapping edits;
- long type, build, or test commands can run concurrently and their combined
  result forms one verification bundle.

Give each worker a bounded surface, concrete question, and expected evidence. Keep
one owner responsible for reconciling results into the root-cause chain.

## Avoid Parallelism When

- the failing line and relevant check are already known;
- workers would read the same files or test the same hypothesis;
- shared-checkout edits could conflict;
- coordination takes longer than the targeted command;
- multiple reviewers would repeat the same risk assessment.

## Independent Issue Pattern

```text
Issue A owner: reproduce -> diagnose -> fix -> targeted verify
Issue B owner: reproduce -> diagnose -> fix -> targeted verify
Integration owner: inspect combined diff -> run shared-contract checks
```

## Verification

Run checks inline by default. For a large suite, independent commands such as
typecheck, lint, build, and tests may run concurrently, but summarize them as one
proportional evidence bundle. Do not require separate Bash agents merely because
several commands exist.

Limit ordinary fan-out to three workers. Agents share the checkout unless explicit
isolation has been arranged, so assign non-overlapping write scopes and coordinate
before touching shared files.
