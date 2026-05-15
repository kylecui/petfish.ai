---
title: Course Development Guide
description: A complete guide to managing the full lifecycle of course development using the PEtFiSh course skill pack.
---

# Course Development Guide

The **course** pack provides a complete suite of skills for building, reviewing, and governing course materials from initial brief to final release. 

Rather than treating course creation as merely writing words, this pack enforces strict separation between instructor and learner materials, maintains quality gates at every phase, and structures work into logical stages that prevent the most common curriculum development failures: scope creep, audience contamination, and undisciplined releases.

This pack bridges the gap between "a folder of drafts" and "a professionally governed course product." Whether you are building a 3-day Kubernetes bootcamp or restructuring a semester-long university curriculum, the course pack ensures structural consistency, audience isolation, and traceable quality decisions.

```bash
# Install the course pack (macOS / Linux)
curl -fsSL https://raw.githubusercontent.com/kylecui/petfish.ai/master/remote-install.sh | bash -s -- --pack course

# Install the course pack (Windows PowerShell)
& ([scriptblock]::Create((irm https://raw.githubusercontent.com/kylecui/petfish.ai/master/remote-install.ps1))) -Pack course
```

---

## Overview

The course pack is designed for tasks ranging from "outline this new subject" to "run a final quality control check on the full curriculum." It excels at maintaining structural consistency and ensuring clear boundaries between audiences.

### What's in the Pack

The course pack is modular. While the orchestrator ties everything together, each skill is a standalone tool capable of performing deep operations in its specific domain.

| Skill | Purpose | Role in Pipeline |
|---|---|---|
| **`course-development-orchestrator`** | Routes tasks to the correct phase and skill. Understands the full lifecycle and passes context between phases. | **Orchestrator** |
| **`course-directory-structure`** | Initializes, audits, and fixes directory layouts. Enforces naming conventions and detects misplaced files. | **Governance** |
| **`development-plan-governance`** | Manages milestones, change logs, risk registers, and acceptance gates. | **Governance** |
| **`course-outline-design`** | Designs high-level syllabi, module breakdowns, learning objectives, and hour allocations. | **Phase 1: Outline** |
| **`course-content-authoring`** | Writes and restructures chapter content. Ensures terminology consistency and proper transitions. | **Phase 2: Content** |
| **`markdown-course-writing`** | Formats and standardizes Markdown output. Normalizes terms, adds verification placeholders. | **Phase 2: Content** |
| **`course-lab-design`** | Creates exercises, objectives, environment specs, validation criteria, and answer keys. | **Phase 3: Labs** |
| **`learner-materials`** | Generates student-facing handouts, worksheets, glossaries, and recap notes. | **Phase 4: Materials** |
| **`instructor-reference-materials`** | Generates teacher notes, speaking points, timing guidance, and answer keys. | **Phase 4: Materials** |
| **`course-quality-assurance`** | Logs issues, checks completeness, reviews consistency, and classifies severity. | **Phase 5: QA** |
| **`course-quality-control-reporting`** | Forms release decisions, closure reports, and remediation plans. | **Phase 6: QC** |
| **`drawio-course-diagrams`** | Generates structured XML-based draw.io diagrams for architectures and module maps. | **Reference** |
| **`reference-document-review`** | Reads external PDFs, docs, images, and web pages. Extracts and normalizes into course inputs. | **Reference** |
| **`course-methodology-playbook`** | Packages reusable workflows, review heuristics, and conventions from prior projects. | **Methodology** |
| **`skill-reference-discovery`** | Discovers reusable agent skill patterns from external GitHub repositories and sources. | **Methodology** |

### When to Use This Pack vs. When NOT to Use

**Use this pack when:**

- **Building a comprehensive course:** You need to produce a structured training course, workshop, bootcamp, or multi-module curriculum with clear learning objectives and assessments.
- **Separating audiences:** You have materials that must exist in different forms for instructors (answer keys, timing cues, delivery risks) and learners (handouts, exercises, glossaries).
- **Requiring quality gates:** You need a formal process where issues are found (QA), decisions are made (QC), and releases are traceable.
- **Restructuring existing materials:** You inherited a disorganized folder of drafts and need to audit, classify, and reorganize them into a standard structure.
- **Extracting course material from existing docs:** You have internal documentation, meeting transcripts, or reference PDFs that need to be distilled into teaching-ready content.

**Do NOT use this pack when:**

- **Writing a blog post or standard documentation:** Use standard writing skills or the `petfish-style-rewriter` skill instead.
- **Writing application code:** This pack handles curriculum, not software engineering.
- **Generating content without structure:** The pack expects and enforces a strict directory hierarchy. If you want freeform writing, use general-purpose tools.
- **Running a single quick review:** If you just need a grammar check on one file, use direct editing tools rather than the full QA/QC pipeline.

---

## The Course Development Pipeline

The pack operates through a strict pipeline designed to prevent the most common failure mode in course development: jumping straight to writing prose without establishing boundaries, structure, or quality criteria first.

If you use the orchestrator (`course-development-orchestrator`), it automatically routes through these phases. If you manually request a specific action (e.g., "Just write Module 3 Lesson 2"), the agent loads the corresponding individual skill directly.

```text
Project Brief
    │
    ▼
[ Phase 0: Setup ] ──► [ Phase 1: Outline ] ──► [ Phase 2: Content ]
                                                        │
                                                        ▼
[ Phase 7: Release ] ◄── [ Phase 6: QC ] ◄── [ Phase 5: QA ] ◄── [ Phase 4: Materials ] ◄── [ Phase 3: Labs ]
```

### Context Passing

Each phase produces artifacts that feed the next. The outline defines modules and hours; content authoring references that outline to ensure chapters don't exceed allocated time. Lab design references the content to ensure exercises match what was taught. QA references all prior artifacts to check consistency. This tight coupling ensures the curriculum is internally coherent.

!!! warning "Don't Skip Phases"
    The pipeline exists because each phase depends on the outputs of the previous one. If you skip directly from project brief to content authoring, you will inevitably produce chapters that don't align with any agreed-upon structure, miss learning objectives, or allocate time unrealistically.

---

## Quick Start

### Example 1: New Project Initialization

If you are starting a new course project from scratch:

=== "Prompt"

    ```text
    /course-init We are building a new course on "Introduction to Kubernetes" 
    targeting backend developers with 2+ years of experience. 
    Set up the project directory and create the initial project brief.
    ```

=== "Expected Behavior"

    1. The agent loads `course-directory-structure` to bootstrap the standard directory tree.
    2. It creates all 8 documentation directories (`docs/00-project` through `docs/07-qc`) plus `assets/`, `references/`, `release/`, and `archive/`.
    3. It generates `docs/00-project/project-brief.md` with the target audience, prerequisites, and scope.
    4. It generates `docs/00-project/milestone-plan.md` outlining the delivery schedule.
    5. It asks for approval before proceeding to the outline phase.

### Example 2: Taking Over an Existing Project

If you inherited a folder full of messy files:

=== "Prompt"

    ```text
    /course-audit Review the current directory. The files are a mess—there are 
    drafts mixed with final versions, no clear structure. Give me a reorganization 
    plan before moving anything.
    ```

=== "Expected Behavior"

    1. The agent scans the current directory using `course-directory-structure`.
    2. It classifies each file by layer: project governance, outline, content, labs, learner materials, instructor materials, QA, QC, reference, or archive.
    3. It outputs a proposed mapping table (e.g., `draft-kubernetes.md` → `docs/02-content/01-module/01-lesson.md`).
    4. It flags files it cannot confidently classify and asks for your input.
    5. It **waits for your confirmation** before executing any file moves.

### Example 3: Full Pipeline Run

If you want the agent to orchestrate the entire workflow:

=== "Prompt"

    ```text
    We need to build a 2-day workshop on "CI/CD with GitHub Actions" for DevOps 
    engineers. Drive this end-to-end: outline, content, labs, materials, then QA.
    ```

=== "Expected Behavior"

    1. The agent loads `course-development-orchestrator`.
    2. It initializes the directory structure and creates the project brief.
    3. It drafts the syllabus with module breakdown and hour allocation.
    4. After outline approval, it expands each module into chapter content.
    5. It designs lab exercises for each hands-on module.
    6. It generates learner handouts and instructor guides.
    7. It runs QA on the complete package and logs findings.

??? example "Why separate QA and QC?"
    The course pack strictly separates **finding issues** (QA) from **deciding what to do about them** (QC). 
    
    - **QA** creates checklists of problems: "Module 3 references a concept not introduced until Module 5." 
    - **QC** determines if those problems block a release: "This is a severity-2 issue. Accept risk and release with a known limitation, or fix before release?"
    
    This separation ensures accountability. QA never unilaterally decides "it's fine to ship." QC never says "I don't know what the problems are."

---

## Phase 0: Project Setup

Before writing any course content, the project needs clear boundaries. The **orchestrator** and **directory-structure** skills handle this foundational work.

### The Standard Directory Layout

The pack enforces a strict directory hierarchy where every file has exactly one correct home:

```text
docs/
  00-project/        # Project briefs, milestones, risk registers, change logs
  01-outline/        # Syllabi, module breakdowns, hour allocations
  02-content/        # Actual course text (chapters, lessons)
  03-labs/           # Exercises, demos, environment specs
  04-learner-pack/   # Student-facing handouts, glossaries, worksheets
  05-instructor-pack/# Teacher notes, answer keys, timing cues
  06-qa/             # Review checklists, issue logs
  07-qc/             # Release decisions, closure reports
assets/              # Images, diagrams, draw.io files, tables
references/          # Input material (PDFs, transcripts, external docs)
release/             # Stable, versioned deliverables
archive/             # Deprecated or superseded content
```

!!! warning "References vs. Release"
    Files in `references/` are **inputs**—raw material that must be distilled, rewritten, and adapted before entering the course. They are never treated as final course content.
    
    Files in `release/` are **outputs**—stable, versioned deliverables that have passed through QA and QC. Drafts and work-in-progress never enter this directory.

### Directory Semantics

Each directory has strict boundaries about what belongs there:

| Directory | Contains | Does NOT Contain |
|---|---|---|
| `00-project/` | Briefs, milestones, risk registers | Course prose, lesson content |
| `01-outline/` | Syllabi, module maps, hour tables | Full chapter text, lab steps |
| `02-content/` | Chapter text, lesson narratives | QA comments, release decisions |
| `03-labs/` | Exercise steps, environment specs | Instructor-only answer keys (those go in `05-instructor-pack/`) |
| `04-learner-pack/` | Student handouts, glossaries | Answer keys, instructor notes, internal review marks |
| `05-instructor-pack/` | Teaching notes, answer keys, timing | Student-facing handouts |
| `06-qa/` | Issue logs, completeness checklists | Remediation actions (those go in QC) |
| `07-qc/` | Release decisions, closure reports | Raw issue discovery (that's QA's job) |

### Naming Conventions

The pack enforces consistent naming across all files:

- **Directories and files:** lowercase `kebab-case` (e.g., `01-module-intro/`, `lesson-02.md`)
- **Ordered content:** two-digit numeric prefixes (e.g., `01-`, `02-`, `03-`)
- **One topic per file:** each Markdown file covers exactly one lesson, one lab, or one review
- **Avoid meaningless names:** never use `final`, `new`, `v2-latest`, or date-only names

```text
# Good naming
docs/02-content/01-module-kubernetes-basics/01-what-is-k8s.md
docs/03-labs/01-lab-deploy-pod/learner-guide.md
docs/06-qa/qa-review-round-01.md

# Bad naming
docs/kubernetes-draft-final-v3.md
docs/lab-NEW.md
docs/review-notes-kyle.md
```

### Bootstrapping with Scripts

The pack includes Python scripts for automated directory initialization and auditing:

=== "Initialize a New Project"

    ```bash
    uv run .opencode/skills/course-directory-structure/scripts/bootstrap_course_tree.py \
      --root . --mode full --with-placeholders
    ```
    
    This creates the complete directory tree with placeholder `README.md` files in each directory explaining its purpose.

=== "Audit an Existing Project"

    ```bash
    uv run .opencode/skills/course-directory-structure/scripts/check_course_tree.py --root .
    ```
    
    This scans the current directory and reports missing directories, misplaced files, and naming convention violations.

### Project Brief and Milestones

Phase 0 produces two key governance documents:

**`docs/00-project/project-brief.md`** should define:

- Target audience and prerequisites
- Course scope and explicit exclusions
- Delivery format (workshop, bootcamp, self-paced, etc.)
- Expected deliverables
- Success criteria

**`docs/00-project/milestone-plan.md`** should define:

- Phase deadlines
- Deliverable acceptance criteria per phase
- Risk register entries
- Change control process

!!! tip "Start with the brief, not the content"
    The single most common mistake in course development is jumping directly into writing chapters. Without a project brief, you have no shared understanding of who the audience is, what they already know, or what "done" looks like. The brief takes 15 minutes to write and saves days of rework.

---

## Phase 1: Outline Design

Before writing detailed prose, the **`course-outline-design`** skill drafts the syllabus. It ensures that learning objectives map correctly to modules, and that hour allocation is realistic for the target audience.

### What the Outline Skill Produces

A properly constructed outline includes:

- **Module breakdown:** logical grouping of topics into teachable units
- **Learning objectives:** specific, measurable outcomes per module (using Bloom's taxonomy verbs)
- **Hour allocation:** realistic time budgets for lecture, lab, and discussion per module
- **Prerequisite mapping:** which modules depend on concepts from earlier modules
- **Learner benefit statement:** what the student can do after completing each module

### Example Prompts

=== "Draft from Scratch"

    ```text
    /course-outline Draft a syllabus for a 3-day Kubernetes bootcamp targeting 
    backend developers. Day 1 covers fundamentals, Day 2 covers workloads, 
    Day 3 covers production operations.
    ```

=== "Restructure Existing"

    ```text
    /course-outline Our current outline has 12 modules crammed into 2 days. 
    Restructure it to be realistic. Cut or merge where necessary. 
    Show me what you'd remove and why.
    ```

=== "Add a Module"

    ```text
    /course-outline Add a new module on "Service Mesh with Istio" between 
    the Networking and Security modules. Adjust hour allocations to fit 
    within the existing 3-day constraint.
    ```

### Hour Allocation Discipline

The outline skill enforces realistic time budgets. A common failure mode is allocating 1 hour to a topic that requires 3 hours of hands-on lab time. The skill cross-checks:

- Lecture hours vs. content depth
- Lab hours vs. number of exercise steps
- Total hours vs. available calendar time (accounting for breaks, setup, Q&A)

??? example "Sample Outline Output"
    ```markdown
    # CI/CD with GitHub Actions — Course Outline
    
    ## Module 1: Foundations (3h)
    - **Objective:** Explain the CI/CD lifecycle and identify where GitHub Actions fits.
    - Lecture: 1.5h | Lab: 1h | Discussion: 0.5h
    - Prerequisites: Git basics, command-line familiarity
    
    ## Module 2: Workflow Syntax (4h)
    - **Objective:** Write and debug a multi-step GitHub Actions workflow.
    - Lecture: 1.5h | Lab: 2h | Discussion: 0.5h
    - Prerequisites: Module 1
    
    ## Module 3: Advanced Patterns (4h)
    - **Objective:** Implement matrix builds, caching, and reusable workflows.
    - Lecture: 1.5h | Lab: 2h | Discussion: 0.5h
    - Prerequisites: Module 2
    ```

!!! info "Outline First, Content Second"
    The pack enforces a strict rule: **never write chapter content before the outline is approved.** If you ask the agent to write Module 3 before the outline exists, it will either refuse or create a minimal outline first. This prevents the most expensive rework scenario: discovering at QA time that entire modules are redundant or missequenced.

---

## Phase 2: Content Authoring

With the outline approved, **`course-content-authoring`** and **`markdown-course-writing`** expand outline bullet points into readable chapters.

### What Content Authoring Handles

The content skill produces:

- **Chapter narratives:** clear explanations that follow the outline's learning objectives
- **Terminology consistency:** the same concept is never called by different names across chapters
- **Transitions:** each lesson references what came before and previews what comes next
- **Examples and analogies:** concrete illustrations that match the target audience's experience level
- **Key takeaways:** summarized learning points at the end of each chapter

### Content Rules the Agent Enforces

The agent is explicitly instructed to follow these rules during authoring:

1. **No internal markers in content:** "TODO", "TBD", "fill this later" never appear in chapter files. If something is incomplete, it gets logged as a QA issue in `docs/06-qa/` instead.
2. **No audience contamination:** Instructor-only information (answer keys, teaching tips, timing cues) never appears in content files. It belongs in `docs/05-instructor-pack/`.
3. **Consistent formatting:** All chapters follow the same Markdown structure—heading levels, code block languages, admonition styles.
4. **Source attribution:** If content is derived from reference materials, the source is noted in the chapter metadata, not buried in prose.

### Example Prompts

=== "Write a Chapter"

    ```text
    /course-content Draft Module 1 Lesson 2: "Understanding Pods" based on the 
    approved outline. Include a transition from Lesson 1 (cluster architecture) 
    and set up the concepts needed for Lesson 3 (Deployments).
    ```

=== "Rewrite for Audience"

    ```text
    /course-content Rewrite Module 2 for a non-technical audience. The current 
    version assumes deep Linux knowledge. Simplify the examples and add more 
    analogies. Keep the learning objectives intact.
    ```

=== "Expand a Section"

    ```text
    /course-content The "Networking" section in Module 4 is too thin—just 3 
    paragraphs. Expand it with concrete examples of ClusterIP, NodePort, and 
    LoadBalancer services. Include a comparison table.
    ```

### Markdown Formatting Standards

The **`markdown-course-writing`** skill enforces consistent formatting across all course documents:

- **Heading hierarchy:** H1 for lesson title, H2 for major sections, H3 for subsections. Never skip levels.
- **Code blocks:** Always specify the language (` ```yaml `, ` ```bash `, ` ```python `). Never use bare triple backticks.
- **Tables:** Use Markdown tables for comparisons and structured data. Keep them readable (no 10-column monsters).
- **Admonitions:** Use MkDocs-style admonitions for warnings, tips, and notes in course content.

??? example "Good vs. Bad Chapter Structure"
    **Good:** Structured, audience-aware, no internal markers
    ```markdown
    # Understanding Pods
    
    In the previous lesson, we explored the cluster architecture...
    
    ## What is a Pod?
    
    A Pod is the smallest deployable unit in Kubernetes...
    
    ## Pod Lifecycle
    
    Pods move through several phases...
    
    ## Key Takeaways
    
    - A Pod wraps one or more containers
    - Pods are ephemeral by design
    ```
    
    **Bad:** Missing transitions, internal markers, inconsistent format
    ```markdown
    # Pods
    
    TODO: add intro
    
    pods are the smallest unit. they run containers.
    
    (Kyle: check if this is still accurate for k8s 1.29)
    
    ## next steps
    fill in later
    ```

---

## Phase 3: Lab Design

Labs require precise execution steps that students can follow without ambiguity. The **`course-lab-design`** skill creates exercises with a rigid structure that separates what students see from what instructors know.

### Lab Structure

Every lab produced by the skill includes these components:

| Component | Audience | Description |
|---|---|---|
| **Objective** | Both | What the student will accomplish |
| **Prerequisites** | Both | What must be completed before starting |
| **Environment** | Both | Required software, hardware, and configuration |
| **Steps** | Learner | Numbered, unambiguous instructions |
| **Validation** | Learner | How to verify each step succeeded |
| **Answer Key** | Instructor only | Expected outputs, common mistakes, grading rubric |
| **Troubleshooting** | Instructor only | Common failure points and their solutions |
| **Timing** | Instructor only | Expected duration per section |

!!! danger "Audience Separation is Non-Negotiable"
    The lab skill enforces strict separation between learner-facing and instructor-facing content. Answer keys, troubleshooting guides, and timing estimates are **never** placed in the learner guide file. This prevents accidental leakage when distributing materials to students.
    
    - Learner guide: `docs/03-labs/01-lab-deploy-pod/learner-guide.md`
    - Instructor guide: `docs/05-instructor-pack/01-lab-deploy-pod-answers.md`

### Example Prompts

=== "Design a Lab"

    ```text
    /course-lab Create a lab exercise for "Deploying Your First Pod." Students 
    should write a Pod manifest, apply it, verify the Pod is running, and view 
    its logs. Include common failure points for the instructor.
    ```

=== "Add Validation Steps"

    ```text
    /course-lab The Lab 3 exercise is missing validation criteria. Add explicit 
    checks after each major step so students know if they succeeded.
    ```

=== "Design a Capstone"

    ```text
    /course-lab Design a capstone project for the final day. Students should 
    deploy a multi-tier application (frontend + backend + database) using 
    everything learned in the course. Include a grading rubric.
    ```

### Environment Specifications

The lab skill is explicit about environment requirements. Every lab specifies:

- **Software versions:** exact versions of tools (e.g., "kubectl v1.28+", "Docker 24.x")
- **Hardware minimums:** CPU, RAM, and disk requirements for the lab environment
- **Network requirements:** whether internet access is needed during the lab
- **Pre-configured resources:** any cloud accounts, clusters, or databases that must exist before starting

??? example "Sample Environment Spec"
    ```markdown
    ## Environment Requirements
    
    | Resource | Requirement |
    |---|---|
    | Kubernetes Cluster | Minikube v1.32+ or kind v0.20+ |
    | kubectl | v1.28 or later |
    | Docker | 24.x (for building images) |
    | RAM | Minimum 8 GB available |
    | Disk | Minimum 10 GB free |
    | Internet | Required (for pulling container images) |
    
    ### Pre-Lab Setup
    1. Start your local cluster: `minikube start --memory=4096`
    2. Verify connectivity: `kubectl cluster-info`
    3. Create the lab namespace: `kubectl create namespace lab-01`
    ```

---

## Phase 4: Materials

Course delivery requires different views for different audiences. This phase produces two completely separate material sets.

### Learner Materials

The **`learner-materials`** skill creates student-facing assets:

- **Handouts:** condensed summaries of key concepts from each module
- **Worksheets:** fill-in-the-blank or short-answer exercises for reinforcement
- **Glossaries:** definitions of all technical terms used in the course
- **Reading packs:** pre-class preparation materials and background reading
- **Recap notes:** post-class summaries for review

**Critical rule:** Learner materials must never contain:

- Answer keys or solutions
- Instructor timing cues or speaking notes
- Internal review comments or QA annotations
- Draft markers or "TODO" items

### Instructor Materials

The **`instructor-reference-materials`** skill creates teacher-facing assets:

- **Speaking points:** suggested talking points for each section
- **Timing guidance:** expected duration per section with buffer recommendations
- **Answer keys:** full solutions for all exercises and labs
- **Discussion prompts:** suggested questions to ask the class at key moments
- **Demo cues:** step-by-step instructions for live demonstrations
- **Delivery risk reminders:** common pitfalls and how to recover (e.g., "If the demo fails, use the pre-recorded backup in `assets/demos/`")

### Example Prompts

=== "Generate Learner Pack"

    ```text
    Generate the student handout for Module 1. Include a glossary of all 
    terms introduced and a worksheet with 5 review questions.
    ```

=== "Generate Instructor Pack"

    ```text
    Generate the instructor guide for Module 1. Include speaking points, 
    timing for each section, the answer key for the worksheet, and notes 
    on common student questions.
    ```

=== "Generate Pre-Class Reading"

    ```text
    Create a pre-class reading pack for Module 3. Students should arrive 
    with basic understanding of YAML syntax and Linux file permissions.
    ```

!!! tip "Generate Both Simultaneously"
    When working on a module, generate the learner and instructor materials in the same session. This ensures the instructor's answer key exactly matches the learner's worksheet questions, and that timing estimates account for the actual exercise difficulty.

---

## Phase 5: Quality Assurance

The **`course-quality-assurance`** skill hunts for problems. It does not fix them—it documents them with severity classifications so that Phase 6 (QC) can make informed release decisions.

### What QA Checks

The QA skill systematically reviews:

| Check Category | What It Looks For |
|---|---|
| **Completeness** | Missing modules, empty sections, placeholder text |
| **Consistency** | Terms defined differently across chapters, conflicting instructions |
| **Accuracy** | Code examples that won't compile, outdated CLI flags, wrong version numbers |
| **Audience contamination** | Answer keys in learner materials, instructor notes in content files |
| **Lab-content alignment** | Labs that reference concepts not yet taught, or skip taught concepts |
| **Formatting** | Broken Markdown, inconsistent heading levels, bare code blocks |
| **AI slop** | Generic filler text, robotic transitions, unsupported superlatives |

### Severity Classification

Every issue found by QA is classified:

| Severity | Definition | Release Impact |
|---|---|---|
| **Critical** | Factually wrong content that would mislead students | Blocks release |
| **Major** | Missing sections, broken labs, audience contamination | Blocks release |
| **Minor** | Formatting issues, typos, unclear phrasing | Does not block release |
| **Suggestion** | Potential improvements, style recommendations | Informational only |

### Example Prompts

=== "Full QA Review"

    ```text
    /course-qa Review the complete course package. Check all modules, labs, 
    and materials. Log every issue found with severity classification.
    ```

=== "Targeted QA"

    ```text
    /course-qa Review Module 3 and its associated Lab 3. Focus on whether 
    the lab steps actually match what was taught in the chapter.
    ```

=== "Pre-Release QA"

    ```text
    /course-qa This is the final QA pass before release. Focus on blocking 
    issues only—critical and major severity. We already fixed the minor 
    formatting issues from Round 1.
    ```

### QA Output Format

QA findings are written to `docs/06-qa/` as structured Markdown:

```markdown
# QA Review — Round 1

## Summary
- Critical: 2
- Major: 5
- Minor: 12
- Suggestion: 8

## Critical Issues

### QA-001: Incorrect kubectl Command in Lab 2
- **Location:** docs/03-labs/02-lab-deployments/learner-guide.md, line 47
- **Description:** `kubectl create deployment` uses deprecated `--generator` flag
- **Impact:** Students will see a warning message and may get confused
- **Recommendation:** Replace with `kubectl create deploy nginx --image=nginx:1.25`

### QA-002: Answer Key Leaked in Learner Handout
- **Location:** docs/04-learner-pack/module-02-handout.md, line 89
- **Description:** The "Expected Output" section contains the full solution
- **Impact:** Students see answers before attempting the exercise
- **Recommendation:** Move to docs/05-instructor-pack/module-02-answers.md
```

!!! info "QA Does Not Fix"
    The QA skill is explicitly instructed to **log issues, not fix them**. This ensures you maintain a paper trail of what was wrong before the content gets repaired. The `content-crafter` agent or `course-content-authoring` skill handles the actual fixes.

---

## Phase 6: Quality Control

The **`course-quality-control-reporting`** skill makes the release decision. It reviews QA findings, verifies which issues have been closed, and generates a formal report.

### What QC Decides

QC answers exactly four questions:

1. **Which issues have been closed?** (verified fixed)
2. **Which issues are accepted as known risks?** (won't fix before release)
3. **Is this version allowed to be released?** (yes/no/conditional)
4. **If conditional, what are the conditions?** (e.g., "Release for internal preview only")

### Release Decision Types

| Decision | Meaning |
|---|---|
| **Full Release** | All blocking issues closed. Ready for external distribution. |
| **Limited Release** | Some known issues accepted. Released to a restricted audience (e.g., internal preview, pilot cohort). |
| **Internal Trial** | Significant issues remain. Released for internal dry-run only. |
| **Blocked** | Critical issues unresolved. Cannot release in any form. |

### Example Prompts

=== "Standard QC"

    ```text
    /course-qc Check the latest QA report (docs/06-qa/qa-review-round-02.md). 
    Have all blocking issues been resolved? Give me a release recommendation.
    ```

=== "Conditional Release"

    ```text
    /course-qc We have 2 remaining major issues. Evaluate whether we can 
    proceed with a limited release for the pilot cohort next week.
    ```

=== "Release Readiness"

    ```text
    /course-release-ready Check all QA/QC history. Are we clear to move 
    files into release/v1.0/?
    ```

### QC Output Format

QC reports are written to `docs/07-qc/`:

```markdown
# QC Report — 2026-05-15

## Decision: LIMITED RELEASE

## Issue Status
| ID | Severity | Status | Notes |
|---|---|---|---|
| QA-001 | Critical | ✅ Closed | Fixed in commit abc123 |
| QA-002 | Critical | ✅ Closed | Moved to instructor pack |
| QA-003 | Major | ⚠️ Accepted | Known limitation, documented in release notes |
| QA-004 | Major | ✅ Closed | Rewritten |
| QA-005 | Major | ❌ Open | Deferred to v1.1 |

## Conditions
- Release approved for internal pilot cohort only
- QA-005 must be resolved before external release
- Re-review required after QA-005 fix

## Approver
Course Development Lead (via QC review session)
```

---

## Phase 7: Release

Once QC passes, files are eligible to move into the `release/` directory. This directory contains only stable, versioned deliverables.

### Release Directory Structure

```text
release/
  v1.0/
    learner-pack/      # All student-facing materials
    instructor-pack/   # All teacher-facing materials
    labs/              # Lab guides (learner version only)
    slides/            # Presentation files (if applicable)
    RELEASE-NOTES.md   # What's in this version, known issues
  v1.1-preview/
    ...
```

### What Goes Into Release

- ✅ Finalized course content that passed QC
- ✅ Learner handouts and worksheets
- ✅ Instructor guides and answer keys
- ✅ Lab guides (learner version)
- ✅ Release notes with known issues

### What Does NOT Go Into Release

- ❌ QA review logs (stay in `docs/06-qa/`)
- ❌ QC decision reports (stay in `docs/07-qc/`)
- ❌ Raw reference materials (stay in `references/`)
- ❌ Draft or work-in-progress files
- ❌ Project governance files (briefs, milestones)

!!! warning "Never Edit Release Files Directly"
    If you find a typo in a released file, do **not** edit it in `release/`. Edit the source file in `docs/02-content/`, run QA/QC, and then copy the corrected version to a new release folder (e.g., `release/v1.0.1/`). This maintains traceability.

---

## Reference Materials

The pack includes helper skills for processing external inputs that feed into the course pipeline.

### Reference Document Review

The **`reference-document-review`** skill reads external materials and converts them into structured inputs:

- **PDFs:** Extracts key content, normalizes formatting, identifies teaching-relevant sections
- **DOCX/DOC:** Converts to Markdown with preserved structure
- **Images:** Describes diagrams and screenshots for accessibility
- **Web pages:** Captures and normalizes web content with source attribution
- **Meeting transcripts:** Extracts teaching points and action items from messy notes

=== "Process a PDF"

    ```text
    /course-source-review Read the attached Kubernetes documentation PDF. 
    Extract the sections relevant to our Module 3 (Networking) and format 
    them as course input notes.
    ```

=== "Synthesize Multiple Sources"

    ```text
    /course-source-review We have 3 reference documents in references/. 
    Compare their coverage of "Pod Security Standards" and produce a 
    synthesis suitable for our content authoring phase.
    ```

!!! info "References Are Inputs, Not Outputs"
    Reference material processing produces **intermediate artifacts**—extracted notes, gap analyses, and rewrite suggestions. These must be further processed by `course-content-authoring` before they become actual course content. Never promote reference extraction directly to `docs/02-content/`.

### Course Diagrams

The **`drawio-course-diagrams`** skill generates XML-based diagrams for:

- Architecture overviews (e.g., Kubernetes cluster topology)
- Module dependency maps
- Workflow diagrams (e.g., CI/CD pipeline stages)
- Lab topology diagrams
- Timeline visualizations

The output is draw.io-compatible XML saved to `assets/diagrams/`.

---

## Commands and Agents

The course pack provides two layers of quick entry points beyond the skills themselves.

### Commands

Commands are high-frequency workflow triggers. Each command loads the appropriate skill(s) and applies the correct context:

| Command | Purpose | Skills Loaded |
|---|---|---|
| `/course-init` | Initialize or take over a project | `course-directory-structure`, `development-plan-governance` |
| `/course-audit` | Audit directories and file locations | `course-directory-structure` |
| `/course-outline` | Generate or refactor syllabi | `course-outline-design` |
| `/course-content` | Write or rewrite course prose | `course-content-authoring`, `markdown-course-writing` |
| `/course-lab` | Generate exercises and demonstrations | `course-lab-design` |
| `/course-source-review` | Read references and extract material | `reference-document-review` |
| `/course-qa` | Run QA review cycles | `course-quality-assurance` |
| `/course-qc` | Make QC release decisions | `course-quality-control-reporting` |
| `/course-release-ready` | Check if files can move to `release/` | `course-quality-control-reporting` |
| `/course-methodize` | Extract reusable workflows from the session | `course-methodology-playbook` |

### Agents

Agents provide role-based execution. Each agent has a specific persona and strict boundaries:

| Agent | Role | Key Constraint |
|---|---|---|
| **`curriculum-build`** | Primary agent — Project Manager + Lead | Can delegate to any other agent |
| **`directory-curator`** | Manages file trees and naming conventions | Does not write course content |
| **`outline-architect`** | Handles high-level structure and hour allocation | Does not write chapter prose |
| **`content-crafter`** | Writes and polishes course prose | Does not make structural decisions |
| **`lab-designer`** | Builds exercises and validation steps | Enforces learner/instructor separation |
| **`source-synthesizer`** | Distills external reference material | Does not produce final course content |
| **`qa-auditor`** | Finds and logs issues | **Does not edit content directly** |
| **`qc-gatekeeper`** | Approves or denies release candidates | **Does not edit content directly** |

### Three-Layer Architecture

The course pack operates on three layers:

```text
┌─────────────────────────────────────────┐
│  Commands (/course-init, /course-qa)    │  ← "How to quickly trigger a workflow"
├─────────────────────────────────────────┤
│  Agents (qa-auditor, content-crafter)   │  ← "Who does the work"
├─────────────────────────────────────────┤
│  Skills (course-quality-assurance, ...) │  ← "How to do the work"
└─────────────────────────────────────────┘
```

- **Skills** define the detailed procedures and rules
- **Agents** provide role-based personas with access to specific skills
- **Commands** are shortcut entry points that load the right agent + skill combination

---

## Quality Gates

The pack enforces 7 distinct quality gates. Each gate has specific criteria that must be satisfied before proceeding to the next phase. Content should not bypass these gates.

### Gate 1: Project Gate

Before any outline work begins:

- [ ] Clear project goals documented in `docs/00-project/project-brief.md`
- [ ] Target audience and prerequisites defined
- [ ] Deliverable boundaries explicit (what's in scope, what's not)
- [ ] Milestone plan with deadlines
- [ ] Change control process established

### Gate 2: Outline Gate

Before content authoring begins:

- [ ] Module breakdown with logical sequencing
- [ ] Learning objectives per module (using measurable verbs)
- [ ] Hour allocation per module (lecture, lab, discussion)
- [ ] Prerequisite mapping between modules
- [ ] Learner benefit statement for each module

### Gate 3: Content Gate

Before lab design begins:

- [ ] Chapter structure stable (no pending major restructuring)
- [ ] Terminology consistent across all chapters
- [ ] No chapter-to-chapter contradictions
- [ ] All figures, tables, and code examples present and referenced
- [ ] No internal markers ("TODO", "TBD") remaining in content files

### Gate 4: Lab Gate

Before materials generation begins:

- [ ] Every lab has stated objectives
- [ ] Environment requirements specified with exact versions
- [ ] Step-by-step instructions are unambiguous
- [ ] Validation criteria after each major step
- [ ] Learner guide and instructor answer key in separate files
- [ ] Common failure points documented for instructors

### Gate 5: Materials Gate

Before QA begins:

- [ ] Learner pack contains zero instructor-only information
- [ ] Instructor pack contains answer keys for all exercises
- [ ] Instructor pack includes timing estimates and delivery risk notes
- [ ] All links, images, and cross-references resolve correctly

### Gate 6: QA Gate

Before QC begins:

- [ ] Documented list of issues found with severity classification
- [ ] Each issue has a location, description, and recommended fix
- [ ] Critical and major issue counts clearly stated
- [ ] No unclassified issues remaining

### Gate 7: QC Gate

Before release:

- [ ] Every critical issue is closed (verified fixed)
- [ ] Every major issue is either closed or explicitly accepted as a known risk
- [ ] Formal release decision documented (Full / Limited / Internal Trial / Blocked)
- [ ] If conditional release, conditions are explicitly stated
- [ ] Release notes prepared with known issues listed

---

## Taking Over an Existing Project

One of the most common scenarios is inheriting a messy collection of course files. The pack provides a structured approach:

### Step 1: Audit First, Move Nothing

```text
/course-audit Scan the current directory. Classify every file by which layer 
it belongs to (project, outline, content, labs, learner, instructor, qa, qc, 
reference, archive). Don't move anything yet.
```

The agent produces a classification table and a proposed reorganization plan.

### Step 2: Review the Plan

The agent's reorganization plan will:

- Map each existing file to its correct destination in the standard structure
- Flag files that could belong in multiple locations
- Identify files that appear to be duplicates or outdated versions
- Suggest which files should be archived

### Step 3: Execute with Confirmation

Only after you approve the plan does the agent execute the moves:

```text
The plan looks good. Execute the reorganization, but don't touch anything 
in the "unsure" category—leave those for me to decide.
```

!!! warning "Conservative by Default"
    When the agent is unsure about a file's classification, it **does not guess**. It flags the file for human decision. This prevents accidental data loss from misclassified files.

---

## Handling Large-Scale Changes

The pack defines specific triggers for when a change is considered "large-scale" and requires plan updates before implementation:

- Adjusting the course's overall target audience or positioning
- Changing module sequencing or merging/splitting modules
- Adding or removing entire lab exercises
- Restructuring the learner/instructor material boundary
- Changing the delivery format (e.g., from 3-day workshop to self-paced)

For any large-scale change:

1. Update `docs/00-project/change-log.md` with the change rationale
2. Update the milestone plan if deadlines are affected
3. Update the outline if module structure changes
4. **Then** proceed with content modifications

---

## Common Mistakes and How to Avoid Them

??? warning "Jumping Straight to Content"
    **Mistake:** Starting to write chapter prose without a project brief or approved outline.
    
    **Why it fails:** Without agreed-upon structure, you'll write content that doesn't align with any shared vision. At QA time, you discover entire modules are redundant, missequenced, or targeted at the wrong audience level.
    
    **Fix:** Always complete Phase 0 (Setup) and Phase 1 (Outline) before Phase 2 (Content).

??? warning "Mixing Audiences in One File"
    **Mistake:** Putting instructor notes, answer keys, and student handouts in the same document.
    
    **Why it fails:** When you distribute materials to students, you inevitably forget to strip the instructor notes. Students see the answers before attempting exercises.
    
    **Fix:** Enforce the `04-learner-pack/` and `05-instructor-pack/` split from day one. Never combine them "for convenience."

??? warning "Treating References as Course Content"
    **Mistake:** Collecting many reference PDFs and docs but never distilling them into actual course material.
    
    **Why it fails:** You end up with a `references/` folder full of material that "we read" but never integrated. Or worse, you promote raw reference extractions directly into the content directory.
    
    **Fix:** Every reference document must go through `reference-document-review` to produce structured extraction notes. Those notes then feed into `course-content-authoring` for proper course integration.

??? warning "QA Without QC"
    **Mistake:** Running QA to find issues but never running QC to make a release decision.
    
    **Why it fails:** You have a list of problems but no formal record of which problems were fixed, which were accepted, and whether the version is approved for release. This leaves the project in perpetual "almost done" state.
    
    **Fix:** Every QA round must be followed by a QC round that produces a formal release decision.

??? warning "Editing Release Files Directly"
    **Mistake:** Finding a typo in `release/v1.0/module-01.md` and fixing it in place.
    
    **Why it fails:** You lose traceability. The release directory should reflect exactly what passed QC. If you edit it directly, you can't be sure the change was reviewed.
    
    **Fix:** Fix the source file in `docs/02-content/`, run QA/QC on the fix, then create a new release version (`release/v1.0.1/`).

??? warning "Using Date-Based or Author-Based Naming"
    **Mistake:** Files named `kubernetes-draft-kyle-may15.md` or `final-FINAL-v2.md`.
    
    **Why it fails:** These names carry no structural information. Within a week, no one (including you) can tell which file is current or where it belongs.
    
    **Fix:** Use the pack's naming conventions: kebab-case, numeric prefixes, descriptive names that reflect the content's role in the course structure.

---

## Tips and Best Practices

??? tip "One Phase at a Time"
    Do not ask the agent to "Write a course on Docker." It will fail or produce shallow results. Instead, guide it through the pipeline: Outline first, then Content, then Labs. Each phase builds on the previous one's output.

??? tip "Audit Before Moving"
    When inheriting files, always use `/course-audit` first. Let the agent propose a restructuring plan before it starts moving files around. This prevents accidental misclassification.

??? tip "Separate Audiences Early"
    When designing a lab, immediately enforce the split between `learner-guide.md` and `instructor-guide.md`. Trying to decouple answers from instructions later is error-prone and time-consuming.

??? tip "Use the Synthesizer for Messy Inputs"
    If you have a messy meeting transcript, don't dump it into a content file. Feed it to the `source-synthesizer` agent or `reference-document-review` skill to extract the teaching points first. This produces structured notes that are far easier to work with.

??? tip "QA Does Not Fix"
    The `qa-auditor` agent is explicitly instructed to **log issues, not fix them**. This ensures you maintain a paper trail of what was wrong before the `content-crafter` goes in to repair the text. Never combine finding and fixing in the same pass.

??? tip "Version Your Releases"
    Always use version numbers or dates in the release directory: `release/v1.0/`, `release/v1.1/`, `release/2026-06-pilot/`. Never use a bare `release/` with files directly inside—it becomes impossible to track which version was distributed to which audience.

??? tip "Use the Orchestrator for Complex Tasks"
    If your request spans multiple phases (e.g., "restructure the outline and then rewrite Modules 2-4"), use the orchestrator rather than calling individual skills. It maintains context across phases and ensures the pipeline ordering is respected.

??? tip "Methodology Capture"
    After completing a major course development cycle, run `/course-methodize` to extract reusable workflows, templates, and lessons learned. This builds your team's institutional knowledge and makes the next course faster to produce.

---

## Skill Reference

| Skill Name | Description | Trigger Phrases |
|---|---|---|
| `course-development-orchestrator` | Drives course projects end-to-end. | "Course development", "manage curriculum", "drive the course project" |
| `course-directory-structure` | Creates and audits course folder trees. | "Reorganize course files", "audit directory", "initialize project" |
| `development-plan-governance` | Manages milestones, risks, and plans. | "Course development plan", "milestones", "change log" |
| `course-outline-design` | Creates syllabi and module maps. | "Course outline", "syllabus", "hour allocation", "module breakdown" |
| `course-content-authoring` | Expands outlines into chapter prose. | "Write chapter", "expand content", "draft module" |
| `markdown-course-writing` | Normalizes formatting and style. | "Format as markdown", "clean up course notes", "normalize terms" |
| `course-lab-design` | Designs exercises and environments. | "Create a lab", "hands-on exercise", "design a capstone" |
| `learner-materials` | Creates student-facing reading packs. | "Learner handouts", "student guide", "glossary", "worksheet" |
| `instructor-reference-materials` | Creates teaching notes and answer keys. | "Teacher notes", "instructor guide", "answer key", "speaking points" |
| `course-quality-assurance` | Checks completeness and logs issues. | "QA review", "check course quality", "find issues" |
| `course-quality-control-reporting` | Forms release decisions and reports. | "QC report", "release readiness", "release decision" |
| `drawio-course-diagrams` | Generates XML for draw.io diagrams. | "Course diagram", "draw.io architecture", "module map" |
| `reference-document-review` | Extracts insights from input materials. | "Read reference", "summarize notes", "extract from PDF" |
| `course-methodology-playbook` | Packages reusable course guidance. | "Extract methodology", "reusable workflow", "lessons learned" |
| `skill-reference-discovery` | Mines external sources for skill ideas. | "Find agent skills", "extract reusable patterns" |
