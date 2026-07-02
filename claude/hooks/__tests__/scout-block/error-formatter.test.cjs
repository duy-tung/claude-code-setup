/**
 * error-formatter.test.cjs - Unit tests for the scout-block error-formatter module
 *
 * Ported from scout-block/tests/test-error-formatter.cjs to node:test format.
 *
 * Run: node --test .claude/hooks/__tests__/scout-block/error-formatter.test.cjs
 */

const { describe, it } = require('node:test');
const assert = require('node:assert');

const {
  formatBlockedError,
  formatSimpleError,
  formatMachineError,
  formatWarning,
  formatConfigPath,
  colorize,
  COLORS
} = require('../../scout-block/error-formatter.cjs');

describe('formatConfigPath', () => {
  it('uses claudeDir when provided', () =>
    assert.ok(formatConfigPath('/home/user/.claude').includes('.ckignore')));
  it('prefers explicit configPath', () =>
    assert.strictEqual(formatConfigPath('/home/user/.claude', '/tmp/project/.ckignore'), '/tmp/project/.ckignore'));
  it('falls back without claudeDir', () =>
    assert.strictEqual(formatConfigPath(null), '.claude/.ckignore'));
  it('falls back on empty string', () =>
    assert.strictEqual(formatConfigPath(''), '.claude/.ckignore'));
});

describe('formatBlockedError', () => {
  const blockError = formatBlockedError({
    path: 'packages/web/node_modules/react',
    pattern: 'node_modules',
    tool: 'Bash',
    claudeDir: '/home/user/project/.claude',
    configPath: '/home/user/project/.ckignore'
  });

  it('contains BLOCKED', () => assert.ok(blockError.includes('BLOCKED')));
  it('contains the path', () => assert.ok(blockError.includes('packages/web/node_modules/react')));
  it('contains the pattern', () => assert.ok(blockError.includes('node_modules')));
  it('contains the tool', () => assert.ok(blockError.includes('Bash')));
  it('contains the fix hint', () => assert.ok(blockError.includes('!node_modules')));
  it('prefers the explicit config path', () => assert.ok(blockError.includes('/home/user/project/.ckignore')));

  it('truncates long paths', () => {
    const longPath = 'a/'.repeat(50) + 'node_modules/package/index.js';
    const longPathError = formatBlockedError({
      path: longPath,
      pattern: 'node_modules',
      tool: 'Read',
      claudeDir: '.claude'
    });
    assert.ok(longPathError.includes('...'));
  });
});

describe('formatSimpleError', () => {
  const simpleError = formatSimpleError('node_modules', 'packages/web/node_modules');
  it('contains ERROR', () => assert.ok(simpleError.includes('ERROR')));
  it('contains the pattern', () => assert.ok(simpleError.includes('node_modules')));
  it('contains the path', () => assert.ok(simpleError.includes('packages/web/node_modules')));
});

describe('formatMachineError', () => {
  const machineError = formatMachineError({
    path: 'dist/bundle.js',
    pattern: 'dist',
    tool: 'Read',
    claudeDir: '.claude',
    configPath: '/tmp/project/.ckignore'
  });
  const parsed = JSON.parse(machineError);

  it('is valid JSON', () => assert.strictEqual(typeof parsed, 'object'));
  it('has error field', () => assert.strictEqual(parsed.error, 'BLOCKED'));
  it('has path field', () => assert.strictEqual(parsed.path, 'dist/bundle.js'));
  it('has pattern field', () => assert.strictEqual(parsed.pattern, 'dist'));
  it('has tool field', () => assert.strictEqual(parsed.tool, 'Read'));
  it('has config field', () => assert.strictEqual(parsed.config, '/tmp/project/.ckignore'));
  it('has fix field', () => assert.ok(parsed.fix.includes('!dist')));
});

describe('formatWarning', () => {
  const warning = formatWarning('Test warning message');
  it('contains WARN', () => assert.ok(warning.includes('WARN')));
  it('contains the message', () => assert.ok(warning.includes('Test warning message')));
});

describe('colorize', () => {
  it('respects NO_COLOR', () => {
    const original = process.env.NO_COLOR;
    process.env.NO_COLOR = '1';
    try {
      assert.strictEqual(colorize('test', 'red'), 'test');
    } finally {
      if (original !== undefined) process.env.NO_COLOR = original;
      else delete process.env.NO_COLOR;
    }
  });

  it('COLORS constant has expected keys', () =>
    assert.ok('red' in COLORS && 'yellow' in COLORS && 'blue' in COLORS && 'reset' in COLORS));
});
