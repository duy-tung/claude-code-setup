# CLAUDE.md

This file provides Claude Code guidance for ClaudeKit Engineer. The CK CLI installs it with the rest of the AI-facing rules under `.claude/rules/`.

## Role & Responsibilities

Your role is to deliver the requested outcome at the requested scope while following the repository's architecture, safety boundaries, and acceptance criteria.

**Model behavior is defined once, in `./.claude/rules/model-calibration.md`** — scope, delegation, verification, evidence, output length, progress updates, and self-correction. Follow it; other rules and skills point at it rather than restating it.

## Rules

- Model calibration (normative): `./.claude/rules/model-calibration.md`
- Development rules: `./.claude/rules/development-rules.md`
- Orchestration protocols: `./.claude/rules/orchestration-protocol.md`
- Documentation management: `./.claude/rules/documentation-management.md`
- And other rules: `./.claude/rules/*`

**IMPORTANT:** Activate only skills that clearly match the task. A small scoped edit may need no skill; do not load the catalog or a specialist workflow as ceremony.
**IMPORTANT:** DO NOT modify skills in `~/.claude/skills` directory directly. **MUST** modify skills in this current working directory. Unless you are asked to do so.
**IMPORTANT:** Before substantial implementation, read the repository entrypoint (`./README.md` or the more specific governing document) once. Small scoped edits need only their directly relevant context.

## Git

**DO NOT** use `chore` and `docs` in commit messages of file changes in `.claude` directory.

## Hook Response Protocol

### Privacy Block Hook (`@@PRIVACY_PROMPT@@`)

When a tool call is blocked by the privacy-block hook, the output contains a JSON marker between `@@PRIVACY_PROMPT_START@@` and `@@PRIVACY_PROMPT_END@@`. **You MUST use the `AskUserQuestion` tool** to get proper user approval.

**Required Flow:**

1. Parse the JSON from the hook output
2. Use `AskUserQuestion` with the question data from the JSON
3. Based on user's selection:
   - **"Yes, approve access"** → Use `bash cat "filepath"` to read the file (bash is auto-approved)
   - **"No, skip this file"** → Continue without accessing the file

**IMPORTANT:** Always ask the user via `AskUserQuestion` first. Never try to work around the privacy block without explicit user approval.

## Python Scripts (Skills)

When running Python scripts from `.claude/skills/`, use the venv Python interpreter:
- **Linux/macOS:** `.claude/skills/.venv/bin/python3 scripts/xxx.py`
- **Windows:** `.claude\skills\.venv\Scripts\python.exe scripts\xxx.py`

This ensures packages installed by `install.sh` (pypdf, Pillow, openpyxl, etc.) are available.

**IMPORTANT:** If a skill script fails, diagnose it. Fix it only when that repair is inside the requested scope; otherwise report the actionable blocker and fallback.

## Documentation Management

Keep durable project documentation in `./docs`. Update only the files whose public behavior, setup, contract, or architecture changed; do not regenerate the full set for an unrelated small edit. Details: `./.claude/rules/documentation-management.md`.
