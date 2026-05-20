"""Integration tests for Fish Trail Tiered Memory v2 — server-level tool calls.

Tests the full server dispatch path: JSON-RPC message → handler → response,
verifying feature flag gating, handler registration, and end-to-end behavior.
"""

import json
import os
import tempfile
from pathlib import Path

import pytest

from server import ContextStateServer


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def clean_fish_trail_env():
    """Remove all FISH_TRAIL env vars to prevent cross-test pollution."""
    for key in list(os.environ.keys()):
        if key.startswith("FISH_TRAIL_"):
            del os.environ[key]
    yield
    for key in list(os.environ.keys()):
        if key.startswith("FISH_TRAIL_"):
            del os.environ[key]


@pytest.fixture
def base_dir(tmp_path: Path) -> str:
    """Create a minimal fish-trail base directory."""
    bd = str(tmp_path / ".petfish" / "fish-trail")
    os.makedirs(bd)
    # Create required subdirectories
    os.makedirs(os.path.join(bd, "topics"))
    os.makedirs(os.path.join(bd, "sessions"))
    return bd


def _write_config(base_dir: str, config: dict) -> None:
    """Write config.json to the base_dir."""
    config_path = os.path.join(base_dir, "config.json")
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(config, f)


def _tool_call_msg(tool_name: str, arguments: dict, msg_id: int = 1) -> dict:
    """Build a JSON-RPC tools/call message."""
    return {
        "method": "tools/call",
        "id": msg_id,
        "params": {"name": tool_name, "arguments": arguments},
    }


def _extract_result(response: dict) -> dict:
    """Extract parsed JSON from a successful tool call response."""
    assert "result" in response, f"Expected result in response, got: {response}"
    content = response["result"]["content"]
    assert len(content) == 1
    assert content[0]["type"] == "text"
    return json.loads(content[0]["text"])


def _is_error_response(response: dict) -> bool:
    """Check if a response is an error."""
    if "error" in response:
        return True
    result = response.get("result", {})
    return result.get("isError", False)


# ---------------------------------------------------------------------------
# Tests: Feature flag gating
# ---------------------------------------------------------------------------


class TestFeatureFlagGating:
    """Verify that get_memory_context is only registered when flags allow."""

    def test_v2_disabled_by_default(self, base_dir: str):
        """Without config, v2 flags default to disabled — handler not registered."""
        server = ContextStateServer(base_dir)
        assert server._memory_context is None
        assert "get_memory_context" not in server._handlers

    def test_v2_disabled_explicit(self, base_dir: str):
        """Explicit v2_enabled=false → handler not registered."""
        _write_config(base_dir, {"feature_flags": {"v2_enabled": False}})
        server = ContextStateServer(base_dir)
        assert server._memory_context is None
        assert "get_memory_context" not in server._handlers

    def test_v2_enabled_registers_handler(self, base_dir: str):
        """v2_enabled + subsystem flags → handler IS registered."""
        _write_config(
            base_dir,
            {
                "feature_flags": {
                    "v2_enabled": True,
                    "enable_continuous_detection": True,
                    "enable_budget_allocation": True,
                }
            },
        )
        server = ContextStateServer(base_dir)
        assert server._memory_context is not None
        assert "get_memory_context" in server._handlers

    def test_v2_enabled_but_no_subsystems(self, base_dir: str):
        """v2_enabled=true but no subsystem flags → memory_context_enabled=false."""
        _write_config(
            base_dir,
            {
                "feature_flags": {
                    "v2_enabled": True,
                    "enable_continuous_detection": False,
                    "enable_budget_allocation": False,
                }
            },
        )
        server = ContextStateServer(base_dir)
        assert server._memory_context is None
        assert "get_memory_context" not in server._handlers

    def test_tool_call_to_unregistered_handler_returns_error(self, base_dir: str):
        """Calling get_memory_context when not registered → unknown tool error."""
        server = ContextStateServer(base_dir)
        msg = _tool_call_msg("get_memory_context", {})
        response = server.handle_message(msg)
        assert response is not None
        assert "error" in response
        assert "Unknown tool" in response["error"]["message"]


# ---------------------------------------------------------------------------
# Tests: End-to-end tool calls
# ---------------------------------------------------------------------------


class TestGetMemoryContextToolCall:
    """End-to-end tool call tests for get_memory_context."""

    @pytest.fixture
    def v2_server(self, base_dir: str) -> ContextStateServer:
        """Server with v2 enabled."""
        _write_config(
            base_dir,
            {
                "feature_flags": {
                    "v2_enabled": True,
                    "enable_continuous_detection": True,
                    "enable_budget_allocation": True,
                }
            },
        )
        return ContextStateServer(base_dir)

    def test_empty_registry_returns_valid_response(self, v2_server: ContextStateServer):
        """With no topics, returns valid response with empty context."""
        msg = _tool_call_msg("get_memory_context", {})
        response = v2_server.handle_message(msg)
        assert response is not None
        assert not _is_error_response(response)
        result = _extract_result(response)
        assert "context_block" in result
        assert "tokens_used" in result
        assert "metadata" in result
        assert "cache_hit" in result
        assert result["tokens_used"] >= 0

    def test_with_topic_id_argument(self, v2_server: ContextStateServer):
        """Passing current_topic_id argument works without error."""
        msg = _tool_call_msg(
            "get_memory_context", {"current_topic_id": "nonexistent-topic"}
        )
        response = v2_server.handle_message(msg)
        assert response is not None
        assert not _is_error_response(response)
        result = _extract_result(response)
        assert result["tokens_used"] >= 0

    def test_with_budget_tokens_argument(self, v2_server: ContextStateServer):
        """Passing budget_tokens argument works."""
        msg = _tool_call_msg("get_memory_context", {"budget_tokens": 500})
        response = v2_server.handle_message(msg)
        assert response is not None
        assert not _is_error_response(response)

    def test_with_all_arguments(self, v2_server: ContextStateServer):
        """Passing all optional arguments works."""
        msg = _tool_call_msg(
            "get_memory_context",
            {
                "current_topic_id": "test-topic",
                "budget_tokens": 1000,
                "include_warm": False,
                "include_cold_summaries": True,
            },
        )
        response = v2_server.handle_message(msg)
        assert response is not None
        assert not _is_error_response(response)

    def test_metadata_structure(self, v2_server: ContextStateServer):
        """Metadata has expected fields."""
        msg = _tool_call_msg("get_memory_context", {})
        response = v2_server.handle_message(msg)
        result = _extract_result(response)
        meta = result["metadata"]
        assert "topics_active" in meta
        assert "topics_warm" in meta
        assert "topics_cold" in meta
        assert "topics_archived" in meta
        assert "pressure_level" in meta

    def test_cache_hit_false_on_first_call(self, v2_server: ContextStateServer):
        """First call should not be a cache hit."""
        msg = _tool_call_msg("get_memory_context", {})
        response = v2_server.handle_message(msg)
        result = _extract_result(response)
        assert result["cache_hit"] is False

    def test_repeated_calls_may_cache(self, v2_server: ContextStateServer):
        """Second identical call may return cache_hit=true."""
        msg = _tool_call_msg("get_memory_context", {})
        v2_server.handle_message(msg)
        response = v2_server.handle_message(msg)
        result = _extract_result(response)
        # Cache hit depends on implementation — just verify it's a valid bool
        assert isinstance(result["cache_hit"], bool)


# ---------------------------------------------------------------------------
# Tests: Server initialization and JSON-RPC
# ---------------------------------------------------------------------------


class TestServerInitialization:
    """Test server constructor and basic JSON-RPC operations with v2."""

    def test_initialize_message(self, base_dir: str):
        """Server responds to initialize correctly."""
        _write_config(
            base_dir,
            {
                "feature_flags": {
                    "v2_enabled": True,
                    "enable_continuous_detection": True,
                    "enable_budget_allocation": True,
                }
            },
        )
        server = ContextStateServer(base_dir)
        response = server.handle_message(
            {"method": "initialize", "id": 1, "params": {}}
        )
        assert response is not None
        result = response["result"]
        assert result["serverInfo"]["name"] == "fish-trail"

    def test_ping(self, base_dir: str):
        """Server responds to ping."""
        server = ContextStateServer(base_dir)
        response = server.handle_message({"method": "ping", "id": 99, "params": {}})
        assert response is not None
        assert response["id"] == 99

    def test_v2_graceful_degradation_on_init_failure(self, base_dir: str, monkeypatch):
        """If v2 modules fail to init, server still works normally."""
        _write_config(
            base_dir,
            {
                "feature_flags": {
                    "v2_enabled": True,
                    "enable_continuous_detection": True,
                    "enable_budget_allocation": True,
                }
            },
        )
        # Monkeypatch TopicRegistryV2 to raise on init
        import server as server_module

        if hasattr(server_module, "_HAS_MEMORY_V2") and server_module._HAS_MEMORY_V2:
            original_load = server_module.load_feature_flags

            def _failing_load(*args, **kwargs):
                raise RuntimeError("Simulated init failure")

            monkeypatch.setattr(server_module, "load_feature_flags", _failing_load)
            srv = ContextStateServer(base_dir)
            assert srv._memory_context is None
            assert "get_memory_context" not in srv._handlers
            # Other tools still work
            resp = srv.handle_message({"method": "ping", "id": 1, "params": {}})
            assert resp is not None


# ---------------------------------------------------------------------------
# Tests: Feature flags exposed via server
# ---------------------------------------------------------------------------


class TestFeatureFlagsAccess:
    """Test that feature flags are accessible from the server instance."""

    def test_flags_stored_on_server(self, base_dir: str):
        """Feature flags are stored on server._feature_flags."""
        _write_config(
            base_dir,
            {
                "feature_flags": {
                    "v2_enabled": True,
                    "enable_continuous_detection": True,
                    "enable_budget_allocation": True,
                }
            },
        )
        server = ContextStateServer(base_dir)
        assert server._feature_flags is not None
        assert server._feature_flags.v2_enabled is True
        assert server._feature_flags.enable_continuous_detection is True

    def test_flags_none_when_v2_not_available(self, base_dir: str, monkeypatch):
        """If _HAS_MEMORY_V2 is False, flags stay None."""
        import server as server_module

        monkeypatch.setattr(server_module, "_HAS_MEMORY_V2", False)
        srv = ContextStateServer(base_dir)
        assert srv._feature_flags is None
        assert srv._memory_context is None


# ---------------------------------------------------------------------------
# Tests: With topics in registry
# ---------------------------------------------------------------------------


class TestWithTopics:
    """Test get_memory_context when topics exist in registry."""

    @pytest.fixture
    def v2_server_with_topic(self, base_dir: str) -> ContextStateServer:
        """Server with v2 enabled and a topic in the v1 store."""
        _write_config(
            base_dir,
            {
                "feature_flags": {
                    "v2_enabled": True,
                    "enable_continuous_detection": True,
                    "enable_budget_allocation": True,
                }
            },
        )
        # Write a topic file directly to the v1 topics directory
        import json

        topics_dir = os.path.join(base_dir, "topics")
        os.makedirs(topics_dir, exist_ok=True)
        topic_data = {
            "id": "test-topic-001",
            "title": "Test Topic",
            "scope": "Integration testing",
            "status": "active",
            "tags": [],
        }
        with open(os.path.join(topics_dir, "test-topic-001.json"), "w") as f:
            json.dump(topic_data, f)

        server = ContextStateServer(base_dir)
        return server

    def test_context_with_existing_topic(
        self, v2_server_with_topic: ContextStateServer
    ):
        """With a topic in store, get_memory_context still works."""
        msg = _tool_call_msg("get_memory_context", {})
        response = v2_server_with_topic.handle_message(msg)
        assert response is not None
        assert not _is_error_response(response)
        result = _extract_result(response)
        # The v2 registry is separate from v1 store, so topics created via
        # topic_create go to v1 store, not v2 registry. This tests graceful handling.
        assert result["tokens_used"] >= 0
