# Changelog

## [0.2.0] - 2026-05-08

### Added
- Seeded fixture workspace for smoke tests (`tests/fixtures/smoke-workspace/`)
- Local smoke runner (`scripts/run_smoke.py`) — 5-step pipeline validation
- Trigger-eval harness (`scripts/run_trigger_evals.py`) — keyword matching with pass rate reporting
- CI integration for smoke tests and trigger evals

## [0.1.0] - 2026-05-08

### Added
- Initial MVP release with 10 core skills
- research-router: Research type classification and skill chain routing
- research-brief-framer: Structured research brief generation
- research-source-discovery: Source finding and registration
- research-literature-access: Legal full-text access management
- research-note-capture: Excerpt note capture with location and context
- research-insight-log: Ideas, hypotheses, and analogies capture
- research-evidence-ledger: Formal evidence with type classification
- research-synthesis: Evidence aggregation and analysis
- research-report-writer: Evidence-linked report generation
- research-quality-reviewer: Report quality audit and AI slop detection
- 7 JSON schemas with example payloads
- 9 Python scripts (uv-managed)
- Pack infrastructure (AGENTS.md, README, manifest)
