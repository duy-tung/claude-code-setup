# Team Coordination Rules

These rules apply only while operating as a named teammate in an Agent Team.

## Runtime Contract

- The team is implicit and session-scoped; start from the assigned task without a setup step.
- All teammates share the current checkout and can see each other's file changes immediately.
- Models may differ by teammate. Use the model selected by the lead or agent definition.
- Effort inherits from the lead by default.
- Claude Code owns session-team resource cleanup after teammates shut down.

## File Ownership (Critical)

- Edit only the files or directories explicitly assigned to this task.
- Read-only overlap is allowed; writable overlap is not.
- Treat manifests, schemas, generated indexes, and lockfiles as shared files owned by one integrator unless the task says otherwise.
- If an unassigned file must change, stop before editing and message the lead.
- If another teammate changed an owned file unexpectedly, stop and resolve ownership with the lead.
- A tester may edit only its assigned test paths; reading implementation files does not grant write ownership.

## Version-Control Safety

- Never assume private filesystem or version-control state.
- Do not discard, overwrite, stage, or commit another teammate's changes.
- Do not use broad staging commands when concurrent edits are present.
- Commit or push only when the task or lead explicitly assigns that responsibility.
- Never force-push or rewrite shared history.

## Communication

- Address teammates by stable name, not runtime ID.
- Send one direct message per intended recipient.
- Include evidence, affected files, and the requested action; avoid status-only messages.
- Mark the shared task completed before sending the final completion message.
- Inbound messages arrive automatically; do not poll an inbox or task list on a fixed timer.

## Task Claiming

- Set a claimed task to `in_progress` before work begins.
- Claim only unassigned, unblocked work that matches your role and does not overlap active file ownership.
- After completion, inspect the shared task list only when deciding whether another eligible task exists.
- If all work is blocked, message the relevant owner directly, then escalate to the lead if needed.

## Plan Approval

When plan approval is required:

1. Research and plan without editing files.
2. Submit the plan with concrete file ownership, risks, and verification.
3. Wait for the lead's approval response.
4. Revise from specific feedback if rejected.
5. Begin edits only after approval.

## Reports and Documentation

- Save requested reports to `{CK_REPORTS_PATH}`; fallback: `plans/reports/`.
- Use `{type}-{date}-{slug}.md` naming unless the task supplies another path.
- Keep findings concise and list unresolved questions.
- For implementation, state `Docs impact: none|minor|major` and explain any required follow-up.

## Completion and Shutdown

- Report changed files, verification performed, result, and unresolved risks.
- Do not treat idle state as completion; task state is authoritative.
- Approve a shutdown request unless a critical operation must finish first.
- If shutdown must wait, explain the active operation concisely.
- Do not delete runtime team or task state manually.
