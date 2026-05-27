# PPT Reader Extraction Schema

`pptx_extract.py`输出JSON的顶层结构如下：

```json
{
  "file": "input.pptx",
  "slide_count": 12,
  "metadata": {
    "title": "...",
    "subject": "...",
    "creator": "...",
    "last_modified_by": "..."
  },
  "external_relationships": [],
  "slides": [
    {
      "index": 1,
      "slide_file": "ppt/slides/slide1.xml",
      "title": "...",
      "paragraphs": ["..."],
      "notes": ["..."],
      "media": [
        {"relationship_id": "rId2", "target": "ppt/media/image1.png"}
      ],
      "alt_text": ["..."],
      "comments": [],
      "issues": []
    }
  ],
  "issues": []
}
```

## 字段说明

- `paragraphs`：按页面XML中的段落顺序合并文本；适合做大纲分析。
- `notes`：演讲者备注。必须与正文分开处理。
- `media`：图片、视频、音频或其它嵌入资源关系。
- `alt_text`：图形或图片的名称/描述字段，有时包含关键信息。
- `external_relationships`：外部链接或外部资源引用，审阅时需提示。
- `issues`：脚本能机械发现的问题，例如空页、缺标题、占位符、外部关系。

## 推荐使用方式

1. 先看`slide_count`和`issues`判断文件基本健康度。
2. 逐页读取`title`、`paragraphs`、`notes`。
3. 如果`media`很多但`paragraphs`少，必须做视觉渲染，不要只依据文本判断。
4. 如果`external_relationships`非空，在安全审阅或交付前提示用户确认。
