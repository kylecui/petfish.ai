---
name: course-quality-control-reporting
description: Turn QA findings into concrete quality control actions, remediation plans,
  closure tracking, and release or re-review reports.
license: Proprietary
compatibility: Designed for OpenCode. Assumes repo-local `.opencode/skills` discovery
  and standard read/edit/bash tools; optional scripts should run through a repo-local uv environment; requires uv and Python 3.11+.
metadata:
  pack: opencode-course-skills
---

# Purpose

Convert QA findings into controlled remediation and decision-ready reporting.

# QC workflow

1. ingest findings
2. normalize issue list
3. define remediation action per issue
4. assign status:
   - open
   - in progress
   - fixed
   - verified
   - deferred
5. summarize residual risk
6. generate release/hold recommendation

# Reporting expectations

A QC report should answer:

- what was found
- what was fixed
- what remains
- what risk remains
- whether release is recommended

# Default output structure

```markdown
# QC Report

## Source QA baseline
## Remediation summary
## Issue-by-issue status
## Residual risks
## Release recommendation
## Next review gate
```

# Script support

Use:
`uv run scripts/render_qc_report.py --help`

when the user already has structured QA findings or wants a repeatable Markdown report generated from JSON input.

# Gotchas

- Do not mark issues closed without evidence.
- Do not lose severity information during remediation.
- Do not recommend release while unresolved blockers remain.
- Do not turn a QC report into a raw dump of QA comments.

See:
- `assets/qc-report-template.md`
- `references/status-model.md`
