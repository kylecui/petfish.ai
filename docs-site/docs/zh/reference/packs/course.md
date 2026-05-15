# course

**课程开发全生命周期 — 规划、提纲、正文、实验、资料、QA/QC、发布**

| 字段 | 值 |
|---|---|
| 包名 | `opencode-course-skills-pack` |
| 别名 | `course` |
| 版本 | 1.3.2 |
| 技能数 | 15 |
| 命令数 | 10 |
| 代理数 | 8 |
| 兼容性 | opencode |

## 技能列表

- [`course-content-authoring`](../skills/course-content-authoring.md) — Create, revise, expand, compress, or review course chapter content, including explanations, examples, transitions, key t...
- [`course-development-orchestrator`](../skills/course-development-orchestrator.md) — Drive course projects end to end — plans, outlines, content, labs, learner/instructor materials, QA, QC, and release dec...
- [`course-directory-structure`](../skills/course-directory-structure.md) — Create, reorganize, normalize, or audit a course project directory tree,
- [`course-lab-design`](../skills/course-lab-design.md) — Create, modify, review, or operationalize course labs, exercises, demos,
- [`course-methodology-playbook`](../skills/course-methodology-playbook.md) — Reusable course-development methods, review heuristics, historical conventions,
- [`course-outline-design`](../skills/course-outline-design.md) — Create, modify, or review a course outline, syllabus, chapter tree, hour
- [`course-quality-assurance`](../skills/course-quality-assurance.md) — Structured course QA: completeness checks, consistency review, pedagogical
- [`course-quality-control-reporting`](../skills/course-quality-control-reporting.md) — Turn QA findings into concrete quality control actions, remediation plans,
- [`development-plan-governance`](../skills/development-plan-governance.md) — Create, revise, or review a course development plan, including milestones,
- [`drawio-course-diagrams`](../skills/drawio-course-diagrams.md) — Course-related diagrams in draw.io form, including architecture diagrams,
- [`instructor-reference-materials`](../skills/instructor-reference-materials.md) — Instructor-only assets such as teaching notes, speaking points, timing
- [`learner-materials`](../skills/learner-materials.md) — Learner-facing course assets such as handouts, reading packs, worksheets,
- [`markdown-course-writing`](../skills/markdown-course-writing.md) — Polished Markdown artifacts for course plans, outlines, lesson notes, lab guides, learner handouts, instructor guides, Q...
- [`reference-document-review`](../skills/reference-document-review.md) — Read, normalize, compare, extract, or convert reference materials in PDF,
- [`skill-reference-discovery`](../skills/skill-reference-discovery.md) — Search GitHub/public sources for high-quality agent skills, run skill reference scans, compare candidate repositories, e...

## 安装

=== "PowerShell"

    ```powershell
    & ([scriptblock]::Create((irm https://raw.githubusercontent.com/kylecui/petfish.ai/master/remote-install.ps1))) -Pack "course"
    ```

=== "Bash"

    ```bash
    curl -fsSL https://raw.githubusercontent.com/kylecui/petfish.ai/master/remote-install.sh | bash -s -- --pack course
    ```
