# User Research Methods: Interview vs Survey vs Usability Test

## 1) Method selection starts from decision risk

Pick methods by the decision you need to make, not by team preference.

- If you need to discover unknown needs: start with interviews.
- If you need to quantify prevalence: run a survey.
- If you need to diagnose interaction friction: run usability tests.
- For high-stakes launches, combine all three in sequence.

Use this fast rule:

1. Unknown problem space -> interview first.
2. Known hypotheses -> survey for confidence.
3. Known flow pain -> usability testing for fixes.

## 2) Comparison matrix (when to use each)

## Interviews

- Best for: motivations, context, decision triggers, hidden constraints.
- Poor for: estimating percentages, comparing many alternatives quickly.
- Output shape: themes, mental models, language patterns, unmet needs.

## Surveys

- Best for: prevalence, ranking, segmentation, directional sizing.
- Poor for: root-cause depth, nuanced behavior interpretation.
- Output shape: distributions, segment differences, confidence ranges.

## Usability tests

- Best for: task success, confusion points, path deviations, UX defects.
- Poor for: market sizing or latent need discovery.
- Output shape: failure map, severity list, prioritized design fixes.

## 3) Sample size guidance (practical defaults)

Use ranges, then adapt by segment variability.

- Discovery interviews: 8-15 per key segment.
- JTBD-style interviews: 10-20 total with balanced contexts.
- Early usability tests (formative): 5-8 per round.
- Comparative usability tests: 12-20 per variant pair.
- Surveys (directional): >=100 total responses.
- Surveys (segment comparison): >=80 per critical segment.

Stop interviews when:

- no new high-signal themes appear in 3 consecutive sessions,
- and unresolved contradictions are documented explicitly.

## 4) Bias risks and how to prevent them

## Common interview biases

- Leading wording bias: question implies desired answer.
- Social desirability bias: participant tells you what sounds good.
- Recall bias: participant reconstructs behavior inaccurately.

Mitigations:

- ask for recent concrete episodes, not opinions,
- use neutral prompts ("Walk me through the last time..."),
- triangulate with logs or artifacts when possible.

## Common survey biases

- Sampling bias from convenience channels.
- Question-order priming effects.
- Double-barreled questions hiding tradeoffs.

Mitigations:

- predefine sampling frame and quotas,
- randomize option order for ranking blocks,
- pilot with 5-10 respondents before launch.

## Common usability test biases

- Moderator coaching influences user behavior.
- Artificial tasks detached from real goals.
- Overweighting single dramatic failure.

Mitigations:

- use a standardized script,
- anchor tasks in realistic user intent,
- classify issues by frequency x severity.

## 5) Analysis frameworks you should standardize

## Affinity mapping (for interviews and open feedback)

1. Write one observation per note.
2. Cluster by similarity without naming too early.
3. Label clusters with behavioral statements.
4. Link each cluster to evidence snippets.
5. Promote only high-confidence clusters to insights.

Template fields:

- Observation ID
- Verbatim quote
- Context
- Cluster label
- Confidence (low/medium/high)

## Thematic analysis (for mixed qualitative datasets)

1. Define initial codebook from research questions.
2. Code 20-30% sample and revise code definitions.
3. Double-code contentious excerpts.
4. Consolidate themes and contradictions.
5. Write insight statements with evidence references.

## 6) Triangulation pattern (recommended)

Use a three-pass sequence to reduce false conclusions.

1. Interview pass: generate hypotheses.
2. Survey pass: estimate prevalence and segment differences.
3. Usability pass: validate fixability in product flows.

Only move to roadmap decisions when all three signals agree,
or when disagreement is explicitly tracked with a follow-up plan.

## 7) Deliverable checklist for this skill

- Method rationale linked to product decision.
- Sample plan with segment quotas.
- Bias register and mitigation actions.
- Analysis method declared before coding starts.
- Insight table with evidence references.
- Open questions list for next round.

## 8) Example decision mapping

Decision: "Should we redesign onboarding step 2?"

- Interview goal: identify user intent mismatch and trust concerns.
- Survey goal: estimate prevalence of step-2 drop reasons.
- Usability goal: measure task completion and error recovery.

Release recommendation threshold:

- >=20% completion uplift in moderated tests,
- and top dropout reason prevalence >=30% in target segment,
- and no new critical severity issue introduced.
