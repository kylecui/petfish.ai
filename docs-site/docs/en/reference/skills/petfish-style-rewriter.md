# petfish-style-rewriter

> Pack: **petfish**

Rewrite, polish, humanize, simplify, de-AI, formalize, or express content in Petfish's writing style. It rewrites Chinese or English technical, academic, business, course, proposal, patent, and email content into a clear, structured, concise, evidence-based, engineering-oriented style. Trigger especially for phrases such as "用我的语言习惯表达", "说人话", "润色", "去AI味", "按我的风格写", or "make it sound human but still professional".

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
- rewrite in my style
- make this clearer
- make this more professional but less AI-like

Also use this skill for technical papers, course materials, proposals, emails, patent drafts, project documents, and strategy documents when the main task is rewriting or expression control.

## Default Mode

Use `strict` by default unless the user explicitly asks for light polishing.

Modes:

- `strict`: rebuild the structure and expression. Best for AI-like or verbose text.
- `normal`: improve structure and wording while preserving some original phrasing.
- `light`: minimal polishing. Preserve the original structure unless it is clearly broken.
- `academic`: formal paper/report style with explicit sections and restrained claims.
- `email`: support-engineer style; clear status, findings, evidence, action, and polite closure.

## Core Style Model

Petfish's writing style follows this pattern:

1. State the background or context only as much as needed.
2. Identify the real problem.
3. Decompose the problem into 2–4 concrete dimensions.
4. Explain each dimension with condition, limitation, and implication.
5. Converge to a necessity, judgment, or next step.

This is a problem-modeling style, not a slogan-writing style.

## Rewrite Workflow

Before writing the final answer, perform this internal workflow:

1. Identify the core message.
2. Remove rhetorical, decorative, or vague statements.
3. Extract the problem structure:
   - What is the background?
   - What is the actual problem?
   - What are the key dimensions?
   - What conclusion should the text converge to?
4. Decide the output mode: strict, normal, or light.
5. Rewrite the text using the target structure.
6. Check the output against the quality gate.

## Thinking Pattern to Preserve

Before writing, internally identify:

1. What is the main problem?
2. What are the secondary problems?
3. Which problems can be solved directly?
4. Which problems require workarounds?
5. What is the most important contradiction or decision point?

Then express only the clean result, not the full internal exploration.

## Output Structure


*... (286 more lines in full SKILL.md)*
