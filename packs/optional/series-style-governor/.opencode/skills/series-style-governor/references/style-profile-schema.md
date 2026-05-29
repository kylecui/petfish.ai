# Style Profile Schema

The style profile is a machine-readable contract extracted from a baseline Markdown file.

Recommended path:

```text
.series-style/style-profile.json
```

## Required top-level fields

```json
{
  "profile_version": "0.1.0",
  "baseline": {
    "path": "chapters/01-intro.md",
    "mode": "fixed",
    "created_at": "YYYY-MM-DD"
  },
  "language_profile": {},
  "structure_profile": {},
  "terminology_profile": {},
  "markdown_layout_profile": {},
  "rewrite_policy": {}
}
```

## language_profile

```json
{
  "primary_language": "zh-CN",
  "secondary_language": "en",
  "tone": ["technical", "analytical", "consulting"],
  "cjk_english_spacing": "no-space",
  "punctuation": "zh-full-width-for-chinese",
  "preferred_sentence_density": "medium"
}
```

`cjk_english_spacing` values:

- `no-space`: `AI安全`, `Webhook挂载`, `Git提交`
- `space`: `AI 安全`, `Webhook 挂载`, `Git 提交`
- `baseline-mixed`: report inconsistencies before normalizing

## structure_profile

```json
{
  "heading_numbering": "arabic-dot",
  "max_heading_depth": 3,
  "intro_required": true,
  "summary_section_pattern": ["本章小结", "小结", "总结"],
  "common_section_sequence": ["背景", "问题", "分析", "方案", "小结"],
  "figure_caption_pattern": "图 N. 标题",
  "table_caption_pattern": "表 N. 标题"
}
```

## terminology_profile

```json
{
  "preferred_terms": {
    "控制平面": {
      "aliases": ["控制层", "Control Plane"],
      "rule": "架构语境中统一使用控制平面。"
    }
  },
  "forbidden_terms": {
    "赋能": "容易空泛，除非上下文明确说明机制。"
  },
  "abbreviation_rules": {
    "first_use": "中文全称（English Full Name, ACRONYM）",
    "later_use": "ACRONYM或中文简称，按基准决定"
  }
}
```

## markdown_layout_profile

```json
{
  "blank_line_after_heading": true,
  "blank_line_before_heading": true,
  "list_marker": "-",
  "ordered_list_marker": "1.",
  "code_fence_style": "triple-backtick-with-language-when-known",
  "table_alignment": "github-flavored-markdown",
  "image_syntax": "markdown-image"
}
```

## rewrite_policy

```json
{
  "default_mode": "conservative",
  "preserve_citations": true,
  "preserve_claims": true,
  "preserve_examples": true,
  "auto_fix_allowed": [
    "heading-numbering",
    "term-alias-unambiguous",
    "cjk-english-spacing",
    "blank-lines",
    "list-marker"
  ],
  "review_required": [
    "paragraph-move",
    "definition-rewrite",
    "claim-emphasis-change"
  ]
}
```
