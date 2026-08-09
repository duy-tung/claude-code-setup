#!/usr/bin/env bash
# Single verification entrypoint for the kit harness (fail-fast).
# Runs the local quality gates in order: static validators (Tier 0), harness
# integrity checks, and the test suites. Wrapped by `npm run verify`.
set -euo pipefail
cd "$(dirname "$0")"

echo "[verify] Tier 0 — static validators"
python3 eval/tier0_static.py

echo
echo "[verify] harness self-audit (advisory)"
python3 eval/audit_harness.py || true

echo
echo "[verify] eval oracle/no-op integrity"
python3 eval/run.py --all --mock --runs 1 \
  --out eval/results/verify-mock.ndjson
python3 eval/run.py --all --mock-noop --runs 1 \
  --out eval/results/verify-mock-noop.ndjson

echo
echo "[verify] Node test suite"
npm test --silent

echo
echo "[verify] statusline and worktree suites"
npm run test:statusline --silent
npm run test:worktree --silent

echo
echo "[verify] Opus 5 thinking continuation"
python3 -B -m unittest discover \
  -s claude/skills/skill-creator/scripts/tests -p 'test_*.py'

echo
echo "[verify] Opus 5 context defaults"
python3 -B -m unittest discover \
  -s claude/skills/context-engineering/scripts/tests \
  -p 'test_opus5_context_defaults.py'

echo
echo "[verify] OK"
