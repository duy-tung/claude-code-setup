# Claude Code Scripts

Maintainer utility scripts for the kit's skill catalog and validation gates.
These are **not** shipped to end users — they support contributors working in this repo.

## Installation

```bash
pip install -r requirements.txt   # pyyaml (used by the skill scanners)
```

## Scripts

| Script | Purpose |
|--------|---------|
| `scan_skills.py` | Scan `claude/skills/` and regenerate the checked-in catalogs (`guide/SKILLS.md`, `guide/SKILLS.yaml`). Run after any `SKILL.md` description change. |
| `score-skill-description.py` | Score `SKILL.md` descriptions on 5 structural-format criteria and flag confusable pairs / dependency cycles. Invoked by `scan_skills.py`. |
| `validate-skill-crossrefs.py` | Build the skill registry from frontmatter and audit every `/ck:` reference for broken refs, orphans, hubs, and workflow-chain gaps. |
| `validate-skill-frontmatter.py` | Validate every `SKILL.md` frontmatter against `claude/schemas/skill-schema.json` (requires `user-invocable: true`). |
| `win_compat.py` | Windows UTF-8 console helper. Import early in scripts that print Unicode. |

Run `npm run verify` (implemented by repository-root `init.sh`) for the combined
validator, harness-integrity, hook, statusline, and worktree gate.
