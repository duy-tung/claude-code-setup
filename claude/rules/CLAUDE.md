# CLAUDE.md

This file provides Claude Code guidance for ClaudeKit Engineer. The CK CLI installs it with the rest of the AI-facing rules under `.claude/rules/`.

## Role & Responsibilities

Your role is to deliver the requested outcome at the requested scope while following the repository's architecture, safety boundaries, and acceptance criteria.

Delegation is a tool, not the default. Spawn a sub-agent when the work is genuinely independent and parallelizable; do work you can finish in a handful of tool calls yourself. See `./.claude/rules/opus-5-calibration.md` §3.

## Workflows

- Primary workflow: `./.claude/rules/primary-workflow.md`
- Development rules: `./.claude/rules/development-rules.md`
- Orchestration protocols: `./.claude/rules/orchestration-protocol.md`
- Documentation management: `./.claude/rules/documentation-management.md`
- Model calibration (Opus 5): `./.claude/rules/opus-5-calibration.md`
- And other workflows: `./.claude/rules/*`

**IMPORTANT:** Activate only skills that clearly match the task. A small scoped edit
may need no skill; do not load the catalog or a specialist workflow as ceremony.
**IMPORTANT:** DO NOT modify skills in `~/.claude/skills` directory directly. **MUST** modify skills in this current working directory. Unless you are asked to do so.
**IMPORTANT:** You must follow strictly the development rules in `./.claude/rules/development-rules.md` file.
**IMPORTANT:** Before substantial implementation, read the repository entrypoint (`./README.md` or the more specific governing document) once. Small scoped edits need only their directly relevant context.
**IMPORTANT:** Keep reports concise without sacrificing clarity or grammar.
**IMPORTANT:** In reports, list any unresolved questions at the end, if any.

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

**Example AskUserQuestion call:**
```json
{
  "questions": [{
    "question": "I need to read \".env\" which may contain sensitive data. Do you approve?",
    "header": "File Access",
    "options": [
      { "label": "Yes, approve access", "description": "Allow reading .env this time" },
      { "label": "No, skip this file", "description": "Continue without accessing this file" }
    ],
    "multiSelect": false
  }]
}
```

**IMPORTANT:** Always ask the user via `AskUserQuestion` first. Never try to work around the privacy block without explicit user approval.

## Python Scripts (Skills)

When running Python scripts from `.claude/skills/`, use the venv Python interpreter:
- **Linux/macOS:** `.claude/skills/.venv/bin/python3 scripts/xxx.py`
- **Windows:** `.claude\skills\.venv\Scripts\python.exe scripts\xxx.py`

This ensures packages installed by `install.sh` (pypdf, Pillow, openpyxl, etc.) are available.

**IMPORTANT:** If a skill script fails, diagnose it. Fix it only when that repair is
inside the requested scope; otherwise report the actionable blocker and fallback.

## [IMPORTANT] Consider Modularization
- If a code file exceeds 200 lines of code, consider modularizing it
- Check existing modules before creating new
- Analyze logical separation boundaries (functions, classes, concerns)
- Use kebab-case naming with long descriptive names, it's fine if the file name is long because this ensures file names are self-documenting for LLM tools (Grep, Glob, Search)
- Write descriptive code comments
- After modularization, continue with main task
- When not to modularize: Markdown files, plain text files, bash scripts, configuration files, environment variables files, etc.

## Documentation Management

Keep durable project documentation in `./docs`. Update only the files whose public
behavior, setup, contract, or architecture changed; do not regenerate the full set for
an unrelated small edit. A typical structure is:

```
./docs
├── project-overview-pdr.md
├── code-standards.md
├── codebase-summary.md
├── design-guidelines.md
├── deployment-guide.md
├── system-architecture.md
└── project-roadmap.md
```

Follow the instructions in `.claude/rules/CLAUDE.md` and the workflow files it links (see Workflows above) — they are the operating contract for this kit.
