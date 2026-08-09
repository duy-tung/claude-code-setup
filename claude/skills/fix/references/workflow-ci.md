# CI/CD Fix Workflow

Use for a concrete CI failure. Reading the named run and repository is part of
diagnosis; push, rerun, cancel, or deployment actions require the appropriate
authority.

## Workflow

1. Fetch the failed step and enough preceding context to identify the first
   meaningful failure, for example:

   ```bash
   gh run view <run-id> --log-failed
   gh run view <run-id> --log
   ```

2. Reproduce the failing command locally when feasible. Distinguish code defects
   from runner environment, permissions, dependency, secret, and timeout issues.
3. Trace the evidence to the root cause and implement the smallest compatible fix.
4. Collect one proportional bundle: original CI-equivalent command, targeted
   regression check, affected lint/type/build checks, and final-diff inspection.
5. Broaden or independently review only for shared pipelines, security/permission
   changes, releases, or other high-risk surfaces.

If `gh` is unavailable or unauthorized, report the missing evidence instead of
guessing. Ask the user only when logs cannot be accessed, a material contract or
scope choice remains, or an external mutation needs new authority.
