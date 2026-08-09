---
name: ck:journal
description: "Write technical journal entries analyzing recent changes. Use for session reflections, change analysis, decision documentation."
user-invocable: true
when_to_use: "Invoke for technical session reflection or decision records."
category: utilities
keywords: [journal, reflection, changes, session]
argument-hint: "[topic or reflection]"
metadata:
  author: claudekit
  version: "1.1.0"
---

# Journal

Write journal entries covering the most important events, key changes, impacts, and decisions.
Keep journal entries in the `./docs/journals/` directory, and keep them concise.

Write them inline when the session already holds the relevant context — that is the common case, and it costs less than briefing a worker on work you just did. Delegate to the `journal-writer` subagent when the entry needs history you do not have loaded: a long back-catalog of prior entries, or a wide sweep of changes across sessions you were not part of.

## Entry Format (memory quality)

- Lead each entry with a one-line summary so future sessions can skim entries without reading them fully.
- Record corrections (what went wrong and the fix) AND approaches confirmed to work — both are memory.
- Before appending, check existing entries on the same topic: update or consolidate instead of duplicating.
- Delete or amend notes proven wrong; a stale lesson is worse than none.

Invoke `/ck:project-organization` when the entry lands outside `./docs/journals/` or the journal directory has drifted out of shape — not as a routine follow-up to every entry.

## Workflow Position

**Typically follows:** `/ck:ship` (journal after shipping), `/ck:cook` (journal after implementation), `/ck:fix` (journal after bug fix)
**Terminal skill** — no typical successor.
