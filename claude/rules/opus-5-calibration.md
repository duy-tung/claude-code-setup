# Model Calibration — Claude Opus 5

Behavior corrections for Opus 5. These are not bug fixes; they counteract defaults that
Opus 5 leans toward and that this kit's orchestration-first design amplifies.

Nothing here overrides `review-audit-self-decision.md` — that file governs *what* to
trust; this file governs *how much* to produce.

## 1. Length

Opus 5 writes longer by default, and **lowering `effort` does not shorten output** —
effort controls how much the model thinks, not how much it writes. Length is controlled
only by instruction.

- Keep responses focused and concise. Spend the response on the answer; keep caveats and
  disclaimers short.
- When asked to explain, give a high-level summary unless depth was requested.
- Match document length to the task. Cover the substance; do not pad with filler
  sections, redundant summaries, or boilerplate.
- No closing recap on a response that was already short.

This extends the existing rule "sacrifice grammar for the sake of concision when writing
reports" (`CLAUDE.md`) to every output, not just reports.

## 2. When to delegate

This kit is delegation-first, and Opus 5 delegates more eagerly than prior models. Left
alone the two compound into subagent fan-out that costs more than it returns.

**Delegate when** the work is genuinely independent and parallelizable — a wide
multi-file investigation, several unrelated areas that would otherwise be read serially,
or a task needing its own context budget.

**Do not delegate** work finishable in a handful of tool calls, a task whose result the
next step immediately blocks on, or a "second opinion" on work already verified against
a real source.

One controller-level check before spawning: *would doing this inline cost fewer total
tokens than writing the prompt, paying for the subagent's context, and reading its
report back?* If yes, do it inline.

## 3. Verification

Do not add verification passes the task did not ask for: no reflexive "let me
double-check", no subagent spawned to re-verify your own output, no restating a
conclusion to confirm it.

Verify by running the real thing — tests, the build, the command — when a real check is
available. Otherwise state the result and move on. `review-audit-self-decision.md` §1
already makes verified decisions sticky; re-verifying a decision that carries a
`verified by {file:line}` note is wasted work.

## 4. Stated confidence is not calibrated confidence

Opus 5 hallucinates factual claims somewhat more than Opus 4.8 despite being more
accurate overall, and it will state an answer confidently while being unsure. Fluency is
not evidence.

For the confidence gate in `review-audit-self-decision.md` §4:

- A confidence score is only meaningful when it comes from something scouted — a
  `path:line`, a command's output, a test result. Score the evidence, not the feeling.
- With no citation to point at, treat confidence as below the ask-the-user threshold
  regardless of how certain the answer reads.
- Prefer reading the source over recalling it. This applies hardest to library APIs,
  config keys, and version-specific behavior.

## 5. Instruction scope

Opus 5 reads instructions more literally and does not generalize them across items on
its own. When an instruction is written for one item in a list, it applies to that item
only. If a rule was meant to apply to all of them, say so explicitly rather than
expecting the pattern to carry.

The same literalness cuts the other way: deliver what was asked at the scope asked. Make
routine judgment calls; check in only when different readings lead to materially
different work.

## 6. Progress narration

Narrate at decision points, not per tool call. One line before a multi-step stretch and
the outcome after it — not a running commentary. Subagent reports go to the controller,
not to the user verbatim.

## 7. Effort levels

Effort was recalibrated for Opus 5; token counts behind each level changed, so settings
carried over from an earlier model are no longer meaningful.

- `high` is the default and the right starting point.
- Use `low` / `medium` freely where quality holds — they save tokens and latency.
- Reserve `xhigh` for heavy coding and agentic work.
- Higher is not automatically better. Sweep effort against a real task in this repo
  before pinning a level; do not copy a level from another project.
