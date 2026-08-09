# Example: API Latency Diagnosis

## Symptom

One endpoint regressed from 120 ms to roughly 1.8 s.

## Competing hypotheses

| Hypothesis | Decisive check | Result |
|---|---|---|
| N+1 database queries | Query count in one traced request | Refuted: count unchanged |
| Missing database index | Query plan and database duration | Refuted: 8 ms total |
| Sequential downstream calls | Span timeline | Verified: six 280 ms calls serialized |

## Conclusion

The regression is caused by serialized downstream calls. Batch them if the
provider supports batching; otherwise run the independent calls concurrently
under the existing rate limit. Verify with the same trace and the endpoint's
latency regression test.

## Residual risk

Concurrency can increase provider pressure. The implementation should retain the
current request cap and measure error rate alongside latency.
