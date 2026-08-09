# Test Failure Fix Workflow

## Workflow

1. Run the smallest command that reproduces the named failure. Use the full suite
   initially only when failures must be grouped or no narrower selector exists.
2. Read the assertion, fixture/mocks, production path, and recent relevant changes.
3. Determine whether the defect is in product code, test expectations, test data,
   or environment; do not change an assertion merely to make it pass.
4. Fix the shared root cause before downstream failures it generates.
5. Rerun the original failing test, then affected neighboring tests and any shared
   contract checks justified by the blast radius.
6. Inspect the final diff and summarize all results as one evidence bundle.

For one deterministic failure, perform this inline. Use tasks or independent
workers when several failure groups are genuinely independent. Use an independent
reviewer only for broad, difficult, or high-risk changes.

Common commands include `npm test`, `bun test`, `pytest`, and `go test ./...`, but
prefer project-native targeted selectors during iteration.
