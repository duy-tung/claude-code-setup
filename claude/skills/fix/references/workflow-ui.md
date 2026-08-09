# UI Fix Workflow

## Workflow

1. Capture the exact visual/interaction symptom and viewport, state, browser, and
   accessibility conditions needed to reproduce it.
2. Read the affected component, its container/layout constraints, local design
   conventions, and relevant project guidelines when they exist.
3. Trace the root cause through DOM structure, styles, state, event flow, or asset
   behavior; avoid cosmetic overrides that mask an upstream layout/state defect.
4. Implement the smallest cohesive fix.
5. Collect one proportional evidence bundle:
   - focused screenshot or interaction comparison;
   - relevant browser/project-native test;
   - compilation/type/lint check for the affected module;
   - keyboard, focus, contrast, and responsive checks when implicated;
   - final-diff inspection.

Perform localized work inline. Use vision/browser tooling when visual behavior is
part of acceptance criteria. Delegate or create phase tasks only for a broad UI
surface; use independent review for high-risk accessibility, design-system, or
cross-browser changes.

Update design docs only if the design rule itself changed. Generate or edit assets
only when the requested fix requires them.
