# Research Skill Pack

Research workbench for AI agents. Transforms vague research tasks into traceable, evidence-backed, quality-reviewed outputs.

## Skills (50)

| Skill | Purpose |
|---|---|
| `research-router` | Classify research type and recommend skill chain |
| `research-brief-framer` | Structure vague goals into research briefs |
| `research-source-discovery` | Find, filter, and register sources |
| `research-literature-access` | Legal full-text access with credential safety |
| `research-note-capture` | Extract and annotate key passages |
| `research-insight-log` | Capture ideas, hypotheses, and analogies |
| `research-evidence-ledger` | Build traceable evidence with type classification |
| `research-synthesis` | Aggregate evidence into findings and recommendations |
| `research-report-writer` | Write evidence-linked reports |
| `research-quality-reviewer` | Audit reports for evidence, logic, and AI slop |
| `research-citation-auditor` | Audit citation coverage and detect unsupported claims |
| `scientific-literature-review` | Literature search, screening, matrix, and systematic review |
| `scientific-gap-finder` | Identify verifiable research gaps and contribution directions |
| `scientific-methodology-designer` | Transform ideas into verifiable method designs |
| `scientific-experiment-planner` | Experiment design with baselines, ablation, and metrics |
| `scientific-paper-writer` | Paper skeleton and draft from evidence and analysis |
| `scientific-review-rebuttal` | Pre-submission self-review and reviewer rebuttal |
| `product-user-research` | User interviews, surveys, usability tests, and persona synthesis |
| `product-competitor-analysis` | Competitor matrix, positioning, SWOT, and market sizing |
| `product-opportunity-mapper` | JTBD, problem space mapping, and opportunity scoring |
| `product-validation-planner` | Hypothesis lists, MVP design, and validation experiments |
| `product-decision-brief` | Go/no-go/pivot decision briefs from research evidence |
| `planning-environment-scanner` | PESTLE scanning, trend radar, and signal identification |
| `planning-stakeholder-analyst` | Stakeholder mapping, influence/interest analysis, engagement |
| `planning-scenario-planner` | Alternative futures, implications matrix, robust strategies |
| `planning-policy-researcher` | Regulatory landscape, policy trends, compliance impact |
| `planning-technology-assessor` | Technology maturity (TRL), adoption readiness, strategic fit |
| `planning-roadmap-developer` | Strategic roadmap with milestones, dependencies, decision gates |
| `learning-goal-framer` | Convert learning wishes into structured goals and briefs |
| `learning-resource-discovery` | Find, filter, and rank learning resources by type |
| `learning-path-designer` | Design phased learning paths with checkpoints |
| `decision-brief-framer` | Structure decision questions with constraints and preferences |
| `decision-criteria-builder` | Build weighted criteria with must-have and deal-breaker tags |
| `option-comparison-matrix` | Compare options against criteria with scoring |
| `decision-recommendation` | Generate final recommendation with conditions and risks |
| `risk-research-brief` | Define evaluation target, adoption scenario, and risk boundary |
| `vendor-source-diligence` | Vendor and open source project due diligence |
| `security-risk-review` | Security risk review covering data, access, supply chain |
| `compliance-check` | Compliance risk research for privacy, license, regulation |
| `tco-operational-risk` | Total cost of ownership and operational risk assessment |
| `adoption-recommendation` | Final adoption recommendation with verdict and conditions |
| `experience-brief-framer` | Define experience or event goals, constraints, and criteria |
| `venue-destination-research` | Research venues, destinations, and locations |
| `schedule-itinerary-planner` | Design schedules and itineraries with contingencies |
| `logistics-risk-planner` | Plan logistics and identify risks with contingency plans |
| `event-runbook-writer` | Generate executable event runbook with checklists |
| `travel-adapter` | Travel domain adapter — visa, weather, transport, insurance checklists |
| `conference-adapter` | Conference domain adapter — CFP, speakers, AV, registration checklists |
| `training-event-adapter` | Training domain adapter — learning goals, labs, certification checklists |
| `content-selection-adapter` | Content selection adapter — preferences, ratings, availability checklists |

## Research Types

- **Scientific**: Literature review, gap analysis, experiment design, paper writing
- **Product**: User research, competitor analysis, opportunity mapping, MVP validation
- **Planning**: Environment scanning, stakeholder analysis, scenario planning, roadmap
- **Learning**: Goal framing, resource discovery, learning path design
- **Decision**: Decision brief, criteria building, option comparison, recommendation
- **Risk-Procurement**: Risk brief, vendor diligence, security review, compliance, TCO, adoption recommendation
- **Experience-Event**: Experience brief, venue research, schedule planning, logistics, event runbook
- **Adapters**: Lightweight domain adapters (travel, conference, training-event, content-selection) that enhance main research chains with domain-specific fields and checklists

## Install

```powershell
& ([scriptblock]::Create((irm https://raw.githubusercontent.com/kylecui/petfish.ai/master/remote-install.ps1))) -Pack research
```

```bash
curl -fsSL https://raw.githubusercontent.com/kylecui/petfish.ai/master/remote-install.sh | bash -s -- --pack research
```

## Quick Start

1. Install the pack
2. Say "帮我研究一下 [topic]" or "research [topic]"
3. The router classifies your task and recommends a skill chain
4. Follow the chain: brief → sources → notes → evidence → synthesis → report → review

## Core Principle

> Evidence first. Every claim traces back to a source. Generation and review are separated. Facts, inferences, and proposals are never mixed.

## Data Flow

```
User Request → Router → Brief → Sources → Literature Access → Notes → Insights → Evidence → Synthesis → Report → Quality Review
```

## Prerequisites

- Python 3.11+ with `uv`
- OpenCode or compatible agent environment

## License

Apache-2.0
