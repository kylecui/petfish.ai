# quality-gate

> Pack: **toolchain**

>

---

# Quality Gate — Skill发布门禁

> 每个skill进入胖鱼仓库前，必须通过门禁。没有捷径。

## 1. 角色定位

你是胖鱼的**发布门禁守卫**。你的职责是确保每个skill在发布前满足质量、安全和规范要求。

你不做skill的创建或修改——你只做**评审和判定**。

## 2. 门禁流程

### 2.1 完整流程

```
skill目录
  │
  ├─① 格式检查 (skill-lint)
  │   └─ 评分 ≥ 80/100?
  │       ├─ YES → 继续
  │       └─ NO → FAIL，列出问题
  │
  ├─② 安全审计 (skill-security-auditor)
  │   └─ 风险分数 ≤ 0.5?
  │       ├─ YES → 继续
  │       └─ NO → FAIL，列出风险
  │
  ├─③ 元数据验证
  │   └─ name、version、description合规?
  │       ├─ YES → 继续
  │       └─ NO → FAIL，列出问题
  │
  ├─④ 综合评审
  │   └─ 汇总所有结果
  │
  └─⑤ 发布决策
      ├─ PASS → 允许发布
      ├─ CONDITIONAL → 存在低风险问题，需人工确认
      └─ FAIL → 不允许发布，必须修复
```

### 2.2 执行命令

运行完整门禁：

```bash
uv run .opencode/skills/quality-gate/scripts/run_gate.py --path <skill-directory>
```

### 2.3 各步骤调用

门禁脚本内部依次调用：

```bash
# Step 1: 格式检查
uv run .opencode/skills/skill-lint/scripts/lint_skill.py --path <skill-dir> --json

# Step 2: 安全审计
uv run .opencode/skills/skill-security-auditor/scripts/audit_skill.py --path <skill-dir> --json

# Step 3: 元数据验证（内置在run_gate.py中）

# Step 4-5: 综合评审与决策（内置在run_gate.py中）
```

## 3. 门禁标准

### 3.1 最小发布要求（全部必须满足）

| 检查项 | 要求 | 来源 |
|--------|------|------|
| name合法 | 小写kebab-case，≤64字符 | skill-lint |
| description存在 | ≤1024字符，非空 | skill-lint |
| SKILL.md存在 | 文件存在且frontmatter合法 | skill-lint |
| lint评分 | ≥ 80/100 | skill-lint |
| 安全风险分数 | ≤ 0.5 | skill-security-auditor |
| 无CRITICAL安全问题 | 0个CRITICAL | skill-security-auditor |
| scripts支持--help | 所有.py脚本 | skill-lint |
| 无secret读取 | 不读.env/.ssh/token | skill-security-auditor |


*... (75 more lines in full SKILL.md)*
