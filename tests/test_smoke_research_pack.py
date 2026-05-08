"""E2E smoke tests for research-skill-pack.

Exercises the full research pipeline on seeded fixture data:
  - workspace init & validation
  - schema validation
  - evidence linting
  - note linting
  - report quality gate
  - trigger eval harness

Closes #75, #76.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
PACK_ROOT = REPO_ROOT / "packs" / "research-skill-pack"
SCRIPTS_DIR = PACK_ROOT / "scripts"
SKILLS_DIR = PACK_ROOT / ".opencode" / "skills"
FIXTURES_DIR = PACK_ROOT / "tests" / "fixtures" / "smoke-workspace"


def _run(script: Path, args: list[str], timeout: int = 30) -> tuple[int, dict]:
    """Run a pack script and return (returncode, parsed_json_output)."""
    result = subprocess.run(
        [sys.executable, str(script)] + args,
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    try:
        output = json.loads(result.stdout)
    except (json.JSONDecodeError, ValueError):
        output = {"raw_stdout": result.stdout, "raw_stderr": result.stderr}
    return result.returncode, output


@pytest.fixture()
def workspace(tmp_path: Path) -> Path:
    """Copy seeded fixtures into a temp workspace."""
    ws = tmp_path / "workspace"
    shutil.copytree(FIXTURES_DIR, ws)
    return ws


# ---------------------------------------------------------------------------
# #76: Fixture integrity — seeded data exists and is well-formed
# ---------------------------------------------------------------------------


class TestFixtureIntegrity:
    def test_fixtures_exist(self):
        assert FIXTURES_DIR.is_dir(), "Seeded fixtures directory missing"

    def test_all_skills_have_skill_md(self):
        """Every skill listed in pack-manifest.json has a SKILL.md."""
        manifest = json.loads(
            (PACK_ROOT / "pack-manifest.json").read_text(encoding="utf-8")
        )
        for skill_name in manifest["skills"]:
            skill_md = SKILLS_DIR / skill_name / "SKILL.md"
            assert skill_md.is_file(), f"SKILL.md missing for {skill_name}"

    def test_brief_exists(self):
        assert (FIXTURES_DIR / "00_brief" / "research-brief.md").is_file()

    def test_source_index_valid_jsonl(self):
        path = FIXTURES_DIR / "01_sources" / "source-index.jsonl"
        assert path.is_file()
        lines = [l for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]
        assert len(lines) >= 1
        for line in lines:
            entry = json.loads(line)
            assert "source_id" in entry

    def test_excerpt_notes_valid_jsonl(self):
        path = FIXTURES_DIR / "02_notes" / "excerpt-notes.jsonl"
        assert path.is_file()
        lines = [l for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]
        assert len(lines) >= 1
        for line in lines:
            entry = json.loads(line)
            assert "note_id" in entry

    def test_evidence_ledger_valid_jsonl(self):
        path = FIXTURES_DIR / "03_evidence" / "evidence-ledger.jsonl"
        assert path.is_file()
        lines = [l for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]
        assert len(lines) >= 1
        for line in lines:
            entry = json.loads(line)
            assert "evidence_id" in entry

    def test_report_references_evidence(self):
        path = FIXTURES_DIR / "06_outputs" / "report.md"
        assert path.is_file()
        text = path.read_text(encoding="utf-8")
        assert "EV-" in text, "Report should reference at least one evidence ID"


# ---------------------------------------------------------------------------
# #75: E2E smoke — workspace validation
# ---------------------------------------------------------------------------


class TestWorkspaceValidation:
    def test_validate_workspace_passes(self, workspace: Path):
        rc, output = _run(
            SCRIPTS_DIR / "validate_research_workspace.py",
            ["--root", str(workspace)],
        )
        assert rc == 0, f"Workspace validation failed: {output}"
        assert output.get("status") == "pass"

    def test_init_then_validate(self, tmp_path: Path):
        """Init a fresh workspace, then validate it."""
        ws = tmp_path / "fresh"
        rc_init, out_init = _run(
            SCRIPTS_DIR / "init_research_project.py",
            ["--type", "product", "--name", "smoke-init-test", "--path", str(ws)],
        )
        assert rc_init == 0, f"Init failed: {out_init}"

        rc_val, out_val = _run(
            SCRIPTS_DIR / "validate_research_workspace.py",
            ["--root", str(ws)],
        )
        assert rc_val == 0, f"Validation failed after init: {out_val}"
        assert out_val.get("status") == "pass"


# ---------------------------------------------------------------------------
# #75: E2E smoke — schema validation
# ---------------------------------------------------------------------------


class TestSchemaValidation:
    def test_schemas_validate_against_examples(self):
        rc, output = _run(
            SCRIPTS_DIR / "validate_schemas.py",
            [
                "--schemas-dir",
                str(PACK_ROOT / "schemas"),
                "--examples-dir",
                str(PACK_ROOT / "schemas" / "examples"),
            ],
        )
        assert rc == 0, f"Schema validation failed: {output}"
        assert output.get("status") == "pass"


# ---------------------------------------------------------------------------
# #75: E2E smoke — evidence linting
# ---------------------------------------------------------------------------


class TestEvidenceLint:
    def test_lint_seeded_evidence(self, workspace: Path):
        rc, output = _run(
            SKILLS_DIR / "research-evidence-ledger" / "scripts" / "evidence_lint.py",
            ["--input", str(workspace / "03_evidence" / "evidence-ledger.jsonl")],
        )
        assert rc == 0, f"Evidence lint failed: {output}"
        assert output.get("status") == "pass"
        assert output.get("total_entries", 0) >= 1


# ---------------------------------------------------------------------------
# #75: E2E smoke — note linting
# ---------------------------------------------------------------------------


class TestNoteLint:
    def test_lint_seeded_notes(self, workspace: Path):
        rc, output = _run(
            SKILLS_DIR / "research-note-capture" / "scripts" / "note_lint.py",
            ["--input", str(workspace / "02_notes" / "excerpt-notes.jsonl")],
        )
        assert rc == 0, f"Note lint failed: {output}"
        assert output.get("status") == "pass"


# ---------------------------------------------------------------------------
# #75: E2E smoke — report quality gate
# ---------------------------------------------------------------------------


class TestReportQualityGate:
    def test_quality_gate_on_seeded_report(self, workspace: Path):
        rc, output = _run(
            SKILLS_DIR
            / "research-quality-reviewer"
            / "scripts"
            / "report_quality_gate.py",
            [
                "--report",
                str(workspace / "06_outputs" / "report.md"),
                "--ledger",
                str(workspace / "03_evidence" / "evidence-ledger.jsonl"),
            ],
        )
        assert rc == 0, f"Quality gate failed: {output}"
        assert output.get("status") == "pass"
        assert output.get("grade") in {"A", "B"}


# ---------------------------------------------------------------------------
# #75: E2E smoke — full pipeline via run_smoke.py
# ---------------------------------------------------------------------------


class TestFullPipeline:
    def test_smoke_runner_passes(self):
        rc, output = _run(
            SCRIPTS_DIR / "run_smoke.py",
            ["--fixtures", str(FIXTURES_DIR)],
            timeout=60,
        )
        assert rc == 0, f"Smoke runner failed: {output}"
        assert output.get("status") == "pass"
        assert output.get("failed", -1) == 0


# ---------------------------------------------------------------------------
# #74: Trigger eval harness
# ---------------------------------------------------------------------------


class TestTriggerEvals:
    def test_eval_files_exist(self):
        core = PACK_ROOT / "evals" / "trigger" / "core-trigger-evals.json"
        assert core.is_file(), "core-trigger-evals.json missing"

        scientific = PACK_ROOT / "evals" / "trigger" / "scientific-trigger-evals.json"
        assert scientific.is_file(), "scientific-trigger-evals.json missing"

        product = PACK_ROOT / "evals" / "trigger" / "product-trigger-evals.json"
        assert product.is_file(), "product-trigger-evals.json missing"

        router = SKILLS_DIR / "research-router" / "evals" / "trigger-evals.json"
        assert router.is_file(), "research-router trigger-evals.json missing"

    def test_trigger_harness_runs(self):
        rc, output = _run(
            SCRIPTS_DIR / "run_trigger_evals.py",
            [],
            timeout=30,
        )
        # We report results regardless — the harness itself should run
        assert isinstance(output, dict), f"Trigger harness didn't return JSON: {output}"
        assert "total_checks" in output
        assert output.get("total_checks", 0) > 0, "No trigger checks were executed"
