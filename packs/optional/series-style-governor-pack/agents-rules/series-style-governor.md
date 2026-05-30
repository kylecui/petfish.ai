<!-- agents-rules/series-style-governor.md -->
# Series Style Governor Pack

本pack提供跨文档风格一致性治理能力，覆盖风格画像提取、术语漂移检测、排版漂移审计和保守归一化改写。

## Skill路由（强制）

### 必须遵守的路由规则

1. 用户要求跨多个文档统一风格、术语、命名或排版时，**必须**路由到 `series-style-governor` skill
2. 用户提供参考文档并要求其他文档对齐其风格时，**必须**路由到 `series-style-governor` skill
3. 用户要求检查系列文档的术语漂移、命名不一致或排版漂移时，**必须**路由到 `series-style-governor` skill
4. 用户要求保守改写文档以匹配系列基线风格时，**必须**先产出审计报告和改写计划，再执行改写

### 冲突解决

- 单文档润色 → `petfish-style-rewriter`
- 长文写作流程 → 对应写作skill
- 纯Markdown格式修复（无系列上下文）→ `markdown-course-writing`
- 研究笔记摘录 → `research-note-capture`

## 何时启用

- 用户提到"系列风格"、"跨文档一致性"、"风格画像"、"术语漂移"、"排版漂移"
- 用户要求以某个文档为基准统一其他文档风格
- 用户要求审计或改写一批Markdown文档以保持风格一致
- 用户要求构建或更新系列风格规范

## 何时不启用

- 单文档编辑或润色
- 纯排版格式修复（无系列上下文）
- 研究或调研任务
- 代码编写或调试

## 不可违反的规则

- 不引入新事实、不删除引用和脚注、不改变技术论断
- 不把作者语言变成通用AI腔
- 不因为术语相似就合并不同概念
- 改写可能改变语义时标记 `review-needed`，不静默应用
- 基线文件不覆盖，除非用户显式要求
- 后续文档结构优于基线时报告建议升级，不降级
- 保留原始论证意图、立场和结论
- 保留Markdown标题层级，除非明确违反基线结构
- 中文技术写作默认中文英文之间无空格，除非基线另有惯例

## Handoff边界

本skill负责：
- 跨文档风格一致性审计
- 风格画像提取与管理
- 保守机械改写（风格归一化）
- 术语漂移检测与归一化

不负责：
- 单文档润色 → petfish-style-rewriter
- 长文写作流程 → fat-slim-writer等写作skill
- 研究笔记/引用管理 → research-note-capture
- 课程结构设计 → course-content-authoring
- 纯Markdown格式修复（无系列上下文）→ markdown-course-writing

组合规则：
- 可与petfish-style-rewriter组合：先归一化再润色
- 需要写作时先运行本skill归一化，再交给写作skill
<!-- /agents-rules/series-style-governor.md -->
