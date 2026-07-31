# AI应用系统架构师教材 — 排版参数规范

> 本文件是教材PDF排版系统的唯一权威参数表。所有排版修改必须先更新本文件，再同步到代码。
> 实现位置：`05-visual-assets/handbook-layout/book-template.typ` + `build_pdf.py`

---

## 1. 构建 Pipeline

```
build_pdf.py
  │
  ├─ Step 1: Markdown → Typst (pandoc)
  │   ├─ preprocess_md(): 紧凑排版 + 符号替换
  │   └─ pandoc -f markdown -t typst --wrap=none
  │
  ├─ Step 2: fix_typst_paths() 后处理（9个子步骤，见§10）
  │
  ├─ Step 3: 生成 book.typ（标题页+目录+#include各章）
  │
  └─ Step 4: typst compile --root <project> → PDF
```

**构建命令**：
```powershell
$env:Path = "C:\Users\崔崟\AppData\Local\Pandoc;" + $env:Path
cd 05-visual-assets\handbook-layout
python build_pdf.py              # 全量
python build_pdf.py --ch 0       # 仅Ch00（pilot）
python build_pdf.py --ch 0,1,2   # 指定章节
```

---

## 2. 页面设置

| 参数 | 值 | 实现位置 |
|------|-----|----------|
| 纸张 | A4 | `book-template.typ` |
| 上下左右页边距 | 3.0cm | 同上 |
| 页眉 | "AI应用系统架构师 · 驾驭工程"，10.5pt TNR+SimSun，居中，第2页起显示 | 同上 |
| 页脚 | 页码，10.5pt TNR+SimSun，居中 | 同上 |
| 语言 | zh / cn | 同上 |

---

## 3. 字体对照表

| 元素 | 中文字体 | 西文字体 | 字号 | 其他 |
|------|----------|----------|------|------|
| 正文 | 宋体 SimSun | Times New Roman | 12pt（小四） | 基准 |
| H1 章标题 | 黑体 SimHei | Arial | 16pt | 加粗，居中 |
| H2 | 黑体 | Arial | 14pt | 加粗 |
| H3 | 黑体 | Arial | 13pt | 加粗 |
| H4 | 黑体 | Arial | 12pt | 加粗 |
| 图注+说明 | 仿宋 FangSong | Times New Roman | 9pt（小五） | 居中 |
| 表注编号说明 | 仿宋 | Times New Roman | 9pt（小五） | 居中 |
| 表格内容 | 仿宋 | Times New Roman | 10.5pt（五号） | — |
| 代码块 | — | Consolas | 10pt | 灰底 |
| 行内代码 | — | Consolas | 11pt | — |
| 页眉/页脚 | SimSun | Times New Roman | 10.5pt | 居中 |
| 标题页书名 | SimHei | Times New Roman | 24pt | 加粗，居中 |
| 标题页副标题 | 楷体 KaiTi | Times New Roman | 14pt | 居中 |

---

## 4. 间距对照表

| 元素 | 行距 leading | 段距 spacing | 其他间距 |
|------|-------------|-------------|----------|
| 正文 | 20pt | 24pt | 首行缩进 2em |
| 标题 | 20pt | 各级段前/段后（见§5） | 0em 缩进 |
| 图注+说明 | 20pt | — | 图上 6pt；图→图注 2pt；图注块下 2pt |
| 表格内容 | 16pt | 0pt | — |
| 代码块 | 14pt | — | 段后 6pt |
| 引用块 | 20pt | — | 左缩进 1.5em |
| 数学公式 | — | — | 段前 6pt，段后 6pt，居中 |
| 分隔线 | — | — | 上下各 0.5em，30%宽度 0.5pt 灰线居中 |

---

## 5. 标题样式

| 层级 | 字号 | 字体 | 对齐 | 段前 | 段后 | 备注 |
|------|------|------|------|------|------|------|
| H1 | 16pt | Arial+SimHei bold | 居中 | 24pt | 18pt | 另起一页（weak pagebreak） |
| H2 | 14pt | Arial+SimHei bold | 左对齐 | 24pt | 6pt | — |
| H3 | 13pt | Arial+SimHei bold | 左对齐 | 12pt | 6pt | — |
| H4 | 12pt | Arial+SimHei bold | 左对齐 | 12pt | 6pt | — |

所有标题：`first-line-indent: 0em`，`leading: 20pt`。

---

## 6. 图片（图示 + 图注 + 说明）

### 6.1 Markdown源文件格式

```markdown
![图标题文字](diagrams/m0/fig0_1_8layer_overview.png)

图说明文字段落。这行会自动合并进图注caption块。
```

- 第一行：图片 + alt文本。alt文本成为Typst自动编号的图注内容。
- 第二行：描述段落。pandoc转换后是独立段落，build_pdf.py会将其合并进caption块。
- **不要手动添加** `**图X.X标题**` 行——图的编号由Typst自动生成，格式为**逐章编号** `图X.Y.`（如图0.1、图1.2），X=章号，Y=章内序号。

### 6.2 Typst渲染参数

```typst
// 步骤1: 覆盖默认caption格式，去掉Typst的"图 N —"前缀
show figure.caption: it => it.body

// 步骤2: 自定义图片figure渲染，手动构建"图X.Y. body"格式
show figure.where(kind: image): it => {
    set par(first-line-indent: 0em, leading: 20pt)
    v(6pt)                          // 图片上方间距
    align(center)[#it.body]         // 图片居中
    if it.caption != none {
      v(2pt)                        // 图注与图片间距
      set text(size: 9pt, font: ("Times New Roman", "FangSong"))
      context {
        let ch = counter("chapter").get().first() - 1
        let fig = counter(figure.where(kind: image)).get().at(0)
        align(center)[图#ch.#fig. #it.caption]  // 逐章编号 图X.Y.
      }
    }
    v(2pt)                          // 图注块下方间距
}
```

- **图注字体**：仿宋 + Times New Roman，小五号(9pt)
- **行距**：20pt（与正文行距一致）
- **位置**：居中
- **编号**：Typst自动生成，**逐章编号** `图X.Y.`（X=章号，Y=章内序号），由 `counter("chapter")` + `counter(figure.where(kind: image))` 组合实现
- **图计数器重置**：在H1 show rule中 `counter(figure.where(kind: image)).update(0)` 实现每章从1开始
- **caption覆盖**：`show figure.caption: it => it.body` 去掉Typst默认的"图 N —"前缀
- **图说明合并**：由build_pdf.py步骤6自动处理

### 6.3 build_pdf.py后处理（步骤6）

检测 `#figure(...)` 块后的第一个 `#h(2em)` 段落（即描述文字），将其合并进 figure 的 `caption: [...]` 块内部。

转换前：
```typst
#figure(image("path", alt: "图标题"),
  caption: [
    图标题
  ]
)

#h(2em) 图说明文字...
```

转换后：
```typst
#figure(image("path", alt: "图标题"),
  caption: [
    图标题
    图说明文字...
  ]
)

```

---

## 7. 表格

### 7.1 Markdown源文件格式

```markdown
| 列1 | 列2 |
|-----|-----|
| 数据 | 数据 |

**表1  表标题文字**
```

- 表格本身在上方
- 表注 `**表N  标题**` 在表格**下方**
- 表注编号格式为 `表X.Y.`（X=章号，Y=章内序号），由 build_pdf.py 步骤7自动转换
- 表注文字由 `add_table_captions.py` 脚本从表头关键词生成

### 7.2 Typst渲染参数

**表格内容**：
```typst
// 宽表格（6列+）自动缩小字体，防止溢出页面
show table: it => {
    let n = if it.columns == auto { 2 } else { it.columns.len() }
    let sz = if n > 5 { 8pt } else { 10.5pt }
    let ld = if n > 5 { 12pt } else { 16pt }
    set text(font: ("Times New Roman", "FangSong"), size: sz)
    set par(leading: ld, first-line-indent: 0em, spacing: 0pt)
    it
}
```

**表格跨页分页**（允许长表格自动分页）：
```typst
// table figure 默认不可分页，这里去掉 figure 的不可分页包裹
show figure.where(kind: table): it => {
    set par(first-line-indent: 0em)
    it.body
}
```

**表注重样式**（由 build_pdf.py 步骤7处理）：
```typst
// build_pdf.py 将 pandoc 的 #strong[表N  标题] 替换为：
#align(center)[#text(size: 9pt, font: ("Times New Roman", "FangSong"))[表N  标题]]
```

- **表注字体**：仿宋 + Times New Roman，小五号(9pt)
- **位置**：居中
- **编号**：`表X.Y.` 格式（X=章号，Y=章内序号），由 build_pdf.py 步骤7自动转换

### 7.3 Markdown预处理

表格行中的 `<` → `＜`，`>` → `＞`（全角尖括号，避免Typst标签解析）。

---

## 8. 代码块

| 参数 | 值 |
|------|-----|
| 字体 | Consolas, 10pt |
| 行距 | 14pt |
| 背景 | luma(245) 浅灰 |
| 内边距 | x: 12pt, y: 8pt |
| 宽度 | 100% |
| 边框 | 0.5pt + luma(180) |
| 段后 | 6pt |

行内代码：Consolas, 11pt。

### Markdown预处理

代码块内：`<=` → `≤`，`>=` → `≥`，单独 `<` → `＜`，`>` → `＞`（全角尖括号，避免pandoc误解析为HTML标签导致行截断）。

---

## 9. 其他元素

### 引用块 (quote)
```typst
block(width: 100%, inset: (left: 1.5em, right: 0em))[
    par(first-line-indent: 0em, leading: 20pt)
]
```

### 列表 (list / enum)
`first-line-indent: 0em`（不缩进）。

### 数学公式 (block equation)
`v(6pt)` → `align(center)` → `v(6pt)`。

### 分隔线 (horizontal rule)
pandoc `#horizontalrule` → Typst：`v(0.5em)` + 居中30%宽度0.5pt灰色线 + `v(0.5em)`。

### 标题页
24pt SimHei 书名 + 14pt KaiTi 副标题 + 12pt SimSun "教材版"。

### 目录页
16pt SimHei "目录" + `#outline(indent: 2em, depth: 2)`。

---

## 10. build_pdf.py 后处理步骤

pandoc转换后，`fix_typst_paths()`按顺序执行9个步骤：

| 步骤 | 处理 | 说明 |
|------|------|------|
| 0 | 图片路径重写 | `diagrams/mN/` → `../../05-visual-assets/diagrams-export/MN/` |
| 0.5 | 表格列宽自适应 | `columns: N` → `columns: (auto, 1fr, ...)`，首列自适应内容宽度 |
| 1 | `#horizontalrule` → Typst等效语法 | 分隔线 |
| 2 | 去除 `<[^>]+>` HTML残留 | span标签清理 |
| 3 | 代码块fence不平衡修复 | 补全缺失的 `\`\`\`` |
| 4 | 首行缩进插入 | 标题/块结构后的文本段落前插入 `#h(2em)`，跳过列表项 `[-*+]\s` 和 `\d+[.)]\s` |
| 5 | 图片路径检查 | 缺失图片替换为灰底占位符 |
| 6 | 图说明合并进caption | `#figure(...)` 后的描述段落合并进 `caption: [...]`，用 `#linebreak()` 分隔标题和说明 |
| 7 | 表注重样式 | `#strong[表N  标题]` → `#align(center)[#text(9pt, FangSong)[表X.Y. 标题]]`（逐章编号） |

### 步骤4详情：首行缩进插入

Typst的 `first-line-indent` 在标题/表格/图片后不生效，因此由后处理统一插入 `#h(2em)`。

**插入条件**：在标题行、空行、块结构（`#figure`/`#table`/`#quote`/`#align`/`#block`）后的第一个文本段落前插入。

**跳过列表**（不插入缩进的行）：
```
#v(  #line(  #pagebreak  #horizontalrule
#metadata  #outline  #set   #show
#import  #let   #include  #context
#colbreak  #h(2em)  #strong[图  #strong[表
#figure  #align(  #block(  #table
```

---

## 11. Markdown预处理（preprocess_md）

pandoc转换前，`preprocess_md()`处理：

| 处理 | 规则 | 适用范围 |
|------|------|----------|
| 紧凑排版 | 中英文之间去空格（"AI模型" not "AI 模型"） | 正文、引用块、表格行 |
| 编号保护 | "图0.0 标题"中编号后空格保留 | 全文 |
| 标题跳过 | 以 `#` 开头的标题行不紧凑排版 | 标题行 |
| 代码块保护 | 代码块内不紧凑排版 | 代码块内 |
| 代码块符号 | `<=` → `≤`，`>=` → `≥`，`<` → `＜`，`>` → `＞` | 代码块内 |
| 表格全角尖括号 | `<` → `＜`，`>` → `＞` | 表格行 |

### 紧凑排版函数 `compact_cn_en()`

```python
cjk = r'\u4e00-\u9fff\u3000-\u303f\uff00-\uffef'
latin = r'a-zA-Z0-9'

# 保护 图/表/§ 编号后的空格
PLACEHOLDER = "\x00"
text = re.sub(r'([图表§]\d+\.?\d*)\s+', lambda m: m.group(1) + PLACEHOLDER, text)

# 中文→英文/数字：去空格
text = re.sub(rf'([{cjk}])\s+([{latin}])', r'\1\2', text)
# 英文/数字→中文：去空格
text = re.sub(rf'([{latin}])\s+([{cjk}])', r'\1\2', text)
# 恢复保护的空格
text = text.replace('\x00', ' ')

```

---

## 12. Pandoc陷阱与预防规则

### 12.1 `---`紧邻标题导致假表格

**问题**：Markdown中 `---`（水平线）紧邻 `## 标题`（无空行分隔）时，pandoc的 `simple_tables` 扩展会将 `---` 解析为单列表格分隔符，导致后续内容全部渲染为Typst `#table`。

**正确写法**：
```markdown
---

## 1.6 标题
```

**错误写法**（会触发假表格）：
```markdown
---
## 1.6 标题
```

**规则**：`---` 后必须有空行才能接标题。

### 12.2 代码块内 `<` 导致行截断

**问题**：代码块内包含 `<` 字符（如 `< 30s`）时，pandoc可能将其误解析为HTML标签起始，导致后续内容被截断或错误嵌套。

**解决**：`preprocess_md()` 在代码块内将 `<` → `＜`，`>` → `＞`（全角尖括号）。

### 12.3 图计数器逐章重置

**实现**：在H1 show rule中同时执行：
```typst
counter("chapter").update(c => c + 1)
counter(figure.where(kind: image)).update(0)
```
- `counter("chapter")`：自定义章号计数器（Typst的heading counter在自定义show rule中不自动递增）
- `counter(figure.where(kind: image)).update(0)`：每章重置图编号

图编号在caption中通过 `counter("chapter").get().first() - 1` 获取0-based章号（因H1 show rule先递增counter再渲染内容）。

---

## 13. 工具脚本

| 脚本 | 用途 | 路径 |
|------|------|------|
| `build_pdf.py` | 主构建脚本：MD→Typst→PDF | `05-visual-assets/handbook-layout/` |
| `add_table_captions.py` | 为表格自动添加"表N  标题"编号 | 同上 |
| `find_blank_issues.py` | 检查缺失的空行 | 同上 |
| `gen_radar.py` | 用matplotlib生成FDE雷达图PNG | 同上 |

---

## 14. 关键文件

| 文件 | 用途 |
|------|------|
| `05-visual-assets/handbook-layout/book-template.typ` | Typst排版模板（所有show rule和set rule） |
| `05-visual-assets/handbook-layout/build_pdf.py` | 构建脚本（预处理+后处理+编译） |
| `01-content/textbook/Ch00-Ch09*.md` | 10章教材Markdown源文件 |
| `05-visual-assets/diagrams-export/MN/` | 教材插图PNG（规范导出目录，PDF构建实际读取） |
| `05-visual-assets/diagrams-source/MN/` | drawio源文件（规范编辑目录） |
| `01-content/textbook/diagrams/` | 旧版插图副本（已废弃，不再用于PDF构建） |
| `05-visual-assets/print-ready/AI应用系统架构师_教材_A4.pdf` | 全量PDF输出 |
| `05-visual-assets/print-ready/逐章PDF/` | 10个逐章PDF |

---

## 15. 修改规范

调整任何排版参数时：

1. **先改本文件** — 更新对应参数表
2. **再改代码** — 同步到 `book-template.typ` 或 `build_pdf.py`
3. **重建PDF** — 运行 `python build_pdf.py`
4. **视觉验证** — 检查输出PDF中对应元素是否正确

### 字号对照（中国标准）

| 名称 | pt值 | 用途 |
|------|------|------|
| 小四 | 12pt | 正文 |
| 五号 | 10.5pt | 表格内容 |
| 小五 | 9pt | 图注、表注 |
| 六号 | 7.5pt | 脚注（暂未使用） |

### 间距关系约束

- **段距 > 行距**：spacing(24pt) > leading(20pt)
- **图注行距 = 正文行距**：leading(20pt)
- **表格行距 < 正文行距**：leading(16pt) < 20pt
- **代码行距 < 表格行距**：leading(14pt) < 16pt
