# Evidence-Based Persona and Journey Mapping Guide

## 1) Purpose: build decision tools, not marketing posters

Persona and journey outputs are useful only if they change product decisions.
Treat them as evidence-compressed models of behavior and friction.

Do not create personas from assumptions, stakeholder opinions, or brand tone.
Use verified patterns from user research artifacts.

## 2) Evidence standard for persona construction

A persona is valid when each major attribute is traceable to evidence.

Required evidence-backed blocks:

- Core job context (what user is trying to get done).
- Trigger conditions (what starts the task).
- Success criteria (what "done well" means to user).
- Constraints (time, risk, policy, budget, skills).
- Decision heuristics (how they choose among options).

Exclude non-actionable demographic decoration unless it affects behavior.

## 3) Persona construction workflow

1. Aggregate raw observations by behavior, not demographics.
2. Identify recurring goal-conflict patterns.
3. Draft provisional personas as hypotheses.
4. Stress-test personas against outlier cases.
5. Keep only personas with distinct decision implications.

Target count guidance:

- 2-4 primary personas for most product teams.
- Add secondary personas only when roadmap impact is clear.

## 4) Persona template (practitioner version)

Use this compact template:

## Persona name

- Primary job:
- Typical trigger:
- Top 3 desired outcomes:
- Top 3 constraints:
- Current workaround:
- Purchase/adoption blocker:
- Evidence anchors (interview IDs, logs, tickets):

## Decision implications

- Must-have capability:
- Nice-to-have capability:
- Messaging/positioning implication:
- Validation risk to watch:

## 5) Red flags: persona fiction signals

If any appears, pause and revise:

- Persona has adjectives but no behavior pattern.
- Persona cannot be linked to specific evidence IDs.
- Two personas lead to identical product priorities.
- Persona narrative ignores contradictory data.

## 6) Journey map structure that drives action

Map journeys as problem-solving progress, not UI screens only.

Recommended stages:

1. Trigger (why now)
2. Discovery (how options are found)
3. Evaluation (how options are compared)
4. Onboarding/first value
5. Repeated use
6. Escalation/support
7. Renewal/expansion/churn

For each stage capture:

- user goal,
- actions,
- friction points,
- emotional state,
- current workaround,
- opportunity hypothesis,
- evidence references.

## 7) Touchpoint identification method

A touchpoint is any interaction that can change user progress probability.

Touchpoint categories:

- Product UI interaction
- Human-assisted interaction (sales, support, CSM)
- System event (notification, error, policy gate)
- External dependency event (integration or compliance step)

Identify touchpoints by tracing real user episodes end-to-end.
Avoid only mapping internal system components.

## 8) Moment-of-truth analysis

Moments of truth are points where user trust or progress can sharply shift.

Scoring formula:

Moment score = impact on decision x failure likelihood x recovery difficulty

Rate each on 1-5 scale.
Prioritize moments scoring >=40 (out of 125) for immediate design work.

For each high-score moment, define:

- failure signal,
- detection metric,
- recovery mechanism,
- owner and timeline.

## 9) Decision handoff format

Before product planning, create this one-page handoff:

- Persona summary table (evidence-backed only)
- Journey stage friction heatmap
- Top 3 moments of truth and expected impact
- Recommended actions (now/next/later)
- Open assumptions requiring validation

## 10) Concrete example

Case: B2B analytics onboarding drop-off.

- Persona A (Ops lead): needs reliable setup under strict time pressure.
- Moment of truth: data-source connection success in first 30 minutes.
- Journey friction: permission errors with unclear resolution path.
- Action: guided setup with role-aware checks and fallback support path.

Expected movement: higher activation, faster support resolution, better week-1 retention.
