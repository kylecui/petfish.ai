---
name: course-delivery-review
description: Close the loop after course delivery. Use when reviewing teaching feedback,
  quiz score distributions, completion rates, or frequent Q&A questions to diagnose
  content issues and plan course iteration. Trigger for 授课反馈, 交付复盘, delivery
  review, 课程迭代, 学员反馈, 完课率, post-delivery retrospective.
license: Proprietary
compatibility: Designed for OpenCode. Assumes repo-local `.opencode/skills` discovery
  and standard read/edit/bash tools; optional scripts should run through a repo-local uv environment; requires uv and Python 3.11+.
metadata:
  pack: opencode-course-skills
  version: "1.0.0"
  author: kylecui-skill-pack
---

# Purpose

Turn post-delivery feedback into diagnosed issues and a concrete course iteration plan,
closing the loop from teaching back into content authoring.

# Inputs

Collect whatever is available; do not block on missing channels:

- learner feedback (surveys, interviews, informal comments)
- quiz/assessment score distributions per lesson or module
- completion rate (per module, per lab, overall)
- frequent Q&A questions (答疑高频问题) from delivery sessions

# Diagnostic categories

Classify each finding into one primary category:

- outdated content (内容过时): facts, tools, or versions no longer current
- difficulty mismatch (难度错配): content too hard or too easy for the actual audience baseline
- ineffective exercise (练习失效): labs/quizzes that learners fail for reasons unrelated to the learning objective, or complete without learning
- duration drift (时长偏差): lessons or labs that consistently overrun or underrun their allocated time

# Mapping to the QC status model

Reuse the pack QA/QC conventions; do not invent a parallel model:

- severity: blocker / major / minor (e.g. wrong technical fact = blocker; systematic difficulty mismatch in a core module = major; single-lesson duration drift = minor)
- status: open / in-progress / fixed / verified / deferred (see the QC status model used by course-quality-control-reporting)

Each diagnosed issue gets: category, severity, status, evidence (which input channel surfaced it), and scope (module/lesson).

# Default output structure

Write the iteration report to `docs/07-qc/` (delivery review is a QC-loop artifact):

```markdown
# Delivery Review <course> <date/round>

## Input summary
## Diagnosed issues (category / severity / status / evidence / scope)
## Iteration plan (which module, which lesson, what to change)
## Deferred items and rationale
## Next review checkpoint
```

The iteration plan must name concrete targets: module, lesson, and the specific change
(rewrite section, replace lab, adjust duration budget, update outdated references).

# Feeding the revision loop

- Route content changes to `course-content-authoring`; route outline-level changes (module structure, hour reallocation) to `course-outline-design` first.
- Route lab/exercise fixes to `course-lab-design`.
- After revision, record status transitions and run QA/QC before any re-release; the delivery review report feeds the next QC round as findings input.

# Gotchas

- Do not treat one vocal complaint as a pattern; require evidence from at least one quantitative channel (scores, completion) or repeated qualitative signals.
- Do not diagnose from completion rate alone; a low rate can mean difficulty mismatch, duration drift, or logistics — separate the hypotheses.
- Do not bypass QA/QC: iteration suggestions are inputs to authoring, not direct edits to release material.
- Do not lose severity/status when converting feedback into issues.
