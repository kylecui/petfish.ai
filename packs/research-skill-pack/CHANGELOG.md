# Changelog

## [0.5.0] - 2026-05-09

### Added
- planning-environment-scanner: PESTLE environmental scanning, trend radar, and signal identification
- planning-stakeholder-analyst: Stakeholder mapping by influence/interest, engagement strategies
- planning-scenario-planner: Alternative futures development, implications matrix, robust strategies
- planning-policy-researcher: Regulatory landscape analysis, policy trends, compliance impact
- planning-technology-assessor: Technology maturity (TRL), adoption readiness, strategic fit
- planning-roadmap-developer: Strategic roadmap synthesis with milestones, dependencies, decision gates
- Trigger evals for all 6 planning skills (planning-trigger-evals.json)
- Smoke test coverage for planning skill directories

## [0.4.0] - 2026-05-09

### Added
- product-user-research: User interview, survey, usability test design and persona synthesis
- product-competitor-analysis: Competitor matrix, positioning, SWOT, and market sizing
- product-opportunity-mapper: JTBD framework, problem space mapping, opportunity scoring
- product-validation-planner: Hypothesis lists, MVP design, validation experiments, decision trees
- product-decision-brief: Go/no-go/pivot decision briefs from multi-source evidence
- Trigger evals for all 5 product skills (product-trigger-evals.json)
- Smoke test coverage for product skill directories

## [0.3.1] - 2026-05-08

### Fixed
- SKILL.md schema alignment for insight-log, evidence-ledger, source-discovery, and note-capture — added `## Schema` sections matching lint script requirements (closes #83, #82, #78)

## [0.3.0] - 2026-05-08

### Added
- research-citation-auditor: Citation audit and evidence mapping checker
- scientific-literature-review: Literature search, screening, matrix, and review generation
- scientific-gap-finder: Identify verifiable research gaps from literature matrix
- scientific-methodology-designer: Transform research ideas into verifiable method designs
- scientific-experiment-planner: Experiment design with hypothesis, variables, baselines, and ablation
- scientific-paper-writer: Paper skeleton and draft generation from evidence and analysis
- scientific-review-rebuttal: Pre-submission self-review and reviewer rebuttal support
- Trigger evals for all 7 new skills (scientific-trigger-evals.json)
- Smoke test coverage for new skill directories

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
