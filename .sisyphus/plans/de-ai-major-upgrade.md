# De-AI Major Upgrade Plan

**Date**: 2025-07-06
**Status**: Draft — pending user approval
**Scope**: Upgrade PEtFiSh's de-AI + personal style capabilities by integrating 13 GitHub repos + fresh style extraction from user's 11 writing samples

---

## Part 0: Research Findings Summary

### Repos Studied (13 repos, 3 categories)

| Category | Repos | Core Value for PEtFiSh |
|---|---|---|
| **De-AI Rewriting** | humanizer, Humanizer-zh, stop-slop, taste-skill, shuorenhua | Specific AI-pattern detection rules + rewriting moves (empty phrases, triplets, formulaic sentences, "correct-but-boring" problem) |
| **AI Detection** | chatgpt-comparison-detection, AIGC_text_detector, openai-detector | Linguistic-level detection features (perplexity, burstiness, syntactic symmetry, token likelihood density) |
| **Style/Personality** | nuwa-skill, writing-style-skill, agent-style, WRITING.md | Multi-dimensional style extraction methodology; opinionated writing with personality |

### Current Skill Audit (petfish-style-rewriter v4.1.0)

**Strengths** (keep these):
- Sophisticated academic humanization framework (10-feature linguistic detection + 7 humanization moves)
- Multi-mode: strict/normal/light/academic/email
- 5 reference files + 3 Python validators (style_check, audit_headings, normalize_text)
- Already covers burstiness, perplexity, authorial voice, controlled asymmetry
- Strong Chinese-English mixed-term rules

**Gaps** (this upgrade targets these):
1. **No personal style profile** — uses generic "Petfish style" rules, not extracted from user's actual writing
2. **No standalone detection skill** — detection is embedded in the rewriter; can't be used independently
3. **Chinese academic patterns under-developed** — the 10-feature framework is English-centric
4. **No style extraction workflow** — can't ingest new writing samples to update the profile
5. **"Correct but boring" gap** — taste-skill's aesthetic dimension is missing
6. **Email register gap** — user's email style (casual, direct, lowercase openings) is not captured

### User's Writing Style Fingerprint (from 11 PDFs)

**Chinese Academic (7 papers):**
- 谦逊框架：标题用"浅析/浅见/浅论"（modest scope-claiming）
- 短句主导：平均句长 20-30字，偶有长复合句但不堆叠
- 技术密度适中：术语首次出现带括号英文/全称，后续直接使用
- 论证结构：背景（从历史脉络起）→ 问题分析 → 分维度讨论 → 应对策略 → 展望
- 特殊习惯：用"笔者"而非"我们"；数字编号列表密集；过渡用"因此/此外/然而"
- 情感克制：不使用"令人瞩目/ groundbreaking"等夸张词

**English Academic (XDP paper):**
- Standard CS paper voice: "we propose/design/implement"
- Passive voice for method descriptions: "is implemented/evaluated"
- Direct technical statements, no hedging in contributions
- Minor grammar imperfections (L1 interference: articles, tense consistency)

**Email/Business (3 emails):**
- 完全不同的语域：casual, lowercase openings ("hi professor"), stream-of-consciousness
- Direct task instructions with numbered steps
- Polite but not formal ("Thanks & Regards", "Let me know if you have concerns")
- Technical precision maintained even in casual register

**Cross-lingual fingerprint:**
- 双语思维：中英文写作的底层逻辑一致（problem → decomposition → solution），但表达面具不同
- 共享特征：技术精确性 > 修辞效果；列表/编号偏好；直接结论导向

---

## Part 1: Proposed Architecture

### Option Chosen: Pipeline Architecture (3 skills + 1 data asset)

```
                    ┌─────────────────────┐
                    │  style-extractor    │ ← one-time / periodic
  Writing samples   │  (NEW skill)        │    Input: PDFs/docs
  ──────────────►   │  Extracts profile   │──→ style-profile.md (DATA)
                    └─────────────────────┘
                                                │
                                                ▼
  Input text       ┌─────────────────────┐    ┌─────────────────────┐
  ──────────────►   │  de-ai-detector     │──→ │  petfish-style-     │
                    │  (NEW skill)        │    │  rewriter (UPGRADED)│──→ Output
                    │  Scans for AI       │    │  Uses profile +     │
                    │  patterns           │    │  detection report   │
                    └─────────────────────┘    └─────────────────────┘
```

**Why 3 skills, not 1:**
- `style-extractor` is used rarely (when profile needs refresh) — shouldn't load on every rewrite
- `de-ai-detector` can be used standalone ("检测这段话的AI味") without rewriting
- `petfish-style-rewriter` stays the main workhorse but gets enriched inputs

**Why not a new pack:**
- All three belong to the same domain (writing quality)
- Pack rename has high touchpoint cost (just did this for calibrate)
- `petfish-style-skill` pack already has the right name scope

### Skill Details

#### 1. `style-extractor` (NEW)

**Purpose**: Analyze a person's writing samples and produce a structured style profile.

**Workflow** (adapted from nuwa-skill methodology):
1. Input: directory of writing samples (PDF/DOCX/MD/TXT)
2. Convert all to markdown (doc-reader)
3. Analyze across 8 dimensions:
   - Sentence-level: length distribution, complexity, rhythm (burstiness)
   - Vocabulary: formality level, domain density, favored transitions, unique expressions
   - Structural: paragraph shape, argumentation pattern, list usage, heading style
   - Tonal: hedging, certainty markers, first-person voice, emotional register
   - Punctuation: comma/semicolon/dash patterns, parenthetical habits
   - Cross-lingual: Chinese vs English differences, shared thinking patterns
   - Register sensitivity: how style shifts between academic/email/casual
   - AI distinguishability: what makes this person's writing NOT look like AI
4. Output: `style-profile.md` — structured profile with quantitative stats + qualitative patterns + representative excerpts

**Triggers**: "提炼我的写作风格", "extract my style", "分析我的文风", "update style profile"

**Pack location**: `petfish-style-skill/.opencode/skills/style-extractor/`

#### 2. `de-ai-detector` (NEW)

**Purpose**: Scan text for AI writing patterns and produce a detection report (no rewriting).

**Detection layers** (integrated from humanizer, stop-slop, AIGC detector):
- **Layer 1 — Surface patterns**: empty phrases, triplet abuse, "not X but Y", dash overuse, AI vocabulary
- **Layer 2 — Linguistic features**: burstiness score, sentence-length variance, syntactic symmetry, token predictability
- **Layer 3 — Structural signals**: paragraph templating, connector stacking, logical over-coherence, missing human noise
- **Layer 4 — Chinese-specific**: 四字成语堆砌, 排比句过密, "不仅...而且..."滥用, 总结性套话

**Output**: Detection report with severity scores + specific flagged passages + rewrite suggestions

**Triggers**: "检测AI味", "detect AI writing", "这段话像AI写的吗", "AI slop check"

**Pack location**: `petfish-style-skill/.opencode/skills/de-ai-detector/`

#### 3. `petfish-style-rewriter` (UPGRADED)

**Changes**:
- Load `style-profile.md` as the primary style reference (replaces generic rules)
- Accept detection report as optional input (from de-ai-detector)
- Add `taste` dimension (from taste-skill): not just correct, but engaging
- Strengthen Chinese-specific de-AI rules (from Humanizer-zh, shuorenhua)
- Add email register calibration (from user's actual email samples)
- Version bump: 4.1.0 → 5.0.0

#### 4. `style-profile.md` (DATA ASSET)

**Location**: `petfish-style-skill/.opencode/assets/style-profile.md`

This is NOT a skill — it's a data file that both de-ai-detector and petfish-style-rewriter reference. It contains the extracted style profile from the user's writing samples.

---

## Part 2: De-AI Detection Pattern Library

### Integrated from all repos (the "greatest hits")

#### English AI Patterns (from humanizer, stop-slop, openai-detector)

| Pattern | Signal | Source | Detection Method |
|---|---|---|---|
| Triplet abuse | "clear, concise, and actionable" | stop-slop | Regex: 3+ adjective/noun lists |
| Empty "not X but Y" | "not just a tool, but a paradigm" | stop-slop | Regex: "not (just\|only\|merely).*but" |
| Dash overuse | "—" every 2-3 sentences | humanizer | Count per paragraph |
| AI vocabulary | "delve, leverage, robust, seamless, nuanced" | humanizer | Word list match |
| Low burstiness | CV < 0.4 for sentence length | openai-detector | style_check.py (existing) |
| Syntactic symmetry | Same sentence template 3+ times | AIGC detector | Template extraction + match |
| Connector stacking | "Therefore... Moreover... Furthermore..." | stop-slop | Transition word density |
| Paragraph templating | Every para same shape/length | AIGC detector | Paragraph length variance |

#### Chinese AI Patterns (from Humanizer-zh, shuorenhua, + new)

| Pattern | Signal | Example | Detection Method |
|---|---|---|---|
| 四字成语堆砌 | 3+ 成语 per paragraph | "日新月异、蓬勃发展、举足轻重" | Count per paragraph |
| 排比句过密 | 3+ parallel clauses in sequence | "不仅...而且...更加..." | Pattern match |
| 总结性套话 | Hollow summary phrases | "总而言之/综上所述/不可否认" | Phrase list match |
| 中英空格AI味 | Unnatural spacing | "利用 AI 技术" vs "利用AI技术" | PEtFiSh rule: compact terms |
| "基于...的"过载 | Method framing overuse | "基于深度学习的...方法" | Count per section |
| 过度正式的连接词 | "此外/然而/因此" too frequent | Every sentence starts with one | Transition density |
| 缺乏个人声音 | No "笔者认为/我们发现" | Pure third-person passive | First-person ratio |
| 结构完美但无味 | Correct but boring | taste-skill problem | Burstiness + vocabulary diversity |

---

## Part 3: Workflow Optimization

### Current Recommended Workflow (from de-ai-slop.md)

```
Input → Detect AI patterns → Rewrite to remove → Done
```

### Problems with this workflow

1. **No style target** — "remove AI patterns" without knowing what the HUMAN target sounds like
2. **No register awareness** — academic vs email vs casual need different treatments
3. **No feedback loop** — can't learn from what the user accepts/rejects
4. **Single-pass** — one rewrite pass is often insufficient for deep de-AI
5. **No verification** — doesn't check if the output itself still reads as AI

### Optimized Workflow (PEtFiSh integrated)

```
                    ┌─────────────────────────┐
                    │  style-profile.md       │
                    │  (pre-extracted)        │
                    └────────┬────────────────┘
                             │
  Input ──► de-ai-detector ──► petfish-style-rewriter ──► de-ai-detector (verify) ──► Output
             │                      │                       │
             │                      │                       │
             ▼                      ▼                       ▼
        Detection              Rewrite using          Re-scan: if AI score
        Report (severity       profile +              still high → another
        + flagged passages)    detection report       rewrite pass
```

**Key improvements:**
1. **Style profile feeds the rewriter** — target is the user's voice, not generic "human"
2. **Detection runs BEFORE and AFTER** — verify the rewrite actually reduced AI signal
3. **Iterative loop** — if post-rewrite detection still flags issues, do another pass
4. **Register-aware** — profile contains separate fingerprints for academic/email/casual

### When to use which combination

| User intent | Detection | Rewrite | Verify |
|---|---|---|---|
| "检测AI味" | ✅ | ❌ | ❌ |
| "润色" (polish) | ❌ | ✅ (light mode) | ❌ |
| "去AI味" (de-AI) | ✅ | ✅ (strict mode) | ✅ |
| "按我的风格写" | ❌ | ✅ (profile-based) | ❌ |
| "改成自然的人话" | ✅ | ✅ (standard mode) | ✅ |
| "论文润色" | ✅ | ✅ (academic mode) | ✅ |

---

## Part 4: Style Extraction Plan (from user's 11 PDFs)

### Methodology (nuwa-skill inspired, PEtFiSh adapted)

**Phase A — Quantitative Analysis**
1. Sentence length distribution (mean, median, CV for burstiness)
2. Vocabulary frequency analysis (top 50 content words, domain terms)
3. Transition word inventory (Chinese: 因此/此外/然而/笔者; English: however/moreover/therefore/we)
4. Paragraph length distribution
5. First-person ratio (笔者/我们/we vs passive voice)
6. List/numbering density
7. Punctuation pattern (逗号/分号/冒号/破折号 frequency)

**Phase B — Qualitative Analysis**
1. Argumentation pattern (how does the user build an argument?)
2. Scope-claiming style (浅析/浅见 vs contribution claims)
3. Register sensitivity (how does email style differ from paper style?)
4. Authorial voice markers (what phrases does the user favor?)
5. AI-distinguishability (what makes this writing recognizably human?)

**Phase C — Output: style-profile.md**

Structured as:
```markdown
# Petfish Personal Style Profile

## Extracted: 2025-07-06
## Samples: 7 Chinese academic, 1 English academic, 3 emails

## Chinese Academic Fingerprint
[Sentence stats + vocabulary + patterns + excerpts]

## English Academic Fingerprint
[Sentence stats + vocabulary + patterns + excerpts]

## Email Register Fingerprint
[Tone + structure + signature phrases]

## Cross-Lingual Thinking Pattern
[Shared logic + divergent expression]

## AI Distinguishability Signals
[What makes this NOT AI — burstiness, imperfection, vocabulary choices]

## Do / Don't List
[Concrete rules derived from the analysis]
```

---

## Part 5: Implementation Plan

### Phase 1: Style Profile Extraction (output only, no skill creation)
- [ ] Run quantitative analysis on all 11 converted markdown files
- [ ] Run qualitative analysis
- [ ] Produce `style-profile.md`
- **Deliverable**: 1 markdown file in `tmp/de-ai-slop/style-profile.md` (review before integrating)

### Phase 2: New Skill — de-ai-detector
- [ ] Create skill structure: SKILL.md + references/detection-rules.md + references/chinese-patterns.md + scripts/detect_ai.py
- [ ] Integrate detection patterns from all repos
- [ ] Create detection report output template
- **Deliverable**: Complete `de-ai-detector` skill in petfish-style-skill pack

### Phase 3: New Skill — style-extractor
- [ ] Create skill structure: SKILL.md + references/extraction-dimensions.md + scripts/analyze_style.py
- [ ] Adapt nuwa-skill methodology into PEtFiSh workflow
- [ ] Create style-profile output template
- **Deliverable**: Complete `style-extractor` skill in petfish-style-skill pack

### Phase 4: Upgrade petfish-style-rewriter
- [ ] Add style-profile loading mechanism
- [ ] Add detection-report input format
- [ | Add Chinese-specific de-AI rules from Humanizer-zh/shuorenhua
- [ ] Add taste dimension from taste-skill
- [ ] Update AGENTS.md routing for 3-skill pipeline
- [ ] Version bump 4.1.0 → 5.0.0
- **Deliverable**: Upgraded rewriter, pack-manifest v5.0.0

### Phase 5: Integration & Touchpoints
- [ ] Update pack-manifest.json (skill_count: 3, version: 5.0.0)
- [ ] Update pack AGENTS.md (3-skill routing rules)
- [ ] Update agents-rules/petfish-style.md
- [ ] Update README/docs/website
- [ ] Update catalog_query.py (new skill triggers)
- [ ] Update installers (pack contents)
- [ ] Sync external repo + market
- **Deliverable**: Full ecosystem integration

### Phase 6: Verification
- [ ] skill-lint on all 3 skills
- [ ] pytest
- [ ] Pre-release gate
- [ ] GitHub release

---

## Part 6: Decisions Needed

### D1: Pack rename?
Current: `petfish-style-skill` (1 skill)
Options:
- **Keep** (recommended): name is broad enough for "writing style" domain
- Rename to `writing-quality-pack` or `de-ai-style-pack`

### D2: style-profile.md location?
- **Option A**: Inside the pack (`assets/style-profile.md`) — ships with the pack, generic
- **Option B**: User's project root (`.petfish/style-profile.md`) — per-user, not shipped
- **Option C**: Both — pack ships a template, user's actual profile is project-local

**Recommendation**: Option C. Pack contains `references/style-profile-template.md` (the schema). User's extracted profile goes to `.petfish/style-profile.md` (project-local, gitignored or committed per user choice).

### D3: Detection script language?
- The existing `style_check.py` is Python with basic burstiness/length stats
- **Upgrade it** or **create new `detect_ai.py`**?
- Recommendation: Create new `detect_ai.py` in de-ai-detector skill, keep `style_check.py` in rewriter for backward compat

### D4: Implementation sequence?
- **Sequential** (Phase 1→6 as listed): safe, each phase builds on previous
- **Parallel** (Phase 2+3 in parallel, then 4, then 5): faster

**Recommendation**: Phase 1 first (you review the style profile), then Phase 2+3 parallel, then 4+5.

---

## Part 7: Risk Assessment

| Risk | Probability | Impact | Mitigation |
|---|---|---|---|
| Style profile overfits to academic register | Medium | Medium | Include email samples; add register-sensitivity dimension |
| De-AI detector too aggressive (false positives) | High | High | Severity scoring + "needs review" tier; user can override |
| Rewriter output loses user's technical precision | Medium | High | Profile includes "preserve" rules for domain terms |
| Skill boundary confusion (when detector vs rewriter) | Medium | Low | Clear AGENTS.md routing table |
| Chinese detection patterns miss domain-specific AI usage | Low | Medium | Allow user to add custom patterns |
