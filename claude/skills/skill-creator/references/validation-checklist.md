# Skill Validation Checklist

Quick validation before packaging. Run `scripts/package_skill.py` for automated checks.

## Critical (Must Pass)

### Metadata
- [ ] `name`: namespaced `namespace:skill-name` (or `skill-name` for legacy), descriptive
- [ ] `description`: under 200 characters, specific triggers, not generic

### Size Limits
- [ ] SKILL.md: under 300 lines
- [ ] Each reference file: under 300 lines
- [ ] No info duplication between SKILL.md and references

### Structure
- [ ] SKILL.md exists with valid YAML frontmatter
- [ ] Unused example files deleted
- [ ] File names: kebab-case, self-documenting

## Scripts (If Applicable)

- [ ] Tests exist and pass
- [ ] Cross-platform (Node.js/Python preferred)
- [ ] Env vars: respects hierarchy `process.env` > `$HOME/.claude/skills/${SKILL}/.env` (global) > `$HOME/.claude/skills/.env` (global) > `$HOME/.claude/.env` (global) > `./.claude/skills/${SKILL}/.env` (cwd) > `./.claude/skills/.env` (cwd) > `./.claude/.env` (cwd)
- [ ] Dependencies documented (requirements.txt, .env.example)
- [ ] Manually tested with real use cases

## Quality

### Writing Style
- [ ] Imperative form: "To accomplish X, do Y"
- [ ] Third-person metadata: "This skill should be used when..."
- [ ] Concise, no fluff

### Practical Utility
- [ ] Teaches *how* to do tasks, not *what* tools are
- [ ] Based on real workflows
- [ ] Includes concrete trigger phrases/examples

## Integration

- [ ] No duplication with existing skills
- [ ] Related topics consolidated (e.g., cloudflare + docker → devops)
- [ ] Composable with other skills

## Automated Validation

Run packaging script to validate:

```bash
scripts/package_skill.py <path/to/skill-folder>
```

Checks performed:
- YAML frontmatter format
- Required fields present
- Description length (<200 chars)
- Directory structure
- File organization

Fix all errors before distributing.

## Subagent Delegation Design

Make delegation conditional on an independent, parallelizable deliverable:

1. State the evidence or artifact the worker owns.
2. Set a small fan-out cap and partition scope to avoid duplicate work.
3. Require source paths, command output, or diffs in the worker report.
4. Provide an inline path when coordination would cost more than the task.
5. Do not add verifier agents solely to verify another agent's report.

**Anti-pattern (unconditional):**
```
- Always delegate every test run; direct testing is forbidden
```

**Correct pattern (calibrated):**
```
- For a broad independent test matrix, delegate one partition per worker (max 3)
  and require command output. For a targeted check, run it inline.
```
