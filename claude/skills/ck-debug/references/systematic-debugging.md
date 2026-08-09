# Systematic Debugging

Four-phase debugging framework that establishes root cause evidence before fixes.
Scale each phase to the issue: a deterministic local failure may combine phases in
one short pass; a broad incident needs a durable evidence chain.

## The Iron Law

```
NO FIXES WITHOUT ROOT CAUSE INVESTIGATION FIRST
```

If haven't completed Phase 1, cannot propose fixes.

## The Four Phases

Cover each phase to the depth needed by the risk and uncertainty. Do not create
separate artifacts merely to prove that a phase occurred.

### Phase 1: Root Cause Investigation

**BEFORE attempting ANY fix:**

1. **Read Error Messages Carefully** - Don't skip past errors/warnings, read stack traces completely
2. **Reproduce Consistently** - Can trigger reliably? Exact steps? If not reproducible → gather more data
3. **Check Recent Changes** - What changed? Git diff, recent commits, new dependencies, config changes
4. **Gather Evidence in Multi-Component Systems**
   - For EACH component boundary: log data entering/exiting, verify environment propagation
   - Run once to gather evidence showing WHERE it breaks
   - THEN analyze to identify failing component
5. **Trace Data Flow** - Where does bad value originate? Trace up call stack until finding source (see root-cause-tracing.md)

### Phase 2: Pattern Analysis

**Find pattern before fixing:**

1. **Find Working Examples** - Locate similar working code in same codebase
2. **Compare Against References** - Read the portions needed to understand the relevant contract and pattern before applying it
3. **Identify Differences** - Check differences that could explain the symptom; broaden only when evidence warrants it
4. **Understand Dependencies** - What other components, settings, config, environment needed?

### Phase 3: Hypothesis and Testing

**Scientific method:**

1. **Form Single Hypothesis** - "I think X is root cause because Y", be specific not vague
2. **Test Minimally** - SMALLEST possible change to test hypothesis, one variable at a time
3. **Verify Before Continuing** - Worked? → Phase 4. Didn't work? → NEW hypothesis. DON'T add more fixes
4. **When Don't Know** - Say "I don't understand X", don't pretend, ask for help

### Phase 4: Implementation

**Fix root cause, not symptom:**

1. **Preserve the Reproduction** - Capture the simplest executable repro; add an
   automated failing test when a suitable harness exists and the test has lasting value
2. **Implement Single Fix** - Address root cause identified, ONE change, no "while I'm here" improvements
3. **Verify Fix** - Original repro passes, affected tests pass, and the issue is actually resolved
4. **If Fix Doesn't Work**
   - STOP. Count: How many fixes tried?
   - If < 3: Return to Phase 1, re-analyze with new information
   - **If ≥ 3: STOP and question architecture**
5. **If 3+ Fixes Failed: Question Architecture**
   - Pattern: Each fix reveals new shared state/coupling problem elsewhere
   - STOP and question fundamentals: Is pattern sound? Wrong architecture?
   - Discuss with human partner before more fixes

## Red Flags - STOP and Follow Process

If catch yourself thinking:
- "Quick fix for now, investigate later"
- "Just try changing X and see if it works"
- "Add multiple changes, run tests"
- "Skip executable verification and rely on intuition"
- "It's probably X, let me fix that"
- "I don't fully understand but this might work"
- "One more fix attempt" (when already tried 2+)

**ALL mean:** STOP. Return to Phase 1.

## Human Partner Signals You're Doing It Wrong

- "Is that not happening?" - Assumed without verifying
- "Will it show us...?" - Should have added evidence gathering
- "Stop guessing" - Proposing fixes without understanding
- "Question the fundamentals" - Revisit the diagnosis or architecture, not just symptoms
- "We're stuck?" (frustrated) - Approach isn't working

**When see these:** STOP. Return to Phase 1.

Report the decisive evidence, hypotheses tested, revisions, and conclusion as a
concise reasoning summary. Do not expose private chain-of-thought, assign thinking
levels, or use numeric confidence as proof.

## Common Rationalizations

| Excuse | Reality |
|--------|---------|
| "Issue is simple, don't need process" | Simple issues have root causes too |
| "Emergency, no time for process" | Systematic is FASTER than guess-and-check |
| "Just try this first, then investigate" | First fix sets pattern. Do right from start |
| "One more fix attempt" (after 2+ failures) | 3+ failures = architectural problem |

## Outcome

A successful investigation leaves a reproducible baseline, a root cause supported
by evidence, a focused fix, and fresh proportional verification.
