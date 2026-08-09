# Update Workflow

## Phase 0: Scale Gate

For an explicit one-file or narrowly scoped documentation change, read that target
and the source files that substantiate it, edit inline, run one targeted link/reference
check, and finish. Do not count or read the entire docs tree, spawn readers, regenerate
summaries, or invoke a docs-manager solely because the change is documentation.

Use the broader phases below only for repo-wide documentation sync, an unfamiliar
multi-document contract change, or an explicitly requested full update.

## Phase 1: Parallel Codebase Scouting

1. Scan the codebase and calculate the number of files with LOC in each directory (skip `.claude`, `.opencode`, `.git`, `tests`, `node_modules`, `__pycache__`, `secrets`, etc.)
2. Target directories **that actually exist** - adapt to project structure
3. Activate `ck:scout` skill to explore the code base and return detailed summary reports
4. Merge scout reports into context summary

## Phase 1.5: Parallel Documentation Reading

1. Count docs: `ls docs/*.md 2>/dev/null | wc -l`
2. Get LOC: `wc -l docs/*.md 2>/dev/null | sort -rn`
3. Strategy:
   - 1-3 files: Read directly
   - 4-6 files: Read directly unless independent partitions justify 2 workers
   - 7+ files: Use at most 3 focused readers when parallelism saves time
4. Distribute files by LOC (larger files get dedicated agent)
5. Each agent prompt: "Read these docs, extract: purpose, key sections, areas needing update. Files: {list}"
6. Merge results into context for docs-manager

## Phase 2: Documentation Update

Use `docs-manager` for a broad, independently owned documentation pass. Update a
small, tightly scoped set inline. In either case, pass source paths and fresh
code/tool evidence; do not add a second agent solely to verify the first.

Pass the gathered context to docs-manager agent to update documentation:
- `README.md`: Update README (keep it under 300 lines)
- `docs/project-overview-pdr.md`: Update project overview and PDR
- `docs/codebase-summary.md`: Update codebase summary
- `docs/code-standards.md`: Update codebase structure and code standards
- `docs/system-architecture.md`: Update system architecture
- `docs/project-roadmap.md`: Update project roadmap
- `docs/deployment-guide.md` [optional]: Update deployment guide
- `docs/design-guidelines.md` [optional]: Update design guidelines

## Additional requests
<additional_requests>
  $ARGUMENTS
</additional_requests>

## Phase 3: Size Check (Post-Update)

After docs-manager completes:
1. Run `wc -l docs/*.md 2>/dev/null | sort -rn` to check LOC
2. Use `docs.maxLoc` from session context (default: 800)
3. For files exceeding limit: report and ask user

## Phase 4: Documentation Validation (Post-Update)

Run validation to detect potential hallucinations:
1. Run: `node .claude/scripts/validate-docs.cjs docs/`
2. Display validation report (warnings only, non-blocking)
3. Checks: code references, internal links, config keys

## Important
- Use `docs/` directory as the source of truth.
- **Do not** start implementing.
