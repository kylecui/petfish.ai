# Pack Index Reference

This file is intended for GPT Knowledge upload.

## Core packs

| Alias | Purpose | Default scale |
|---|---|---|
| `init` | Project initializer and `/initproject` wizard | global default |
| `companion` | Companion Gateway, `/petfish`, fish-brain, fish-market | global default |
| `petfish` | Writing style and rewrite guidance | global default |
| `toolchain` | Skill lifecycle pipeline: author, lint, audit, gate, publish, optimize, eval | global default |

## Optional packs

| Alias | Purpose | Typical use |
|---|---|---|
| `course` | Course outline, content, labs, QA, and QC | teaching/courseware |
| `testdocs` | Test case and usage documentation workflows | testing docs |
| `deploy` | Deployment, CI/CD, health check, rollback, ops | operations and delivery |
| `ppt` | Slide and presentation workflows | presentations |
| `calibrate` | Anti-sycophancy review and decision calibration | critical review |
| `context` | Topic governance, context isolation, contamination scoring | long-running projects |
| `trust` | Skill trust governance and policy checks | security-sensitive workflows |
| `research` | Evidence-backed scientific, product, and planning research | research workbench |
| `reflect` | Structured reflection and corrective action capture | postmortem and learning |
| `doc-reader` | Document-to-Markdown conversion and reading | document ingestion |

## Profile mapping

| Profile | Auto-installed packs |
|---|---|
| `minimal` | `context`, `petfish` |
| `course` | `context`, `course`, `doc-reader`, `petfish` |
| `code` | `context`, `deploy`, `petfish`, `testdocs` |
| `ops` | `context`, `deploy`, `petfish` |
| `security` | `context`, `deploy`, `petfish`, `testdocs`, `trust` |
| `research` | `context`, `doc-reader`, `petfish`, `research` |
| `writing` | `context`, `petfish`, `ppt` |
| `skills-package` | `context`, `petfish`, `testdocs` |
| `comprehensive` | `context`, `course`, `deploy`, `doc-reader`, `petfish`, `ppt`, `testdocs`, `trust`, `research`, `reflect` |

## Recommendation discipline

Do not recommend every useful pack. Recommend the minimal sufficient pack set.

Include `context` when:

- the project is long-running;
- multiple topics are likely;
- contamination or context drift matters.

Include `trust` when:

- remote execution is involved;
- security-sensitive code or policy is involved;
- skill publishing, audit, or governance matters.

Include `doc-reader` when:

- the user needs PDF, DOCX, XLSX, PPTX, HTML or document-to-Markdown reading workflows.
