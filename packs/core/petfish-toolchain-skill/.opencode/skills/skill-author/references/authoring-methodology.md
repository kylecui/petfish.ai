# Authoring Methodology

How to extract and structure domain knowledge into a production-grade skill.

## Progressive Disclosure Layers

Design skills in three token-budget layers:

1. **Frontmatter** (~100 tokens): name + description. Agent reads this on every turn.
2. **SKILL.md body** (~2000-5000 tokens): core instructions, workflow, boundaries.
3. **references/assets** (on-demand): detailed rules, templates, examples.

If a section grows past 50 lines, move it to a reference file.

## Knowledge Extraction

When building a skill from user input or existing workflow:

1. **Rules**: Ask "what would an agent do wrong if it didn't know X?" These become
   Domain Rules.
2. **Examples**: Collect 1-2 ideal outputs and 1-2 failure outputs. These seed evals.
3. **Anti-patterns**: Ask "where have you seen this go wrong?" These become explicit
   warnings.
4. **Decision points**: Ask "when does the workflow branch?" These become if/else
   nodes in the workflow.
5. **Edge cases**: Ask "what unusual inputs break the normal flow?" These become
   special-case handling.

## Extracting from Methodology

When a user describes a methodology (e.g., "fat-slim writing", "research pipeline"):

1. Identify the core loop (what repeats).
2. Identify the decision gates (where it branches).
3. Identify the handoff points (where it delegates).
4. Identify the quality checks (how it validates).
5. Map each to a SKILL.md section.

## Writing Execution Modes

Define at least one mode. Common patterns:

- `interactive`: ask user at each decision gate
- `auto`: execute full workflow without stopping
- `review-only`: assess without modifying
- `draft`: produce rough output for later refinement

Each mode changes which steps execute and how much confirmation is required.

## Output Contract Design

For each mode, define:

- Required files or sections
- Required fields within each section
- Validation criteria (what makes output "done")
- Rejection criteria (what makes output "not done")

Contracts prevent the agent from returning vague summaries instead of deliverables.
