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

// Hook sources inject text into every session and every subagent, so they carry
// the same prompt-policy weight as the Markdown rules. Test files are excluded:
// they legitimately contain the forbidden strings as assertion patterns.
function hookSourceFiles(relativeDir = 'claude/hooks') {
  const directory = path.join(ROOT, relativeDir);
  const files = [];
  for (const entry of fs.readdirSync(directory, { withFileTypes: true })) {
    if (entry.name === '__tests__') continue;
    const relativePath = path.join(relativeDir, entry.name);
    if (entry.isDirectory()) files.push(...hookSourceFiles(relativePath));
    if (entry.isFile() && entry.name.endsWith('.cjs')) files.push(relativePath);
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
  assert.match(rules, /model-calibration\.md/);
  assert.match(read('claude/rules/model-calibration.md'), /claude-opus-5/);
});

// ── Always-loaded context budget ────────────────────────────────────────────
// Unscoped .md files under .claude/rules/ load into EVERY session at the same
// priority as .claude/CLAUDE.md. Anthropic's guidance is under 200 lines per
// file, and warns that longer files reduce adherence and that contradictory
// rules get resolved arbitrarily. The budget is what stops this directory from
// silently growing back into the 946-line set this consolidation replaced.
const ALWAYS_LOADED_LINE_BUDGET = 450; // Ratcheted 946 → 815 → 431. Lower it, never raise it.

function alwaysLoadedRules() {
  return markdownFiles('claude/rules')
    .map((file) => ({ file, source: read(file) }))
    // A `paths:` frontmatter key makes a rule load only for matching files.
    .filter(({ source }) => !/^paths:/m.test(source.split('---')[1] || ''));
}

test('always-loaded rules stay within the session context budget', () => {
  const rules = alwaysLoadedRules();
  const measured = rules.map(({ file, source }) => ({
    file,
    lines: source.split('\n').length
  }));
  const total = measured.reduce((sum, entry) => sum + entry.lines, 0);

  // Printed, not just asserted: the number belongs in the review, and a silent
  // pass hides the direction the budget is drifting.
  const breakdown = measured
    .sort((a, b) => b.lines - a.lines)
    .map((entry) => `${path.basename(entry.file)}=${entry.lines}`)
    .join(' ');
  console.log(`    always-loaded rules: ${total} lines (${breakdown})`);

  assert.ok(
    total <= ALWAYS_LOADED_LINE_BUDGET,
    `always-loaded rules total ${total} lines, over the ${ALWAYS_LOADED_LINE_BUDGET} budget.\n` +
    'Move task-specific content to a path-scoped rule or a skill rather than raising this.'
  );
});

// ── Single normative source ─────────────────────────────────────────────────
// Behavior guidance used to be copy-pasted across dozens of files, so a model
// upgrade meant editing every copy and missing some. These phrasings may be
// STATED only in model-calibration.md; every other rule points at it.
const CANONICAL_BEHAVIOR_PHRASES = {
  'delegation threshold': /delegate work (?:that is )?finishable in a handful of tool calls|Do not delegate work finishable/i,
  'evidence states': /\*\*Verified\*\*|verified.{0,12}inferred.{0,12}unknown/i,
  'effort ladder': /\bxhigh\b/i,
  'workflow tiering': /\*\*Small and clear:\*\*|\*\*Multi-step:\*\*/i
};

test('canonical behavior rules are stated only in model-calibration.md', () => {
  const canon = read('claude/rules/model-calibration.md');
  for (const [name, pattern] of Object.entries(CANONICAL_BEHAVIOR_PHRASES)) {
    assert.match(canon, pattern, `canon is missing its own ${name} rule`);
  }

  const others = alwaysLoadedRules()
    .filter(({ file }) => path.basename(file) !== 'model-calibration.md');
  for (const { file, source } of others) {
    for (const [name, pattern] of Object.entries(CANONICAL_BEHAVIOR_PHRASES)) {
      assert.doesNotMatch(
        source, pattern,
        `${file} restates the canonical ${name} rule — reference model-calibration.md instead`
      );
    }
  }
});

test('model-calibration.md declares itself the single normative source', () => {
  const canon = read('claude/rules/model-calibration.md');
  assert.match(canon, /single normative source/i);
  assert.match(canon, /do not restate it/i);
  // The deleted rules must not come back as separate always-loaded files.
  for (const gone of ['primary-workflow.md', 'review-audit-self-decision.md']) {
    assert.ok(
      !fs.existsSync(path.join(ROOT, 'claude', 'rules', gone)),
      `${gone} was absorbed into model-calibration.md; it should not exist`
    );
  }
  // Renames and deletions under claude/ must reach installed user machines.
  const deletions = JSON.parse(read('claude/metadata.json')).deletions;
  for (const gone of [
    'rules/opus-5-calibration.md',
    'rules/primary-workflow.md',
    'rules/review-audit-self-decision.md'
  ]) {
    assert.ok(deletions.includes(gone), `claude/metadata.json deletions[] is missing ${gone}`);
  }
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
    'claude/rules/model-calibration.md',
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

test('runtime hook injections carry no pre-Opus-5 prompt scaffolding', () => {
  const forbidden = [
    // Contradicted the shipped calibration rule while being injected every turn.
    /sacrifice grammar/i,
    /\bUltrathink\b/i,
    /Thinking level\s*:/i,
    // Unconditional approval round after an already-authorized request.
    /Stop here and ask the user/i,
    // Unconditional scope-expansion nudge on every prompt.
    /\[IMPORTANT\] Consider Modularization/i,
    /\bMUST spawn\b/i,
    /when unsure, delegate/i
  ];

  const files = hookSourceFiles();
  assert.ok(files.length > 10, `expected to scan the hook tree, found ${files.length} files`);
  for (const file of files) {
    const source = read(file);
    for (const pattern of forbidden) {
      assert.doesNotMatch(source, pattern, `${file} matched ${pattern}`);
    }
  }
});

test('hook injections scope artifacts and restructuring to the request', () => {
  const contextBuilder = read('claude/hooks/lib/context-builder.cjs');
  // Modularization guidance left the per-turn injection entirely; development-rules.md
  // carries it as File Size Management, loaded once per session.
  assert.doesNotMatch(contextBuilder, /## Modularization/);
  assert.match(read('claude/rules/development-rules.md'), /File Size Management/);

  // Every subagent used to receive a report path with no condition attached.
  const subagentInit = read('claude/hooks/subagent-init.cjs');
  assert.match(subagentInit, /## Naming \(only when this task's deliverable is a written report or plan\)/);
  assert.match(subagentInit, /write a file only when the task asks for one/);

  // The plan checkpoint defers to the scope the user already authorized.
  const planReminder = read('claude/hooks/cook-after-plan-reminder.cjs');
  assert.match(planReminder, /already authorized implementation, continue into it/);

  // Simplification is inline-first; the subagent is the large-diff escape hatch.
  const simplifyGate = read('claude/hooks/simplify-gate.cjs');
  assert.match(simplifyGate, /Do this inline/);
  assert.match(simplifyGate, /Delegate only when/);
});

test('Agent Teams guidance uses the current shared-checkout lifecycle', () => {
  const files = [
    'claude/skills/team/SKILL.md',
    'claude/skills/team/references/agent-teams-official-docs.md',
    'claude/skills/team/references/agent-teams-controls-and-modes.md',
    'claude/skills/team/references/agent-teams-examples-and-best-practices.md',
    'claude/skills/team/references/team-coordination-rules.md',
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
