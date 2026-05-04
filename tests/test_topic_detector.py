import sys
from pathlib import Path

import pytest


sys.path.insert(
    0,
    str(
        Path(__file__).resolve().parents[1]
        / "packs"
        / "context-router-skill"
        / ".opencode"
        / "skills"
        / "context-router"
        / "mcp"
        / "context-state"
    ),
)

from topic_detector import TopicDetector  # pyright: ignore[reportMissingImports]


def topic(topic_id, title, scope=""):
    return {"id": topic_id, "title": title, "scope": scope}


@pytest.fixture
def detector():
    return TopicDetector()


@pytest.mark.parametrize(
    ("text", "expected_confidence"),
    [("重新开始，我们换个新上下文", 0.95), ("Let's start over from scratch.", 0.95)],
)
def test_detect_reset_signals(detector, text, expected_confidence):
    result = detector.detect(text, topic("current", "Current Topic"), [])

    assert result["relation"] == "reset"
    assert result["confidence"] == pytest.approx(expected_confidence)
    assert result["target_topic"] is None


@pytest.mark.parametrize(
    ("text", "expected_confidence"),
    [("这个话题做完了，可以归档", 0.80), ("We are done with this.", 0.80)],
)
def test_detect_archive_signals(detector, text, expected_confidence):
    current = topic("current", "Release Plan")

    result = detector.detect(text, current, [])

    assert result["relation"] == "archive"
    assert result["confidence"] == pytest.approx(expected_confidence)
    assert result["target_topic"] is None
    assert "Release Plan" in result["suggestion"]


def test_detect_switch_with_explicit_phrase_sets_target_topic(detector):
    current = topic("current", "当前话题")
    target = topic("deploy", "部署自动化", "CI CD 发布流程")

    result = detector.detect("切换到部署自动化", current, [current, target])

    assert result["relation"] == "switch"
    assert result["confidence"] == pytest.approx(0.85)
    assert result["target_topic"] == "deploy"
    assert "部署自动化" in result["suggestion"]


def test_detect_switch_by_fuzzy_topic_overlap_sets_target_topic(detector):
    current = topic("current", "Docker 部署", "容器编排与上线")
    target = topic(
        "pytest-workflow",
        "QA Board",
        "python pytest testing coverage workflow",
    )
    other = topic("other", "Frontend Polish", "css animation design")

    result = detector.detect(
        "Need help with python pytest testing coverage workflow details",
        current,
        [current, target, other],
    )

    assert result["relation"] == "switch"
    assert result["confidence"] == pytest.approx(0.60)
    assert result["target_topic"] == "pytest-workflow"
    assert "QA Board" in result["suggestion"]


@pytest.mark.parametrize(
    ("text", "expected_confidence"),
    [("把这两个话题合并一下", 0.70), ("Please merge these topics.", 0.70)],
)
def test_detect_merge_signals(detector, text, expected_confidence):
    result = detector.detect(text, topic("current", "Current Topic"), [])

    assert result["relation"] == "merge"
    assert result["confidence"] == pytest.approx(expected_confidence)
    assert result["target_topic"] is None


@pytest.mark.parametrize(
    ("text", "expected_confidence"),
    [("另外开一个子任务处理监控", 0.80), ("By the way, let's add monitoring.", 0.80)],
)
def test_detect_fork_signals(detector, text, expected_confidence):
    current = topic("current", "Observability")

    result = detector.detect(text, current, [])

    assert result["relation"] == "fork"
    assert result["confidence"] == pytest.approx(expected_confidence)
    assert result["target_topic"] is None
    assert "Observability" in result["suggestion"]


@pytest.mark.parametrize(
    ("text", "expected_confidence"),
    [
        ("把支付和报表桥接一下", 0.60),
        ("Can we bridge these auth and billing topics?", 0.60),
    ],
)
def test_detect_bridge_signals(detector, text, expected_confidence):
    result = detector.detect(text, topic("current", "Current Topic"), [])

    assert result["relation"] == "bridge"
    assert result["confidence"] == pytest.approx(expected_confidence)
    assert result["target_topic"] is None


def test_detect_continue_defaults_to_current_topic_context(detector):
    current = topic("current", "API Retries")

    result = detector.detect("Please explain the retry backoff strategy.", current, [])

    assert result["relation"] == "continue"
    assert result["confidence"] == pytest.approx(0.90)
    assert result["target_topic"] is None
    assert result["suggestion"] == 'Continue current topic "API Retries".'


def test_detect_continue_without_current_topic_uses_generic_suggestion(detector):
    result = detector.detect("Need a bit more detail here.", None, [])

    assert result["relation"] == "continue"
    assert result["confidence"] == pytest.approx(0.90)
    assert result["target_topic"] is None
    assert result["suggestion"] == "Continue in the current context."


def test_extract_keywords_handles_basic_tokenization(detector):
    keywords = detector._extract_keywords("Build API接口 with Python_3 and 数据 2024 a")

    assert keywords == {
        "build",
        "api",
        "接口",
        "接",
        "口",
        "python_3",
        "数据",
        "数",
        "据",
    }


def test_calculate_topic_overlap_returns_float_between_zero_and_one(detector):
    keywords = detector._extract_keywords("python testing pytest coverage")
    overlap = detector._calculate_topic_overlap(
        keywords,
        topic("pytest", "Pytest Coverage", "python unit testing workflow"),
    )

    assert isinstance(overlap, float)
    assert 0.0 <= overlap <= 1.0
    assert overlap == pytest.approx(4 / 6)
