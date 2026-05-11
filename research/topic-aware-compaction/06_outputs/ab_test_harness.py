# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "httpx>=0.27",
# ]
# ///
"""
A/B Test Harness for Topic-Aware Compaction Plugin

Drives two OpenCode Server instances (baseline vs plugin-enabled) through
identical multi-topic conversation sequences, then compares token usage
and summary quality.

Usage:
  1. Prepare two project directories:
     - test-baseline/  (no plugin in .opencode/plugin/)
     - test-plugin/    (with fish-trail-compaction.ts in .opencode/plugin/)
  2. Both must have fish-trail topic data in .petfish/fish-trail/
  3. Start servers:
     OPENCODE_SERVER_PASSWORD=test opencode serve --port 3100  (in test-baseline/)
     OPENCODE_SERVER_PASSWORD=test opencode serve --port 3200  (in test-plugin/)
  4. Run:
     uv run ab_test_harness.py

Environment Variables:
  AB_BASELINE_PORT  - Baseline server port (default: 3100)
  AB_PLUGIN_PORT    - Plugin server port (default: 3200)
  AB_PASSWORD       - Server password (default: "test")
  AB_MODEL          - Model to use (default: "anthropic/claude-sonnet-4-20250514")
"""

from __future__ import annotations

import json
import os
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path

import httpx

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

BASELINE_PORT = int(os.environ.get("AB_BASELINE_PORT", "3100"))
PLUGIN_PORT = int(os.environ.get("AB_PLUGIN_PORT", "3200"))
PASSWORD = os.environ.get("AB_PASSWORD", "test")
MODEL = os.environ.get("AB_MODEL", "anthropic/claude-sonnet-4-20250514")

# Multi-topic conversation sequence designed to trigger compaction.
# We interleave 3 topics with enough messages to exceed context limits.
CONVERSATION_SEQUENCE: list[dict[str, str]] = [
    # Topic 1: Python project setup
    {
        "topic": "python-setup",
        "message": "I'm setting up a new Python project called 'data-pipeline'. "
        "It needs to use uv for dependency management, have a src/ layout, "
        "and include pytest for testing. What's the recommended structure?",
    },
    {
        "topic": "python-setup",
        "message": "Good. Now add a pyproject.toml with these dependencies: "
        "httpx>=0.27, pydantic>=2.0, and structlog. "
        "Also add dev dependencies: pytest, pytest-asyncio, ruff.",
    },
    # Topic 2: Database design
    {
        "topic": "database",
        "message": "Switching topics. I need to design a PostgreSQL schema for "
        "a multi-tenant SaaS application. Each tenant has users, projects, "
        "and tasks. What schema would you recommend with proper isolation?",
    },
    {
        "topic": "database",
        "message": "Add audit logging to the schema. Every mutation to projects "
        "and tasks should be logged with who, when, what changed, and old/new values.",
    },
    # Topic 3: CI/CD pipeline
    {
        "topic": "cicd",
        "message": "New topic: I need a GitHub Actions CI/CD pipeline for the "
        "data-pipeline project. It should run on push to main and PRs. "
        "Steps: lint with ruff, test with pytest, build Docker image, "
        "push to GHCR. Use uv for Python setup.",
    },
    {
        "topic": "cicd",
        "message": "Add a deployment stage that deploys to staging on push to main, "
        "and to production only on release tags. Use Kubernetes with helm charts.",
    },
    # Return to Topic 1 (tests cross-topic recall)
    {
        "topic": "python-setup",
        "message": "Going back to the data-pipeline project. Can you add a "
        "src/data_pipeline/cli.py with a click-based CLI that has commands "
        "for 'run', 'validate', and 'status'? Use the structure we discussed.",
    },
    # More padding to push toward compaction threshold
    {
        "topic": "database",
        "message": "For the database schema, add row-level security policies "
        "so each tenant can only see their own data. Also add a connection "
        "pooling strategy using PgBouncer configuration.",
    },
    {
        "topic": "cicd",
        "message": "Add Slack notifications to the CI/CD pipeline — notify on "
        "failure and on successful production deployment. Use the Slack "
        "GitHub Action. Also add a manual approval step before prod deploy.",
    },
    {
        "topic": "python-setup",
        "message": "Add comprehensive error handling to the CLI. Each command "
        "should catch specific exceptions, log them with structlog, and "
        "return appropriate exit codes. Show me the updated cli.py.",
    },
]

# Recall test questions (asked after compaction should have triggered)
RECALL_QUESTIONS: list[dict[str, str]] = [
    {
        "topic": "python-setup",
        "question": "What dependencies did we add to pyproject.toml for the "
        "data-pipeline project? List all of them including dev dependencies.",
    },
    {
        "topic": "database",
        "question": "Summarize the PostgreSQL schema we designed. What tables "
        "exist and what security measures did we add?",
    },
    {
        "topic": "cicd",
        "question": "What CI/CD stages did we set up? What triggers each stage?",
    },
]


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------


@dataclass
class TokenStats:
    total_input: int = 0
    total_output: int = 0
    total_reasoning: int = 0
    total_cache_read: int = 0
    total_cache_write: int = 0
    message_count: int = 0

    @property
    def total(self) -> int:
        return self.total_input + self.total_output + self.total_reasoning

    def add(self, tokens: dict) -> None:
        self.total_input += tokens.get("input", 0)
        self.total_output += tokens.get("output", 0)
        self.total_reasoning += tokens.get("reasoning", 0)
        cache = tokens.get("cache", {})
        self.total_cache_read += cache.get("read", 0)
        self.total_cache_write += cache.get("write", 0)
        self.message_count += 1


@dataclass
class TestResult:
    variant: str  # "baseline" or "plugin"
    token_stats: TokenStats = field(default_factory=TokenStats)
    recall_scores: dict[str, str] = field(default_factory=dict)
    compaction_count: int = 0
    errors: list[str] = field(default_factory=list)
    wall_time_seconds: float = 0.0


# ---------------------------------------------------------------------------
# OpenCode Server Client
# ---------------------------------------------------------------------------


class OpenCodeClient:
    def __init__(self, port: int, password: str):
        self.base_url = f"http://localhost:{port}"
        self.client = httpx.Client(
            base_url=self.base_url,
            auth=("", password),
            timeout=httpx.Timeout(300.0, connect=10.0),
        )

    def health_check(self) -> bool:
        try:
            resp = self.client.get("/global/health")
            return resp.status_code == 200
        except httpx.ConnectError:
            return False

    def wait_for_ready(self, timeout: float = 60.0) -> bool:
        start = time.time()
        while time.time() - start < timeout:
            if self.health_check():
                return True
            time.sleep(1.0)
        return False

    def create_session(self) -> str:
        resp = self.client.post("/session")
        resp.raise_for_status()
        data = resp.json()
        return data["id"]

    def send_message(self, session_id: str, content: str) -> dict:
        """Send a message and wait for the response."""
        resp = self.client.post(
            f"/session/{session_id}/message",
            json={"content": content},
        )
        resp.raise_for_status()
        return resp.json()

    def get_messages(self, session_id: str) -> list[dict]:
        resp = self.client.get(f"/session/{session_id}/message")
        resp.raise_for_status()
        return resp.json()

    def delete_session(self, session_id: str) -> None:
        try:
            self.client.delete(f"/session/{session_id}")
        except Exception:
            pass

    def close(self) -> None:
        self.client.close()


# ---------------------------------------------------------------------------
# Test runner
# ---------------------------------------------------------------------------


def extract_token_stats(messages: list[dict]) -> TokenStats:
    """Sum token usage across all assistant messages."""
    stats = TokenStats()
    for msg in messages:
        if msg.get("role") != "assistant":
            continue
        tokens = msg.get("tokens")
        if tokens:
            stats.add(tokens)
    return stats


def count_compactions(messages: list[dict]) -> int:
    """Count compaction messages (role=user with compaction parts)."""
    count = 0
    for msg in messages:
        if msg.get("role") != "user":
            continue
        parts = msg.get("parts", [])
        if any(p.get("type") == "compaction" for p in parts):
            count += 1
    return count


def run_test(client: OpenCodeClient, variant: str) -> TestResult:
    """Run the full test sequence against one server instance."""
    result = TestResult(variant=variant)
    start_time = time.time()

    print(f"\n{'=' * 60}")
    print(f"  Running {variant.upper()} test")
    print(f"{'=' * 60}")

    # Check server health
    if not client.wait_for_ready(timeout=30):
        result.errors.append("Server not ready within 30s")
        return result

    # Create session
    try:
        session_id = client.create_session()
        print(f"  Session: {session_id}")
    except Exception as e:
        result.errors.append(f"Failed to create session: {e}")
        return result

    try:
        # Send conversation sequence
        for i, msg in enumerate(CONVERSATION_SEQUENCE):
            print(
                f"  [{i + 1}/{len(CONVERSATION_SEQUENCE)}] Topic: {msg['topic']}...",
                end="",
                flush=True,
            )
            try:
                client.send_message(session_id, msg["message"])
                print(" ✓")
            except Exception as e:
                print(f" ✗ ({e})")
                result.errors.append(f"Message {i + 1} failed: {e}")
                # Continue with remaining messages

        # Send recall questions
        print(f"\n  Recall questions:")
        for i, q in enumerate(RECALL_QUESTIONS):
            print(f"  [Q{i + 1}] Topic: {q['topic']}...", end="", flush=True)
            try:
                resp = client.send_message(session_id, q["question"])
                # Store the response text for manual review
                resp_text = ""
                if isinstance(resp, dict):
                    parts = resp.get("parts", [])
                    resp_text = " ".join(
                        p.get("text", "") for p in parts if p.get("type") == "text"
                    )
                result.recall_scores[q["topic"]] = resp_text[:500]  # truncate
                print(" ✓")
            except Exception as e:
                print(f" ✗ ({e})")
                result.errors.append(f"Recall Q{i + 1} failed: {e}")

        # Collect final token stats
        messages = client.get_messages(session_id)
        result.token_stats = extract_token_stats(messages)
        result.compaction_count = count_compactions(messages)

    finally:
        client.delete_session(session_id)

    result.wall_time_seconds = time.time() - start_time
    return result


# ---------------------------------------------------------------------------
# Report
# ---------------------------------------------------------------------------


def print_report(baseline: TestResult, plugin: TestResult) -> None:
    print(f"\n{'=' * 60}")
    print("  A/B TEST REPORT")
    print(f"{'=' * 60}\n")

    # Token comparison table
    print("Token Usage Comparison:")
    print(f"{'Metric':<25} {'Baseline':>12} {'Plugin':>12} {'Delta':>12} {'%':>8}")
    print("-" * 71)

    metrics = [
        (
            "Input Tokens",
            baseline.token_stats.total_input,
            plugin.token_stats.total_input,
        ),
        (
            "Output Tokens",
            baseline.token_stats.total_output,
            plugin.token_stats.total_output,
        ),
        (
            "Reasoning Tokens",
            baseline.token_stats.total_reasoning,
            plugin.token_stats.total_reasoning,
        ),
        (
            "Cache Read",
            baseline.token_stats.total_cache_read,
            plugin.token_stats.total_cache_read,
        ),
        (
            "Cache Write",
            baseline.token_stats.total_cache_write,
            plugin.token_stats.total_cache_write,
        ),
        ("TOTAL", baseline.token_stats.total, plugin.token_stats.total),
    ]
    for name, b, p in metrics:
        delta = p - b
        pct = (delta / b * 100) if b > 0 else 0
        sign = "+" if delta > 0 else ""
        print(f"{name:<25} {b:>12,} {p:>12,} {sign}{delta:>11,} {sign}{pct:>6.1f}%")

    print(f"\n{'Metric':<25} {'Baseline':>12} {'Plugin':>12}")
    print("-" * 49)
    print(
        f"{'Messages':<25} {baseline.token_stats.message_count:>12} {plugin.token_stats.message_count:>12}"
    )
    print(
        f"{'Compactions':<25} {baseline.compaction_count:>12} {plugin.compaction_count:>12}"
    )
    print(
        f"{'Wall Time (s)':<25} {baseline.wall_time_seconds:>12.1f} {plugin.wall_time_seconds:>12.1f}"
    )
    print(f"{'Errors':<25} {len(baseline.errors):>12} {len(plugin.errors):>12}")

    # Recall comparison
    print(f"\n\nRecall Responses (truncated to 500 chars):")
    for topic in ["python-setup", "database", "cicd"]:
        print(f"\n--- Topic: {topic} ---")
        print(f"  BASELINE: {baseline.recall_scores.get(topic, 'N/A')[:200]}...")
        print(f"  PLUGIN:   {plugin.recall_scores.get(topic, 'N/A')[:200]}...")

    # Errors
    if baseline.errors or plugin.errors:
        print(f"\n\nErrors:")
        for e in baseline.errors:
            print(f"  BASELINE: {e}")
        for e in plugin.errors:
            print(f"  PLUGIN: {e}")

    # Write full results to JSON
    report = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "model": MODEL,
        "baseline": {
            "tokens": {
                "input": baseline.token_stats.total_input,
                "output": baseline.token_stats.total_output,
                "reasoning": baseline.token_stats.total_reasoning,
                "cache_read": baseline.token_stats.total_cache_read,
                "cache_write": baseline.token_stats.total_cache_write,
                "total": baseline.token_stats.total,
            },
            "messages": baseline.token_stats.message_count,
            "compactions": baseline.compaction_count,
            "wall_time_s": round(baseline.wall_time_seconds, 1),
            "errors": baseline.errors,
            "recall": baseline.recall_scores,
        },
        "plugin": {
            "tokens": {
                "input": plugin.token_stats.total_input,
                "output": plugin.token_stats.total_output,
                "reasoning": plugin.token_stats.total_reasoning,
                "cache_read": plugin.token_stats.total_cache_read,
                "cache_write": plugin.token_stats.total_cache_write,
                "total": plugin.token_stats.total,
            },
            "messages": plugin.token_stats.message_count,
            "compactions": plugin.compaction_count,
            "wall_time_s": round(plugin.wall_time_seconds, 1),
            "errors": plugin.errors,
            "recall": plugin.recall_scores,
        },
    }

    report_path = Path(__file__).parent / "ab_test_results.json"
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False))
    print(f"\n\nFull results saved to: {report_path}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    print("Topic-Aware Compaction A/B Test Harness")
    print(f"Baseline: localhost:{BASELINE_PORT}")
    print(f"Plugin:   localhost:{PLUGIN_PORT}")
    print(f"Model:    {MODEL}")

    baseline_client = OpenCodeClient(BASELINE_PORT, PASSWORD)
    plugin_client = OpenCodeClient(PLUGIN_PORT, PASSWORD)

    try:
        # Run baseline first
        baseline_result = run_test(baseline_client, "baseline")

        # Then plugin
        plugin_result = run_test(plugin_client, "plugin")

        # Print comparison report
        print_report(baseline_result, plugin_result)

    finally:
        baseline_client.close()
        plugin_client.close()


if __name__ == "__main__":
    main()
