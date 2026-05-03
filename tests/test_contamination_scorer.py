"""Unit tests for contamination_scorer.py."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

MODULE_DIR = (
    Path(__file__).resolve().parents[1] / "packs/context-router-skill/mcp/context-state"
)
sys.path.insert(0, str(MODULE_DIR))

from contamination_scorer import ContaminationScorer  # pyright: ignore[reportMissingImports]


@pytest.fixture
def scorer() -> ContaminationScorer:
    return ContaminationScorer()


def make_topic(
    *,
    title: str,
    scope: str,
    summary: str,
    tags: list[str],
    created_at: str | None = None,
    updated_at: str | None = None,
) -> dict:
    topic = {
        "title": title,
        "scope": scope,
        "summary": summary,
        "tags": tags,
    }
    if created_at is not None:
        topic["created_at"] = created_at
    if updated_at is not None:
        topic["updated_at"] = updated_at
    return topic


def short_code_topic() -> dict:
    return make_topic(
        title="FastAPI auth middleware",
        scope="python api authentication middleware for admin dashboard",
        summary="Implement request authentication for the internal admin API.",
        tags=["python", "api", "auth"],
    )


def deep_review_topic() -> dict:
    return make_topic(
        title="Release governance review",
        scope="qa qc release readiness evidence report for deployment rollout",
        summary=(
            "This review must document release evidence, risk acceptance, and QA/QC "
            "findings before rollout. " * 20
        ),
        tags=["qa", "qc", "release", "report", "risk", "audit"],
        created_at="2026-05-01T10:00:00Z",
        updated_at="2026-05-01T13:30:00Z",
    )


def high_risk_ops_topic() -> dict:
    return make_topic(
        title="Production cluster build plan",
        scope="build kubernetes deployment topology for production container rollout",
        summary=(
            "We must build the production deployment topology, lock rollback steps, "
            "track server constraints, and preserve every operations decision. " * 20
        ),
        tags=["deploy", "kubernetes", "ops", "container", "rollback", "server"],
        created_at="2026-05-01T08:00:00Z",
        updated_at="2026-05-01T12:30:00Z",
    )


def design_topic() -> dict:
    return make_topic(
        title="Onboarding motion redesign",
        scope="teardown figma animation layout for mobile onboarding experience",
        summary="Create a new motion language in Figma for the first-run mobile flow.",
        tags=["figma", "animation", "layout"],
    )


def test_score_returns_expected_shape_and_dimension_keys(scorer: ContaminationScorer):
    result = scorer.score(short_code_topic(), short_code_topic())

    assert set(result) == {"total", "level", "dimensions"}
    assert set(result["dimensions"]) == {
        "topic_distance",
        "goal_conflict",
        "term_overloading",
        "output_format_divergence",
        "history_bias",
    }


def test_score_total_and_dimension_values_stay_within_bounds(
    scorer: ContaminationScorer,
):
    result = scorer.score(high_risk_ops_topic(), design_topic())

    assert 0 <= result["total"] <= 100
    for value in result["dimensions"].values():
        assert 0 <= value <= 20


def test_low_level_assignment_for_very_similar_topics(scorer: ContaminationScorer):
    topic_a = short_code_topic()
    topic_b = make_topic(
        title="FastAPI auth middleware follow-up",
        scope="python api authentication middleware for admin dashboard",
        summary="Refine authentication checks for the same internal admin API.",
        tags=["python", "api", "auth"],
    )

    result = scorer.score(topic_a, topic_b)

    assert 0 <= result["total"] <= 30
    assert result["level"] == "low"


def test_medium_level_assignment_for_mixed_scope_topics(scorer: ContaminationScorer):
    topic_a = deep_review_topic()
    topic_b = make_topic(
        title="Async job scheduler",
        scope="python implement async task scheduler for webhook retries",
        summary="Build a Python scheduler that retries failed webhooks with backoff.",
        tags=["python", "async", "webhook"],
    )

    result = scorer.score(topic_a, topic_b)

    assert 31 <= result["total"] <= 60
    assert result["level"] == "medium"


def test_high_level_assignment_for_conflicting_distant_topics(
    scorer: ContaminationScorer,
):
    result = scorer.score(high_risk_ops_topic(), design_topic())

    assert 61 <= result["total"] <= 100
    assert result["level"] == "high"


def test_identical_scopes_produce_low_topic_distance(scorer: ContaminationScorer):
    topic_a = short_code_topic()
    topic_b = make_topic(
        title="Auth middleware cleanup",
        scope="python api authentication middleware for admin dashboard",
        summary="Clean up auth checks around the same API middleware.",
        tags=["python", "api", "middleware"],
    )

    result = scorer.score(topic_a, topic_b)

    assert result["dimensions"]["topic_distance"] == 0


def test_completely_different_scopes_produce_high_topic_distance(
    scorer: ContaminationScorer,
):
    topic_a = short_code_topic()
    topic_b = make_topic(
        title="Brand motion system",
        scope="figma animation palette typography for marketing landing page",
        summary="Define motion principles and typography for the landing page refresh.",
        tags=["figma", "animation", "typography"],
    )

    result = scorer.score(topic_a, topic_b)

    assert result["dimensions"]["topic_distance"] >= 18


def test_goal_conflict_keywords_raise_conflict_score(scorer: ContaminationScorer):
    topic_a = make_topic(
        title="User export endpoint",
        scope="add user export endpoint for billing admins",
        summary="Add a new export endpoint for billing administrators.",
        tags=["api", "billing", "export"],
    )
    topic_b = make_topic(
        title="Retire old export endpoint",
        scope="remove legacy user export endpoint from billing service",
        summary="Remove the old export endpoint after the migration.",
        tags=["api", "billing", "cleanup"],
    )

    result = scorer.score(topic_a, topic_b)

    assert result["dimensions"]["goal_conflict"] >= 10


def test_shared_terms_in_different_contexts_flag_term_overloading(
    scorer: ContaminationScorer,
):
    topic_a = make_topic(
        title="Python pipeline analytics",
        scope="optimize python pipeline for analytics etl jobs",
        summary="Python pipeline tunes pandas batching, parquet partitions, and warehouse ingest.",
        tags=["python", "pipeline", "etl"],
    )
    topic_b = make_topic(
        title="Python pipeline release delivery",
        scope="automate python pipeline for wheel publishing and dependency locks",
        summary="Python pipeline handles wheel signing, dependency locks, and virtualenv bootstrap.",
        tags=["python", "pipeline", "packaging"],
    )

    result = scorer.score(topic_a, topic_b)

    assert result["dimensions"]["term_overloading"] > 0


def test_same_format_family_has_zero_output_format_divergence(
    scorer: ContaminationScorer,
):
    topic_a = make_topic(
        title="Webhook retry logic",
        scope="python implement webhook retry function",
        summary="Implement retry logic for failed webhook deliveries in Python.",
        tags=["python", "function", "api"],
    )
    topic_b = make_topic(
        title="Webhook dead-letter consumer",
        scope="typescript implement dead letter queue consumer",
        summary="Implement a TypeScript consumer for failed webhook events.",
        tags=["typescript", "implement", "queue"],
    )

    result = scorer.score(topic_a, topic_b)

    assert result["dimensions"]["output_format_divergence"] == 0


def test_different_format_families_increase_output_format_divergence(
    scorer: ContaminationScorer,
):
    topic_a = make_topic(
        title="Webhook retry logic",
        scope="python implement webhook retry function",
        summary="Implement retry logic for failed webhook deliveries in Python.",
        tags=["python", "function", "api"],
    )
    topic_b = design_topic()

    result = scorer.score(topic_a, topic_b)

    assert result["dimensions"]["output_format_divergence"] > 0


def test_history_bias_is_higher_for_long_and_deep_previous_topics(
    scorer: ContaminationScorer,
):
    low_history = scorer.score(short_code_topic(), design_topic())
    high_history = scorer.score(deep_review_topic(), design_topic())

    assert low_history["dimensions"]["history_bias"] == 0
    assert (
        high_history["dimensions"]["history_bias"]
        > low_history["dimensions"]["history_bias"]
    )
    assert high_history["dimensions"]["history_bias"] >= 15


def test_explain_matches_score_and_adds_reasons(scorer: ContaminationScorer):
    topic_a = deep_review_topic()
    topic_b = make_topic(
        title="Async job scheduler",
        scope="python implement async task scheduler for webhook retries",
        summary="Build a Python scheduler that retries failed webhooks with backoff.",
        tags=["python", "async", "webhook"],
    )

    scored = scorer.score(topic_a, topic_b)
    explained = scorer.explain(topic_a, topic_b)

    assert explained["total"] == scored["total"]
    assert explained["level"] == scored["level"]
    assert explained["dimensions"] == scored["dimensions"]
    assert set(explained) == {"total", "level", "dimensions", "reasons"}
    assert set(explained["reasons"]) == set(scored["dimensions"])
    assert all(
        isinstance(reason, str) and reason for reason in explained["reasons"].values()
    )


def test_end_to_end_similar_topics_score_lower_than_very_different_topics(
    scorer: ContaminationScorer,
):
    similar_a = short_code_topic()
    similar_b = make_topic(
        title="FastAPI auth middleware review",
        scope="python api authentication middleware for admin dashboard",
        summary="Review the same admin API authentication middleware for edge cases.",
        tags=["python", "api", "auth"],
    )
    different_a = high_risk_ops_topic()
    different_b = design_topic()

    similar_result = scorer.score(similar_a, similar_b)
    different_result = scorer.score(different_a, different_b)

    assert similar_result["level"] == "low"
    assert different_result["level"] == "high"
    assert similar_result["total"] < different_result["total"]
