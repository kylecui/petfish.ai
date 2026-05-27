# Changelog

## [0.9.0] - 2026-05-09

### Added
- learning-prerequisite-mapper: Map prerequisite knowledge and learning dependencies
- learning-practice-planner: Design practice tasks, drills, labs, and projects for learning paths
- learning-progress-reviewer: Phase-based learning progress checks and effectiveness review
- participant-experience-designer: Design participant journey with touchpoint optimization for events

### Fixed
- Product skill quality parity: added references/ directories with methodology guides to all 5 product skills (product-user-research, product-competitor-analysis, product-opportunity-mapper, product-validation-planner, product-decision-brief) — closes #88
- evaluate_triggers.py --semantic flag: fixed path resolution to support both repo and installed layouts — closes #89
- research-type-taxonomy.md: added learning, decision, risk-procurement, experience-event, and adapter domain documentation

## [0.8.0] - 2026-05-09

### Added
- travel-adapter: Lightweight domain adapter for travel planning — visa, weather, transport, insurance checklists
- conference-adapter: Lightweight domain adapter for conference planning — CFP, speakers, AV, registration checklists
- training-event-adapter: Lightweight domain adapter for training workshops — learning goals, labs, certification checklists
- content-selection-adapter: Lightweight domain adapter for content selection — preferences, ratings, availability checklists
- Trigger evals for all 4 adapter skills (adapter-trigger-evals.json)

## [0.7.0] - 2026-05-09

### Added
- risk-research-brief: Define evaluation target, adoption scenario, and risk boundary
- vendor-source-diligence: Vendor and open source project due diligence with identity, stability, and lock-in checks
- security-risk-review: Security risk review covering data exposure, access control, supply chain, and prompt injection
- compliance-check: Compliance risk research for privacy, data residency, license, and regulation (not legal advice)
- tco-operational-risk: Total cost of ownership and operational risk assessment with exit planning
- adoption-recommendation: Final adoption recommendation with verdict, conditions, and decision log
- experience-brief-framer: Define experience or event goals, participants, constraints, and success criteria
- venue-destination-research: Research venues, destinations, and locations with evaluation criteria
- schedule-itinerary-planner: Design schedules and itineraries with transitions and contingencies
- logistics-risk-planner: Plan logistics and identify controllable and uncontrollable risks
- event-runbook-writer: Generate executable event runbook with before/during/after phases
- Trigger evals for all 11 risk-procurement and experience-event skills
- Smoke test coverage for risk-procurement and experience-event skill directories

## [0.6.0] - 2026-05-09

### Added
- learning-goal-framer: Convert learning wishes into structured goals and assessment criteria
- learning-resource-discovery: Find, filter, and rank learning resources by type and quality
- learning-path-designer: Design phased learning paths with stages, objectives, and checkpoints
- decision-brief-framer: Structure decision questions with constraints, preferences, and deal-breakers
- decision-criteria-builder: Build weighted decision criteria with must-have and nice-to-have tags
- option-comparison-matrix: Compare options against criteria with scoring and evidence links
- decision-recommendation: Generate final recommendation with conditions, risks, and validation steps
- Trigger evals for all 7 learning and decision skills
- Smoke test coverage for learning and decision skill directories

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
