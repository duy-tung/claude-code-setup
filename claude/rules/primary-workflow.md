# Primary Workflow

Activate only the skills and workflow stages the task needs. Follow
`opus-5-calibration.md` for scope, delegation, output, and verification behavior.

## Scale the workflow first

- **Small and clear:** inspect the minimum context, edit inline, run one targeted check,
  and report the outcome. Do not create plan/report artifacts or spawn agents.
- **Multi-step:** keep a short task checklist. Create a persistent plan only when the
  work has meaningful dependencies, handoffs, or state that must survive the session.
- **Large, risky, or parallel:** use the appropriate planning and specialist agents,
  with explicit file ownership and acceptance criteria.

A phase name below identifies the kind of work, not a mandatory agent call. Apply the
delegation gate in `opus-5-calibration.md` §3 before every spawn.

## 1. Understand and implement

- Read the repository instructions and the files that govern the requested behavior.
- Research external facts only when the answer is unstable, unknown, or required for a
  design decision. Prefer authoritative sources.
- Implement the complete requested outcome; do not leave stubs or placeholders.
- Follow existing architecture and update existing files when they are the natural
  home. Create a new file when it represents a real new responsibility.
- Handle failure modes that are in scope. Do not build speculative abstractions for
  hypothetical future requirements.
- After a coherent edit batch, run the cheapest syntax/type/build check that can catch
  mistakes in the changed surface. Do not compile after every individual file.

Use `planner` only when the task needs an architectural plan or durable handoff. Use
`researcher` only for a bounded research track that can run independently.

## 2. Verify proportionally

- Run tests that exercise the changed behavior. Start targeted; expand for shared
  configuration, public contracts, broad fan-out, migrations, or high-risk changes.
- Add or update tests when the change introduces behavior that existing tests do not
  cover and a regression would matter.
- Do not ignore a relevant failing check. Fix it, or report the exact pre-existing or
  external blocker with evidence.
- Do not repeat the same check through multiple agents. Use `tester` only when test
  selection, environment setup, or failure analysis is itself a sizeable independent
  task.

## 3. Review when risk warrants it

- Review the final diff inline for ordinary changes.
- Use `code-reviewer` for broad, security-sensitive, data-changing, concurrency-heavy,
  or unfamiliar changes where an independent pass can find a different class of bug.
- A passing targeted check plus an inspected small diff is enough for a small change;
  do not add a reviewer solely because implementation occurred.
- Validate findings against the real code and threat model before applying them.

## 4. Integrate and document

- Preserve API and data compatibility unless the request authorizes a breaking change.
- Update documentation only where user-visible behavior, setup, contracts, or durable
  architecture changed.
- Keep docs proportional to the change. Do not regenerate unrelated summaries or write
  a journal by default.
- Follow a persistent plan when one exists, and update only the state affected by the
  work.

## 5. Diagnose and fix

- A diagnose, explain, or status request is read-only unless the user also asks for a
  change.
- A fix request includes diagnosis, implementation, and proportional verification; do
  not stop after the diagnosis to request redundant approval.
- Capture the failing behavior, identify the root cause, apply the narrowest complete
  fix, then rerun the check that reproduced it.
- If the same approach fails repeatedly, revisit the hypothesis instead of adding more
  verification passes.

## 6. Visual explanations

Use a visual only when it materially clarifies a multi-component relationship, flow, or
state change.

- `/ck:preview --explain <topic>` for a visual explanation
- `/ck:preview --diagram <topic>` for architecture or data flow
- `/ck:preview --slides <topic>` for a step-by-step walkthrough
- `/ck:preview --ascii <topic>` for terminal-only output
- Add `--html` for a self-contained HTML artifact

Save visuals under the active plan when one exists; otherwise use `plans/visuals/`.
