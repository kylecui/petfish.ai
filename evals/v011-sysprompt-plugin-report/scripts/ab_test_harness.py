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
MODEL = os.environ.get("AB_MODEL", "github-copilot/claude-sonnet-4")

# Multi-topic conversation sequence designed to trigger compaction.
# We interleave 3 topics with verbose requests to fill context window.
# Each message asks for detailed code/config output to maximize token usage.
CONVERSATION_SEQUENCE: list[dict[str, str]] = [
    # --- Round 1: Initial setup per topic ---
    {
        "topic": "python-setup",
        "message": "I'm setting up a new Python project called 'data-pipeline'. "
        "It needs to use uv for dependency management, have a src/ layout, "
        "and include pytest for testing. Show me the COMPLETE directory tree "
        "and the full pyproject.toml with all sections filled out. Include "
        "dependencies: httpx>=0.27, pydantic>=2.0, structlog. Dev deps: "
        "pytest>=8.0, pytest-asyncio>=0.24, ruff>=0.8. Include [tool.ruff] "
        "and [tool.pytest.ini_options] sections.",
    },
    {
        "topic": "database",
        "message": "I need to design a PostgreSQL schema for a multi-tenant SaaS app. "
        "Each tenant has users, projects, and tasks. Write the COMPLETE SQL "
        "migration file with: all CREATE TABLE statements with proper types, "
        "constraints, indexes, foreign keys, CHECK constraints, DEFAULT values, "
        "and comments. Include an audit_log table. Use UUID primary keys. "
        "Add created_at/updated_at triggers.",
    },
    {
        "topic": "cicd",
        "message": "I need a GitHub Actions CI/CD pipeline for the data-pipeline "
        "project. Write the COMPLETE .github/workflows/ci.yml with: "
        "lint job (ruff check + format), test job (pytest with coverage), "
        "build job (Docker multi-stage build, push to GHCR with SHA/latest/semver tags), "
        "deploy-staging (helm upgrade on push to main), "
        "deploy-production (manual approval + helm upgrade on release tags), "
        "Slack notifications on failure and success. Include all env vars, "
        "secrets references, and matrix strategies.",
    },
    # --- Round 2: Detailed implementation ---
    {
        "topic": "python-setup",
        "message": "Write the COMPLETE src/data_pipeline/cli.py with a click-based "
        "CLI. Commands: 'run' (accepts --config, --dry-run, --workers), "
        "'validate' (validates config file, prints errors), 'status' (shows "
        "running pipeline status from a PID file). Include full error handling "
        "with structlog, proper exit codes, and docstrings. Show the entire file.",
    },
    {
        "topic": "database",
        "message": "Write the COMPLETE row-level security policies for the schema. "
        "Include: RLS policies for every table, a set_tenant() function, "
        "app_user role setup, a PgBouncer configuration file (pgbouncer.ini) "
        "with transaction-mode pooling, and a connection helper in Python "
        "using psycopg with proper tenant context setting. Show all SQL and "
        "the Python connection manager class.",
    },
    {
        "topic": "cicd",
        "message": "Write the COMPLETE Dockerfile for the data-pipeline project. "
        "Use multi-stage build: builder stage with uv for deps, runtime stage "
        "with minimal Python image. Include health check, non-root user, "
        "proper COPY ordering for layer caching, and .dockerignore. "
        "Also write a docker-compose.yml for local development with: "
        "the app, PostgreSQL 16, Redis, and PgBouncer services.",
    },
    # --- Round 3: Testing & config ---
    {
        "topic": "python-setup",
        "message": "Write COMPLETE test files: tests/conftest.py with fixtures "
        "for config, temp dirs, mock HTTP responses. tests/test_cli.py "
        "testing all three CLI commands with click.testing.CliRunner. "
        "Include parametrized tests, error cases, and edge cases. "
        "Show full files with all imports.",
    },
    {
        "topic": "database",
        "message": "Write a COMPLETE database migration management setup. "
        "Include: alembic.ini, alembic/env.py configured for async with "
        "multi-tenant awareness, an initial migration file, and a seed "
        "data script that creates a demo tenant with sample users, "
        "projects, and tasks. Show all files in full.",
    },
    {
        "topic": "cicd",
        "message": "Write COMPLETE Kubernetes manifests for the data-pipeline: "
        "Deployment (with resource limits, probes, env from secrets), "
        "Service, Ingress with TLS, HPA (auto-scaling on CPU/memory), "
        "ConfigMap, Secret template, and a Helm values.yaml with "
        "staging and production overrides. Show all YAML files.",
    },
    # --- Round 4: Advanced features ---
    {
        "topic": "python-setup",
        "message": "Add a src/data_pipeline/config.py with a Pydantic Settings "
        "class that reads from env vars and .env files. Fields: database_url, "
        "redis_url, log_level, workers, batch_size, retry_count, "
        "slack_webhook_url (optional), sentry_dsn (optional). Include "
        "validators, model_config, and a COMPLETE example .env file. "
        "Also add src/data_pipeline/logging.py with structlog configuration.",
    },
    {
        "topic": "database",
        "message": "Write a COMPLETE Python repository pattern for the database. "
        "Include: base repository class, TenantRepository, UserRepository, "
        "ProjectRepository, TaskRepository, AuditLogRepository. Each with "
        "CRUD methods, proper SQL queries with parameterization, and "
        "connection pool management. Use psycopg3 async. Show full code.",
    },
    {
        "topic": "cicd",
        "message": "Add a COMPLETE monitoring and observability setup to the CI/CD. "
        "Write: a Prometheus ServiceMonitor, Grafana dashboard JSON "
        "for key metrics (request latency, error rate, DB pool usage, "
        "queue depth), AlertManager rules for SLO breaches, and a "
        "PagerDuty integration config. Show all files.",
    },
    # --- Round 5: Integration & polish ---
    {
        "topic": "python-setup",
        "message": "Write src/data_pipeline/pipeline.py — the main pipeline "
        "orchestrator. It should: read config, connect to DB and Redis, "
        "run tasks in parallel using asyncio, handle graceful shutdown "
        "on SIGTERM/SIGINT, implement retry with exponential backoff, "
        "and report metrics. Include the COMPLETE file with all imports, "
        "type hints, docstrings, and error handling.",
    },
    {
        "topic": "database",
        "message": "Write COMPLETE database performance optimization SQL: "
        "EXPLAIN ANALYZE examples for common queries, indexes for "
        "the most frequent access patterns, a pg_stat_statements "
        "monitoring query, a vacuum/analyze maintenance script, "
        "and partition strategy for the audit_log table by month. "
        "Include all SQL statements.",
    },
    {
        "topic": "cicd",
        "message": "Write a COMPLETE end-to-end test workflow for CI: "
        "a docker-compose.test.yml that spins up all services, "
        "runs integration tests against real PostgreSQL and Redis, "
        "generates coverage reports, and tears down. Include the "
        "GitHub Actions job definition and a test_integration.py "
        "with real HTTP endpoint tests using httpx.",
    },
    # --- Round 6: More depth to push context ---
    {
        "topic": "python-setup",
        "message": "Write src/data_pipeline/middleware.py with: request "
        "tracing middleware (generates trace IDs), rate limiting middleware, "
        "authentication middleware (validates JWT tokens), and tenant "
        "context middleware (extracts tenant from JWT, sets DB context). "
        "COMPLETE file with all classes and type hints.",
    },
    {
        "topic": "database",
        "message": "Design and write a COMPLETE event sourcing extension for the "
        "audit_log. Include: event store table, aggregate reconstruction "
        "function, snapshot table, event replay utility, and a Python "
        "EventStore class with publish/subscribe using PostgreSQL LISTEN/NOTIFY. "
        "Show all SQL and Python code.",
    },
    {
        "topic": "cicd",
        "message": "Write a COMPLETE chaos engineering test suite: a Litmus "
        "ChaosEngine manifest for pod kill, network delay, and disk fill "
        "experiments. Include a GitHub Actions workflow that runs chaos "
        "tests against staging after each deploy, validates SLO metrics "
        "during chaos, and auto-rolls-back if SLOs are breached. "
        "Show all YAML and the validation script.",
    },
    # --- Round 7: Cross-topic recap (final) ---
    {
        "topic": "python-setup",
        "message": "Give me a COMPLETE summary of every file we created for "
        "the data-pipeline project. List each file path and a one-line "
        "description of what it contains.",
    },
    {
        "topic": "database",
        "message": "Give me a COMPLETE summary of the entire database design. "
        "List all tables, their relationships, all indexes, all RLS "
        "policies, and all monitoring/maintenance scripts we created.",
    },
    {
        "topic": "cicd",
        "message": "Give me a COMPLETE summary of the entire CI/CD and "
        "infrastructure setup. List all workflows, Kubernetes manifests, "
        "monitoring configs, and security measures we implemented.",
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
    session_id: str = ""
    per_message_tokens: list[dict] = field(default_factory=list)


# ---------------------------------------------------------------------------
# OpenCode Server Client
# ---------------------------------------------------------------------------


class OpenCodeClient:
    def __init__(self, port: int, password: str):
        self.base_url = f"http://localhost:{port}"
        self.client = httpx.Client(
            base_url=self.base_url,
            auth=("opencode", password),
            timeout=httpx.Timeout(900.0, connect=10.0),
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
            json={"parts": [{"type": "text", "text": content}]},
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
        info = msg.get("info", {})
        if info.get("role") != "assistant":
            continue
        tokens = info.get("tokens")
        if tokens:
            stats.add(tokens)
    return stats


def count_compactions(messages: list[dict]) -> int:
    """Count compaction messages (role=user with compaction parts)."""
    count = 0
    for msg in messages:
        info = msg.get("info", {})
        if info.get("role") != "user":
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
        consecutive_failures = 0
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
                consecutive_failures = 0
            except Exception as e:
                print(f" ✗ ({e})")
                result.errors.append(f"Message {i + 1} failed: {e}")
                consecutive_failures += 1
                if consecutive_failures >= 5:
                    print("  ⚠ 5 consecutive failures, stopping conversation")
                    break

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
        result.session_id = session_id
        result.per_message_tokens = []
        for msg in messages:
            info = msg.get("info", {})
            if info.get("role") != "assistant":
                continue
            t = info.get("tokens", {})
            cache = t.get("cache", {})
            result.per_message_tokens.append(
                {
                    "input": t.get("input", 0),
                    "output": t.get("output", 0),
                    "cache_read": cache.get("read", 0),
                    "effective_ctx": t.get("input", 0) + cache.get("read", 0),
                }
            )

    finally:
        # Preserve sessions for post-hoc analysis
        print(f"  Session preserved: {session_id}")

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
    baseline_peak = max(
        (m["effective_ctx"] for m in baseline.per_message_tokens), default=0
    )
    plugin_peak = max(
        (m["effective_ctx"] for m in plugin.per_message_tokens), default=0
    )
    print(f"{'Peak Context Window':<25} {baseline_peak:>12,} {plugin_peak:>12,}")
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
    def _variant_report(result: TestResult) -> dict:
        peak_ctx = max(
            (m["effective_ctx"] for m in result.per_message_tokens), default=0
        )
        return {
            "tokens": {
                "input": result.token_stats.total_input,
                "output": result.token_stats.total_output,
                "reasoning": result.token_stats.total_reasoning,
                "cache_read": result.token_stats.total_cache_read,
                "cache_write": result.token_stats.total_cache_write,
                "total": result.token_stats.total,
            },
            "messages": result.token_stats.message_count,
            "compactions": result.compaction_count,
            "wall_time_s": round(result.wall_time_seconds, 1),
            "errors": result.errors,
            "recall": result.recall_scores,
            "session_id": result.session_id,
            "peak_context_window": peak_ctx,
            "per_message_tokens": result.per_message_tokens,
        }

    report = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "model": MODEL,
        "baseline": _variant_report(baseline),
        "plugin": _variant_report(plugin),
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
