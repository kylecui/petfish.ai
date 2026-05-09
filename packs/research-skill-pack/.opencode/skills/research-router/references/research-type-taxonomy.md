# Research Type Taxonomy

## Scientific Research
Research aimed at advancing knowledge through systematic investigation.

### Characteristics
- Hypothesis-driven or research-question-driven
- Requires literature review and gap analysis
- Methods must be reproducible
- Results must be falsifiable or verifiable
- Peer review is the quality standard

### Sub-types
- Empirical research (experiments, measurements)
- Theoretical research (models, proofs)
- Literature review / survey / meta-analysis
- Design science research (artifact + evaluation)

---

## Product / Design Research
Research aimed at understanding users, markets, and opportunities to inform product decisions.

### Characteristics
- User-centered or market-centered
- Evidence from interviews, analytics, feedback, competitive analysis
- Output informs product decisions, not academic publications
- Speed and actionability matter more than exhaustiveness

### Sub-types
- User research (interviews, surveys, usability)
- Market research (competitors, trends, sizing)
- Design research (prototyping, testing, iteration)
- Discovery research (problem space, JTBD, opportunities)

---

## Planning / Strategy Research
Research aimed at informing strategic decisions, policies, roadmaps, or organizational plans.

### Characteristics
- Environment and stakeholder driven
- Must handle high uncertainty
- Output is actionable plans or recommendations
- Multiple scenarios often required
- Political and organizational context matters

### Sub-types
- Environmental scanning (PESTLE, trends)
- Stakeholder analysis
- Scenario planning
- Policy research
- Technology assessment
- Roadmap development

---

## Learning Research
Research aimed at transforming learning intentions into structured, executable, and assessable learning plans.

### Characteristics
- Goal-driven: starts from a learning wish, ends with measurable capability
- Baseline-aware: assesses current knowledge before planning
- Resource-curated: finds, filters, and ranks learning materials
- Phase-structured: breaks learning into stages with checkpoints
- Practice-oriented: includes hands-on tasks, not just reading lists

### Sub-types
- Goal framing (learning brief, target capability, baseline assessment)
- Prerequisite mapping (knowledge dependencies, skill trees)
- Resource discovery (courses, docs, repos, mentors)
- Path design (phased roadmap with milestones)
- Practice planning (drills, labs, projects)
- Progress review (phase-based effectiveness checks)

---

## Decision Research
Research aimed at structuring complex decisions with weighted criteria, option comparison, and evidence-based recommendations.

### Characteristics
- Problem-first: starts by framing the decision question and constraints
- Criteria-driven: builds explicit evaluation dimensions with weights
- Multi-option: compares alternatives systematically
- Risk-aware: surfaces trade-offs, deal-breakers, and conditions
- Actionable: ends with a clear recommendation, not just analysis

### Sub-types
- Decision brief (problem framing, constraints, stakeholders)
- Criteria building (must-have vs nice-to-have, weight assignment)
- Option comparison (scoring matrix, sensitivity analysis)
- Recommendation (verdict with conditions, risks, and escape clauses)

---

## Risk-Procurement Research
Research aimed at evaluating adoption risks of vendors, tools, open-source projects, or technologies before commitment.

### Characteristics
- Due-diligence driven: systematic investigation before adoption
- Multi-dimensional: covers security, compliance, cost, and operational risk
- Vendor-aware: assesses organizational health, support, and lock-in
- Compliance-sensitive: checks regulatory, licensing, and privacy requirements
- TCO-focused: looks beyond purchase price to total cost of ownership

### Sub-types
- Risk brief (evaluation target, adoption scenario, risk boundary)
- Vendor/source diligence (organizational health, community, support)
- Security risk review (data flow, access control, supply chain)
- Compliance check (privacy, licensing, regulatory)
- TCO and operational risk (total cost, operational burden, migration cost)
- Adoption recommendation (go/no-go/conditional verdict)

---

## Experience-Event Research
Research aimed at designing, planning, and executing events, trips, or experiences with participant-centered optimization.

### Characteristics
- Experience-centered: optimizes for participant satisfaction and outcomes
- Logistics-aware: covers venue, schedule, transport, and contingencies
- Risk-managed: identifies and mitigates event-specific risks
- Runbook-oriented: produces executable checklists, not just plans
- Adaptable: supports conferences, training, travel, and custom events via adapters

### Sub-types
- Experience brief (goals, audience, constraints, success criteria)
- Venue/destination research (location evaluation, comparison)
- Schedule/itinerary planning (time blocks, contingencies, pacing)
- Participant experience design (journey mapping, touchpoint optimization)
- Logistics and risk planning (transport, accommodation, weather, backup plans)
- Event runbook (executable checklists with owners and timing)

---

## Adapters
Lightweight domain enhancers that inject domain-specific fields and checklists into main research chains.

### Characteristics
- SKILL.md-only: no scripts, schemas, or references
- Not independently triggered: injected by the router into a chain
- Domain-specific: adds checklists, fields, and gotchas for a particular domain
- Composable: multiple adapters can apply to the same chain

### Available Adapters
- Travel adapter (visa, weather, transport, insurance, packing)
- Conference adapter (CFP, speakers, AV, registration, networking)
- Training-event adapter (learning goals, labs, certification, feedback)
- Content-selection adapter (preferences, ratings, availability, curation)

---

## Mixed Research
When a task combines multiple types.

### Signals
- "研究一下这个技术方向，评估能不能做成产品" → Scientific + Product
- "调研行业现状，形成战略方案" → Planning + Product
- "做文献综述，然后设计实验" → Scientific (pure)
- "分析竞品，制定路线图" → Product + Planning
- "我想学X，帮我找资料和制定计划" → Learning (pure)
- "选A还是B，帮我分析利弊" → Decision (pure)
- "评估这个开源项目能不能用" → Risk-Procurement (pure)
- "帮我规划团建活动" → Experience-Event (pure)
- "学习这个技术然后评估能不能引入" → Learning + Risk-Procurement
- "调研供应商并制定采购路线图" → Risk-Procurement + Planning
