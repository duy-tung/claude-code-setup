const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');

const ROOT = path.resolve(__dirname, '..', '..', '..');

function read(relativePath) {
  return fs.readFileSync(path.join(ROOT, relativePath), 'utf8');
}

function activeLines(source) {
  return source
    .split('\n')
    .filter((line) => !line.trimStart().startsWith('#'))
    .join('\n');
}

function markdownFiles(relativeDir) {
  const directory = path.join(ROOT, relativeDir);
  const files = [];
  for (const entry of fs.readdirSync(directory, { withFileTypes: true })) {
    const relativePath = path.join(relativeDir, entry.name);
    if (entry.isDirectory()) files.push(...markdownFiles(relativePath));
    if (entry.isFile() && entry.name.endsWith('.md')) files.push(relativePath);
  }
  return files;
}

test('shipped profile pins Opus 5 while leaving experimental teams opt-in', () => {
  const settings = JSON.parse(read('claude/settings.json'));
  assert.equal(settings.model, 'claude-opus-5');
  assert.equal(settings.effortLevel, 'high');
  assert.equal(settings.env?.CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS, undefined);

  const readme = read('README.md');
  assert.match(readme, /Claude Code[^\n]*\*\*2\.1\.219\+\*\*/);
  assert.match(readme, /claude --model claude-opus-5 --effort high/);
  assert.match(readme, /CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1 claude/);
});

test('top-level guidance loads the Opus 5 calibration rules', () => {
  const rules = read('claude/rules/CLAUDE.md');
  assert.match(rules, /opus-5-calibration\.md/);
  assert.match(read('claude/rules/opus-5-calibration.md'), /claude-opus-5/);
});

test('active runtime and command examples contain no pre-Opus-5 exact pin', () => {
  const files = [
    'claude/settings.json',
    'README.md',
    'eval/README.md',
    'eval/run.py',
    'package.json',
    '.github/workflows/verify.yml',
  ];
  // Moving Claude Code aliases (`opus`, `sonnet`, `haiku`) remain valid. This
  // check targets exact versioned pins in active runtime/example surfaces; test
  // fixtures and historical migration prose are intentionally out of scope.
  const preOpus5Pin = /claude-(?:opus|sonnet|haiku)-(?:[0-4](?:[-.]\d+)*)(?!\d)/i;
  for (const file of files) {
    assert.doesNotMatch(read(file), preOpus5Pin, `${file} has a stale exact pin`);
  }
});

test('active API helper avoids legacy request controls', () => {
  const source = activeLines(
    read('claude/skills/skill-creator/scripts/improve_description.py')
  );
  const forbidden = [
    /budget_tokens\s*[=:]/,
    /["']type["']\s*:\s*["']enabled["']/,
    /\b(?:temperature|top_p|top_k)\s*[=:]/,
    /context-1m-[0-9-]+/,
    /["']thinking["']\s*:\s*\{\s*["']type["']\s*:\s*["']disabled["'][^}]*\}[^\n]*(?:xhigh|max)/,
  ];
  for (const pattern of forbidden) {
    assert.doesNotMatch(source, pattern, `legacy Opus request control matched ${pattern}`);
  }
  assert.match(source, /["']type["']\s*:\s*["']adaptive["']/);
  assert.match(source, /["']content["']\s*:\s*response\.content/);
  assert.match(source, /stop_reason["']?,?\s*[^\n]*["']refusal["']/);
});

test('default workflows do not reintroduce unconditional delegation or review loops', () => {
  const files = [
    'claude/rules/CLAUDE.md',
    'claude/rules/development-rules.md',
    'claude/rules/orchestration-protocol.md',
    'claude/rules/primary-workflow.md',
    'claude/skills/cook/SKILL.md',
    'claude/skills/fix/SKILL.md',
    'claude/skills/docs/references/init-workflow.md',
    'claude/skills/docs/references/update-workflow.md',
    'claude/skills/ship/SKILL.md',
    'claude/skills/ship/references/ship-workflow.md',
    'claude/skills/skill-creator/references/validation-checklist.md',
    'claude/agents/code-reviewer.md',
    'claude/agents/docs-manager.md',
    'claude/agents/tester.md',
    'claude/skills/ck-code-review/SKILL.md',
    'claude/skills/scout/SKILL.md',
    ...markdownFiles('claude/skills/cook/references'),
    ...markdownFiles('claude/skills/fix/references'),
  ];
  const forbidden = [
    /when unsure, delegate/i,
    /review code after every implementation/i,
    /regardless of task simplicity/i,
    /Task tool calls\s*=\s*0/i,
    /Thinking level:\s*Ultrathink/i,
    /don't inline/i,
    /MUST spawn/i,
    /approval at each (?:step|phase)/i,
  ];

  for (const file of files) {
    const source = read(file);
    for (const pattern of forbidden) {
      assert.doesNotMatch(source, pattern, `${file} matched ${pattern}`);
    }
  }
});

test('Claude-facing markdown has no pseudo-thinking or degraded-grammar setting', () => {
  const forbidden = /sacrifice grammar|\bUltrathink\b|Thinking level\s*:/i;
  for (const file of markdownFiles('claude')) {
    assert.doesNotMatch(read(file), forbidden, `${file} matched ${forbidden}`);
  }

  for (const file of markdownFiles('claude/skills/sequential-thinking')) {
    assert.doesNotMatch(
      read(file),
      /\bThought\s+\d+\/\d+/,
      `${file} exposes legacy numbered thought markers`
    );
  }
});

test('Agent Teams guidance uses the current shared-checkout lifecycle', () => {
  const files = [
    'claude/skills/team/SKILL.md',
    'claude/skills/team/references/agent-teams-official-docs.md',
    'claude/skills/team/references/agent-teams-controls-and-modes.md',
    'claude/skills/team/references/agent-teams-examples-and-best-practices.md',
    'claude/rules/team-coordination-rules.md',
    'docs/agent-teams-guide.md',
  ];
  const combined = files.map(read).join('\n');
  assert.doesNotMatch(combined, /TeamCreate|TeamDelete/);
  assert.doesNotMatch(combined, /type\s*[:=]\s*["']broadcast["']/i);
  assert.doesNotMatch(combined, /isolated worktree/i);
  assert.doesNotMatch(combined, /every teammate (?:must|uses?) (?:run )?(?:on )?Opus/i);
  assert.match(combined, /implicit[^\n]*team/i);
  assert.match(combined, /cleanup[^\n]*automatic|automatic[^\n]*cleanup/i);
  assert.match(combined, /shared checkout/i);
  assert.match(combined, /direct message/i);
});

test('agent allowlists use the current Agent parameter syntax', () => {
  for (const file of markdownFiles('claude/agents')) {
    const frontmatter = read(file).split('---', 3)[1] || '';
    assert.doesNotMatch(
      frontmatter,
      /\bTask\([^)]*\)/,
      `${file} uses the legacy Task(...) alias instead of Agent(...)`
    );
  }

  for (const file of markdownFiles('claude')) {
    assert.doesNotMatch(
      read(file),
      /\bTask\([^)]*\)/,
      `${file} uses the legacy Task(...) invocation alias`
    );
  }
});

test('context tooling uses Opus 5 one-million-token default', () => {
  assert.match(
    read('claude/skills/context-engineering/scripts/context_analyzer.py'),
    /DEFAULT_TOKEN_LIMIT\s*=\s*1_000_000/
  );
});

test('behavior eval prompts do not pre-seed legacy self-verification', () => {
  const tasksDir = path.join(ROOT, 'eval', 'tasks');
  for (const entry of fs.readdirSync(tasksDir, { withFileTypes: true })) {
    if (!entry.isDirectory()) continue;
    const taskPath = path.join(tasksDir, entry.name, 'task.json');
    if (!fs.existsSync(taskPath)) continue;
    const task = JSON.parse(fs.readFileSync(taskPath, 'utf8'));
    const prompt = task.prompt || '';
    assert.doesNotMatch(
      prompt,
      /verify (?:your own work|by running|before finishing)|run the tests to verify/i,
      `${entry.name} pre-seeds the behavior under evaluation`
    );
    assert.equal(
      task.workflow_artifact_budget,
      0,
      `${entry.name} should reject plan/journal artifacts for this small task`
    );
  }
});

// The per-file allowlist above predates this sweep and only covers the skills the
// migration happened to touch. These checks scan every shipped skill instead, so a
// newly added or previously unaudited skill cannot reintroduce the patterns.
// document-skills/ is excluded: it is vendored Anthropic content, and diverging
// from upstream there costs more than it buys.
function shippedSkillFiles() {
  return markdownFiles('claude/skills')
    .filter((file) => !file.includes(`${path.sep}document-skills${path.sep}`));
}

test('no shipped skill opens with unconditional delegation', () => {
  // "Use the X subagent to ..." as an instruction, rather than a conditional that
  // says when delegating beats doing the work inline.
  const unconditionalDelegation = /^\s*Use the `?[\w-]+`? (?:subagent|agent) to /mi;
  const files = shippedSkillFiles();
  assert.ok(files.length > 30, `expected the full skill tree, found ${files.length} files`);

  for (const file of files) {
    assert.doesNotMatch(read(file), unconditionalDelegation, `${file} delegates unconditionally`);
  }
});

test('no shipped skill chains another skill unconditionally', () => {
  const unconditionalChain = /\*\*IMPORTANT:?\*\*\s*Invoke\s+"?\/ck:/i;
  for (const file of shippedSkillFiles()) {
    assert.doesNotMatch(read(file), unconditionalChain, `${file} chains a skill unconditionally`);
  }
});

test('no shipped skill performs multi-persona role theater', () => {
  // Personas as sections to fill produce padded answers on Opus 5; the same
  // angles work as lenses to check.
  const personaTheater = /You orchestrate (?:four|three|five|several|\d+) (?:specialized )?\w+/i;
  for (const file of shippedSkillFiles()) {
    assert.doesNotMatch(read(file), personaTheater, `${file} scaffolds persona role-play`);
  }
});

test('recalibrated skills keep their delegation and output guidance conditional', () => {
  const ask = read('claude/skills/ask/SKILL.md');
  assert.match(ask, /lenses|angles to check/i);
  assert.match(ask, /Match depth to the question/i);
  assert.doesNotMatch(ask, /comprehensive breakdown/i);

  const journal = read('claude/skills/journal/SKILL.md');
  assert.match(journal, /Write them inline when the session already holds the relevant context/i);
  assert.match(journal, /not as a routine follow-up/i);

  const xia = read('claude/skills/xia/SKILL.md');
  assert.match(xia, /read it inline when/i);
});

// Tree-wide prompt-policy scan. The patterns below are phrased as the risky
// *instruction*; the scanner suppresses the prohibitions that state the same
// words, so the kit's own rules do not trip their own guard.
const { findInstructionHits } = require('./lib/prompt-policy.cjs');

const PROMPT_POLICY_PATTERNS = {
  'self-recheck': /\b(?:double[- ]check|re-?verify)\b/,
  'subagent-verify': /(?:subagent|agent) to (?:verify|double[- ]check|review your)/,
  'restrictive-review-filter': /only report (?:the )?(?:critical|high|severe|blocking)|be conservative\b/,
  'numeric-confidence': /confidence score|\d{1,3}% confiden/,
  'final-verification': /final verification (?:step|pass)/
};

// Verified legitimate on inspection. Each entry names why the phrase is domain
// logic rather than Opus 5 over-verification. Keep this list short; a growing
// list means the pattern is wrong, not that the exceptions are.
const PROMPT_POLICY_EXEMPTIONS = {
  // Re-runs the dependent test after a fix lands — not a recheck of reasoning.
  'claude/skills/ck-code-review/references/task-management-reviews.md': ['self-recheck'],
  // Conditional re-measurement to rule out noise in a benchmarking loop.
  'claude/skills/ck-loop/references/guard-and-noise.md': ['self-recheck'],
  // Re-greps stale third-party scout output, which calibration §5 requires.
  'claude/agents/planner.md': ['self-recheck']
};

test('no shipped guidance instructs Opus 5 to over-verify or self-score', () => {
  const files = [
    ...markdownFiles('claude/skills'),
    ...markdownFiles('claude/agents'),
    ...markdownFiles('claude/rules'),
    ...markdownFiles('docs')
  ].filter((file) => !file.includes(`${path.sep}document-skills${path.sep}`));
  assert.ok(files.length > 200, `expected the full guidance tree, found ${files.length} files`);

  const failures = [];
  for (const file of files) {
    const source = read(file);
    const exempt = PROMPT_POLICY_EXEMPTIONS[file.split(path.sep).join('/')] || [];
    for (const [name, pattern] of Object.entries(PROMPT_POLICY_PATTERNS)) {
      if (exempt.includes(name)) continue;
      const hits = findInstructionHits(source, pattern);
      if (hits.length) failures.push(`${file} [${name}] → ${hits.join(' | ')}`);
    }
  }
  assert.deepEqual(failures, [], `prompt-policy violations:\n${failures.join('\n')}`);
});

test('every prompt-policy exemption still points at a real file and pattern', () => {
  for (const [file, names] of Object.entries(PROMPT_POLICY_EXEMPTIONS)) {
    const source = read(file);
    for (const name of names) {
      assert.ok(PROMPT_POLICY_PATTERNS[name], `exemption names unknown pattern ${name}`);
      assert.ok(
        findInstructionHits(source, PROMPT_POLICY_PATTERNS[name]).length > 0,
        `${file} no longer needs its ${name} exemption — remove it`
      );
    }
  }
});
