# Handoff & Boundary Design

How to define what a skill owns and where it hands off.

## Boundary Statement

Every skill must have a boundary statement with two sections:

### This skill owns

List 3-5 responsibilities that are definitively within scope.
Be specific: not "writing" but "long-form content production with draft-review cycles".

### This skill does not own

List 2-4 responsibilities that belong elsewhere, with the target skill named.

Example:
```
This skill owns:
- Structured code review with severity classification
- Evidence-based finding presentation
- Review scope definition and prioritization

This skill does not own:
- Code modification or refactoring → handoff to refactor-skill
- Test generation → handoff to test-generator
- Deployment validation → handoff to deploy-verifier
```

## Handoff Triggers

Define when to hand off:

1. **Scope overflow**: user request exceeds the skill's defined scope
2. **Prerequisite missing**: a required input needs another skill to produce
3. **Quality gate failure**: output needs a review skill before delivery
4. **Mode mismatch**: user wants a related but different interaction mode

## Composition Rules

When two skills might both be relevant:

1. Declare which skill leads and which supports
2. Define the handoff point (which step, what output)
3. Specify whether context transfers or resets

Example:
```
When research-brief and research-source-discovery both match:
- research-brief leads (frames the question)
- research-source-discovery supports (finds sources)
- Handoff: brief's search_queries field feeds discovery's input
- Context: fully inherited
```

## Escalation

For skills in a pipeline (e.g., research chain), define:

- What triggers escalation (blocked, ambiguous, low confidence)
- Where to escalate (user? another skill? abort?)
- What context to pass
