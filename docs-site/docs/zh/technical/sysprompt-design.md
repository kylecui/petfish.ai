# System Prompt Architecture

PEtFiSh 如何构建 AI agent 指令，以实现一致性、可维护性与 token 效率。

---

## 难题

大多数 AI agent 环境将所有内容塞进一个单一的指令文件中。随着项目增长，这个文件会变得臃肿不堪 —— 数千行的规则、惯例、工具使用模式与领域知识互相争夺 agent 的注意力。

PEtFiSh 采取了不同的方式：**分层指令注入 (layered instruction injection)** 结合按需加载。

---

## 架构概览

```text
┌─────────────────────────────────────────────┐
│  Platform System Prompt (immutable)         │
├─────────────────────────────────────────────┤
│  AGENTS.md — Project-level rules           │
│  ├── Companion Gateway (always-on)         │
│  ├── Release discipline                    │
│  ├── Python environment policy             │
│  ├── Pack-specific rules (injected)        │
│  └── Development lessons                   │
├─────────────────────────────────────────────┤
│  Skills — On-demand prompt modules         │
│  ├── SKILL.md (loaded when triggered)      │
│  ├── references/ (lazy-loaded)             │
│  └── scripts/ (executed, not loaded)       │
├─────────────────────────────────────────────┤
│  Commands & Agents — Workflow entry points  │
└─────────────────────────────────────────────┘
```

每一层都有特定的角色和加载策略。

---

## 第 1 层：AGENTS.md — 始终在线的核心

`AGENTS.md` 文件在每次交互时都会被平台加载。它包含适用于**所有**任务的规则，不限具体领域。

### 这里放什么

- **Companion Gateway**：在每条消息前运行的 6 步预处理管道
- **跨领域策略**：发布纪律、Python 环境规则、跨仓库保护
- **开发教训**：从生产事故中总结的硬核模式（例如，"bash 嵌套的 Python 脚本使用 `chr()` 而非转义字面量"）
- **Pack 专属规则**：在 pack 安装时通过标记注入

### 这里不放什么

- 专属领域的业务流（交由 skills 处理）
- 详细的 API 文档（交由 skill references 处理）
- 一次性的配置说明（交由 commands 处理）

### 设计原则：断言式默认值

AGENTS.md 规则被写成**强制指令**，而不是建议：

```markdown
<!-- Good: Clear, enforceable -->
## Release Discipline (Mandatory)
- Every merge to master = one release
- Tag format: vX.Y.Z (semantic versioning)
- Forbidden: master merges without release tags

<!-- Bad: Vague, unenforced -->
## Release Guidelines
- Consider creating releases when merging to master
- Try to use semantic versioning
```

Agent 将 AGENTS.md 的内容视为项目的法则。含糊的建议在压力下会被忽略，但明确的规则不会。

---

## 第 2 层：Pack 专属规则 — 安装时注入

当安装一个 pack 时，它的规则会被注入到 AGENTS.md 文件的 HTML 注释标记之间：

```markdown
<!-- agents-rules/deploy-ops.md -->
# Repo Deployment & Operations Rules
...skill routing rules, work principles, output preferences...
<!-- /agents-rules/deploy-ops.md -->
```

### 基于标记的注入

安装脚本使用 HTML 注释标记来：

1. **插入 (Insert)**：首次安装时添加规则
2. **替换 (Replace)**：升级时（`--force`）更新规则
3. **移除 (Remove)**：卸载时清理规则

这使得 AGENTS.md 保持为平台可读的单一文件，同时支持模块化的规则管理。

### 路由表

每个 pack 的规则都包含强制的**技能路由部分 (skill routing section)**，它明确告诉 agent 遇到何种任务必须使用哪个 skill：

```markdown
## Skill Routing (Mandatory)

1. User says "deploy" → MUST use repo-runtime-discovery first
2. User says "帮我部署" → MUST route to repo-service-lifecycle
3. Deployment complete → MUST verify with deployment-verifier
```

没有路由表时，agent 会自行猜测使用哪个 skill。有了路由表，路由就变成了确定性的操作。

### 冲突解决

当不同 pack 的规则重叠时，每个 pack 都会包含明确的冲突解决说明：

```markdown
### Conflict Resolution
- When review intent AND style rewrite intent coexist →
  load BOTH anti-sycophancy-calibration AND petfish-style-rewriter
- When "help me review" context is simple proofreading →
  treat as proofreading, don't enable calibration skill
```

---

## 第 3 层：Skills — 按需提示词模块

Skills 是核心的复用单元。只有当 agent 判定需要时，一个 skill 才会被加载到上下文中。

### 加载触发器

Agent 会将用户意图与 frontmatter 中的 skill 描述进行匹配：

```yaml
---
name: deployment-executor
description: >-
  Execute deployment/upgrade/redeployment per confirmed plan.
  Trigger for 执行发布, 切换release, 配置注入, 迁移与启动.
---
```

`description` 字段是 agent 在加载前唯一能看到的内容。如果触发关键词不在描述中，该 skill 就不会被激活。这就是为什么 PEtFiSh 强制执行 [description与body触发词对齐](../developer/skill-authoring.md#activation)。

### 延迟加载的参考资料 (References)

Skills 包含 `references/` 目录用于存放详细知识：

```text
skill/
├── SKILL.md           # Loaded on trigger
├── references/
│   ├── api-guide.md   # Loaded only when needed
│   └── patterns.md    # Loaded only when needed
└── scripts/
    └── deploy.py      # Executed, never loaded as context
```

SKILL.md 会指示 agent：“仅在需要 API 细节时读取 `references/api-guide.md`”。这样可以将初始上下文负载降至最低。

### 脚本与参考资料的区别

| 资产 | 是否加载到上下文？ | 目的 |
|---|---|---|
| `SKILL.md` | 是，在触发时 | 给 agent 的操作指令 |
| `references/*.md` | 按需 | agent 在需要时查阅的详细知识 |
| `scripts/*.py` | 否（仅执行） | agent 调用的工具，无需阅读 |
| `schemas/*.json` | 按需 | 用于结构化输出的验证模式 |
| `assets/*` | 按需 | 模板、图表、静态资源 |

这种区分对 token 预算至关重要。一个作为工具调用的 500 行 Python 脚本消耗的上下文 token 为零。而同样的文本若作为参考资料加载，则会消耗约 2,000 个 tokens。

---

## 第 4 层：Commands 与 Agents

Commands 和 agents 提供了工作流的入口，但不会增加持久上下文。

- **Commands**：常见工作流的具名快捷方式（例如 `/course-init`, `/course-qa`）
- **Agents**：具有特定工具权限和 skill 装载列表的基于角色的配置

两者都依赖 skills 来实现实际逻辑 —— 它们是路由机制，而不是知识存储库。

---

## Token 预算管理

PEtFiSh 的架构围绕有限的上下文窗口而设计。每消耗一个 token 的指令，就是在与用户的实际工作内容争夺空间。

### 预算分配

```text
Platform system prompt:     ~5,000 tokens (fixed, not controllable)
AGENTS.md core rules:       ~3,000 tokens (always loaded)
Pack-specific rules:        ~2,000 tokens (injected per installed pack)
Active skill SKILL.md:      ~1,000 tokens (loaded on demand)
Skill references:           ~500-2,000 tokens (lazy loaded)
────────────────────────────────────────────
Available for user work:    Remaining context window
```

### 节省 Token 的策略

1. **细粒度的 Skill 拆分**：摒弃单一的巨型指令文件，将知识拆分到约 80 个 skills 中。每次交互仅加载相关的 1-2 个。

2. **延迟加载参考资料**：仅当 agent 明确需要时才读取 skill 的 reference，而非在开头全盘加载。

3. **脚本执行优于上下文加载**：Python 脚本是 agent 用于*调用*的工具，而不是用来*阅读*的文档。一个 500 行的 lint 脚本在上下文中占用 0 tokens。

4. **AGENTS.md 的断言式精简**：规则被写成简练的指令，而不是冗长的解释性文本。对比：
   ```
   # Verbose (costs tokens, adds no enforcement value)
   When working with Python environments, it's important to remember
   that this project uses uv as its package manager. Please make sure
   to use uv for all Python-related operations.

   # Terse (same enforcement, fewer tokens)
   Python environments: uv only. No pip. No bare python3 for scripts
   with dependencies.
   ```

5. **基于 Pack 的条件加载**：只有当 pack 安装时，相关的规则才存在于 AGENTS.md 中。仅使用 `course` 和 `petfish` pack 的项目不必为 `deploy` 规则买单。

---

## AGENTS.md 作为指令合并目标

PEtFiSh 将 AGENTS.md 视为**合并目标 (merge target)**，而不是一个模板。多个 packs 向同一文件贡献规则且互不覆盖。

### 合并机制

```text
Base AGENTS.md (project-level rules)
  + companion pack rules (between markers)
  + deploy pack rules (between markers)
  + course pack rules (between markers)
  + research pack rules (between markers)
  = Final AGENTS.md
```

每个 pack 拥有自己的区块。安装则添加，升级则替换，卸载则移除。文件的其余部分保持原样。

### 为什么不使用独立文件？

大多数 AI 平台只读取唯一的指令文件（如 `AGENTS.md`, `CLAUDE.md`, `.cursorrules`）。PEtFiSh 无法控制平台的文件加载逻辑 —— 因此必须将所有内容合并到平台期望的那个单一文件中。

这是一种实用的约束妥协，而不是设计偏好。如果平台支持多文件指令，PEtFiSh 也会原生支持。

---

## 多平台适配

PEtFiSh 支持 8 个 AI 平台，每个平台拥有不同的指令文件格式：

| Platform | File | Token Sensitivity |
|---|---|---|
| OpenCode | `AGENTS.md` | Low (large context) |
| Claude Code | `CLAUDE.md` | Medium |
| Cursor | `.cursor/rules/*.mdc` | High (multiple small files) |
| GitHub Copilot | `.github/copilot-instructions.md` | High |
| Windsurf | `.windsurfrules` | Medium |

安装器会为各平台调整内容：

- **完整内容**：面向拥有超大上下文窗口的平台（如 OpenCode）
- **浓缩内容**：面向有 token 限制的平台（如 Cursor, Copilot）
- **平台专属钩子**：在需要时添加（如 Claude Code shell 钩子）

---

## 设计教训

### 1. 描述是唯一的触发面

在决定加载什么内容时，agent 只能看到 skill descriptions。内容主体在决策时是不可见的。这意味着：

- 每一个触发关键词必须出现在描述中
- 必须强制保证描述与主体内容的触发对齐（PEtFiSh 使用 `skill-lint` 解决该问题）
- 中英文关键词同样重要 —— 用户可能用任意一种语言表达

### 2. 规则必须具备可执行性

在 token 压力下，含糊的指令（"尝试去...", "考虑..."）会被忽略。有效的规则应当：

- **非黑即白**：做 X 或者不做 X
- **可观察**：可以通过检查输出来验证
- **有明确后果**：打破规则会有相应的声明后果

### 3. 经验教训应当存在于 AGENTS.md 中

当生产事故暴露出非直觉的模式时，应当将其作为规则记录在 AGENTS.md 中 —— 而不是留在 commit 信息或 issue 讨论里。PEtFiSh 的 AGENTS.md 专设了一个 "Development Lessons" 部分来实现此目的。

来自真实事故的例子：
```markdown
### bash-embedded Python: use chr() instead of escape literals
When Python code runs inside bash double-quoted strings, backslash
escaping compounds across layers. Use chr(92) for backslash, chr(47)
for forward slash. This lesson cost two patch releases (v0.11.10, v0.11.11).
```

### 4. 一个文件，多个属主

合并目标模式行之有效，但需要纪律约束：

- 每个 pack 必须明确拥有专属唯一标记间的单一区块
- Pack 规则不得引用其专属区块外的内容
- 卸载操作必须无副作用地彻底清理该区块

---

## 延伸阅读

- [Companion Gateway](companion-gateway.md) — 始终在线的预处理管道
- [Token Cost Engineering](compaction.md) — 管理上下文窗口预算的策略
- [Skill Authoring Guide](../developer/skill-authoring.md) — 如何编写高效的 skills