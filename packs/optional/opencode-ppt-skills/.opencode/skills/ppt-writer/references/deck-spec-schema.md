# Deck Spec Schema

`build_deck.py`接收一个JSON文件作为输入。推荐结构如下：

```json
{
  "meta": {
    "title": "Deck Title",
    "subtitle": "Optional subtitle",
    "author": "Optional author"
  },
  "theme": {
    "primary": "1E2761",
    "secondary": "CADCFC",
    "accent": "F96167",
    "background": "FFFFFF",
    "text": "1F2937",
    "font_face": "Microsoft YaHei"
  },
  "slides": [
    {
      "type": "title",
      "title": "Deck Title",
      "subtitle": "Subtitle"
    },
    {
      "type": "section",
      "title": "第一部分",
      "subtitle": "章节说明"
    },
    {
      "type": "bullets",
      "title": "页面标题",
      "body": "一句话导语",
      "items": ["要点一", "要点二", "要点三"]
    },
    {
      "type": "two-column",
      "title": "双栏页面",
      "left_title": "左侧",
      "left_items": ["A", "B"],
      "right_title": "右侧",
      "right_items": ["C", "D"]
    },
    {
      "type": "comparison",
      "title": "对比页面",
      "columns": [
        {"title": "方案A", "items": ["优点", "不足"]},
        {"title": "方案B", "items": ["优点", "不足"]}
      ]
    },
    {
      "type": "process",
      "title": "流程页面",
      "steps": [
        {"title": "Step 1", "body": "说明"},
        {"title": "Step 2", "body": "说明"}
      ]
    },
    {
      "type": "quote",
      "title": "关键判断",
      "quote": "一句重要判断",
      "attribution": "来源或说明"
    }
  ]
}
```

## 支持的页面类型

- `title`：封面。
- `section`：章节页。
- `bullets`：标题 + 导语 + 要点。
- `two-column`：左右并列，用于问题/方案、现状/目标等。
- `comparison`：2-3列对比。
- `process`：横向步骤或方法论。
- `quote`：关键判断或结论页。

## 推荐做法

- 先用Markdown表格规划页序，再转成JSON。
- 每页`items`控制在3-5条。
- 标题尽量是判断句。
- 长段落放到讲稿或备注，不要塞进页面。
- 中文和英文术语之间不加无意义空格，例如“AI安全”“Webhook挂载”“Git提交”。
