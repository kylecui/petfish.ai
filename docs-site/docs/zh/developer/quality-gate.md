# 质量门禁流水线 (Quality Gate Pipeline)

质量门禁 (Quality Gate) 是 PEtFiSh 的发布决策系统。它按顺序运行三项检查——代码检查 (lint)、安全审计 (security audit) 和元数据验证 (metadata validation)——然后输出通过 (PASS)、有条件通过 (CONDITIONAL) 或失败 (FAIL) 的决策。

---

## 概览 (Overview)

```text
skill/
  │
  ├─ 1. Lint (代码检查)
  │    └─ 得分 ≥ 80/100
  │
  ├─ 2. Security Audit (安全审计)
  │    └─ 风险 ≤ 0.5 且无 CRITICAL (严重) 问题
  │
  ├─ 3. Metadata Validation (元数据验证)
  │    └─ Name、version、description 均有效
  │
  └─ 4. Decision (决策)
       ├─ PASS         → 准备发布
       ├─ CONDITIONAL  → 带着已知问题继续
       └─ FAIL         → 发布前必须修复
```

---

## 运行门禁 (Running the Gate)

### 通过 /petfish

```bash
/petfish gate .opencode/skills/my-skill/
```

### 通过脚本

```bash
# 单个 skill
uv run python .opencode/skills/quality-gate/scripts/run_gate.py \
  --path .opencode/skills/my-skill/

# 递归运行 — 目录下的所有 skills
uv run python .opencode/skills/quality-gate/scripts/run_gate.py \
  --path .opencode/skills/ --recursive
```

---

## 第 1 阶段：代码检查 (Lint)

运行 `lint_skill.py` 检查结构、格式和触发的可靠性。

### 检查内容

| 检查项 | 规则 | 严重程度 |
|---|---|---|
| 前置元数据字段 | `name`, `version`, `description` 存在 | ERROR |
| 名称格式 | 小写的短横线命名法 (kebab-case)，且与目录匹配 | ERROR |
| 描述长度 | ≤500个字符 | WARNING |
| 触发覆盖率 | 描述内容涵盖主体中 ≥80% 的触发关键词 | ERROR (<50%), WARNING (50–80%) |
| 文件结构 | SKILL.md 存在于预期路径 | ERROR |
| 脚本约定 | 没有 `pip install`，没有裸 `python3` 命令 | WARNING |

### 评分机制

每条规则都有助于得出 0–100 的总分。通过此阶段需要门禁得分 **≥80**。

### 独立运行代码检查

```bash
/petfish lint .opencode/skills/my-skill/

# 或者直接运行：
uv run python .opencode/skills/skill-lint/scripts/lint_skill.py \
  --path .opencode/skills/my-skill/

# CI 环境中输出 JSON 格式：
uv run python .opencode/skills/skill-lint/scripts/lint_skill.py \
  --path .opencode/skills/my-skill/ --json
```

---

## 第 2 阶段：安全审计 (Security Audit)

运行 `audit_skill.py` 扫描安全风险。

### 扫描内容

| 领域 | 示例 |
|---|---|
| SKILL.md 指令 | 提示注入向量 (Prompt injection vectors)，凭据访问模式 |
| `scripts/` | 危险命令 (`rm -rf`, `eval`)，网络访问，超出作用域的文件写入 |
| `references/` | 嵌入的密钥，硬编码的 token |
| MCP/工具作用域 | 权限过大，无作用域限制的工具访问 |

### 风险得分 (Risk Score)

输出一个 0.0–1.0 的风险得分。门禁要求得分 **≤0.5** 并且 **无严重 (CRITICAL) 发现**。

| 得分范围 | 含义 |
|---|---|
| 0.0–0.2 | 低风险 |
| 0.2–0.5 | 中等风险 — 建议进行审查 |
| 0.5–0.8 | 高风险 — 很可能会被拦截 |
| 0.8–1.0 | 极高风险 — 必须修复 |

### 独立运行审计

```bash
/petfish audit .opencode/skills/my-skill/

# 或者直接运行：
uv run python .opencode/skills/skill-security-auditor/scripts/audit_skill.py \
  --path .opencode/skills/my-skill/
```

---

## 第 3 阶段：元数据验证 (Metadata Validation)

如果 skill 属于某个 pack，则验证 pack 级别的元数据：

- `name` 字段与目录名匹配
- `version` 遵循语义化版本规范 (semver)
- `description` 存在且非空
- Pack 清单 (manifest)（如果存在）列出了该 skill

---

## 决策逻辑 (Decision Logic)

| 条件 | 决策 |
|---|---|
| Lint ≥80 且 audit ≤0.5 且无 CRITICAL 且 metadata 有效 | **PASS (通过)** |
| Lint ≥60 且 audit ≤0.7 且存在 trigger-coverage ERROR | **CONDITIONAL (有条件通过)** |
| Lint <60 或 audit >0.7 或存在 CRITICAL 发现 | **FAIL (失败)** |

### 有条件通过处理 (CONDITIONAL Handling)

CONDITIONAL 结果意味着存在次要问题但并非阻塞性问题。常见原因：

- 触发覆盖率在 50–80% 之间 (WARNING 级别)
- 中等安全风险 (0.2–0.5)
- 缺少可选字段

您可以继续进行，但应当解决提到的已知问题。

---

## 持续集成 (CI Integration)

门禁脚本支持为 CI 流水线输出 JSON 格式：

```bash
# 返回退出码 (exit code)：PASS 为 0，CONDITIONAL 为 1，FAIL 为 2
uv run python .opencode/skills/quality-gate/scripts/run_gate.py \
  --path .opencode/skills/my-skill/ --json
```

### 批量门禁验证

在发布之前为 pack 中的所有 skills 运行门禁：

```bash
uv run python .opencode/skills/quality-gate/scripts/run_gate.py \
  --path packs/my-pack/.opencode/skills/ --recursive
```

---

## 修复常见失败 (Fixing Common Failures)

### 触发覆盖率过低

```
ERROR: trigger-coverage 35% (threshold: 50%)
```

**修复方法**：将主体激活 (activation) 部分缺失的触发关键词添加到前置元数据的 `description` 中。必须覆盖中文和英文的关键词。

### 代码检查得分低于 80

查阅代码检查输出中详细的违反规则说明。最常见的问题包括：

- 缺少 `version` 字段
- 描述超过了 500 个字符
- 目录名与 `name` 字段不匹配

### 安全审计警告

审查每一个发现项。常见的误报 (false positives) 包括：

- 合法需要网络访问的脚本（例如，API 客户端）
- 作为 skill 核心功能一部分的文件写入操作

对于合法的操作，请记录说明理由。对于真正的风险，请进行修复。