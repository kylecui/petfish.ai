# Skill 创作指南 (Skill Authoring Guide)

了解如何从头开始创建、组织和验证 PEtFiSh 技能 (skills)。

---

## 什么是 Skill？

Skill 是一个包含 `SKILL.md` 文件的目录，该文件具有 YAML 前置元数据 (frontmatter) 和 Markdown 指令。Skill 告诉 AI 代理 *如何* 执行特定任务——它们是被打包为可复用模块的提示工程 (prompt engineering)。

```text
my-skill/
├── SKILL.md              # 必填项：前置元数据 (frontmatter) + 指令
├── references/           # 可选项：参考文档、示例
├── scripts/              # 可选项：用于自动化的 Python 脚本 (scripts)
├── assets/               # 可选项：模板 (templates)、模式 (schemas)、图片
└── evals/
    └── trigger/          # 可选项：触发器评估 (trigger evaluation) 测试集
        └── my-skill.json
```

---

## 快速开始

创建 skill 的最快方法：

```bash
# 使用 /petfish 提供的 skill-author 技能
/petfish create my-new-skill
```

这会搭建目录结构并生成一个初始的 `SKILL.md`。您也可以手动创建它。

---

## SKILL.md 结构

每个 skill 都需要一个包含 YAML 前置元数据和 Markdown 主体的 `SKILL.md` 文件。

### 前置元数据 (Frontmatter)

```yaml
---
name: my-skill
version: 1.0.0
description: >-
  包含触发关键词的单行描述。这是代理用来决定是否加载此 skill 的读取内容。保持在 500 个字符以内。
  请包含中文和英文的触发短语。
---
```

| 字段 (Field) | 是否必填 | 备注 |
|---|---|---|
| `name` | 是 | 小写的短横线命名法 (kebab-case)。必须与目录名匹配。 |
| `version` | 是 | 语义化版本 (Semver) 格式 (`1.0.0`)。 |
| `description` | 是 | 500 个字符以内。必须覆盖主体中 ≥80% 的触发词。 |

!!! warning "Description 是匹配面"
    代理仅读取 `description` 来决定是否激活一个 skill。主体 (body) 中的触发短语对匹配器是不可见的。如果一个关键词不在 description 中，该 skill 将不会因为该关键词而触发。

### 主体 (Body)

主体包含实际的指令。您可以根据您的 skill 的需要来组织结构，但请遵循以下约定：

```markdown
# Role (角色)

You are a [role description].

## Activation (激活条件)

Use this skill when: [trigger conditions]

## Workflow (工作流)

1. Step one
2. Step two
3. Step three

## Boundaries (边界)

- MUST: [requirements]
- MUST NOT: [prohibitions]

## Output Format (输出格式)

[Expected output structure]
```

---

## 命名规则

- **目录名** = 前置元数据中的 `name` 字段
- 仅使用小写的短横线命名法 (`kebab-case`)：使用 `my-skill`，而不是 `mySkill` 或 `My_Skill`
- 目录名中不能有空格或下划线
- 优先使用描述性的名称：`deployment-executor` 优于 `deploy`

---

## 添加脚本 (Adding Scripts)

Python 脚本放在 `scripts/` 目录中。它们将 skill 的能力扩展到了提示指令之外。

```text
my-skill/
└── scripts/
    └── validate.py
```

### 脚本要求

- 使用 PEP 723 内联元数据 (inline metadata) 声明依赖项：

```python
# /// script
# requires-python = ">=3.11"
# dependencies = ["pyyaml>=6.0"]
# ///
```

- 通过 `uv run` 运行：

```bash
uv run python .opencode/skills/my-skill/scripts/validate.py --input data.json
```

- 永远不要使用 `pip install`。对于有外部依赖的脚本，永远不要直接使用裸 `python3` 命令。

---

## 添加参考文件 (Adding References)

参考文件提供领域知识 (domain knowledge)，skill 指令可以指向这些知识：

```text
my-skill/
└── references/
    ├── best-practices.md
    └── examples.md
```

!!! tip "懒加载 (Lazy loading)"
    参考文件应按需加载，而不是一次性全部加载。指示 skill 仅在需要时阅读特定的参考文件。

---

## 添加 Schema (Adding Schemas)

位于 `schemas/` 中的 JSON schema 定义了结构化的输出格式：

```text
my-skill/
└── schemas/
    └── output.json
```

!!! warning "Schema-SKILL.md 对齐 (Schema–SKILL.md alignment)"
    如果您同时拥有 schema 和 SKILL.md 字段描述，它们**必须**完全匹配——相同的字段名、相同的必填/可选标记、相同的类型。不匹配会导致验证失败。详情请参见 [Schema 对齐规范 (Schema alignment discipline)](../../technical/index.md)。

---

## 触发评估 (Trigger Evaluation)

测试您的 skill 是否能在正确的输入下正确触发，并在错误的输入下保持静默。

### 创建测试集

```text
my-skill/
└── evals/
    └── trigger/
        └── my-skill.json
```

```json
{
  "skill_name": "my-skill",
  "should_trigger": [
    "help me validate the deployment",
    "check if the service is healthy"
  ],
  "should_not_trigger": [
    "write a poem about clouds",
    "fix this CSS bug"
  ]
}
```

### 运行评估

```bash
/petfish eval .opencode/skills/my-skill/
```

或者通过脚本运行：

```bash
uv run python .opencode/skills/skill-trigger-evaluator/scripts/evaluate_triggers.py \
  --path .opencode/skills/my-skill/evals/trigger/my-skill.json
```

---

## 验证 (Validation)

在发布之前，请验证您的 skill：

### 代码检查 (Lint)

```bash
/petfish lint .opencode/skills/my-skill/
```

检查内容：

- 前置元数据的完整性（`name`, `version`, `description`）
- 描述长度（≤500个字符）
- 触发关键词覆盖率（描述内容涵盖主体的 ≥80%）
- 文件结构约定
- 得分必须 ≥80/100 才能通过

### 安全审计 (Security Audit)

```bash
/petfish audit .opencode/skills/my-skill/
```

扫描内容：

- 提示注入向量 (Prompt injection vectors)
- 密钥访问模式 (Secret access patterns)
- 危险命令的使用
- 权限过大
- 风险得分必须 ≤0.5 且无严重 (CRITICAL) 发现

### 完整质量门禁 (Full Quality Gate)

```bash
/petfish gate .opencode/skills/my-skill/
```

依次运行代码检查 → 安全审计 → 元数据验证，然后输出一个决策：

| 决策 (Decision) | 含义 |
|---|---|
| **PASS (通过)** | 准备好发布 |
| **CONDITIONAL (有条件通过)** | 存在次要问题；可带着已知问题继续 |
| **FAIL (失败)** | 存在阻塞性问题；发布前必须修复 |

---

## 打包为 Pack (Packaging into a Pack)

Skill 以 **packs** 的形式分发——位于 `packs/` 下的目录，将相关的 skills 打包在一起。

```text
packs/my-pack/
├── .opencode/
│   └── skills/
│       ├── skill-one/
│       │   └── SKILL.md
│       └── skill-two/
│           └── SKILL.md
├── pack-manifest.json
├── AGENTS.md
└── opencode.example.json
```

### pack-manifest.json

```json
{
  "name": "my-pack",
  "version": "1.0.0",
  "description": "What this pack does",
  "skills": ["skill-one", "skill-two"],
  "commands": [],
  "agents": []
}
```

### 新 Pack 检查清单

引入一个新的 pack 需要更新 **9 个触点 (touchpoints)**。遗漏任何一个都会导致用户静默安装失败。完整的检查清单请参见 [贡献指南 (Contributing Guide)](contributing.md)。

---

## 常见错误 (Common Mistakes)

| 错误 | 后果 | 修复方法 |
|---|---|---|
| 触发关键词仅在主体中，而不在描述中 | Skill 永远不会因为这些关键词而被激活 | 将关键词添加到前置元数据的描述中 |
| 描述仅有英文 | 中文用户无法触发该 skill | 添加中文触发短语 |
| Schema 字段名与 SKILL.md 不同 | 运行时会出现验证失败 | 交叉检查并对齐 |
| 在脚本中使用 `pip install` | 会破坏由 uv 管理的环境 | 使用 PEP 723 内联元数据 |
| 贪婪加载参考文件 | 浪费上下文 token | 按需懒加载 |