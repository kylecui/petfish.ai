# Research Skill Pack — Implementation Plan

> Status: Pending Momus Review  
> Reference: `dev_reference/skills_design_plan/research-skill-pack-plan-v2.md`  
> Branch: dev  
> Pack name: `research-skill-pack`  
> Pack alias: `research`

---

## 1. Objective

Create the 11th PEtFiSh skill pack: a **research workbench** (`research-skill-pack`) that transforms vague research tasks into traceable, evidence-backed, quality-reviewed research outputs. The pack covers three research domains (scientific, product, planning) through a shared substrate of 10 MVP core skills.

This plan covers **Phase 0 + Phase 1 + Phase 2** (plan freeze → SKILL.md authoring → scripts & schemas). Phase 3 (end-to-end validation) is out of scope for this plan but is the immediate next step.

---

## 2. Scope Decisions

### 2.1 What is IN scope

| Item | Count | Detail |
|---|---|---|
| MVP core skills | 10 | research-router, research-brief-framer, research-source-discovery, research-literature-access, research-note-capture, research-insight-log, research-evidence-ledger, research-synthesis, research-report-writer, research-quality-reviewer |
| Python scripts | 9 | init_research_project.py, validate_research_workspace.py, validate_schemas.py, source_index.py, literature_access_record.py, note_lint.py, insight_lint.py, evidence_lint.py, report_quality_gate.py |
| JSON schemas | 7 | source-index, literature-access, access-attempts, excerpt-notes, insight-log, evidence-ledger, quality-review |
| Templates & assets | 7+ | research-brief-template.md, literature-access-template.json, excerpt-notes-empty.jsonl, insight-log-empty.jsonl, evidence-ledger-empty.jsonl, research-report-template.md, quality-gates.md |
| Pack infrastructure | 5 | pack-manifest.json, AGENTS.md, README.md, opencode.json.example, CHANGELOG.md |
| Eval skeletons | 2 | core-trigger-evals.json, mvp-evals.json |

### 2.2 What is OUT of scope

- Domain-specific packs (scientific-*, product-*, planning-*) — Phase 4-6
- research-citation-auditor — Phase 5
- scientific-review-rebuttal — Phase 4
- Full eval suite — Phase 7
- Security threat model doc — Phase 8
- Installer integration (install.sh/install.ps1 alias registration) — separate PR after MVP validated
- `dedupe_sources.py` — deferred to post-MVP (source dedup is useful but not required for core flow)
- MCP server integration — not planned

### 2.3 Key constraints

- All Python scripts use `uv run`; no `pip install`
- Scripts with external deps use PEP 723 inline metadata or pack-level pyproject.toml
- All scripts: non-interactive, `--help` support, structured output (JSON or Markdown)
- SKILL.md descriptions bilingual (Chinese + English) per existing pack convention
- Pack directory lives at `packs/optional/research-skill-pack/`
- Installed skills are derived artifacts — not tracked in git

---

## 3. Pack Directory Structure

```text
packs/optional/research-skill-pack/
  README.md
  AGENTS.md
  CHANGELOG.md
  pack-manifest.json
  opencode.json.example
  pyproject.toml

  .opencode/skills/
    research-router/
      SKILL.md
      references/
        routing-rules.md
        research-type-taxonomy.md
      evals/
        trigger-evals.json

    research-brief-framer/
      SKILL.md
      assets/
        research-brief-template.md
        research-questions-template.md
      references/
        brief-quality-rubric.md

    research-source-discovery/
      SKILL.md
      references/
        source-quality-rubric.md
      scripts/
        source_index.py

    research-literature-access/
      SKILL.md
      references/
        legal-access-policy.md
        credential-safety.md
      scripts/
        literature_access_record.py
      assets/
        literature-access-template.json

    research-note-capture/
      SKILL.md
      references/
        excerpt-note-method.md
      scripts/
        note_lint.py
      assets/
        excerpt-notes-empty.jsonl
        reading-note-template.md

    research-insight-log/
      SKILL.md
      references/
        insight-types.md
      scripts/
        insight_lint.py
      assets/
        insight-log-empty.jsonl

    research-evidence-ledger/
      SKILL.md
      references/
        evidence-taxonomy.md
      scripts/
        evidence_lint.py
      assets/
        evidence-ledger-empty.jsonl

    research-synthesis/
      SKILL.md
      references/
        synthesis-patterns.md
        confidence-grading.md

    research-report-writer/
      SKILL.md
      assets/
        research-report-template.md
        executive-summary-template.md

    research-quality-reviewer/
      SKILL.md
      references/
        quality-gates.md
        ai-slop-checklist.md
      scripts/
        report_quality_gate.py

  schemas/
    source-index.schema.json
    literature-access.schema.json
    access-attempts.schema.json
    excerpt-notes.schema.json
    insight-log.schema.json
    evidence-ledger.schema.json
    quality-review.schema.json
    examples/
      source-index-example.json
      evidence-ledger-example.json
      literature-access-example.json
      access-attempts-example.json
      excerpt-notes-example.json
      insight-log-example.json
      quality-review-example.json

  scripts/
    init_research_project.py
    validate_research_workspace.py
    validate_schemas.py

  evals/
    trigger/
      core-trigger-evals.json
    output/
      mvp-evals.json
```

---

## 4. Research Workspace Structure (generated by init_research_project.py)

```text
research/
  CONTEXT.md
  00_brief/
    research-brief.md
    research-questions.md
    scope-boundaries.md
  01_sources/
    source-index.jsonl
    bibliography.bib
    literature-access.json
    access-attempts.jsonl
    source-notes/
  02_notes/
    excerpt-notes.jsonl
    reading-notes/
    insight-log.jsonl
    idea-inbox.md
    quote-bank.md
  03_evidence/
    evidence-ledger.jsonl
    claim-map.md
    contradiction-log.md
    uncertainty-log.md
  04_methods/
    research-design.md
  05_analysis/
    synthesis-matrix.md
  06_outputs/
    report.md
    executive-summary.md
  07_reviews/
    quality-review.md
  adr/
```

---

## 5. Skill Summary Table

| # | Skill | Trigger (when to use) | Key Output |
|---|---|---|---|
| 1 | research-router | User says "research", "investigate", "survey", "lit review" or gives vague research intent | Research task plan with recommended skill chain |
| 2 | research-brief-framer | Vague research goal needs structuring | research-brief.md, research-questions.md |
| 3 | research-source-discovery | Need to find papers, docs, competitors, reports | source-index.jsonl, search-strategy.md |
| 4 | research-literature-access | Need full text of paywalled literature | access-attempts.jsonl, literature-access.json |
| 5 | research-note-capture | Reading sources, extracting key passages | excerpt-notes.jsonl, reading-notes/*.md |
| 6 | research-insight-log | Ideas, analogies, hypotheses during research | insight-log.jsonl, idea-inbox.md |
| 7 | research-evidence-ledger | Promoting notes to formal evidence for claims | evidence-ledger.jsonl, claim-map.md |
| 8 | research-synthesis | Aggregating evidence into findings | synthesis-matrix.md, key-findings.md |
| 9 | research-report-writer | Writing final research report from evidence | report.md, executive-summary.md |
| 10 | research-quality-reviewer | Reviewing report quality, logic, citations, AI slop | quality-review.md, ai-slop-review.md |

---

## 6. Core Data Flow

```text
User Request
  ↓
research-router (classify → skill chain)
  ↓
research-brief-framer (question → brief)
  ↓
research-source-discovery (find → register)
  ↓
research-literature-access (legal access → version record)
  ↓
research-note-capture (read → excerpt → annotate)
  ↓
research-insight-log (connect → hypothesize → record)
  ↓
research-evidence-ledger (promote notes → formal evidence)
  ↓
research-synthesis (cluster → compare → conclude)
  ↓
research-report-writer (evidence → report)
  ↓
research-quality-reviewer (audit → grade → feedback)
```

---

## 7. Evidence Type System

| Type | Meaning | Can enter report? |
|---|---|---|
| EXTRACTED | Directly from source | Yes, with citation |
| INFERRED | Derived from multiple facts | Yes, with reasoning |
| AMBIGUOUS | Conflicting sources or insufficient evidence | Yes, as uncertainty |
| PROPOSED | Our suggestion/hypothesis | Yes, labeled as recommendation |

---

## 8. Script Specifications

All scripts: Python 3.11+, `uv run`, non-interactive, `--help`, structured output.

| Script | Location | Purpose | Input | Output |
|---|---|---|---|---|
| init_research_project.py | scripts/ | Initialize research workspace | --type, --name, --path | Directory tree |
| validate_research_workspace.py | scripts/ | Audit workspace completeness | --root | Validation report (JSON) |
| validate_schemas.py | scripts/ | Validate JSON schemas against example payloads | --schemas-dir, --examples-dir | Pass/fail per schema |
| source_index.py | research-source-discovery/scripts/ | Add/update source entries | --add/--update args | Updated source-index.jsonl |
| literature_access_record.py | research-literature-access/scripts/ | Record access attempts | --work-id, --attempts | Updated access-attempts.jsonl |
| note_lint.py | research-note-capture/scripts/ | Validate excerpt notes | --input path | Lint report (JSON) |
| insight_lint.py | research-insight-log/scripts/ | Validate insight entries | --input path | Lint report (JSON) |
| evidence_lint.py | research-evidence-ledger/scripts/ | Validate evidence entries | --input path | Lint report (JSON) |
| report_quality_gate.py | research-quality-reviewer/scripts/ | Run quality gates on report | --report, --ledger | Quality report (JSON+MD) |

### 8.1 Quality Review Example Payload

The v2 plan provides examples for 6 of 7 schemas (Sections 6.2–6.7). The 7th schema (`quality-review`) uses this example:

```json
{
  "review_id": "QR-000001",
  "report_path": "06_outputs/report.md",
  "reviewer": "research-quality-reviewer",
  "review_date": "2026-05-08",
  "overall_grade": "B",
  "dimensions": [
    {
      "dimension": "question-alignment",
      "score": "pass",
      "notes": "Report addresses all three research questions from the brief."
    },
    {
      "dimension": "evidence-completeness",
      "score": "partial",
      "notes": "2 of 5 key claims lack evidence_id references."
    },
    {
      "dimension": "citation-coverage",
      "score": "partial",
      "notes": "Executive summary makes 3 claims without inline citations."
    },
    {
      "dimension": "logic-chain",
      "score": "pass",
      "notes": "No logical jumps detected between findings and recommendations."
    },
    {
      "dimension": "counter-evidence",
      "score": "fail",
      "notes": "No contradicting evidence discussed; only supporting sources cited."
    },
    {
      "dimension": "method-fit",
      "score": "pass",
      "notes": "Thematic synthesis appropriate for the research type."
    },
    {
      "dimension": "actionability",
      "score": "pass",
      "notes": "Recommendations include priority and conditions."
    },
    {
      "dimension": "expression-quality",
      "score": "partial",
      "notes": "Section 4 uses 'increasingly important' without source support."
    },
    {
      "dimension": "risk-disclosure",
      "score": "pass",
      "notes": "Limitations section covers data freshness and sample size."
    }
  ],
  "blocking_issues": [
    "2 key claims missing evidence references",
    "No contradicting evidence discussed"
  ],
  "recommendations": [
    "Add evidence_id to claims CL-000003 and CL-000005",
    "Add a contradiction analysis subsection",
    "Replace 'increasingly important' with sourced trend data"
  ]
}
```

This example is saved as `schemas/examples/quality-review-example.json` and validated against `schemas/quality-review.schema.json`.

---

## 9. Implementation Phases

### Phase 0: Plan Freeze (this document)
- [x] Confirm pack name, alias, scope
- [x] Confirm MVP 10 skills
- [x] Confirm directory structure
- [x] Confirm data schemas
- [ ] Momus review pass

### Phase 1: Directory + SKILL.md + Templates
**Deliverables:**
- Pack directory with all 10 SKILL.md files
- pack-manifest.json
- AGENTS.md (pack-level)
- README.md
- All template/asset files
- All reference files
- Eval skeletons

**Exit criteria:**
- Every SKILL.md has valid frontmatter (name, description)
- Description is bilingual, ≤1024 chars
- Skill names match `^[a-z0-9]+(-[a-z0-9]+)*$`
- Trigger scenarios, inputs, outputs, workflow, quality gates documented per skill
- Templates match the schemas defined in v2 plan

**Verification (exact steps):**

> All verification commands use PowerShell (pwsh). On macOS/Linux, adapt paths accordingly.

1. Check all 10 SKILL.md files exist:
   ```pwsh
   Get-ChildItem -Path packs/optional/research-skill-pack/.opencode/skills/*/SKILL.md | Measure-Object
   ```
   Expected: Count = 10.

2. Validate frontmatter for each SKILL.md:
   ```pwsh
   Get-ChildItem -Path packs/optional/research-skill-pack/.opencode/skills/*/SKILL.md | ForEach-Object {
     $count = (Select-String -Path $_.FullName -Pattern "^---" | Measure-Object).Count
     "$($_.Directory.Name): $count"
   }
   ```
   Expected: each skill shows `2` (opening and closing frontmatter delimiters).

3. Validate skill names match regex:
   ```pwsh
   Get-ChildItem -Directory -Path packs/optional/research-skill-pack/.opencode/skills/ | ForEach-Object {
     if ($_.Name -notmatch '^[a-z0-9]+(-[a-z0-9]+)*$') { "FAIL: $($_.Name)" }
   }
   ```
   Expected: no output (all names pass).

4. Validate description length:
   ```pwsh
   Get-ChildItem -Path packs/optional/research-skill-pack/.opencode/skills/*/SKILL.md | ForEach-Object {
     $desc = (Select-String -Path $_.FullName -Pattern "^description:" | Select-Object -First 1).Line
     if ($desc.Length -gt 1024 + "description: ".Length) { "TOO LONG: $($_.Directory.Name)" }
   }
   ```
   Expected: no output (all descriptions ≤1024 chars).

5. Run skill-lint on each skill:
   ```pwsh
   Get-ChildItem -Directory -Path packs/optional/research-skill-pack/.opencode/skills/ | ForEach-Object {
     uv run packs/core/petfish-companion-skill/.opencode/skills/skill-lint/scripts/lint_skill.py --path $_.FullName
   }
   ```
   Expected: score ≥ 80 for each skill.

6. Verify pack-manifest.json:
   ```pwsh
   $manifest = Get-Content packs/optional/research-skill-pack/pack-manifest.json | ConvertFrom-Json
   if ($manifest.skill_count -ne 10) { "FAIL: skill_count = $($manifest.skill_count)" }
   $actualFiles = Get-ChildItem -Recurse -File packs/optional/research-skill-pack/ -Exclude ".git*" | ForEach-Object {
     $_.FullName.Replace((Resolve-Path packs/optional/research-skill-pack/).Path, '').TrimStart('\','/')
   }
   # Verify all actual files are listed in $manifest.contents
   ```
   Expected: `skill_count` == 10, `skills` has all 10 names, `contents` covers all files.

7. Verify all asset/template files exist:
   ```pwsh
   $requiredFiles = @(
     "packs/optional/research-skill-pack/.opencode/skills/research-brief-framer/assets/research-brief-template.md",
     "packs/optional/research-skill-pack/.opencode/skills/research-literature-access/assets/literature-access-template.json",
     "packs/optional/research-skill-pack/.opencode/skills/research-note-capture/assets/excerpt-notes-empty.jsonl",
     "packs/optional/research-skill-pack/.opencode/skills/research-insight-log/assets/insight-log-empty.jsonl",
     "packs/optional/research-skill-pack/.opencode/skills/research-evidence-ledger/assets/evidence-ledger-empty.jsonl",
     "packs/optional/research-skill-pack/.opencode/skills/research-report-writer/assets/research-report-template.md",
     "packs/optional/research-skill-pack/.opencode/skills/research-quality-reviewer/references/quality-gates.md"
   )
   $requiredFiles | ForEach-Object { if (!(Test-Path $_)) { "MISSING: $_" } }
   ```
   Expected: no output (all files exist).

8. Verify pack infrastructure files exist:
   ```pwsh
   $infraFiles = @(
     "packs/optional/research-skill-pack/README.md",
     "packs/optional/research-skill-pack/AGENTS.md",
     "packs/optional/research-skill-pack/CHANGELOG.md",
     "packs/optional/research-skill-pack/pack-manifest.json",
     "packs/optional/research-skill-pack/opencode.json.example"
   )
   $infraFiles | ForEach-Object { if (!(Test-Path $_)) { "MISSING: $_" } }
   ```
   Expected: no output (all files exist).

9. Verify eval skeletons exist:
   ```pwsh
   $evalFiles = @(
     "packs/optional/research-skill-pack/evals/trigger/core-trigger-evals.json",
     "packs/optional/research-skill-pack/evals/output/mvp-evals.json"
   )
   $evalFiles | ForEach-Object { if (!(Test-Path $_)) { "MISSING: $_" } }
   ```
   Expected: no output (both files exist).

10. Verify reference files exist (at least one per skill that declares references/):
    ```pwsh
    $refDirs = Get-ChildItem -Directory -Path packs/optional/research-skill-pack/.opencode/skills/*/references -ErrorAction SilentlyContinue
    $refDirs | ForEach-Object {
      $count = (Get-ChildItem -File $_.FullName | Measure-Object).Count
      if ($count -eq 0) { "EMPTY: $($_.FullName)" }
    }
    ```
    Expected: no output (every references/ directory has at least one file).

### Phase 2: Scripts + Schemas
**Deliverables:**
- 9 Python scripts with --help (see Section 8 for exact list)
- 7 JSON schemas (see Section 3 schemas/ directory)
- pyproject.toml with dependencies

**Exit criteria:**
- `uv run scripts/init_research_project.py --help` works
- `uv run scripts/validate_research_workspace.py --root research/` catches missing files
- Lint scripts detect common errors (missing source_id, missing location, etc.)
- All schemas validate the example JSONL entries from the v2 plan

**Verification (exact steps):**

> All verification commands use PowerShell (pwsh). On macOS/Linux, adapt paths accordingly.
> Temp directory: use `$env:TEMP` on Windows, `/tmp` on Unix.

1. All 9 scripts respond to --help without error:
   ```pwsh
   Set-Location packs/research-skill-pack
   uv run scripts/init_research_project.py --help
   uv run scripts/validate_research_workspace.py --help
   uv run scripts/validate_schemas.py --help
   uv run .opencode/skills/research-source-discovery/scripts/source_index.py --help
   uv run .opencode/skills/research-literature-access/scripts/literature_access_record.py --help
   uv run .opencode/skills/research-note-capture/scripts/note_lint.py --help
   uv run .opencode/skills/research-insight-log/scripts/insight_lint.py --help
   uv run .opencode/skills/research-evidence-ledger/scripts/evidence_lint.py --help
   uv run .opencode/skills/research-quality-reviewer/scripts/report_quality_gate.py --help
   ```
   Expected: each exits 0 and prints usage info.

2. Init script creates workspace:
   ```pwsh
   $testDir = Join-Path $env:TEMP "test-research-$(Get-Random)"
   uv run scripts/init_research_project.py --type mixed --name test-research --path $testDir
   ```
   Expected: directory tree matches Section 4 (00_brief/ through 07_reviews/ plus adr/).

3. Validate script catches missing files:
   ```pwsh
   $emptyDir = Join-Path $env:TEMP "empty-research-$(Get-Random)"
   New-Item -ItemType Directory -Path $emptyDir -Force
   uv run scripts/validate_research_workspace.py --root $emptyDir
   ```
   Expected: exits non-zero, reports missing directories/files.

4. Validate script passes on fresh workspace:
   ```pwsh
   uv run scripts/validate_research_workspace.py --root $testDir
   ```
   Expected: exits 0, reports no errors.

5. Schema validation (using uv-managed script):
   ```pwsh
   # validate_schemas.py is a dev helper that imports jsonschema via PEP 723 inline metadata.
   # It validates 7 schemas against example payloads bundled in schemas/examples/.
   uv run scripts/validate_schemas.py --schemas-dir schemas/ --examples-dir schemas/examples/
   ```
   Expected: all 7 schemas pass. Example payloads are:
   - `source-index-example.json` — from v2 plan Section 6.2
   - `evidence-ledger-example.json` — from v2 plan Section 6.3
   - `literature-access-example.json` — from v2 plan Section 6.4
   - `access-attempts-example.json` — from v2 plan Section 6.5
   - `excerpt-notes-example.json` — from v2 plan Section 6.6
   - `insight-log-example.json` — from v2 plan Section 6.7
   - `quality-review-example.json` — defined below in Section 8.1

6. Lint script detects errors:
   ```pwsh
   $badNote = Join-Path $env:TEMP "bad-note.jsonl"
   '{"note_id":"NOTE-1","source_id":"","original_text":"test"}' | Set-Content $badNote
   uv run .opencode/skills/research-note-capture/scripts/note_lint.py --input $badNote
   ```
   Expected: reports error for empty source_id.

7. No pip install in any file:
   ```pwsh
   Set-Location -Path (git rev-parse --show-toplevel)
   Select-String -Path (Get-ChildItem -Recurse -File packs/optional/research-skill-pack/) -Pattern "pip install"
   ```
   Expected: no matches.

---

## 10. Quality Gates for This Implementation

Before declaring Phase 1+2 complete:

1. **Structure audit**: `validate_research_workspace.py` passes on a freshly initialized workspace
2. **Skill format**: Every SKILL.md passes `skill-lint` checks
3. **Script health**: All 9 scripts respond to `--help` without error
4. **Schema validity**: All 7 schemas are valid JSON Schema draft-07
5. **Pack manifest**: `pack-manifest.json` lists all skills and contents accurately
6. **No secrets**: No credentials, tokens, or passwords in any file
7. **uv compliance**: No `pip install` anywhere; all scripts runnable via `uv run`

---

## 11. Integration with PEtFiSh Ecosystem

### 11.1 Installer Registration (deferred)
After MVP validation, register alias `research` in install.sh and install.ps1. Add to platforms.json if needed.

### 11.2 Profile Mapping (deferred)
Candidate profiles for auto-install:
- New `research` profile → `research`, `petfish`
- `comprehensive` profile → add `research`

### 11.3 Companion Skill Sense
Add research-related keywords to companion's Tier 1 triggers:
- 研究, 调研, 综述, 文献, 论文, 竞品分析, 产品研究, 规划研究, evidence, literature review

### 11.4 AGENTS.md Merge
Pack's AGENTS.md will be merged into target project's instructions file during install, following existing merge conventions.

---

## 12. Risks and Mitigations

| Risk | Mitigation |
|---|---|
| 10 skills is too many for MVP | Each skill is narrowly scoped; router provides single entry point |
| SKILL.md descriptions too long, poor trigger accuracy | Keep descriptions ≤1024 chars, test with trigger evals |
| Evidence ledger feels heavy for simple tasks | research-router recommends light mode for simple tasks |
| Scripts have external Python deps | Use PEP 723 inline metadata or pack pyproject.toml with uv |
| Overlap with existing course pack's QA/QC skills | Research QA focuses on evidence/citation; course QA focuses on curriculum structure — clearly distinct |

---

## 13. Definition of Done

Phase 1+2 complete when:
- [ ] 10 SKILL.md files exist with valid frontmatter and complete workflow documentation
- [ ] Pack directory matches Section 3 structure
- [ ] 9 scripts all respond to `--help`
- [ ] 7 JSON schemas validate example data from v2 plan
- [ ] init_research_project.py creates the workspace from Section 4
- [ ] pack-manifest.json is accurate
- [ ] README.md documents installation and quick start
- [ ] AGENTS.md provides research workflow rules
- [ ] No `pip install`, no hardcoded credentials
- [ ] All file/skill names follow naming conventions
