# Reading-Notes: Agent Comprehension Memory

**Branch**: `contract-driven-companion` (dev)
**Status**: Awaiting Momus review
**Date**: 2026-06-18

---

## 0. Context

User's "先读后写" discipline requires agents to take notes while reading. Research confirmed:
- GraphDB (Neo4j) is overkill for single-agent notes
- SQLite is the proven lightweight pattern but premature at <10K entries
- evidence-ledger (research pack) has the right JSONL+lint pattern but wrong schema (academic, not code)
- **Decision**: new lightweight `reading-notes` format in core companion, zero coupling to research pack

## 1. Problem

Agent reads files (code/docs/config) every session but forgets understanding next session. Must re-read from scratch. No persistent comprehension memory exists in core companion.

## 2. Scope

### In Scope
- `reading-notes.jsonl` format (one JSONL file per project under `.petfish/notes/`)
- Schema with `file_type` enum (code/doc/config/test) covering all file types
- `reading_notes_lint.py` validator (pure stdlib, inspired by evidence_lint.py pattern)
- fish-brain SKILL.md Section 10: when to take notes, how to retrieve
- Pack AGENTS.md: reading-notes behavior instruction

### Out of Scope
- SQLite migration (Phase 2, when JSONL >10K entries)
- tree-sitter AST extraction (future enhancement)
- Graph database (research rejected as overkill)
- Modifying evidence-ledger in research pack (zero coupling)

## 3. Design

### 3.1 Schema

```jsonl
{
  "note_id": "CN-000001",
  "file_path": "src/auth.ts",
  "file_type": "code",
  "symbol": "validateToken",
  "language": "typescript",
  "summary": "Validates JWT signature and expiration",
  "dependencies": ["src/utils/jwt.ts"],
  "line_range": {"start": 42, "end": 78},
  "confidence": "high",
  "tags": ["auth"]
}
```

| Field | Type | Required | Notes |
|---|---|---|---|
| note_id | string | ✅ | `CN-\d{6}` sequential |
| file_path | string | ✅ | relative to project root |
| file_type | enum | ✅ | code/doc/config/test |
| symbol | string\|null | ❌ | function/class/module; null for docs |
| language | string | ✅ | typescript/python/markdown/yaml etc. |
| summary | string | ✅ | one sentence: what this file/symbol does |
| dependencies | array | ❌ | referenced file paths |
| line_range | object\|null | ❌ | {start,end}; null for whole-file or docs |
| confidence | enum | ✅ | high/medium/low |
| tags | array | ❌ | free-form labels |

### 3.2 File Location

`.petfish/notes/reading-notes.jsonl` — one file per project. Append-only.

### 3.3 Lint Script

`fish-brain/scripts/reading_notes_lint.py` (~60 lines, pure stdlib):
- Validate note_id format (CN-\d{6})
- Validate file_type enum
- Validate confidence enum
- Check required fields present
- Warn on missing summary or empty dependencies for code files

### 3.4 Agent Behavior (SKILL.md Section 10)

When to take notes:
- Reading a file for the first time in a project
- Understanding a function/class/module for a task
- Discovering non-obvious dependencies or architecture patterns

When NOT to take notes:
- Quick lookups (grep, single-line check)
- Files already noted (check by file_path before re-noting)
- Trivial files (empty, generated, boilerplate)

How to retrieve:
- Before reading a file, check if a note exists (grep reading-notes.jsonl by file_path)
- If note exists with high confidence → use the summary, skip full re-read
- If note is stale (file modified after note) → re-read and update note

## 4. Integration Points

| File | Change | Risk |
|---|---|---|
| `.petfish/notes/reading-notes.jsonl` | NEW data file | None (runtime created) |
| `fish-brain/scripts/reading_notes_lint.py` | NEW script (~60 lines) | None |
| `fish-brain/SKILL.md` Section 10 | Additive | Low |
| `packs/.../AGENTS.md` | Additive reading-notes behavior | Low |

**NOT changing**: evidence-ledger, research pack, install pipeline (notes dir created at runtime like fish-trail).

## 5. Non-Coupling with Research Pack

- evidence-ledger stays in optional/research-skill-pack, unchanged
- reading-notes lives in core/petfish-companion-skill, independent schema
- Shared pattern (JSONL + lint + sequential IDs) but NOT shared code
- No import, no dependency, no schema alignment required

## 6. Claim Boundary

This establishes:
- Agent can persist file-level comprehension across sessions
- Retrieval avoids redundant re-reads for already-understood files

This does NOT establish:
- Full codebase graph understanding (no AST, no call graph)
- Real-time incremental indexing (notes are written by agent, not auto-extracted)
- Accuracy of summaries (agent-authored, may contain errors)
- Cross-project knowledge transfer (one JSONL per project)

## 7. QA Scenarios (executable, tool + steps + expected results)

### QA-1: Lint script validates correct entries

**Tool**: `uv run python`
**Steps**:
1. Create `.petfish/notes/reading-notes.jsonl` with 3 valid entries (code/doc/config)
2. Run `uv run python fish-brain/scripts/reading_notes_lint.py --input .petfish/notes/reading-notes.jsonl`
**Expected**: exit code 0, output contains `status: pass`, `errors: 0`

### QA-2: Lint script rejects invalid entries

**Tool**: `uv run python`
**Steps**:
1. Create `.petfish/notes/test-invalid.jsonl` with entries:
   - Entry with `note_id: "BAD-ID"` (wrong format, should be CN-\d{6})
   - Entry with `file_type: "movie"` (not in enum)
   - Entry missing `summary` (required field)
2. Run `uv run python fish-brain/scripts/reading_notes_lint.py --input .petfish/notes/test-invalid.jsonl`
**Expected**: exit code 1, output contains 3 errors matching each violation

### QA-3: Agent note-taking behavior (SKILL.md integration)

**Tool**: manual verification (agent instruction compliance)
**Steps**:
1. Read `fish-brain/SKILL.md` Section 10
2. Verify it contains: "When to take notes" subsection with ≥3 trigger conditions
3. Verify it contains: "How to retrieve" subsection with stale-check rule
4. Verify it contains: "When NOT to take notes" with ≥2 exclusion conditions
**Expected**: all 3 subsections present with specified content

### QA-4: AGENTS.md reading-notes instruction present

**Tool**: `grep`
**Steps**:
1. Run `grep -c "reading-notes" packs/core/petfish-companion-skill/AGENTS.md`
**Expected**: count ≥ 1 (the instruction section exists)

### QA-5: Non-coupling verification

**Tool**: `grep`
**Steps**:
1. Run `grep -r "evidence-ledger\|evidence_ledger\|EV-" packs/core/petfish-companion-skill/.opencode/skills/fish-brain/scripts/reading_notes_lint.py`
**Expected**: zero matches (no coupling to research pack's evidence-ledger)
2. Run `grep -r "reading-notes\|reading_notes\|CN-" packs/optional/research-skill-pack/`
**Expected**: zero matches (research pack unaffected)

### QA-6: Staleness detection logic documented

**Tool**: manual verification
**Steps**:
1. Read SKILL.md Section 10 "How to retrieve"
2. Verify it specifies: "Before reading a file, check if a note exists by file_path"
3. Verify it specifies: "If file mtime > note timestamp → note is stale → re-read and update"
**Expected**: both rules explicitly present

## 8. Success Criteria for Momus

- [ ] Scope is bounded and doesn't touch research pack
- [ ] Schema is code+doc+config unified (not split into separate formats)
- [ ] Lint script is pure stdlib, follows evidence_lint.py pattern
- [ ] Integration is additive (no existing file behavior change)
- [ ] Non-coupling with evidence-ledger is explicit
- [ ] Claim boundary is honest about limitations
- [ ] QA-1 through QA-6 are executable with specific tools + steps + expected results
