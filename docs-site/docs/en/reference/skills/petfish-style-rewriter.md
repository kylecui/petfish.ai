# petfish-style-rewriter

> Pack: **petfish**

Rewrite, polish, humanize, de-AI, or formalize Chinese or English technical, academic, business, course, proposal, patent, and email content into Petfish's structured, evidence-based, engineering-oriented style. Supports custom style profiles, de-ai-detector reports, enhanced Chinese de-AI rules, and optional taste enhancement. Triggers: 用我的语言习惯表达, 说人话, 润色, 去AI味, 按我的风格写, 改得更像人写的, 论文润色, 学术写作, abstract rewrite, rewrite my paper.

**Compatibility:** opencode

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

*... (276 more lines in full SKILL.md)*
