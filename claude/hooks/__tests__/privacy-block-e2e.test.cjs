/**
 * privacy-block-e2e.test.cjs - End-to-end tests for the privacy-block hook
 *
 * Spawns the real hook with tool-input JSON on stdin and asserts on the exit
 * code (0 = allowed, 2 = blocked). Complements the unit coverage in
 * privacy-block.test.cjs. Ported from hooks/tests/test-privacy-block.cjs.
 *
 * Run: node --test .claude/hooks/__tests__/privacy-block-e2e.test.cjs
 */

const { describe, it, before, after } = require('node:test');
const assert = require('node:assert');
const { spawnSync } = require('child_process');
const path = require('path');
const fs = require('fs');
const os = require('os');

const HOOK_PATH = path.join(__dirname, '..', 'privacy-block.cjs');

function runHook(input, cwd) {
  const result = spawnSync('node', [HOOK_PATH], {
    input: JSON.stringify(input),
    encoding: 'utf-8',
    ...(cwd ? { cwd } : {})
  });
  return { blocked: result.status === 2, stderr: result.stderr || '' };
}

describe('privacy-block blocks sensitive paths', () => {
  const cases = [
    { name: '.env file', input: { tool_input: { file_path: '.env' } }, contains: 'PRIVACY BLOCK' },
    { name: '.env.local', input: { tool_input: { file_path: '.env.local' } }, contains: 'PRIVACY_PROMPT' },
    { name: 'credentials.json', input: { tool_input: { file_path: 'config/credentials.json' } } },
    { name: 'id_rsa', input: { tool_input: { file_path: '~/.ssh/id_rsa' } } },
    { name: '.env in bash command', input: { tool_input: { command: 'cat .env' } } },
    { name: 'secrets.yaml', input: { tool_input: { file_path: 'secrets.yaml' } } },
    { name: 'private.key', input: { tool_input: { file_path: 'certs/private.key' } } },
    { name: 'URL-encoded .env (%2eenv)', input: { tool_input: { file_path: '%2eenv' } } },
    { name: 'bash variable FILE=.env', input: { tool_input: { command: 'FILE=.env cat $FILE' } } },
    { name: 'command substitution $(cat .env)', input: { tool_input: { command: 'echo $(cat .env)' } } }
  ];

  for (const c of cases) {
    it(`blocks ${c.name}`, () => {
      const result = runHook(c.input);
      assert.ok(result.blocked, `expected block for ${c.name}`);
      if (c.contains) {
        assert.ok(result.stderr.includes(c.contains), `stderr should mention ${c.contains}`);
      }
    });
  }
});

describe('privacy-block allows APPROVED: prefix', () => {
  const cases = [
    { name: 'APPROVED:.env', input: { tool_input: { file_path: 'APPROVED:.env' } }, contains: 'User-approved' },
    { name: 'APPROVED:.env.local', input: { tool_input: { file_path: 'APPROVED:.env.local' } } },
    { name: 'APPROVED:credentials.json', input: { tool_input: { file_path: 'APPROVED:config/credentials.json' } } },
    { name: 'APPROVED in bash command', input: { tool_input: { command: 'cat APPROVED:.env' } } }
  ];

  for (const c of cases) {
    it(`allows ${c.name}`, () => {
      const result = runHook(c.input);
      assert.ok(!result.blocked, `expected allow for ${c.name}`);
      if (c.contains) {
        assert.ok(result.stderr.includes(c.contains), `stderr should mention ${c.contains}`);
      }
    });
  }
});

describe('privacy-block allows safe files', () => {
  const cases = [
    { name: 'regular source file', input: { tool_input: { file_path: 'src/index.ts' } } },
    { name: 'package.json', input: { tool_input: { file_path: 'package.json' } } },
    { name: 'README.md', input: { tool_input: { file_path: 'README.md' } } }
  ];

  for (const c of cases) {
    it(`allows ${c.name}`, () => assert.ok(!runHook(c.input).blocked));
  }
});

describe('privacy-block exempts example/sample/template files', () => {
  const cases = [
    { name: '.env.example', input: { tool_input: { file_path: '.env.example' } } },
    { name: '.env.local.example', input: { tool_input: { file_path: '.env.local.example' } } },
    { name: '.env.sample', input: { tool_input: { file_path: '.env.sample' } } },
    { name: '.env.template', input: { tool_input: { file_path: '.env.template' } } },
    { name: 'config/.env.example', input: { tool_input: { file_path: 'config/.env.example' } } },
    { name: 'credentials.example', input: { tool_input: { file_path: 'credentials.example' } } },
    { name: 'cat .env.example in bash', input: { tool_input: { command: 'cat .env.example' } } }
  ];

  for (const c of cases) {
    it(`allows ${c.name}`, () => assert.ok(!runHook(c.input).blocked));
  }
});

describe('privacy-block honors the privacyBlock config toggle', () => {
  let tmpDir;
  let tmpClaudeDir;

  before(() => {
    tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), 'privacy-e2e-'));
    tmpClaudeDir = path.join(tmpDir, '.claude');
    fs.mkdirSync(tmpClaudeDir, { recursive: true });
  });

  after(() => {
    fs.rmSync(tmpDir, { recursive: true, force: true });
  });

  const cases = [
    { name: 'privacyBlock: false allows .env', config: { privacyBlock: false }, input: { tool_input: { file_path: '.env' } }, expectBlock: false },
    { name: 'privacyBlock: false allows credentials.json', config: { privacyBlock: false }, input: { tool_input: { file_path: 'credentials.json' } }, expectBlock: false },
    { name: 'privacyBlock: true blocks .env', config: { privacyBlock: true }, input: { tool_input: { file_path: '.env' } }, expectBlock: true }
  ];

  for (const c of cases) {
    it(c.name, () => {
      fs.writeFileSync(path.join(tmpClaudeDir, '.ck.json'), JSON.stringify(c.config));
      const result = runHook(c.input, tmpDir);
      assert.strictEqual(result.blocked, c.expectBlock);
    });
  }
});
