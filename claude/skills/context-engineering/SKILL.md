---
name: ck:context-engineering
description: >-
  Check context usage limits, monitor time remaining, optimize token consumption, debug context failures.
  Use when asking about context percentage, rate limits, usage warnings, context optimization, agent architectures, memory systems.
user-invocable: true
when_to_use: "Invoke for context budget, memory, or agent architecture issues."
category: utilities
keywords: [context, tokens, limits, memory, optimization]
argument-hint: "[topic or question]"
metadata:
  author: claudekit
  version: "1.0.0"
---

# Context Engineering

Context engineering curates the smallest high-signal token set for LLM tasks. The goal: maximize reasoning quality while minimizing token usage.

## When to Activate

- Designing/debugging agent systems
- Context limits constrain performance
- Optimizing cost/latency
- Building multi-agent coordination
- Implementing memory systems
- Evaluating agent performance
- Developing LLM-powered pipelines

## Core Principles

1. **Context quality > quantity** - High-signal tokens beat exhaustive content
2. **Attention is finite** - U-shaped curve favors beginning/end positions
3. **Progressive disclosure** - Load information just-in-time
4. **Isolation prevents degradation** - Partition work across sub-agents
5. **Measure before optimizing** - Know your baseline

**IMPORTANT:**
- Be concise while preserving grammar and clarity.
- Optimize only after measuring the task's quality, cost, and latency.
- Pass these rules to subagents.

## Quick Reference

| Topic | When to Use | Reference |
|-------|-------------|-----------|
| **Fundamentals** | Understanding context anatomy, attention mechanics | [context-fundamentals.md](./references/context-fundamentals.md) |
| **Degradation** | Debugging failures, lost-in-middle, poisoning | [context-degradation.md](./references/context-degradation.md) |
| **Optimization** | Compaction, masking, caching, partitioning | [context-optimization.md](./references/context-optimization.md) |
| **Compression** | Long sessions, summarization strategies | [context-compression.md](./references/context-compression.md) |
| **Memory** | Cross-session persistence, knowledge graphs | [memory-systems.md](./references/memory-systems.md) |
| **Multi-Agent** | Coordination patterns, context isolation | [multi-agent-patterns.md](./references/multi-agent-patterns.md) |
| **Evaluation** | Testing agents, LLM-as-Judge, metrics | [evaluation.md](./references/evaluation.md) |
| **Tool Design** | Tool consolidation, description engineering | [tool-design.md](./references/tool-design.md) |
| **Pipelines** | Project development, batch processing | [project-development.md](./references/project-development.md) |
| **Runtime Awareness** | Usage limits, context window monitoring | [runtime-awareness.md](./references/runtime-awareness.md) |

## Runtime baseline

- The default and maximum context window is 1M tokens.
- Anthropic has not published a quality-degradation onset inside that
  window. A percentage is capacity telemetry, not a quality guarantee.
- Treat warning/compaction thresholds as workload-specific operating heuristics.
  Tune them from remaining work, retrieval quality, latency, and measured evals.
- Measure multi-agent cost and cache hit rate on the actual workload; do not carry
  universal percentages or multipliers forward from another model or harness.

## Four-Bucket Strategy

1. **Write**: Save context externally (scratchpads, files)
2. **Select**: Pull only relevant context (retrieval, filtering)
3. **Compress**: Reduce tokens while preserving info (summarization)
4. **Isolate**: Split across sub-agents (partitioning)

## Anti-Patterns

- Exhaustive context over curated context
- Critical info in middle positions
- No compaction triggers before limits
- Delegation used only to create context isolation, without an independent payoff
- Tools without clear descriptions

## Guidelines

1. Place critical info at beginning/end of context
2. Compact when projected remaining work, signal density, or runtime capacity calls
   for it; do not infer a quality cliff from a fixed percentage
3. Use sub-agents for independent context isolation when the coordination cost pays
4. Design tools with 4-question framework (what, when, inputs, returns)
5. Optimize for tokens-per-task, not tokens-per-request
6. Validate with probe-based evaluation
7. Monitor KV-cache hit rates in production
8. Start minimal, add complexity only when proven necessary

## Runtime Awareness

The system automatically injects usage awareness via PostToolUse hook:

```xml
<usage-awareness>
Claude Usage Limits: 5h=45%, 7d=32%
Context Window Usage: 67%
</usage-awareness>
```

**Operational indicators:**
- Warning thresholds are configurable heuristics, not published quality
  boundaries.
- Near-capacity alerts should account for the remaining task and the runtime's own
  compaction reserve before recommending a reset.

**Data Sources:**
- Usage limits: Anthropic OAuth API (`https://api.anthropic.com/api/oauth/usage`)
- Context window: Statusline temp file (`/tmp/ck-context-{session_id}.json`)

## Scripts

- [context_analyzer.py](./scripts/context_analyzer.py) - Context health analysis, degradation detection
- [compression_evaluator.py](./scripts/compression_evaluator.py) - Compression quality evaluation
