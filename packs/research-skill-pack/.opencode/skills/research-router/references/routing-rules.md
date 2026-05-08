# Research Routing Rules

## Classification Matrix

| Signal | Scientific | Product | Planning | Learning | Decision | Risk-Procurement | Experience-Event |
|---|---|---|---|---|---|---|---|
| "论文/paper/literature" | ✓ | | | | |
| "竞品/competitor/market" | | ✓ | | | |
| "规划/strategy/roadmap" | | | ✓ | | |
| "用户/user/interview" | | ✓ | | | |
| "环境扫描/PESTLE/stakeholder" | | | ✓ | | |
| "情景规划/scenario/policy" | | | ✓ | | |
| "技术评估/TRL/roadmap" | | | ✓ | | |
| "实验/experiment/hypothesis" | ✓ | | | | |
| "产品机会/MVP/JTBD" | | ✓ | | | |
| "文献综述/gap分析" | ✓ | | | | |
| "学习/learning/goal/path" | | | | ✓ | |
| "决策/decision/criteria/option" | | | | | ✓ |
| "风险/risk/vendor/compliance/TCO" | | | | | | ✓ | |
| "活动/event/travel/venue/itinerary" | | | | | | | ✓ |

## Complexity Assessment

| Indicator | Light Route | Full Route |
|---|---|---|
| Single focused question | ✓ | |
| Multiple sub-questions | | ✓ |
| Cross-domain | | ✓ |
| Long-term project | | ✓ |
| Report as deliverable | | ✓ |
| Quick fact check | ✓ | |

## Default Skill Chains

### Scientific (Full)
research-brief-framer → research-source-discovery → research-literature-access → research-note-capture → research-insight-log → research-evidence-ledger → research-synthesis → research-report-writer → research-quality-reviewer

### Product (Full)
research-brief-framer → research-source-discovery → research-note-capture → research-insight-log → research-evidence-ledger → research-synthesis → research-report-writer → research-quality-reviewer

### Planning (Full)
research-brief-framer → planning-environment-scanner → planning-stakeholder-analyst → planning-scenario-planner → planning-policy-researcher → planning-technology-assessor → planning-roadmap-developer → research-evidence-ledger → research-synthesis → research-report-writer → research-quality-reviewer

### Learning (Full)
learning-goal-framer → learning-resource-discovery → learning-path-designer → research-evidence-ledger → research-synthesis → research-report-writer → research-quality-reviewer

### Decision (Full)
decision-brief-framer → decision-criteria-builder → option-comparison-matrix → decision-recommendation → research-evidence-ledger → research-synthesis → research-report-writer → research-quality-reviewer

### Risk-Procurement (Full)
risk-research-brief → vendor-source-diligence → security-risk-review → compliance-check → tco-operational-risk → adoption-recommendation → research-evidence-ledger → research-synthesis → research-report-writer → research-quality-reviewer

### Experience-Event (Full)
experience-brief-framer → venue-destination-research → schedule-itinerary-planner → logistics-risk-planner → event-runbook-writer → research-evidence-ledger → research-synthesis → research-report-writer → research-quality-reviewer

### Light Route (any type)
research-brief-framer → research-source-discovery → research-evidence-ledger → research-report-writer

## Mixed Research

When a task spans multiple types:
1. Identify the primary type (drives main structure)
2. Identify secondary types (inform specific sections)
3. Create separate evidence streams per type
4. Merge at synthesis stage

## Adapter Routing

Adapters are lightweight domain enhancers. They do NOT replace main skill chains — they inject domain-specific fields and checklists into existing flows.

| Signal | Adapter | Enhances |
|---|---|---|
| "旅行/trip/vacation/travel itinerary" | travel-adapter | Experience-Event chain |
| "会议/conference/workshop/CFP/speaker" | conference-adapter | Experience-Event chain |
| "培训/training/workshop delivery/lab training" | training-event-adapter | Experience-Event chain |
| "内容推荐/content selection/看什么/what to watch" | content-selection-adapter | Decision chain |

### Adapter Usage Pattern
1. Router detects domain signal → activates adapter
2. Adapter injects domain fields into the brief
3. Main chain proceeds with enriched input
4. Adapter adds domain-specific verification at runbook/recommendation stage
