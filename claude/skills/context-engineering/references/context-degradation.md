# Context Degradation Patterns

Predictable degradation as context grows. Not binary - a continuum.

## Degradation Patterns

| Pattern | Cause | Detection |
|---------|-------|-----------|
| **Lost-in-Middle** | U-shaped attention | Critical info recall drops 10-40% |
| **Context Poisoning** | Errors compound via reference | Persistent hallucinations despite correction |
| **Context Distraction** | Irrelevant info overwhelms | Single distractor degrades performance |
| **Context Confusion** | Multiple tasks mix | Wrong tool calls, mixed requirements |
| **Context Clash** | Contradictory info | Conflicting outputs, inconsistent reasoning |

## Lost-in-Middle Phenomenon

- Information in middle gets 10-40% lower recall
- Models allocate massive attention to first token (BOS sink)
- As context grows, middle tokens fail to get sufficient attention
- **Mitigation**: Place critical info at beginning/end

```markdown
[CURRENT TASK]              # Beginning - high attention
- Critical requirements

[DETAILED CONTEXT]          # Middle - lower attention
- Supporting details

[KEY FINDINGS]              # End - high attention
- Important conclusions
```

## Context Poisoning

**Entry points**:
1. Tool outputs with errors/unexpected formats
2. Retrieved docs with incorrect/outdated info
3. Model-generated summaries with hallucinations

**Detection symptoms**:
- Degraded quality on previously successful tasks
- Tool misalignment (wrong tools/parameters)
- Persistent hallucinations

**Recovery**:
- Truncate to before poisoning point
- Explicit note + re-evaluation request
- Restart with clean context, preserve only verified info

## Model Degradation Thresholds

Third-party estimates for older model generations. Treat as rough priors, not measurements — no vendor publishes a "degradation onset" figure, and the numbers below predate the current releases.

| Model | Degradation Onset | Severe Degradation |
|-------|-------------------|-------------------|
| GPT-5.2 | ~64K tokens | ~200K tokens |
| Claude Opus 4.5 | ~100K tokens | ~180K tokens |
| Claude Sonnet 4.5 | ~80K tokens | ~150K tokens |
| Gemini 3 Pro | ~500K tokens | ~800K tokens |

**Claude Opus 5: no published figure.** Its context window is 1M by default (no smaller variant), which sets the ceiling but says nothing about where quality starts to slide. Do not carry a 4.x row over to it — and do not read the larger window as a larger usable budget.

Degradation onset is workload-dependent (retrieval depth, tool-output volume, how much of the context is stale), so a single number would not transfer between projects anyway. Measure it instead:

1. Pick a task in this repo with a checkable outcome (a test that passes, a known answer).
2. Run it at rising context sizes — pad with real project material, not filler.
3. Record where accuracy first drops and where it falls off. Those two points are this project's thresholds.
4. Set the compaction and isolation triggers below off the measured onset, not off the table.

Until measured, use the **Detection Heuristics** further down — they react to observed symptoms rather than to an assumed token count.

## Four-Bucket Mitigation

1. **Write**: Save externally (scratchpads, files)
2. **Select**: Pull only relevant (retrieval, filtering)
3. **Compress**: Reduce tokens (summarization)
4. **Isolate**: Split across sub-agents (partitioning)

## Detection Heuristics

```python
def calculate_health(utilization, degradation_risk, poisoning_risk):
    """Health score: 1.0 = healthy, 0.0 = critical"""
    score = 1.0
    score -= utilization * 0.5 if utilization > 0.7 else 0
    score -= degradation_risk * 0.3
    score -= poisoning_risk * 0.2
    return max(0, score)

# Thresholds: healthy >0.8, warning >0.6, degraded >0.4, critical <=0.4
```

## Guidelines

1. Monitor context length vs performance correlation
2. Place critical info at beginning/end
3. Implement compaction before degradation
4. Validate retrieved docs before adding
5. Use versioning to prevent outdated clash
6. Segment tasks to prevent confusion
7. Design for graceful degradation

## Related Topics

- [Context Optimization](./context-optimization.md) - Mitigation techniques
- [Multi-Agent Patterns](./multi-agent-patterns.md) - Isolation strategies
