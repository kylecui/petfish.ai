# 胖鱼 fish-* 功能与 Skills 命名体系设计

> 本文档用于重新整理 PEtFiSh / 胖鱼的功能、skills、packs、命令与目录命名体系。  
> 目标是将胖鱼现有能力统一到 `fish-*` 命名空间下，形成更清晰、更一致、更容易扩展的产品结构。

---

## 0. 总体判断

胖鱼当前已经具备几条主线：

1. **项目初始化**：根据用户项目目标初始化 AI-agent 友好的项目目录。
2. **Skill 生命周期管理**：覆盖发现、创建、校验、安全审计、调优、安装、追踪。
3. **多平台适配**：支持 OpenCode、Claude Code、Codex、Cursor、Copilot、Windsurf、Antigravity 等平台。
4. **项目能力包**：覆盖课程开发、部署运维、PPT、测试文档、写作风格等场景。
5. **上下文治理**：从原有 context-router 演进到 fish-trail，管理长期话题轨迹和上下文污染。

因此，本次整理不应只是“给旧名字加 fish 前缀”，而应该借此机会重新分层，将胖鱼整理成一个统一的 `fish-*` 能力体系。

---

## 1. 命名原则

### 1.1 统一前缀

所有可安装 pack、内部 skill、命令模块、状态目录，统一使用：

```text
fish-*
```

基本格式：

```text
fish-<能力名>
```

例如：

```text
fish-init
fish-core
fish-trail
fish-mine
fish-author
fish-lint
fish-audit
fish-gate
```

### 1.2 使用短词

优先使用简短、明确、可记忆的能力名。

推荐：

```text
fish-mine
fish-author
fish-lint
fish-audit
fish-gate
fish-tune
fish-eval
fish-track
```

避免：

```text
fish-repo-skill-miner
fish-skill-description-optimizer
fish-petfish-companion
```

原因：

1. 过长的名字不利于传播；
2. `fish-*` 已经隐含这是胖鱼能力；
3. 在胖鱼上下文中反复出现 `skill`、`petfish` 会显得冗余。

### 1.3 名称表达能力边界

每个 `fish-*` 名称应表达一个清晰能力边界：

| 名称 | 能力边界 |
|---|---|
| `fish-init` | 初始化项目 |
| `fish-core` | 胖鱼核心总控 |
| `fish-trail` | topic graph 与上下文治理 |
| `fish-mine` | 从仓库挖掘 skills |
| `fish-author` | 创建 skills |
| `fish-gate` | 发布质量门禁 |

### 1.4 保留旧名作为 legacy alias

迁移期间不应破坏旧用户体验。

旧名字应保留为 alias：

```yaml
name: fish-trail
legacy_names:
  - context-router-skill
aliases:
  - fish-trail
  - context
```

---

## 2. 顶层产品结构

建议将胖鱼整体组织为五层。

```text
PEtFiSh / 胖鱼
├── fish-core        # 胖鱼核心调度与状态
├── fish-packs       # 可安装能力包
├── fish-skills      # 内部生命周期 skills
├── fish-trail       # 话题轨迹与上下文治理
└── fish-platforms   # 多平台适配层
```

### 2.1 分层说明

| 层级 | 作用 | 对应现有内容 |
|---|---|---|
| `fish-core` | 总控、状态、目录、安装、平台检测 | `petfish-companion`、`/petfish` |
| `fish-packs` | 面向用户安装的能力包 | `init`、`course`、`deploy`、`ppt` 等 |
| `fish-skills` | skill 生命周期内部能力 | companion 内部 10 个 skills |
| `fish-trail` | topic graph、active context、上下文防污染 | `context-router` 升级方向 |
| `fish-platforms` | OpenCode、Claude、Codex 等适配 | `platforms.json` 与安装脚本 |

---

## 3. Pack 重命名方案

### 3.1 当前 packs 到 fish packs 的映射

| 当前 alias | 当前 pack | 新 alias | 新 pack / skill 名 | 定位 |
|---|---|---|---|---|
| `init` | `project-initializer-skill` | `fish-init` | `fish-init` | 项目初始化向导 |
| `companion` | `petfish-companion-skill` | `fish-core` | `fish-core` | 胖鱼常驻伙伴与总控 |
| `course` | `opencode-course-skills-pack` | `fish-course` | `fish-course` | 课程开发能力包 |
| `testdocs` | `opencode-skill-pack-testcases-usage-docs` | `fish-testdocs` | `fish-testdocs` | 测试用例与使用文档 |
| `deploy` | `repo-deploy-ops-skill-pack` | `fish-deploy` | `fish-deploy` | 仓库部署与运维 |
| `petfish` | `petfish-style-skill` | `fish-style` | `fish-style` | 说人话 / 工程写作风格 |
| `ppt` | `opencode-ppt-skills` | `fish-slides` | `fish-slides` | PPT / 演示文稿制作 |
| `calibrate` | `anti-sycophancy-calibration-pack` | `fish-calibrate` | `fish-calibrate` | 反迎合与决策校准 |
| `context` | `context-router-skill` | `fish-trail` | `fish-trail` | 话题轨迹、上下文治理 |
| `trust` | 预留或缺失项 | `fish-trust` | `fish-trust` | skill 可信度 / 安全治理 |

### 3.2 关于 `fish-trust`

如果现有配置中已经出现 `trust` 自动安装映射，但 packs 列表中尚无明确对应 pack，则建议补充 `fish-trust`，而不是删除该能力。

理由：

1. 胖鱼本质上是 skill installer 与 skill governance 工具；
2. 安装、审计、推荐第三方 skills 时，需要独立的可信度评估能力；
3. `fish-trust` 可承载供应链安全、来源可信度、license 检查、恶意 skill 风险判断等功能。

---

## 4. 内置 Skills 重命名方案

当前 companion pack 中包含一组内部 skills，覆盖 skill 生命周期。建议统一改为以下命名。

| 当前 skill | 新 skill 名 | 功能定位 | 主要脚本 |
|---|---|---|---|
| `petfish-companion` | `fish-core` | 总控调度、状态感知、平台检测 | `catalog_query.py`、`check_installed.py`、`detect_platform.py` |
| `marketplace-connector` | `fish-market` | 跨市场搜索 skills 和 MCP server | `marketplace_search.py` |
| `repo-skill-miner` | `fish-mine` | 从仓库挖掘候选 skills | `mine_repo.py` |
| `skill-author` | `fish-author` | 创建新 skill 脚手架 | `generate_skill.py` |
| `skill-lint` | `fish-lint` | 格式与质量检查 | `lint_skill.py` |
| `skill-security-auditor` | `fish-audit` | 静态安全审计 | `audit_skill.py` |
| `quality-gate` | `fish-gate` | 发布门禁流水线 | `run_gate.py` |
| `skill-description-optimizer` | `fish-tune` | 优化 description 与触发描述 | `optimize_description.py` |
| `skill-trigger-evaluator` | `fish-eval` | 测试触发准确率 | `evaluate_triggers.py` |
| `skill-usage-tracker` | `fish-track` | 使用追踪、统计和反馈 | `track_usage.py` |

### 4.1 为什么用 `fish-tune` 而不是 `fish-optimize`

`optimize` 含义过宽，容易涵盖性能优化、代码优化、项目优化等含义。

`fish-tune` 更准确表达：

```text
对 skill description、触发边界、正负样例进行调优
```

---

## 5. fish-trail 体系

`fish-trail` 是胖鱼的新核心能力，应从原来的 `context-router` 升级而来。

### 5.1 fish-trail 的定位

```text
fish-trail 是胖鱼的话题轨迹管理器。
它通过 topic graph、topic card、decision log 和 active context 管理长期协作中的上下文。
```

一句话：

```text
fish-trail 负责让 Agent 知道当前任务属于哪个 topic、该加载哪些历史决策、哪些上下文不能混进来。
```

### 5.2 fish-trail 内部子能力

MVP 阶段建议只发布一个 skill：

```text
fish-trail
```

内部脚本拆分：

```text
scripts/
├── topic_detect.py
├── topic_route.py
├── topic_update.py
├── topic_report.py
├── topic_validate.py
└── topic_handoff.py
```

后续可拆成以下子能力：

| 子能力 | 名称 | 作用 |
|---|---|---|
| topic graph | `fish-trail-map` | 维护 `topic_graph.json` |
| active context | `fish-trail-route` | 生成 `active_context.md` |
| decision memory | `fish-trail-decision` | 维护决策日志 |
| pollution guard | `fish-trail-guard` | 检测上下文污染和不应混入的 topic |
| handoff | `fish-trail-handoff` | 生成新会话交接包 |

### 5.3 fish-trail 与 Graphify 的关系

fish-trail 借鉴 Graphify 的机制，但管理对象不同。

| Graphify | fish-trail |
|---|---|
| 项目文件图谱 | 话题图谱 |
| `graph.json` | `topic_graph.json` |
| `GRAPH_REPORT.md` | `TOPIC_REPORT.md` |
| 文件关系 | topic 关系 |
| 项目导航 | 上下文路由 |
| 先图谱后源文件 | 先 topic card 后历史上下文 |
| confidence tags | evidence level |
| stale graph | stale topic |

---

## 6. 命令体系重命名

当前用户入口是 `/petfish`。如果要全面进入 `fish-*` 命名体系，有两个方案。

---

### 6.1 方案 A：保留 `/petfish`，子命令改为 fish 风格

```bash
/petfish fish-status
/petfish fish-catalog
/petfish fish-suggest
/petfish fish-install <alias>
/petfish fish-detect
/petfish fish-search <keyword>
/petfish fish-mine <repo>
/petfish fish-author <name>
/petfish fish-lint [path]
/petfish fish-audit <path>
/petfish fish-gate <path>
/petfish fish-tune <path>
/petfish fish-eval <path>
/petfish fish-track
/petfish fish-trail
```

优点：

- 兼容现有 `/petfish` 品牌；
- 不需要新增顶层命令。

缺点：

- 命令偏长；
- `petfish fish-*` 存在重复感。

---

### 6.2 方案 B：新增 `/fish` 作为短命令

```bash
/fish status
/fish catalog
/fish suggest
/fish install <alias>
/fish detect
/fish search <keyword>
/fish mine <repo>
/fish author <name>
/fish lint [path]
/fish audit <path>
/fish gate <path>
/fish tune <path>
/fish eval <path>
/fish track
/fish trail
```

优点：

- 更自然；
- 更利于传播；
- 与 `fish-*` 命名体系一致。

缺点：

- 需要保留 `/petfish` 作为兼容别名；
- 需要迁移文档和用户习惯。

### 6.3 推荐方案

建议采用：

```text
正式新命令：/fish
兼容旧命令：/petfish
内部 skill 名：fish-*
pack alias：fish-*
```

---

## 7. Skill 生命周期流水线

胖鱼当前生命周期可整理为：

```text
Discover → Create → Validate → Optimize → Install → Track
```

重命名后，建议变成以下 fish pipeline：

```text
fish-search
  ↓
fish-mine
  ↓
fish-author
  ↓
fish-lint
  ↓
fish-audit
  ↓
fish-gate
  ↓
fish-tune
  ↓
fish-eval
  ↓
fish-install
  ↓
fish-track
```

### 7.1 生命周期阶段说明

| 阶段 | fish 模块 | 作用 |
|---|---|---|
| 发现 | `fish-search` / `fish-market` | 搜索外部 skills 和 MCP |
| 挖掘 | `fish-mine` | 从 repo 中挖掘可复用 skill |
| 创建 | `fish-author` | 创建新 skill |
| 格式检查 | `fish-lint` | 检查 `SKILL.md`、目录结构、metadata |
| 安全审计 | `fish-audit` | 检查脚本、权限、网络、凭据风险 |
| 发布门禁 | `fish-gate` | 综合 lint / audit / metadata，给出 PASS / FAIL |
| 触发调优 | `fish-tune` | 优化 description 和触发边界 |
| 触发评测 | `fish-eval` | 用 query set 测试触发准确率 |
| 安装 | `fish-install` | 跨平台安装 pack |
| 追踪 | `fish-track` | 记录使用、反馈和推荐 |

### 7.2 pipeline 示例

```bash
/fish search "ppt skill"
/fish mine https://github.com/example/repo
/fish author fish-slides-helper
/fish lint packs/fish-slides-helper
/fish audit packs/fish-slides-helper
/fish gate packs/fish-slides-helper
/fish tune packs/fish-slides-helper
/fish eval packs/fish-slides-helper
/fish install fish-slides-helper
/fish track
```

---

## 8. 自动安装 Profile 重命名

当前 profile 包括：

```text
minimal
course
code
ops
security
writing
skills-package
comprehensive
```

建议保持 profile 名称不变，但内部安装内容全部改为 fish packs。

| Profile | 自动安装 fish packs |
|---|---|
| `minimal` | `fish-style` |
| `course` | `fish-course`, `fish-style`, `fish-trail` |
| `code` | `fish-deploy`, `fish-style`, `fish-testdocs`, `fish-trail` |
| `ops` | `fish-deploy`, `fish-style`, `fish-trail` |
| `security` | `fish-deploy`, `fish-style`, `fish-testdocs`, `fish-audit`, `fish-trail` |
| `writing` | `fish-style`, `fish-slides`, `fish-calibrate` |
| `skills-package` | `fish-style`, `fish-testdocs`, `fish-core`, `fish-gate`, `fish-trail` |
| `comprehensive` | `fish-course`, `fish-deploy`, `fish-style`, `fish-slides`, `fish-testdocs`, `fish-calibrate`, `fish-trust`, `fish-trail` |

### 8.1 关于 fish-trail 的默认安装

建议除 `minimal` 外，大多数 profile 默认安装 `fish-trail`。

原因：

```text
fish-trail 不是某一类任务的工具，而是长期协作的上下文底座。
```

---

## 9. 仓库目录重组建议

### 9.1 目标目录结构

```text
SKILL_builder/
├── packs/
│   ├── fish-init/
│   ├── fish-core/
│   ├── fish-course/
│   ├── fish-testdocs/
│   ├── fish-deploy/
│   ├── fish-style/
│   ├── fish-slides/
│   ├── fish-calibrate/
│   ├── fish-trail/
│   └── fish-trust/
│
├── fish-internal/
│   ├── fish-market/
│   ├── fish-mine/
│   ├── fish-author/
│   ├── fish-lint/
│   ├── fish-audit/
│   ├── fish-gate/
│   ├── fish-tune/
│   ├── fish-eval/
│   └── fish-track/
│
├── platforms/
│   └── fish-platforms.json
│
├── installers/
│   ├── fish-install.ps1
│   ├── fish-install.sh
│   ├── fish-remote-install.ps1
│   └── fish-remote-install.sh
│
├── docs/
│   ├── fish-naming.md
│   ├── fish-pack-development.md
│   ├── fish-security-model.md
│   └── fish-trail-design.md
│
└── README.md
```

### 9.2 渐进式目录迁移

如果不想一次性大改目录，可以先做兼容层。

```text
packs/project-initializer-skill      → packs/fish-init
packs/petfish-companion-skill        → packs/fish-core
packs/opencode-course-skills-pack    → packs/fish-course
packs/context-router-skill           → packs/fish-trail
```

旧目录保留一段时间，新增 manifest 里的 `legacy_aliases`。

---

## 10. Pack Manifest 统一格式

每个 fish pack 建议使用统一 manifest。

```yaml
name: fish-trail
legacy_names:
  - context-router-skill
aliases:
  - fish-trail
  - context
type: project
category: context-governance
description: Topic graph and context routing pack for long-running AI-assisted projects.
provides:
  skills:
    - fish-trail
  commands:
    - /fish trail
    - /fish topic route
  artifacts:
    - .petfish/fish-trail/topic_graph.json
    - .petfish/fish-trail/active_context.md
requires:
  tools:
    - python>=3.10
    - uv
platforms:
  - opencode
  - claude
  - codex
  - cursor
  - antigravity
security:
  audit_required: true
  network_access: false
  writes_project_state: true
```

### 10.1 Manifest 字段说明

| 字段 | 说明 |
|---|---|
| `name` | 新 fish 名称 |
| `legacy_names` | 旧名称 |
| `aliases` | 可用于安装和调用的别名 |
| `type` | pack 类型 |
| `category` | 能力分类 |
| `description` | 简要说明 |
| `provides.skills` | 提供的 skills |
| `provides.commands` | 提供的命令 |
| `provides.artifacts` | 生成的项目产物 |
| `requires` | 环境依赖 |
| `platforms` | 支持平台 |
| `security` | 安全属性 |

---

## 11. 最终 fish 命名清单

### 11.1 用户可安装 Packs

```text
fish-init
fish-core
fish-course
fish-testdocs
fish-deploy
fish-style
fish-slides
fish-calibrate
fish-trail
fish-trust
```

### 11.2 内部生命周期 Skills

```text
fish-market
fish-search
fish-mine
fish-author
fish-lint
fish-audit
fish-gate
fish-tune
fish-eval
fish-track
fish-install
```

其中：

```text
fish-search 可以作为 fish-market 的用户命令名，二者也可以合并。
```

### 11.3 上下文与话题治理

```text
fish-trail
fish-trail-map
fish-trail-route
fish-trail-decision
fish-trail-guard
fish-trail-handoff
```

MVP 阶段只需要：

```text
fish-trail
```

后续再拆分内部能力。

### 11.4 平台与安装

```text
fish-platforms
fish-install
fish-upgrade
fish-detect
fish-registry
```

### 11.5 质量与安全

```text
fish-lint
fish-audit
fish-gate
fish-trust
fish-eval
fish-tune
```

---

## 12. 品牌化分层

为了便于对外讲清楚，建议用以下表达。

| 层级 | 名称 | 作用 |
|---|---|---|
| 胖鱼核心 | `fish-core` | 总控与状态 |
| 胖鱼入口 | `fish-init` | 项目初始化 |
| 胖鱼工具箱 | `fish-packs` | 各类项目能力包 |
| 胖鱼工厂 | `fish-author` / `fish-mine` | skill 生产 |
| 胖鱼质检 | `fish-lint` / `fish-audit` / `fish-gate` | skill 质量与安全 |
| 胖鱼调优 | `fish-tune` / `fish-eval` | 触发与效果优化 |
| 胖鱼记忆 | `fish-track` | 使用追踪 |
| 胖鱼轨迹 | `fish-trail` | topic graph 与上下文路由 |
| 胖鱼信任 | `fish-trust` | 可信 skill 与供应链治理 |

### 12.1 一句话品牌叙事

```text
fish-init 负责开局，
fish-core 负责陪伴，
fish-trail 负责记路，
fish-gate 负责把关，
fish-track 负责复盘。
```

---

## 13. 迁移策略

建议三阶段迁移，避免一次性破坏旧用户体验。

---

### Phase 1：双命名

保留旧 alias，新增 fish alias。

```text
init       → fish-init
companion  → fish-core
course     → fish-course
context    → fish-trail
```

安装命令同时支持：

```bash
./install.sh --pack context
./install.sh --pack fish-trail
```

### Phase 2：README 主推 fish 命名

README 主表只显示 fish 命名。

旧名字放到：

```text
Legacy aliases
```

示例：

```markdown
| New name | Legacy alias |
|---|---|
| fish-trail | context |
| fish-core | companion |
| fish-init | init |
```

### Phase 3：内部目录迁移

目录从旧名字迁移到 fish 名字，并在 manifest 中保留：

```yaml
legacy_names:
  - old-name
```

同时保留 compatibility shim：

```text
packs/context-router-skill/README.md
```

内容说明：

```text
This pack has moved to packs/fish-trail.
```

---

## 14. 最优先改名的三项

如果只先改最重要的三项，建议：

```text
petfish-companion → fish-core
context-router    → fish-trail
quality-gate      → fish-gate
```

原因：

1. `fish-core` 解决胖鱼核心身份混乱；
2. `fish-trail` 形成真正的产品亮点；
3. `fish-gate` 让质量门禁成为品牌级能力。

随后再逐步改：

```text
skill-author                 → fish-author
repo-skill-miner             → fish-mine
skill-security-auditor       → fish-audit
skill-description-optimizer  → fish-tune
skill-trigger-evaluator      → fish-eval
skill-usage-tracker          → fish-track
```

---

## 15. README 对外叙事建议

README 可改为如下表达。

```markdown
# PEtFiSh / 胖鱼

PEtFiSh is organized as fish-* packs.

## Core packs

- `fish-init` — Initialize AI-agent-friendly projects.
- `fish-core` — Manage installed packs, platforms, and project state.
- `fish-trail` — Maintain topic graph and active context to prevent context pollution.
- `fish-style` — Write in a clearer, less AI-slop style.

## Skill lifecycle

- `fish-search` — Search external skill and MCP marketplaces.
- `fish-mine` — Mine reusable skills from repositories.
- `fish-author` — Create new skills.
- `fish-lint` — Validate skill format and structure.
- `fish-audit` — Audit security risks.
- `fish-gate` — Run release quality gates.
- `fish-tune` — Tune skill descriptions.
- `fish-eval` — Evaluate trigger accuracy.
- `fish-track` — Track usage and feedback.
```

中文表述：

```markdown
胖鱼以 fish-* 能力包组织：

- `fish-init`：初始化 AI-agent 友好的项目；
- `fish-core`：管理已安装能力、平台和项目状态；
- `fish-trail`：维护话题轨迹，避免上下文污染；
- `fish-gate`：发布前质量门禁；
- `fish-track`：使用追踪和反馈复盘。
```

---

## 16. 推荐最终结构

### 16.1 对外核心能力

```text
fish-init     初始化项目
fish-core     胖鱼核心伙伴
fish-trail    话题轨迹与上下文治理
fish-style    说人话与工程写作风格
fish-course   课程开发
fish-deploy   仓库部署运维
fish-slides   PPT / 演示材料
fish-testdocs 测试用例与使用文档
fish-calibrate 反迎合与决策校准
fish-trust    可信 skill 与供应链治理
```

### 16.2 对内生命周期能力

```text
fish-search   搜索 skills / MCP
fish-market   外部市场连接
fish-mine     从 repo 挖掘 skills
fish-author   创建 skills
fish-lint     格式检查
fish-audit    安全审计
fish-gate     发布门禁
fish-tune     触发描述调优
fish-eval     触发准确率评测
fish-track    使用追踪
fish-install  安装与升级
```

---

## 17. 最终建议

胖鱼应从现在开始统一使用以下对外叙事：

```text
PEtFiSh is organized as fish-* packs.

fish-init     初始化项目
fish-core     胖鱼核心伙伴
fish-trail    话题轨迹与上下文治理
fish-mine     从仓库挖掘 skills
fish-author   创建 skills
fish-lint     格式质量检查
fish-audit    安全审计
fish-gate     发布门禁
fish-tune     触发描述优化
fish-eval     触发准确率评测
fish-track    使用追踪
```

这套命名会让胖鱼从“一个 skill installer 项目”变成一个更完整的品牌体系。

最终产品叙事可以是：

> 胖鱼不是简单安装 skills 的工具。  
> 它用 `fish-init` 开局，用 `fish-core` 管理能力，用 `fish-trail` 记住话题轨迹，用 `fish-gate` 把关质量，用 `fish-track` 复盘使用效果。  
> 它维护的是一个长期 AI-agent 友好的项目工作区。
