# Skill Description Optimization Guide

## Why the description matters

In AgentSkills-style systems, the description is the primary matching surface. It is the shortest high-signal summary of **what the skill does**, **when it should trigger**, and **when it should stay out of the way**. A weak description lowers trigger precision, lowers recall, or both.

## Best practices

1. **Lead with the job**
   - Start with the exact outcome: analyze, lint, deploy, audit, refactor, generate, review.
2. **State the activation condition**
   - Use explicit patterns such as `Use this skill when the user asks to...`.
3. **Include concrete trigger phrases**
   - Good trigger phrases look like real requests, not taxonomy labels.
4. **Define the boundary**
   - Say what the skill does not cover, or narrow scope with `only`, `not`, `instead of`, `rather than`.
5. **Favor specific verbs over vague helpers**
   - `deploy`, `audit`, `lint`, `rewrite`, `generate` beat `help`, `assist`, `support`, `manage`.
6. **Keep overlap low**
   - If two sibling skills share the same nouns and verbs, they compete for the same request.
7. **Keep it dense**
   - Short descriptions should usually land in the 100-500 character range. Longer is acceptable only when every clause adds routing value.

## Common anti-patterns

### 1. Catch-all descriptions

Bad:

> Helps with skills, tooling, workflows, and project setup.

Why it fails:

- too broad
- no clear activation signal
- likely overlaps with multiple siblings

### 2. Keyword stuffing

Bad:

> Skill skill skill trigger trigger install create generate validate deploy review optimize all skills.

Why it fails:

- high noise, low meaning
- semantic matcher gets weak boundaries
- reads like a bag of words, not an activation rule

### 3. Missing negation boundaries

Bad:

> Use this skill for deployment requests.

Why it fails:

- does not distinguish deploy planning vs runtime debugging vs rollback
- causes sibling collisions

### 4. Outcome-free wording

Bad:

> Assists with quality.

Why it fails:

- no object
- no workflow
- no real trigger phrase

## Description anatomy

A strong description usually has four parts:

1. **Purpose clause**
   - what the skill does
   - example: `Analyze and optimize skill descriptions to maximize trigger accuracy.`
2. **Trigger phrases**
   - what the user is likely to say
   - example: `Use this skill when the user asks to optimize description, improve trigger, or fix skill description.`
3. **Boundary markers**
   - how the skill stays narrow
   - example: `It focuses on description matching, not general skill authoring.`
4. **Negation / exclusion**
   - what not to use it for
   - example: `Do not use it for full pack QA unless the request is specifically about description quality.`

## Good vs bad examples

### Pair 1: skill creation

Bad:

> Create or help with skills.

Good:

> Generate new skills from scratch when the user asks to create a skill, scaffold a new skill, or build a reusable skill package. Use it for new-skill authoring, not for linting or publish review.

### Pair 2: linting

Bad:

> Check if a skill looks okay.

Good:

> Validate a skill directory when the user asks to lint skill, check skill validity, or review skill quality. It checks frontmatter, structure, duplication, and script safety; it does not publish or rewrite the skill.

### Pair 3: deployment

Bad:

> Use for servers and apps.

Good:

> Deploy a repo to a target host when the user asks to deploy this project, run the service on a server, or bring the repo online. Use it for deployment execution, not for browser testing or postmortem analysis.

### Pair 4: description tuning

Bad:

> Improve skill metadata.

Good:

> Analyze and optimize a skill description when the user says optimize description, improve trigger, or the skill is not triggering. It tunes activation phrasing and overlap boundaries, not the full skill implementation.

## How OpenCode / Claude Code / Cursor match skills

These systems do not rely only on exact string matching. In practice, they lean on **semantic similarity** between the user request and the skill description. That has two implications:

1. Exact trigger phrases help because they anchor common request shapes.
2. Meaning matters more than raw keyword count.

So the goal is not to stuff synonyms. The goal is to write a short, semantically sharp routing rule.

## Precision vs recall

Description quality changes two core metrics:

- **Precision**: when the skill triggers, was it the right skill?
- **Recall**: when the skill should have triggered, did it trigger?

Typical failure modes:

- too broad → recall goes up, precision collapses
- too narrow → precision goes up, recall collapses
- overlap with siblings → both become unstable
- no negation boundary → false positives increase

## Practical checklist

Before you finalize a description, ask:

- Can I tell what the skill actually does in one sentence?
- Can I tell when it should activate?
- Does it include realistic user phrasing?
- Does it avoid vague verbs?
- Does it say what it is not for?
- Would it collide with sibling skills in the same pack?

If any answer is no, the description is not ready.
