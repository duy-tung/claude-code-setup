#!/usr/bin/env node
/**
 * Plan Subagent Stop Hook - Next Step Reminder
 *
 * Fires when Plan subagent completes. Presents user-choice next steps before implementation.
 * Also outputs full absolute path so new sessions (after /clear) can find the plan in worktrees.
 *
 * Exit Codes:
 *   0 - Success (non-blocking)
 */

// Crash wrapper
try {
  const fs = require('fs');
  const path = require('path');
  const { isHookEnabled, readSessionState } = require('./lib/ck-config-utils.cjs');

  // Early exit if hook disabled in config
  if (!isHookEnabled('cook-after-plan-reminder')) {
    process.exit(0);
  }

  async function main() {
  try {
    const stdin = fs.readFileSync(0, 'utf-8').trim();
    if (!stdin) process.exit(0);

    // Get active plan path from session state
    const sessionId = process.env.CK_SESSION_ID;
    let planPath = null;

    if (sessionId) {
      const state = readSessionState(sessionId);
      if (state?.activePlan) {
        planPath = state.activePlan;
        // Ensure it's absolute
        if (!path.isAbsolute(planPath) && state.sessionOrigin) {
          planPath = path.resolve(state.sessionOrigin, planPath);
        }
      }
    }

    // Output neutral next-step options with full absolute path if available.
    // Scope the checkpoint to the original request: an unconditional stop turns
    // an already-authorized "plan and build X" into a redundant approval round.
    console.log('Planning complete. Lead with the outcome: what the plan does and the single recommended next step.');
    console.log('If the original request already authorized implementation, continue into it without a separate approval round.');
    console.log('Otherwise ask which next step the user wants — implement, validate, red-team, revise, or end — and ask only once.');
    if (planPath) {
      const planMdPath = path.join(planPath, 'plan.md');
      console.log(`Implementation command: /ck:cook ${planMdPath}`);
    } else {
      // Fallback when plan path unavailable
      console.log('Implementation command: /ck:cook {full-absolute-path-to-plan.md}');
    }
    console.log('Add --auto only if the user explicitly asks for autonomous implementation.');

    process.exit(0);
  } catch (error) {
    // Silent fail - non-blocking
    process.exit(0);
  }
  }

  main();
} catch (e) {
  // Minimal crash logging (zero deps — only Node builtins)
  try {
    const fs = require('fs');
    const p = require('path');
    const logDir = p.join(__dirname, '.logs');
    if (!fs.existsSync(logDir)) fs.mkdirSync(logDir, { recursive: true });
    fs.appendFileSync(p.join(logDir, 'hook-log.jsonl'),
      JSON.stringify({ ts: new Date().toISOString(), hook: p.basename(__filename, '.cjs'), status: 'crash', error: e.message }) + '\n');
  } catch (_) {}
  process.exit(0); // fail-open
}
