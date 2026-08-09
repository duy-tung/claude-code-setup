/**
 * Prompt-policy scanner.
 *
 * The Opus 5 rules are written as prohibitions ("Do not invent numeric
 * confidence scores"), so a plain substring scan for a risky phrase flags the
 * very rule that bans it. Every naive guard we could write here would fire on
 * `model-calibration.md` first and get deleted.
 *
 * This scanner only reports a phrase when it reads as an *instruction* — that
 * is, when the surrounding clause does not negate it. That keeps the guard
 * pointed at "double-check your answer" while staying silent on "do not
 * double-check your answer".
 *
 * Deliberately clause-scoped rather than sentence-scoped: prose in this repo
 * routinely puts a prohibition and an allowance in one sentence ("Delegate only
 * when X; do not delegate Y"), and a sentence-wide negation check would let the
 * instruction half through.
 */

// Markers that turn a following phrase into a prohibition or a contrast.
const NEGATION_SOURCE = [
  "do not", "don't", "dont", "never", "avoid", "without",
  "rather than", "instead of", "no need to", "not ",
  "stop ", "skip ", "remove ", "drop ", "against ", "anti-pattern"
];

// Note the absence of ":" — a colon introduces its list rather than separating
// it, so the qualifier before it still governs ("Anti-patterns: narrating a
// numeric confidence score"). Splitting there stranded the negation and flagged
// the kit's own anti-pattern lists as instructions.
const CLAUSE_SPLIT_RE = /[.;!?]|\s+—\s+|\s+--\s+/;

// A line that starts a new block: list item, heading, table row, quote, fence.
// Anything else is treated as a soft-wrapped continuation of the line above.
const BLOCK_START_RE = /^\s*(?:[-*+]\s|\d+[.)]\s|#{1,6}\s|\||>|```)/;

/**
 * Undo Markdown soft wrapping so a negation is not separated from the phrase it
 * negates. "Do not add artificial\ndepth, ... or numeric confidence scores."
 * is one clause, not two — splitting on every newline made that read as an
 * instruction and produced a false positive on the kit's own rules.
 *
 * List items, headings, and table rows stay separate: a prohibition in one
 * bullet must not excuse an instruction in the next.
 *
 * @param {string} text
 * @returns {string[]} logical lines
 */
function unwrap(text) {
  const out = [];
  for (const rawLine of text.split('\n')) {
    if (!rawLine.trim()) { out.push(''); continue; }
    const previous = out[out.length - 1];
    const isContinuation = previous && previous.trim() && !BLOCK_START_RE.test(rawLine);
    if (isContinuation) out[out.length - 1] = `${previous} ${rawLine.trim()}`;
    else out.push(rawLine);
  }
  return out;
}

/**
 * Split text into clauses. Negation binds within a clause, not across one.
 * @param {string} text
 * @returns {string[]}
 */
function clauses(text) {
  return unwrap(text).flatMap((line) => line.split(CLAUSE_SPLIT_RE));
}

/**
 * Does this clause negate whatever it introduces?
 * @param {string} clause
 * @param {number} matchIndex - index of the risky phrase within the clause
 * @returns {boolean}
 */
function isNegated(clause, matchIndex) {
  // Only text BEFORE the phrase can negate it. "double-check, do not skip" is
  // still an instruction to double-check.
  const before = clause.slice(0, matchIndex).toLowerCase();
  return NEGATION_SOURCE.some((marker) => before.includes(marker));
}

/**
 * Find risky phrases that read as instructions rather than prohibitions.
 *
 * @param {string} text - file contents
 * @param {RegExp} pattern - risky phrase; matched case-insensitively per clause
 * @returns {string[]} the matched instruction phrases, in order
 */
function findInstructionHits(text, pattern) {
  const hits = [];
  const scoped = new RegExp(pattern.source, pattern.flags.replace(/[gm]/g, '') + 'i');
  // A heading can negate its whole section. "## Anti-patterns" followed by a
  // bare list of bad practices is the idiom this repo uses most, and each bullet
  // reads as an instruction when taken on its own.
  let sectionNegated = false;

  for (const line of unwrap(text)) {
    const heading = line.match(/^\s*#{1,6}\s+(.*)$/);
    if (heading) {
      sectionNegated = isNegated(`${heading[1].toLowerCase()} x`, heading[1].length + 1);
      continue;
    }
    if (sectionNegated) continue;

    for (const clause of line.split(CLAUSE_SPLIT_RE)) {
      const match = clause.match(scoped);
      if (!match) continue;
      if (isNegated(clause, match.index)) continue;
      hits.push(match[0].trim());
    }
  }
  return hits;
}

module.exports = { findInstructionHits, isNegated, clauses, unwrap, NEGATION_SOURCE };
