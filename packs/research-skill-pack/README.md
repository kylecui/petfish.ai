# Research Skill Pack

Research workbench for AI agents. Transforms vague research tasks into traceable, evidence-backed, quality-reviewed outputs.

## Skills (17)

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

## Research Types

- **Scientific**: Literature review, gap analysis, experiment design, paper writing
- **Product**: User research, competitor analysis, opportunity mapping, MVP validation
- **Planning**: Environment scanning, stakeholder analysis, scenario planning, roadmap

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
