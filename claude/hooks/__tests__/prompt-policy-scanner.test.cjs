const test = require('node:test');
const assert = require('node:assert/strict');
const { findInstructionHits, isNegated, unwrap } = require('./lib/prompt-policy.cjs');

const SELF_RECHECK = /\b(?:double[- ]check|re-?verify)\b/;
const CONFIDENCE = /confidence score/;
const SUBAGENT_VERIFY = /(?:subagent|agent) to (?:verify|double[- ]check)/;

test('flags a risky phrase written as an instruction', () => {
  assert.deepEqual(findInstructionHits('Double-check your answer before replying.', SELF_RECHECK), ['Double-check']);
  assert.deepEqual(findInstructionHits('Report a confidence score with each finding.', CONFIDENCE), ['confidence score']);
  assert.deepEqual(
    findInstructionHits('Use a subagent to verify the work.', SUBAGENT_VERIFY),
    ['subagent to verify']
  );
});

// These are verbatim lines from the shipped rules. A guard that fires on them
// is worse than no guard: it would be silenced by deleting the correct rule.
test('stays silent on the repo\'s own prohibitions', () => {
  const realProhibitions = [
    'Do not spawn a subagent merely to verify or double-check completed work.',
    'Do not invent numeric confidence scores. Mark a claim as verified, inferred, or unknown when that distinction matters.',
    'claims `verified`, `inferred`, or `unknown`; do not provide a confidence score.',
    'Do not convert them into a numeric confidence score.',
    // Soft-wrapped in the source file: the negation sits on the previous line.
    'Do not add artificial\ndepth, repeated self-checks, or numeric confidence scores.',
    'Anti-patterns: asking what grep can answer, narrating a numeric confidence score',
    '`verified`, `inferred`, or `unknown` evidence states rather than a confidence score'
  ];
  for (const line of realProhibitions) {
    for (const pattern of [SELF_RECHECK, CONFIDENCE, SUBAGENT_VERIFY]) {
      assert.deepEqual(
        findInstructionHits(line, pattern), [],
        `false positive on prohibition: ${line}`
      );
    }
  }
});

test('negation binds to its own clause, not the whole sentence', () => {
  // The prohibition covers the first clause only; the second is a live instruction.
  const mixed = 'Do not delegate small work; double-check your answer before replying.';
  assert.deepEqual(findInstructionHits(mixed, SELF_RECHECK), ['double-check']);

  // A trailing negation must not retroactively excuse a leading instruction.
  assert.deepEqual(
    findInstructionHits('Double-check the output, never skip it.', SELF_RECHECK),
    ['Double-check']
  );
});

test('isNegated only considers text preceding the phrase', () => {
  const clause = 'do not double-check';
  assert.equal(isNegated(clause, clause.indexOf('double-check')), true);
  assert.equal(isNegated('double-check, do not skip', 0), false);
});

test('reports every instruction occurrence across clauses', () => {
  const text = 'Double-check the diff.\nLater, re-verify the build.';
  assert.deepEqual(findInstructionHits(text, SELF_RECHECK), ['Double-check', 're-verify']);
});

test('soft-wrapped prose keeps its negation, list items stay separate', () => {
  assert.deepEqual(unwrap('Do not add artificial\ndepth or scores.'), ['Do not add artificial depth or scores.']);
  assert.deepEqual(unwrap('- Do not delegate\n- Double-check the diff'), ['- Do not delegate', '- Double-check the diff']);

  // A prohibition in one bullet must not excuse an instruction in the next.
  assert.deepEqual(
    findInstructionHits('- Never re-verify your own work\n- Double-check the diff', SELF_RECHECK),
    ['Double-check']
  );
});

test('an anti-pattern heading negates its whole section', () => {
  const section = [
    '## Anti-patterns',
    '',
    '- subjective confidence scores without evidence;',
    '- repeated verification of a fresh passing check;'
  ].join('\n');
  assert.deepEqual(findInstructionHits(section, CONFIDENCE), []);

  // The negation must not leak past the next heading.
  const resumed = `${section}\n\n## Reporting\n\n- Include a confidence score.`;
  assert.deepEqual(findInstructionHits(resumed, CONFIDENCE), ['confidence score']);
});
