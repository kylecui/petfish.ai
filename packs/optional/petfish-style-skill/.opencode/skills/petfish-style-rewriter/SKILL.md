---
name: petfish-style-rewriter
description: Rewrite, polish, humanize, de-AI, or formalize Chinese or English technical, academic, business, course, proposal, patent, and email content into Petfish's structured, evidence-based, engineering-oriented style. Supports custom style profiles, de-ai-detector reports, enhanced Chinese de-AI rules, and optional taste enhancement. Triggers: 用我的语言习惯表达, 说人话, 润色, 去AI味, 按我的风格写, 改得更像人写的, 论文润色, 学术写作, abstract rewrite, rewrite my paper.
compatibility: opencode
metadata:
  version: "5.0.0"
  author: "Petfish"
  owner: "Petfish"
  default_mode: "strict"
---

# Petfish Style Rewriter

## Purpose

Rewrite the user's text into Petfish's preferred writing style.

This style is not casual writing. It is structured, professional, engineering-oriented, and problem-driven. It values clear reasoning over rhetorical force.

The goal is to make the text sound like a real technical professional wrote it, not like a generic AI model generated it.

## Activation Rules

Use this skill when the user asks for any of the following:

-用我的语言习惯表达
-按我的风格写
-说人话
-去AI味
-润色一下
-改得更自然
-改得更像人写的
-论文润色
-学术写作
-改写摘要
-改写abstract
-改写related work
- rewrite in my style
- make this clearer
- make this more professional but less AI-like
- rewrite my paper
- rewrite my abstract
- humanize my academic writing
- make this sound like a real researcher wrote it

Also use this skill for technical papers, course materials, proposals, emails, patent drafts, project documents, strategy documents, and academic papers (including abstracts, introductions, related work sections, method sections, results, discussions, and conclusions) when the main task is rewriting or expression control.

## Default Mode

Use `strict` by default unless the user explicitly asks for light polishing.

Modes:

- `strict`: rebuild the structure and expression. Best for AI-like or verbose text.
- `normal`: improve structure and wording while preserving some original phrasing.
- `light`: minimal polishing. Preserve the original structure unless it is clearly broken.
- `academic`: formal paper/report style with restrained claims, authorial voice, and controlled human-like asymmetry. See the "Academic Writing Mode" section below.
- `email`: support-engineer style; clear status, findings, evidence, action, and polite closure.

Select `academic` mode when the input is, or should read as, a research artifact: paper drafts, thesis chapters, abstracts, related work, survey articles, technical reports in academic register, or grant proposals. In academic mode, the engineering-style rules still apply to argument clarity, but the text is also shaped to read like a competent human researcher wrote it — with burstiness, authorial voice, hedged claims, and occasional controlled imperfection. Loading `references/academic-writing.md` is required for academic-mode rewrites.

## Academic Writing Mode

Academic mode is a first-class mode. It preserves engineering-style argument clarity while adding burstiness, authorial voice, hedged claims, and deliberate template-breaking so the text reads like a real researcher wrote it. Load `references/academic-writing.md` before any academic-mode rewrite; it contains the full linguistic detection framework (10 features), humanization techniques (7 moves), section templates, tension-resolution rules, and the academic self-check.

## Core Style Model

Petfish's style is problem-modeling, not slogan-writing: state minimal background, identify the real problem, decompose it into 2–4 concrete dimensions, explain each dimension with condition/limitation/implication, and converge to a necessity or next step. See `references/style-guide.md` for the full structure, paragraph patterns, and tone rules.

## Rewrite Workflow

Before writing the final answer, perform this internal workflow:

1. Identify the core message.
2. Remove rhetorical, decorative, or vague statements.
3. Extract the problem structure:
   - What is the background?
   - What is the actual problem?
   - What are the key dimensions?
   - What conclusion should the text converge to?
4. Decide the output mode: strict, normal, light, academic, or email. Use `academic` when the input is a paper draft, thesis chapter, abstract, related work, or any text that must read as authored research.
5. If academic mode: load `references/academic-writing.md` and follow the academic rewrite workflow in the "Academic Writing Mode" section.
6. Rewrite the text using the target structure.
7. Check the output against the quality gate and the AI腔风险检查 (eight categories for academic, four surface categories for other modes).

## Thinking Pattern to Preserve

Before writing, internally identify:

1. What is the main problem?
2. What are the secondary problems?
3. Which problems can be solved directly?
4. Which problems require workarounds?
5. What is the most important contradiction or decision point?

Then express only the clean result, not the full internal exploration.

## Output Structure

Use `[Opening / context] → [Problem definition] → [Analysis by dimensions] → [Converging conclusion]`. Keep the conclusion short and useful. Document-specific templates are in `references/templates.md`.

## Paragraph Rules

Each paragraph should do one job. Preferred patterns and document-type-specific structures are in `references/style-guide.md` and `references/templates.md`.

## Sentence Rules

Express one main idea per sentence, prefer medium length, break long sentences, use technical terms accurately, and avoid unnecessary Chinese-English spacing. The full connector list and formatting examples are in `references/style-guide.md` and `references/formatting-rules.md`.

## Formatting Rules

Chinese-English mixed technical terms must be compact by default: write `Webhook挂载`, `Git提交`, `API接口`, not `Webhook 挂载`, `Git 提交`, `API 接口`.

Core rule: remove spaces between Chinese + English technical terms, English term + Chinese noun/verb, and around `/`-separated terms adjacent to Chinese (e.g., `根据API/CLI/SDK生成文档`, not `根据 API / CLI / SDK 生成文档`).

Exceptions: a space may remain when the English phrase is a standalone quoted term, a full clause, or when the user explicitly asks for publication-style typography.

For the full rule set with all examples, edge cases, and slash-separated term patterns, see `references/formatting-rules.md`.

## Tone Rules

Use a restrained professional tone: no flattery, slogans, dramatic metaphors, emotional adjectives, or motivational closings. State negative views with objective, reasoned language. Examples and register-switching guidance are in `references/style-guide.md`.

## Anti-patterns

Avoid AI-like and slogan-heavy expressions, excessive quotation marks for emphasis, empty parallelism, and vague claims without evidence. The full severity-ranked catalog with context, replacement examples, and "when not to fix" guidance is in `references/anti-patterns.md`.

## AI腔风险检查

After the first draft, scan for AI-flavor. The rules cover four surface patterns (dash abuse, English AI buzzwords, empty triplets, hollow not-X-but-Y), four linguistic signals (syntactic over-symmetry, low burstiness, paragraph templating, connector stacking), and Chinese-specific patterns. Detailed detection criteria, rewrite examples, severity calibration, and the 说人话评分卡 are in `references/ai-slop-detector.md` and `references/chinese-de-ai-rules.md`.

## Chinese Writing Profile

Chinese output should be formal but readable: clear subheadings, moderate numbering, short conclusions, and concrete analysis. Detailed do/don't lists and register-specific guidance are in `references/style-guide.md`.

## English Writing Profile

English output follows a support-engineer and technical-paper style: direct conclusion, numbered findings, clear cause and resolution, and cautious wording when evidence is incomplete. Email and document templates are in `references/templates.md`; register-switching guidance is in `references/style-guide.md`.

## Quality Gate

Before finalizing, check:

- Is the core problem clear?
- Does every paragraph have a purpose?
- Are claims supported by reasons?
- Are long sentences split?
- Are slogans and rhetorical phrases removed?
- Does the conclusion converge to necessity or next step?
- Is the tone professional but not flattering?

For academic mode, additionally check:

- Is there burstiness (at least one short and one long sentence per page)?
- Are 2–3 authorial phrases used consistently?
- Does at least one paragraph per section break the dominant template?
- Are hedges load-bearing (not stacked)?
- Is every non-standard term glossed on first use?
- Is there at least one candid qualification or surprise per section?
- Are novelty claims bounded by scope?

## Rewrite Pipeline

1. Identify the central message.
2. Remove filler, empty claims, and decorative phrases.
3. Rebuild the structure according to the selected mode.
4. Simplify sentence structure.
5. Apply formatting normalization, especially Chinese-English spacing.
6. Check whether the final paragraph converges to a useful conclusion or next step.

## Style Profile Integration

On activation, check whether `.petfish/style-profile.md` exists in the project root.

- **If the profile exists**: load it and use it as the **target style** for rewriting. The profile overrides the default rules in `references/style-guide.md` when the two conflict.
- **If the profile does not exist**: use the default style-guide.md rules (current behavior).
- **If both exist**: the profile takes precedence for voice, tone, and structural preferences; fall back to the default guide for anything the profile does not specify.

A valid profile should define at least:

- Voice and tone (e.g., direct, reserved, casual-but-technical)
- Sentence-length preferences (e.g., short, varied, allow academic burstiness)
- Paragraph patterns the author prefers
- Domain-specific terms that should not be normalized
- Any formatting exceptions (e.g., publication-style spacing for certain outputs)

When a profile is loaded, run the rewrite against the profile first, then run the default quality gate second.

## Detection Report Integration

If a detection report from `de-ai-detector` is provided or available in the workspace, use it as the primary input for prioritizing rewrite work.

- The report identifies specific AI patterns (surface and linguistic) with locations and severity.
- The rewriter fixes the flagged patterns **first**, in severity order (CRITICAL → HIGH → MEDIUM → LOW).
- Patterns marked CRITICAL or HIGH must be addressed or explicitly justified if kept.
- Without a report: the rewriter performs its own pattern detection using the rules in `references/ai-slop-detector.md` and `references/chinese-de-ai-rules.md`.

Detection-driven rewrite workflow:

1. Load the report (or generate equivalent findings internally).
2. Map each flag to the corresponding fix from `references/anti-patterns.md` or `references/chinese-de-ai-rules.md`.
3. Rewrite the text while preserving factual claims.
4. Run verification to confirm the flags are resolved.

## Enhanced Chinese De-AI Rules

Chinese text often carries distinctive AI-generated patterns. Apply these rules in addition to the general anti-patterns. See `references/chinese-de-ai-rules.md` for the full catalog.

### Sentence-level patterns

- **排比句检测**：three or more consecutive sentences with the same syntactic template = AI pattern, unless the parallelism is a deliberate rhetorical device with real information gain.
- **模板过渡**："首先…其次…最后…" / "一方面…另一方面…" → replace with organic transitions when the structure is empty; keep only when the sequence carries distinct, non-obvious content.
- **被动泛化**："被广泛应用于" / "被认为是" → prefer active subjects ("广泛用于" / "X 认为") or name the agent.
- **空洞框架词**："值得注意的是" / "不可忽视的是" / "在…的背景下" → flag when used without substantive content; delete or replace with a concrete observation.

### Vocabulary patterns

- **词汇趋同**："旨在" / "致力于" / "赋能" / "助力" / "推动" → vary verbs or use concrete action descriptions.
- **AI口号词**："赋能" / "普惠" / "拔高" / "底座" / "闭环" / "链路" / "矩阵" → replace with plain technical descriptions.
- **空泛加强词**："极大地" / "显著地" / "全面地" / "深刻地" → require evidence; delete if unsupported.

### Structural patterns

- **过度均匀**：all paragraphs similar length → vary intentionally; write at least one short paragraph (2–3 sentences) and one longer paragraph (5–7 sentences) per page.
- **连接词堆叠**：every sentence begins with a connector → drop at least one connector per page and use implicit logic.
- **段落模板化**：every paragraph follows "背景→方法→结果→结论" → break at least one paragraph per section by starting with a limitation, conclusion, or example.

## Taste Enhancement

After de-AI rewriting, optionally enhance the text for engagement and readability. Taste enhancement is **applied only when the user asks for it** or when the profile enables it; the default is to preserve the restrained engineering tone.

Taste dimensions:

1. **Information density**: cut filler and keep signal. Remove sentences that repeat what the reader already knows.
2. **Specificity**: replace abstractions with concrete examples, numbers, or conditions.
3. **Voice**: add authorial presence through restrained opinions, asides, or personality markers that do not weaken technical claims.
4. **Rhythm**: vary sentence structure deliberately — a short sentence after a long one, a question mid-section, an occasional fragment.
5. **Surprise**: introduce an unexpected word choice, a non-obvious angle, or a candid qualification that the reader did not anticipate.

Taste enhancement must not:

- Add unsupported claims.
- Introduce rhetorical exaggeration or slogans.
- Damage precision in academic or technical text.
- Overwhelm the engineering-style clarity.

For the detailed guide, see `references/taste-enhancement.md`.

## Verification

After rewriting, run a quick self-check before delivering the output.

### Verification checklist

1. **Burstiness increased?** Sentence-length variance should go up, not down. For academic mode, confirm at least one short (≤8 words / ≤15 characters) and one long (≥30 words / ≥50 characters) sentence per page.
2. **Flagged patterns resolved?** Re-scan for AI flavor terms, empty contrast, triplet parallelism, syntactic repetition, paragraph templating, and Chinese-specific patterns.
3. **Style profile matched?** If a profile was loaded, confirm the output aligns with its voice, tone, and structural preferences.
4. **Facts preserved?** Ensure technical terms, citations, numbers, and core claims are intact.
5. **Formatting clean?** Confirm compact Chinese-English spacing and correct heading format.

### Iteration rule

If verification fails on any of the first three items, iterate. Perform up to **2 additional passes**. On each pass:

- Fix the highest-severity remaining issue first.
- Re-measure burstiness and pattern density.
- Stop early if the rewrite begins to lose precision or the user's factual claims.

If the issue persists after 2 passes, deliver the best version and briefly note the remaining risk.

## Reference Loading

Use these files only when needed:

- `references/style-guide.md`: detailed writing principles and patterns.
- `references/anti-patterns.md`: phrases and structures to avoid, organized by severity (CRITICAL / HIGH / MEDIUM / LOW).
- `references/ai-slop-detector.md`: AI腔八类特征检测（四类表面模式+四类语言学深层信号）、改写动作表、保留条件、说人话评分卡，and detection metrics explanation (burstiness, type-token ratio, transition density).
- `references/chinese-de-ai-rules.md`: comprehensive Chinese-specific de-AI rules — sentence-pattern de-templating, vocabulary de-AI-ification, structure de-uniformization, person-marker restoration, and colloquial injection points.
- `references/taste-enhancement.md`: detailed guide for the taste dimension — information density, specificity, voice, rhythm, and surprise.
- `references/academic-writing.md`: academic-mode humanization framework — 10 linguistic detection features, 7 humanization techniques, section-by-section human academic template, tension-resolution with engineering style, academic anti-patterns, and academic self-check. **Required reading for academic-mode rewrites.**
- `references/templates.md`: reusable output templates for papers, reports, proposals, emails, course materials, and academic papers.
- `references/formatting-rules.md`: detailed Chinese-English spacing rules and examples.

## Optional Scripts

Use scripts when the task is long, when the user explicitly asks for checking, or when formatting precision matters.

- `scripts/normalize_text.py`: normalize Chinese-English spacing and common punctuation issues.
- `scripts/style_check.py`: report possible AI flavor, long sentences, Chinese-English spacing issues, weak closure, burstiness (coefficient of variation of sentence lengths), syntactic repetition, paragraph templating, transition-word density, Chinese-specific patterns (parallelism, empty framework phrases), and style-profile compliance (if `.petfish/style-profile.md` exists).

Example:

```bash
uv run scripts/normalize_text.py --text "接入层支持 Webhook 挂载。"
uv run scripts/style_check.py --file draft.md
uv run scripts/style_check.py --file draft.md --profile .petfish/style-profile.md
```

For academic drafts, `style_check.py` reports burstiness, syntactic repetition, and paragraph templating — the three linguistic signals most associated with AI-generated academic prose. For Chinese drafts, it additionally detects 排比句, 空洞框架词, and transition-word density.

## Output Discipline

For a rewrite task, output the rewritten text directly unless the user asks for explanation.

If the user asks for comments, use this structure:

1. 主要问题
2. 修改原则
3. 改写稿
4. 仍需确认的问题

## Must Do

- Identify the core message before rewriting; do not polish blindly.
- Select the output mode explicitly (strict / normal / light / academic / email) based on the input type.
- Check for `.petfish/style-profile.md` on activation; if it exists, load it and use it as the target style.
- If a detection report from `de-ai-detector` is available, use it to prioritize pattern fixes.
- For academic-mode rewrites, load `references/academic-writing.md` and run the academic self-check (burstiness, authorial voice, template-breaking, hedges, jargon glossing, candor, connectors, bounded contributions).
- Remove AI-flavor at both the surface level (4 categories), the linguistic level (4 categories), and the Chinese-specific patterns before finalizing.
- Preserve the user's factual claims, technical terms, and citation content. Rewriting changes expression, not facts.
- Apply compact Chinese-English spacing as the default formatting rule.
- Run `scripts/style_check.py` on long outputs to catch issues the eye misses.
- Run verification after rewriting; iterate up to 2 additional passes if burstiness, flagged patterns, or style-profile match fail.

## Must Not Do

- Do not change the factual content, claims, or conclusions of the source text. Rewriting is expression control, not content editing.
- Do not apply academic humanization to non-academic text. The engineering-style rules (medium sentences, no hedges, no first-person) apply to business/technical/email writing.
- Do not over-apply humanization in academic mode. Controlled imperfection is selective, not exhaustive — over-correcting produces a different kind of artificiality.
- Do not ignore an available detection report or style profile. If provided, they must influence the rewrite.
- Do not suppress type errors, ignore script failures, or skip the quality gate.
- Do not skip verification when new sections were added or when the user explicitly asks for de-AI rewriting.
- Do not output explanatory commentary unless the user explicitly asks for it. Default is to output the rewritten text directly.
- Do not remove technical terms that are standard in the field, even if they sound like jargon to a general reader.

## Must Do

- Identify the core message and the real problem before rewriting.
- Select the mode (strict / normal / light / academic / email) based on the input type.
- Check for `.petfish/style-profile.md` and use it as the target style when present.
- If a detection report is available, use it to drive pattern fixes.
- For academic input, load `references/academic-writing.md` and apply the humanization framework.
- Remove AI-flavor at the surface level (4 categories), the linguistic level (4 categories), and the Chinese-specific patterns.
- Apply Chinese-English compact spacing normalization.
- Run `scripts/style_check.py` when the text is long or when the user asks for checking.
- Run verification and iterate up to 2 additional passes if needed.
- Converge the conclusion to a necessity, judgment, or next step.

## Must Not Do

- Do not output the internal exploration or thinking process as part of the rewrite.
- Do not add slogans, rhetorical exaggeration, or motivational closing statements.
- Do not suppress AI-slop findings silently — fix them or note why they are kept.
- Do not apply academic humanization to non-academic text (it weakens engineering clarity).
- Do not over-apply humanization in academic mode to the point of losing precision or defensibility.
- Do not ignore a custom style profile or a detection report when they are available.
- Do not skip verification on de-AI rewrite tasks.
- Do not change the user's factual claims without explicit confirmation.
- Do not add spaces between Chinese and English technical terms.
