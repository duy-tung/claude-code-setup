# Skills Installation Guide

This guide explains how to install dependencies for Claude Code skills.

## Overview

Most skills in this kit are pure instructions (markdown) or use only the Python/Node standard library and need no installation. External dependencies are concentrated in a few skills:

| Skill(s) | Dependency | Kind |
|----------|------------|------|
| document-skills (docx, pdf, pptx, xlsx) | `document-skills/requirements.txt` (pypdf, Pillow, openpyxl, python-pptx, defusedxml, lxml, pdf2image, markitdown, pandas, reportlab, ...) | Python (venv) |
| pdf | Poppler (`pdftoppm`) | System |
| tech-graph | librsvg (`rsvg-convert`) for PNG export | System |
| repomix | `repomix` CLI | npm (global) |
| sequential-thinking, plans-kanban | local `npm install` (dev/test only) | npm (local) |
| repo tooling (`scan_skills.py` etc.) | `../scripts/requirements.txt` (pyyaml) | Python (venv) |

Some document-skills workflows use additional heavyweight tools that are NOT auto-installed — LibreOffice (PDF conversion, xlsx formula recalculation), pandoc (docx text extraction), and node packages like pptxgenjs/playwright for html2pptx. Each skill's `SKILL.md` Dependencies section is the source of truth; install those only if you use the corresponding workflow.

## Automated Installation (Recommended)

### Linux/macOS

```bash
cd .claude/skills
chmod +x install.sh
./install.sh            # add --with-sudo to allow system package installs
```

The script will:
- Detect your OS and package manager (apt/dnf/pacman/apk/brew)
- Install system dependencies (librsvg, Poppler)
- Install Node.js (if missing) and global packages (pnpm, repomix)
- Create a Python virtual environment at `.claude/skills/.venv`
- Install Python packages for document-skills and any skill with a `scripts/requirements.txt`
- Verify all installations and print a remediation report for anything skipped

### Windows (PowerShell)

Run as Administrator:

```powershell
cd .claude\skills
Set-ExecutionPolicy Bypass -Scope Process -Force
.\install.ps1
```

Options:
```powershell
# Skip Chocolatey installation if already installed
.\install.ps1 -SkipChocolatey

# Show help
.\install.ps1 -Help
```

### What Gets Installed

**System tools:**
- librsvg / `rsvg-convert` (tech-graph PNG export)
- Poppler / `pdftoppm` (pdf skill image rendering)

**Node.js packages (global):**
- pnpm (package manager)
- repomix (repository packaging)

**Python packages (in `.claude/skills/.venv`):**
- document-skills set: pypdf, Pillow, openpyxl, python-pptx, defusedxml, lxml, pdf2image, six, markitdown, pandas, reportlab
- pyyaml (repo tooling)
- pytest, pytest-cov, pytest-mock (test dependencies, where a skill declares them)

## Manual Installation

If you prefer manual installation or the automated script fails:

### Python environment

```bash
# Create virtual environment
python3 -m venv .claude/skills/.venv
source .claude/skills/.venv/bin/activate  # Windows: .claude\skills\.venv\Scripts\activate

# Document skills (docx, pdf, pptx, xlsx)
pip install -r .claude/skills/document-skills/requirements.txt

# Repo tooling (scan_skills.py, validators)
pip install -r .claude/scripts/requirements.txt
```

### System tools

```bash
# Ubuntu/Debian
sudo apt-get install -y librsvg2-bin poppler-utils

# Fedora/RHEL
sudo dnf install -y librsvg2-tools poppler-utils

# Arch
sudo pacman -S librsvg poppler

# Alpine
apk add librsvg poppler-utils

# macOS
brew install librsvg poppler
```

```powershell
# Windows
winget install oschwartz10612.Poppler
choco install rsvg-convert -y    # librsvg is not on winget/scoop
```

### Node.js tools

```bash
npm install -g pnpm repomix
```

## Running Python Skill Scripts

Always use the venv interpreter so installed packages are found:

- **Linux/macOS:** `.claude/skills/.venv/bin/python3 <script>.py`
- **Windows:** `.claude\skills\.venv\Scripts\python.exe <script>.py`

## Environment Variables

Skills that need configuration ship an `.env.example` next to their code (e.g. `.claude/.env.example`, `.claude/skills/.env.example`). Copy the template to the same location without the `.example` suffix and fill in values.

## Troubleshooting

### "externally-managed-environment" Error

If you see this error when installing packages:

```bash
# Use virtual environment (recommended)
python3 -m venv .claude/skills/.venv
source .claude/skills/.venv/bin/activate
pip install -r .claude/skills/document-skills/requirements.txt
```

### Missing System Tools

If scripts fail with "command not found":

```bash
# Check if tool is installed
which rsvg-convert
which pdftoppm
which node

# Verify tool works
rsvg-convert --version
pdftoppm -v
node --version
```

### Pillow/lxml Build Failures

Prebuilt wheels cover most platforms. If pip falls back to building from source, install build tools first:

```bash
# Ubuntu/Debian
sudo apt-get install -y gcc python3-dev libjpeg-dev zlib1g-dev

# macOS
xcode-select --install
```

### Permission Errors

On Linux/macOS, you may need to make scripts executable:

```bash
chmod +x .claude/skills/install.sh
```

## Getting Help

If dependencies fail to install or scripts don't work:

1. Check the relevant `requirements.txt` for specific versions
2. Verify system tools are installed and in PATH
3. Review the skill's `SKILL.md` Dependencies section for additional setup
4. Open an issue: https://github.com/duy-tung/claude-code-setup/issues
