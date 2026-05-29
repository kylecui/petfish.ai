# Skill Type Taxonomy

Detailed profiles for each skill type with structural guidance.

## automation

Script or command-driven. Single entry point, deterministic flow.
- SKILL.md: role → command detection → execution → result parsing
- Scripts: always needed (the automation itself)
- References: command flags, output format spec
- Evals: does the command run? does it handle errors?

## workflow

Multi-stage process with decision gates. Often interactive.
- SKILL.md: role → intake → stages with conditions → output contract
- References: stage detail, checklists, templates
- Assets: stage templates, output templates
- Evals: does each stage produce required output? are decision gates respected?

## knowledge

Domain rules and heuristics. No scripts, no mutation.
- SKILL.md: role → when to apply → rule application flow → output
- References: detailed rules, examples, anti-patterns
- Evals: are rules applied correctly? are conflicts handled?

## writing

Content creation or editing. Has drafts, reviews, and final versions.
- SKILL.md: role → intake (audience, tone, length) → drafting flow → review criteria
- References: style rules, tone guidelines, quality checklist
- Assets: draft templates, review templates
- Evals: does output meet the writing contract? is tone consistent?

## review

Assessment, scoring, or quality judgment. Must be structured.
- SKILL.md: role → rubric definition → assessment flow → finding classification
- References: rubric detail, severity definitions, evidence requirements
- Evals: are findings evidence-backed? is severity classification consistent?

## research

Evidence collection, synthesis, analysis. Traceability is critical.
- SKILL.md: role → question framing → search strategy → evidence handling → synthesis
- References: source quality criteria, evidence types, citation format
- Evals: are claims traceable to sources? are evidence types labeled correctly?

## project

Repo or task management. Often initializes or restructures files.
- SKILL.md: role → project detection → initialization/modification flow → validation
- Scripts: often needed for scaffolding or validation
- Evals: does output match the project structure contract?

## hybrid

Combines multiple types. Define which type leads and which supports.
- SKILL.md: identify the primary type, then layer secondary behaviors
- Example: course-author = writing (primary) + workflow (staging) + review (QA)
- Evals: test each type's contribution independently
