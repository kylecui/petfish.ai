# Markdown Layout Rules

## Headings

- Use one H1 per document unless the baseline clearly differs.
- Preserve the baseline numbering convention.
- Keep one blank line before and after headings.
- Avoid skipping heading levels, such as H2 to H4.

## Lists

- Use `-` for unordered lists unless the baseline uses another marker consistently.
- Use ordered lists when the sequence matters.
- Keep list item grammar parallel when possible.

## Tables

- Use GitHub-flavored Markdown tables.
- Keep captions consistent with the baseline, usually before or after the table but not mixed.
- Align table columns only when this improves readability; do not over-format.

## Code blocks

- Use fenced code blocks.
- Add language identifiers when known: `bash`, `json`, `yaml`, `python`, `markdown`, `text`.
- Do not rewrite code for style unless the user asks.

## Chinese-English typography

Default convention for this skill:

- No space between Chinese and English technical terms: `AI安全`, `Webhook挂载`, `Git提交`.
- Preserve spaces inside English phrases: `Control Plane`, `Data Plane`.
- Prefer Chinese full-width punctuation in Chinese sentences.
- Use half-width punctuation inside code, config, URLs, and English fragments.

If the baseline strongly and consistently uses another convention, follow the baseline and report the decision.
