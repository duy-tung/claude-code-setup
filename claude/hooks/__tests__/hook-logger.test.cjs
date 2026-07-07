#!/usr/bin/env node

const { beforeEach, describe, it } = require('node:test');
const assert = require('node:assert');
const fs = require('fs');
const os = require('os');
const path = require('path');

// Isolate the log in a temp dir: other test files spawn hooks that append to
// the shared .logs/ file, which raced with this file's assertions.
process.env.CK_HOOK_LOG_DIR = fs.mkdtempSync(path.join(os.tmpdir(), 'hook-logger-test-'));
const LOG_FILE = path.join(process.env.CK_HOOK_LOG_DIR, 'hook-log.jsonl');
const { createHookTimer, logHook, logHookCrash } = require('../lib/hook-logger.cjs');

function readEntries() {
  if (!fs.existsSync(LOG_FILE)) return [];
  return fs.readFileSync(LOG_FILE, 'utf8')
    .split('\n')
    .filter(Boolean)
    .map(line => JSON.parse(line));
}

beforeEach(() => {
  fs.writeFileSync(LOG_FILE, '', 'utf8');
});

describe('hook-logger', () => {
  it('writes structured hook fields', () => {
    logHook('privacy-block', {
      event: 'PreToolUse',
      tool: 'Grep',
      target: '.env',
      note: 'approval-required',
      status: 'block',
      exit: 2
    });

    const [entry] = readEntries();
    assert.strictEqual(entry.hook, 'privacy-block');
    assert.strictEqual(entry.event, 'PreToolUse');
    assert.strictEqual(entry.tool, 'Grep');
    assert.strictEqual(entry.target, '.env');
    assert.strictEqual(entry.note, 'approval-required');
    assert.strictEqual(entry.status, 'block');
    assert.strictEqual(entry.exit, 2);
  });

  it('merges base timer fields into the final entry', async () => {
    const timer = createHookTimer('usage-context-awareness', {
      event: 'PostToolUse',
      tool: 'Grep'
    });

    await new Promise(resolve => setTimeout(resolve, 5));
    timer.end({ status: 'skip', note: 'throttled' });

    const [entry] = readEntries();
    assert.strictEqual(entry.hook, 'usage-context-awareness');
    assert.strictEqual(entry.event, 'PostToolUse');
    assert.strictEqual(entry.tool, 'Grep');
    assert.strictEqual(entry.status, 'skip');
    assert.strictEqual(entry.note, 'throttled');
    assert.ok(entry.dur >= 0);
  });

  it('normalizes crash logging', () => {
    logHookCrash('scout-block', new Error('boom'), { event: 'PreToolUse', tool: 'Read' });

    const [entry] = readEntries();
    assert.strictEqual(entry.hook, 'scout-block');
    assert.strictEqual(entry.event, 'PreToolUse');
    assert.strictEqual(entry.tool, 'Read');
    assert.strictEqual(entry.status, 'crash');
    assert.strictEqual(entry.error, 'boom');
  });

  it('rotates under lock and preserves the newest entries', () => {
    const lines = [];
    for (let i = 0; i < 1000; i++) {
      lines.push(JSON.stringify({ ts: `2026-03-18T12:00:${String(i % 60).padStart(2, '0')}.000Z`, hook: 'seed', status: 'ok', note: String(i) }));
    }
    fs.writeFileSync(LOG_FILE, lines.join('\n') + '\n', 'utf8');

    logHook('hook-logger', { status: 'ok', note: 'latest' });

    const entries = readEntries();
    assert.strictEqual(entries.length, 500);
    assert.strictEqual(entries.at(-1).note, 'latest');
  });
});
