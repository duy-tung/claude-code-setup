#!/usr/bin/env python3
"""
Context Analyzer - Health analysis and degradation detection for agent contexts.

Usage:
    python context_analyzer.py analyze <context_file>
    python context_analyzer.py budget --system 2000 --tools 1500 --docs 3000 --history 5000
"""

import argparse
import json
import math
import os
import re
import sys
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

MAX_FILE_SIZE_MB = 100
DEFAULT_TOKEN_LIMIT = 1_000_000  # Claude Opus 5: default and maximum context window
DEFAULT_WARNING_UTILIZATION = 0.80  # Operational heuristic, not a quality boundary
DEFAULT_CRITICAL_UTILIZATION = 0.90


def load_json_file(path: str):
    """Load JSON file with proper error handling and size validation."""
    try:
        size_mb = os.path.getsize(path) / (1024 * 1024)
        if size_mb > MAX_FILE_SIZE_MB:
            print(f"Error: File too large ({size_mb:.1f}MB). Max {MAX_FILE_SIZE_MB}MB", file=sys.stderr)
            sys.exit(1)
        with open(path, encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: File not found: {path}", file=sys.stderr)
        sys.exit(1)
    except PermissionError:
        print(f"Error: Permission denied: {path}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in {path}: {e}", file=sys.stderr)
        sys.exit(1)


class HealthStatus(Enum):
    HEALTHY = "healthy"
    WARNING = "warning"
    DEGRADED = "degraded"
    CRITICAL = "critical"


@dataclass
class ContextAnalysis:
    total_tokens: int
    token_limit: int
    utilization: float
    health_status: HealthStatus
    health_score: float
    degradation_risk: float
    poisoning_risk: float
    warning_utilization: float
    critical_utilization: float
    recommendations: list = field(default_factory=list)


def estimate_tokens(text: str) -> int:
    """Estimate token count (~4 chars per token for English)."""
    return len(text) // 4


def estimate_message_tokens(messages: list) -> int:
    """Estimate tokens in message list."""
    total = 0
    for msg in messages:
        if isinstance(msg, dict):
            content = msg.get("content", "")
            total += estimate_tokens(str(content))
            # Add overhead for role, metadata
            total += 10
        else:
            total += estimate_tokens(str(msg))
    return total


def measure_attention_distribution(context_length: int, sample_size: int = 100) -> list:
    """
    Simulate U-shaped attention distribution.
    Real implementation would extract from model attention weights.
    """
    attention = []
    for i in range(sample_size):
        position = i / sample_size
        # U-shaped curve: high at start/end, low in middle
        if position < 0.1:
            score = 0.9 - position * 2
        elif position > 0.9:
            score = 0.7 + (position - 0.9) * 2
        else:
            score = 0.3 + 0.1 * math.sin(position * math.pi)
        attention.append(score)
    return attention


def detect_lost_in_middle(messages: list, critical_keywords: list) -> list:
    """Identify critical items in attention-degraded regions."""
    if not messages:
        return []

    total = len(messages)
    warnings = []

    for i, msg in enumerate(messages):
        position = i / total
        content = str(msg.get("content", "") if isinstance(msg, dict) else msg)

        # Middle region (10%-90%)
        if 0.1 < position < 0.9:
            for keyword in critical_keywords:
                if keyword.lower() in content.lower():
                    warnings.append({
                        "position": i,
                        "position_pct": f"{position:.1%}",
                        "keyword": keyword,
                        "risk": "high" if 0.3 < position < 0.7 else "medium"
                    })
    return warnings


def detect_poisoning_patterns(messages: list) -> dict:
    """Detect potential context poisoning indicators."""
    error_patterns = [
        r"error", r"failed", r"exception", r"cannot", r"unable",
        r"invalid", r"not found", r"undefined", r"null"
    ]
    # Simple contradiction check - look for both positive and negative statements
    contradiction_keywords = [
        ("is correct", "is not correct"),
        ("should work", "should not work"),
        ("will succeed", "will fail"),
        ("is valid", "is invalid"),
    ]

    errors_found = []
    contradictions = []

    for i, msg in enumerate(messages):
        content = str(msg.get("content", "") if isinstance(msg, dict) else msg).lower()

        # Check error patterns
        for pattern in error_patterns:
            if re.search(pattern, content):
                errors_found.append({"position": i, "pattern": pattern})

        # Check for contradiction keywords (simplified)
        for pos_phrase, neg_phrase in contradiction_keywords:
            if pos_phrase in content and neg_phrase in content:
                contradictions.append({"position": i, "type": "self-contradiction"})

    total = max(len(messages), 1)
    return {
        "error_density": len(errors_found) / total,
        "contradiction_count": len(contradictions),
        "poisoning_risk": min(1.0, (len(errors_found) * 0.1 + len(contradictions) * 0.3))
    }


def calculate_health_score(
    utilization: float,
    degradation_risk: float,
    poisoning_risk: float,
    warning_utilization: float = DEFAULT_WARNING_UTILIZATION,
) -> float:
    """
    Calculate composite health score.
    1.0 = healthy, 0.0 = critical
    """
    score = 1.0
    # Capacity-pressure heuristic. Anthropic publishes no Opus 5 quality onset.
    if utilization > warning_utilization:
        score -= (utilization - warning_utilization) * 1.5
    # Degradation penalty
    score -= degradation_risk * 0.3
    # Poisoning penalty
    score -= poisoning_risk * 0.2
    return max(0.0, min(1.0, score))


def get_health_status(score: float) -> HealthStatus:
    """Map health score to status."""
    if score > 0.8:
        return HealthStatus.HEALTHY
    elif score > 0.6:
        return HealthStatus.WARNING
    elif score > 0.4:
        return HealthStatus.DEGRADED
    return HealthStatus.CRITICAL


def analyze_context(
    messages: list,
    token_limit: int = DEFAULT_TOKEN_LIMIT,
    critical_keywords: Optional[list] = None,
    warning_utilization: float = DEFAULT_WARNING_UTILIZATION,
    critical_utilization: float = DEFAULT_CRITICAL_UTILIZATION,
) -> ContextAnalysis:
    """
    Comprehensive context health analysis.

    Args:
        messages: List of context messages
        token_limit: Model's context window size
        critical_keywords: Keywords that should be at attention-favored positions

    Returns:
        ContextAnalysis with health metrics and recommendations
    """
    critical_keywords = critical_keywords or ["goal", "task", "important", "critical", "must"]

    # Calculate token utilization
    total_tokens = estimate_message_tokens(messages)
    utilization = total_tokens / token_limit

    # Check for lost-in-middle issues
    middle_warnings = detect_lost_in_middle(messages, critical_keywords)
    degradation_risk = min(1.0, len(middle_warnings) * 0.2)

    # Check for poisoning
    poisoning = detect_poisoning_patterns(messages)
    poisoning_risk = poisoning["poisoning_risk"]

    # Calculate health
    health_score = calculate_health_score(
        utilization, degradation_risk, poisoning_risk, warning_utilization
    )
    health_status = get_health_status(health_score)

    # Generate recommendations
    recommendations = []
    if utilization > critical_utilization:
        recommendations.append(
            "Context is above the configured critical capacity heuristic. "
            "Compact if projected remaining work will exceed the available window."
        )
    elif utilization > warning_utilization:
        recommendations.append(
            "Context is above the configured warning heuristic. Review signal "
            "density and projected remaining work."
        )

    if middle_warnings:
        recommendations.append(f"Found {len(middle_warnings)} critical items in middle region. "
                               "Consider moving to beginning/end.")

    if poisoning_risk > 0.3:
        recommendations.append("High poisoning risk detected. Review recent tool outputs for errors.")

    if health_status == HealthStatus.CRITICAL:
        recommendations.append("CRITICAL: Consider context reset with clean state.")

    return ContextAnalysis(
        total_tokens=total_tokens,
        token_limit=token_limit,
        utilization=utilization,
        health_status=health_status,
        health_score=health_score,
        degradation_risk=degradation_risk,
        poisoning_risk=poisoning_risk,
        warning_utilization=warning_utilization,
        critical_utilization=critical_utilization,
        recommendations=recommendations
    )


def calculate_budget(system: int, tools: int, docs: int, history: int,
                     buffer_pct: float = 0.15,
                     warning_utilization: float = DEFAULT_WARNING_UTILIZATION,
                     critical_utilization: float = DEFAULT_CRITICAL_UTILIZATION) -> dict:
    """Calculate context budget allocation."""
    subtotal = system + tools + docs + history
    buffer = int(subtotal * buffer_pct)
    total = subtotal + buffer

    return {
        "allocation": {
            "system_prompt": system,
            "tool_definitions": tools,
            "retrieved_docs": docs,
            "message_history": history,
            "reserved_buffer": buffer
        },
        "total_budget": total,
        "warning_threshold": int(total * warning_utilization),
        "critical_threshold": int(total * critical_utilization),
        "recommendations": [
            ("Review projected context needs at "
             f"{int(total * warning_utilization):,} tokens"),
            ("Configured critical capacity at "
             f"{int(total * critical_utilization):,} tokens"),
            f"Reserved {buffer:,} tokens ({buffer_pct:.0%}) for responses"
        ]
    }


def main():
    parser = argparse.ArgumentParser(description="Context health analyzer")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Analyze command
    analyze_parser = subparsers.add_parser("analyze", help="Analyze context health")
    analyze_parser.add_argument("context_file", help="JSON file with messages array")
    analyze_parser.add_argument(
        "--limit",
        type=int,
        default=DEFAULT_TOKEN_LIMIT,
        help="Context-window token limit (default: 1,000,000 for Claude Opus 5)",
    )
    analyze_parser.add_argument("--keywords", nargs="+", help="Critical keywords to track")
    analyze_parser.add_argument(
        "--warning-threshold", type=float, default=DEFAULT_WARNING_UTILIZATION,
        help="Capacity warning heuristic as a fraction (default: 0.80)",
    )
    analyze_parser.add_argument(
        "--critical-threshold", type=float, default=DEFAULT_CRITICAL_UTILIZATION,
        help="Critical capacity heuristic as a fraction (default: 0.90)",
    )

    # Budget command
    budget_parser = subparsers.add_parser("budget", help="Calculate context budget")
    budget_parser.add_argument("--system", type=int, default=2000, help="System prompt tokens")
    budget_parser.add_argument("--tools", type=int, default=1500, help="Tool definitions tokens")
    budget_parser.add_argument("--docs", type=int, default=3000, help="Retrieved docs tokens")
    budget_parser.add_argument("--history", type=int, default=5000, help="Message history tokens")
    budget_parser.add_argument("--buffer", type=float, default=0.15, help="Buffer percentage")
    budget_parser.add_argument(
        "--warning-threshold", type=float, default=DEFAULT_WARNING_UTILIZATION
    )
    budget_parser.add_argument(
        "--critical-threshold", type=float, default=DEFAULT_CRITICAL_UTILIZATION
    )

    args = parser.parse_args()

    if not 0 < args.warning_threshold < args.critical_threshold <= 1:
        parser.error("thresholds must satisfy 0 < warning < critical <= 1")

    if args.command == "analyze":
        data = load_json_file(args.context_file)
        messages = data if isinstance(data, list) else data.get("messages", [])
        result = analyze_context(
            messages,
            args.limit,
            args.keywords,
            args.warning_threshold,
            args.critical_threshold,
        )
        print(json.dumps({
            "total_tokens": result.total_tokens,
            "token_limit": result.token_limit,
            "utilization": f"{result.utilization:.1%}",
            "health_status": result.health_status.value,
            "health_score": f"{result.health_score:.2f}",
            "warning_utilization": f"{result.warning_utilization:.0%}",
            "critical_utilization": f"{result.critical_utilization:.0%}",
            "degradation_risk": f"{result.degradation_risk:.2f}",
            "poisoning_risk": f"{result.poisoning_risk:.2f}",
            "recommendations": result.recommendations
        }, indent=2))

    elif args.command == "budget":
        result = calculate_budget(
            args.system,
            args.tools,
            args.docs,
            args.history,
            args.buffer,
            args.warning_threshold,
            args.critical_threshold,
        )
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
