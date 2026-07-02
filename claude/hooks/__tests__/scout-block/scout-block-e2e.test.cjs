/**
 * scout-block-e2e.test.cjs - End-to-end tests for the scout-block hook
 *
 * Spawns the real hook with tool-input JSON on stdin and asserts on the
 * exit code (0 = allowed, 2 = blocked). Ported from
 * scout-block/tests/test-monorepo-scenarios.cjs and hooks/tests/test-scout-block.cjs.
 *
 * Run: node --test .claude/hooks/__tests__/scout-block/scout-block-e2e.test.cjs
 */

const { describe, it } = require('node:test');
const assert = require('node:assert');
const { spawnSync } = require('child_process');
const path = require('path');

const HOOK_PATH = path.join(__dirname, '..', '..', 'scout-block.cjs');

function runHook(input) {
  const result = spawnSync('node', [HOOK_PATH], {
    input: JSON.stringify(input),
    encoding: 'utf-8'
  });
  return result.status === 2 ? 'BLOCKED' : result.status === 0 ? 'ALLOWED' : `ERROR(${result.status})`;
}

const SCENARIOS = [
  // Subfolder blocked directories in monorepo structures (regression: subfolder bug)
  { input: { tool_name: 'Bash', tool_input: { command: 'ls packages/web/node_modules' } }, expected: 'BLOCKED', desc: 'ls subfolder node_modules' },
  { input: { tool_name: 'Bash', tool_input: { command: 'cd apps/api/node_modules' } }, expected: 'BLOCKED', desc: 'cd subfolder node_modules' },
  { input: { tool_name: 'Bash', tool_input: { command: 'cat packages/shared/node_modules/lodash/index.js' } }, expected: 'BLOCKED', desc: 'cat file in subfolder node_modules' },
  { input: { tool_name: 'Read', tool_input: { file_path: 'packages/web/node_modules/react/package.json' } }, expected: 'BLOCKED', desc: 'Read subfolder node_modules' },
  { input: { tool_name: 'Grep', tool_input: { pattern: 'export', path: 'packages/web/node_modules' } }, expected: 'BLOCKED', desc: 'Grep in subfolder node_modules' },
  { input: { tool_name: 'Glob', tool_input: { pattern: 'packages/web/node_modules/**/*.js' } }, expected: 'BLOCKED', desc: 'Glob subfolder node_modules' },
  { input: { tool_name: 'Read', tool_input: { file_path: 'a/b/c/d/node_modules/pkg/index.js' } }, expected: 'BLOCKED', desc: 'deep nested node_modules' },
  { input: { tool_name: 'Bash', tool_input: { command: 'ls packages/web/dist' } }, expected: 'BLOCKED', desc: 'ls subfolder dist' },
  { input: { tool_name: 'Bash', tool_input: { command: 'cat apps/api/build/server.js' } }, expected: 'BLOCKED', desc: 'cat subfolder build' },

  // Root-level blocking
  { input: { tool_name: 'Bash', tool_input: { command: 'ls node_modules' } }, expected: 'BLOCKED', desc: 'ls root node_modules' },
  { input: { tool_name: 'Read', tool_input: { file_path: 'node_modules/lodash/index.js' } }, expected: 'BLOCKED', desc: 'Read root node_modules' },
  { input: { tool_name: 'Bash', tool_input: { command: 'cat .git/config' } }, expected: 'BLOCKED', desc: 'cat .git file' },
  { input: { tool_name: 'Bash', tool_input: { command: 'cat dist/bundle.js' } }, expected: 'BLOCKED', desc: 'cat dist file' },
  { input: { tool_name: 'Glob', tool_input: { pattern: '**/node_modules/**' } }, expected: 'BLOCKED', desc: 'Glob node_modules pattern' },

  // Build commands bypass path blocking
  { input: { tool_name: 'Bash', tool_input: { command: 'npm run build' } }, expected: 'ALLOWED', desc: 'npm run build' },
  { input: { tool_name: 'Bash', tool_input: { command: 'pnpm build' } }, expected: 'ALLOWED', desc: 'pnpm build' },
  { input: { tool_name: 'Bash', tool_input: { command: 'yarn build' } }, expected: 'ALLOWED', desc: 'yarn build' },
  { input: { tool_name: 'Bash', tool_input: { command: 'npm test' } }, expected: 'ALLOWED', desc: 'npm test' },
  { input: { tool_name: 'Bash', tool_input: { command: 'npm install' } }, expected: 'ALLOWED', desc: 'npm install' },
  { input: { tool_name: 'Bash', tool_input: { command: 'pnpm --filter web run build' } }, expected: 'ALLOWED', desc: 'pnpm filter build' },
  { input: { tool_name: 'Bash', tool_input: { command: 'npx tsc' } }, expected: 'ALLOWED', desc: 'npx tsc' },
  { input: { tool_name: 'Bash', tool_input: { command: 'jest --coverage' } }, expected: 'ALLOWED', desc: 'jest with flags' },

  // Safe operations
  { input: { tool_name: 'Read', tool_input: { file_path: 'packages/web/src/App.tsx' } }, expected: 'ALLOWED', desc: 'Read safe path' },
  { input: { tool_name: 'Bash', tool_input: { command: 'ls packages/web/src' } }, expected: 'ALLOWED', desc: 'ls safe path' },
  { input: { tool_name: 'Grep', tool_input: { pattern: 'import', path: 'src' } }, expected: 'ALLOWED', desc: 'Grep in src' },
  // '**/*.ts' with no directory anchor is rejected by the broad-pattern detector
  { input: { tool_name: 'Glob', tool_input: { pattern: '**/*.ts' } }, expected: 'BLOCKED', desc: 'Glob unanchored **/*.ts (broad pattern)' },
  { input: { tool_name: 'Glob', tool_input: { pattern: 'src/**/*.ts' } }, expected: 'ALLOWED', desc: 'Glob anchored src/**/*.ts' },
  { input: { tool_name: 'Bash', tool_input: { command: 'find packages -name "*.json" | head' } }, expected: 'ALLOWED', desc: 'find without blocked dirs' },

  // Names containing blocked words but NOT the dirs
  { input: { tool_name: 'Read', tool_input: { file_path: 'my-node_modules-project/file.js' } }, expected: 'ALLOWED', desc: 'node_modules in project name' },
  { input: { tool_name: 'Bash', tool_input: { command: 'ls build-tools' } }, expected: 'ALLOWED', desc: 'build- prefix directory' }
];

describe('scout-block hook end-to-end', () => {
  for (const scenario of SCENARIOS) {
    it(`${scenario.desc} -> ${scenario.expected}`, () => {
      assert.strictEqual(runHook(scenario.input), scenario.expected);
    });
  }
});
