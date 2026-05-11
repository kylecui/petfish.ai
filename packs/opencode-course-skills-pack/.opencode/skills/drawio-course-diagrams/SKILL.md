---
name: drawio-course-diagrams
description: Course-related diagrams in draw.io form, including architecture diagrams,
  module maps, timelines, workflows, role flows, lab topologies, or slide-ready visual
  structures.
license: Proprietary
compatibility: Designed for OpenCode. Assumes repo-local `.opencode/skills` discovery
  and standard read/edit/bash tools; optional scripts should run through a repo-local uv environment; requires uv and Python 3.11+.
metadata:
  pack: opencode-course-skills
---

# Purpose

Create or revise diagrams intended for draw.io/diagrams.net usage in course projects.

# Activation cues

Use this skill when the user asks to:

- draw a course structure
- create a module map
- visualize a workflow or lifecycle
- prepare a lab topology
- convert an architecture explanation into a diagram
- revise an existing draw.io concept or page layout

# Working method

1. Identify the diagram type:
   - hierarchy
   - flow
   - timeline
   - topology
   - matrix
   - swimlane
2. Define the nodes, groups, and relationships in text first.
3. Produce one of:
   - a draw.io page plan
   - a node-and-edge specification
   - a Mermaid or ASCII intermediate draft if that helps alignment
   - draw.io XML only when the user explicitly wants machine-ready content
4. Keep labels short and presentation-safe.

# Diagram design rules

- One page, one main message.
- Use left-to-right for flow, top-to-bottom for hierarchy unless there is a strong reason otherwise.
- Separate permanent architecture from transient process.
- Distinguish actor, artifact, system, and decision node.
- For training diagrams, prefer readability over technical density.

# Output options

Depending on the request, produce:

- a draw.io editing plan
- a detailed layout specification
- a Mermaid draft for quick review
- final draw.io XML skeleton
- annotation notes for a human to finish in draw.io

# Gotchas

- Do not dump raw XML unless the user actually needs import-ready content.
- Do not overload one page with both lesson structure and system architecture unless the user asks.
- Do not use ambiguous arrows; define direction and meaning.
- Do not make learners reverse-engineer the teaching logic from a messy visual.

See:
- `assets/diagram-patterns.md`
- `assets/drawio-page-template.md`
