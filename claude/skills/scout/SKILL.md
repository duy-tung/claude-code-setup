---
name: ck:scout
description: "Discover files, symbols, callers, tests, and codebase relationships. Use for focused orientation, dependency mapping, or bounded parallel scouting."
user-invocable: true
when_to_use: "Invoke for file discovery, codebase orientation, or dependency mapping before broader changes."
category: dev-tools
keywords: [codebase, scouting, file-discovery, search]
argument-hint: "[search-target] [ext]"
metadata:
  author: claudekit
  version: "1.0.0"
---

# Scout

Find the minimum code context needed for the task. Direct search is the default;
agents are reserved for genuinely independent broad discovery.

## Arguments

- Default: use targeted Glob/Grep/Read or `rg` directly.
- `ext`: use the external Gemini/OpenCode workflow in
  `references/external-scouting.md` for an explicitly broad search where it adds
  useful independent coverage.

## Scale Gate

- **Small/clear target:** search directly with exact symbols, filenames, extensions,
  or likely directories; read the matching implementation and nearest test/caller;
  return paths inline and stop.
- **Standard cross-directory target:** begin with direct search, then use one Explore
  worker only if a distinct dependency surface remains unclear.
- **Broad orientation, migration, or explicit codebase audit:** split only independent
  areas across workers. Keep ordinary concurrent fanout at three or less.

Do not create scout tasks, scan every directory, invoke project organization, or
write a report artifact for a small lookup.

## Direct Search Workflow

1. Extract concrete search targets from the request: symbol, behavior, config key,
   route, test name, or file type.
2. Start narrow and evidence-driven:

   ```bash
   rg -n "<symbol|route|config-key>" <likely-paths>
   rg --files <likely-paths> | rg "<name|extension>"
   ```

3. Read only enough matching code to identify ownership, direct callers, tests, and
   public contracts relevant to the task.
4. Broaden patterns or directories only when the first result leaves a material gap.
5. Return concise paths and why they matter. Include unresolved questions only when
   they affect the next decision.

## Conditional Parallel Workflow

Use parallel scouting only when there are two or more independent search domains
whose results can be integrated without overlap.

1. Define a bounded deliverable and directory/pattern ownership for each worker.
2. Choose the applicable reference:
   - `references/internal-scouting.md` for Explore workers.
   - `references/external-scouting.md` only when `ext` was requested or external
     search has a clear advantage.
3. Launch no more than three ordinary workers concurrently.
4. Register Claude Tasks only when coordinating two or more meaningful workers and
   the task tools are available. Otherwise track the scopes inline.
5. Integrate file-backed findings; do not forward duplicate worker summaries.

If workstreams overlap in the same directory or dependency chain, prefer one
controller or sequential searches rather than artificial parallelism.

## Evidence and Output

For a small scout, respond inline:

```markdown
- `path/to/file.ts:line` — owns the requested behavior
- `path/to/file.test.ts:line` — nearest regression test
```

For a broad requested audit, a reusable report may include relevant files,
relationships, search coverage, and material unknowns. Create that artifact only when
the user/plan needs it; project organization is not a finalize prerequisite.

Distinguish verified paths/symbols from inferred relationships. Do not invent numeric
confidence.

## References

- `references/internal-scouting.md` - Explore worker patterns for broad independent scopes
- `references/external-scouting.md` - Gemini/OpenCode workflow for explicit `ext` searches
- `references/task-management-scouting.md` - Task coordination for multi-worker scouting

## Workflow Position

**Typically precedes:** `/ck:debug`, `/ck:fix`, or a broad `/ck:code-review` when
dependency discovery is actually needed.

**Related:** `/ck:brainstorm` for design exploration.
