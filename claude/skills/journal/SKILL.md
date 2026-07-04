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

Use the `journal-writer` subagent to explore the memories and recent code changes, and write some journal entries.
Journal entries should be concise and focused on the most important events, key changes, impacts, and decisions.
Keep journal entries in the `./docs/journals/` directory.

## Entry Format (memory quality)

- Lead each entry with a one-line summary so future sessions can skim entries without reading them fully.
- Record corrections (what went wrong and the fix) AND approaches confirmed to work — both are memory.
- Before appending, check existing entries on the same topic: update or consolidate instead of duplicating.
- Delete or amend notes proven wrong; a stale lesson is worse than none.

**IMPORTANT:** Invoke "/ck:project-organization" skill to organize the outputs.

## Workflow Position

**Typically follows:** `/ck:ship` (journal after shipping), `/ck:cook` (journal after implementation), `/ck:fix` (journal after bug fix)
**Terminal skill** — no typical successor.
