# Petfish Style Rewriter Skill V3

This package provides an opencode-compatible writing skill for rewriting Chinese or English text into Petfish's preferred style.

## Goal

The skill is not a generic polishing tool. It is designed to convert AI-like, rhetorical, verbose, or loosely structured text into a clear, professional, problem-driven writing style.

## Core Features

- Petfish-style structural rewrite
- Strict/normal/light/academic/email modes
- Structure-first analysis workflow
- Anti-pattern rules for AI-like writing
- Chinese and English writing profiles
- Chinese-English spacing normalization
- Quality checker script with scoring
- Text normalization script
- Eval prompts and expected criteria

## V3 Changelog

- Added `academic` and `email` modes
- Added "Thinking Pattern to Preserve" section
- Added "Formatting Rules" section with Chinese-English compact spacing rules
- Added "Rewrite Pipeline" section
- Added "Output Discipline" section
- Added `normalize_text.py` for automated spacing normalization
- Upgraded `style_check.py` with scoring architecture, JSON output, and broader pattern lists
- Added `references/formatting-rules.md`
- Added skill-level `README.md`
- Added zh-en spacing eval

## Installation

Copy this package into the root of an opencode project:

```bash
cp -r .opencode /path/to/your/project/
cp AGENTS.md /path/to/your/project/
```

Or copy only the skill directory:

```bash
cp -r .opencode/skills/petfish-style-rewriter /path/to/your/project/.opencode/skills/
```

## Usage Examples

```text
用我的语言习惯表达下面这段内容：
...
```

```text
请把这段话说人话，但保持正式和专业：
...
```

```text
Rewrite this email in my technical support writing style:
...
```

## Modes

- `strict`: strongest Petfish-style fitting; default for formal writing.
- `normal`: preserves some original wording while improving structure.
- `light`: minimal polishing; preserves most original structure.
- `academic`: formal paper/report style with explicit sections and restrained claims.
- `email`: support-engineer style; clear status, findings, evidence, action, and polite closure.

## Quality Check

```bash
uv run .opencode/skills/petfish-style-rewriter/scripts/normalize_text.py --file draft.md --output draft.normalized.md
uv run .opencode/skills/petfish-style-rewriter/scripts/style_check.py --file draft.normalized.md
```

The checker produces a score out of 100 and lists specific issues. It helps identify likely problems such as long sentences, rhetorical phrases, buzzwords, weak structure, and Chinese-English spacing issues.
