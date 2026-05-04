<p align="center">
  <img src="assets/petfish-logo.png" alt="胖鱼 PEtFiSh logo" width="360" />
</p>

# 胖鱼 PEtFiSh

**AI Worker's Companion — Skill lifecycle management for AI-assisted projects.**

Repo name: `SKILL_builder`
Product name: `胖鱼 PEtFiSh`

<p align="center">
  <img src="assets/petfish-icon-256.png" alt="胖鱼 PEtFiSh icon" width="128" />
</p>

---

## What is PEtFiSh? / 胖鱼是什么？

PEtFiSh is your AI coding companion. It manages the full lifecycle of AI skills — from discovery and creation to validation, publishing, and usage tracking. Supports 8 AI coding platforms with a single install command.

胖鱼是AI工作者的伙伴。从skill的发现、创建、验证、发布到使用追踪，管理AI skill的全生命周期。支持8个AI编程平台，一条命令完成skill安装。

```
┌─────────────────────────────────────────────────────┐
│  ><(((^>  胖鱼 PEtFiSh v0.4                        │
│                                                     │
│  Discover  → mine skills from any repo              │
│  Create    → author new skills from scratch          │
│  Validate  → lint, security audit, quality gate      │
│  Optimize  → improve descriptions & triggers         │
│  Install   → one command, 8 platforms                │
│  Track     → usage analytics & recommendations       │
│                                                     │
│  /petfish — your always-on companion                │
└─────────────────────────────────────────────────────┘
```

---

## Quick Start / 快速开始

**One command to get started** — install the initializer + companion globally, then use `/initproject` in any project.

一条命令开始使用 — 全局安装初始化器和伙伴命令，然后在任意项目中输入`/initproject`。

> The install script automatically resolves the **latest stable release** — no version pinning needed.
> 安装脚本自动获取**最新稳定release版本**，无需手动指定版本号。

```powershell
# Windows (PowerShell)
& ([scriptblock]::Create((irm https://raw.githubusercontent.com/kylecui/SKILL_builder/master/remote-install.ps1))) -Pack "init,companion"
```

```bash
# macOS / Linux / WSL
curl -fsSL https://raw.githubusercontent.com/kylecui/SKILL_builder/master/remote-install.sh | bash -s -- --pack init,companion
```

Then type `/initproject` — PEtFiSh will:
1. Ask your project type (code/course/ops/writing/comprehensive/...)
2. Create the project scaffold / 创建项目脚手架
3. Install matching skill packs automatically / 自动安装匹配的skill pack
4. Walk you through a setup wizard (each step skippable) / 引导完成配置向导（每步可跳过）

---

## Companion: /petfish / 伙伴命令

The `companion` pack installs the `/petfish` command — your always-on AI skill assistant with 14 subcommands.

`companion` pack安装`/petfish`命令 — 你的常驻AI skill助手，包含14个子命令。

### Core Commands / 核心命令

| Command / 命令 | Description / 描述 |
|----------------|-------------------|
| `/petfish` | Show installed skill status / 查看已装skill状态 |
| `/petfish catalog` | Browse all available skills / 浏览全量技能目录 |
| `/petfish suggest` | Recommend skills based on project structure / 基于项目特征推荐skill |
| `/petfish install <alias>` | Get install command for a pack / 获取安装命令 |
| `/petfish detect` | Detect current AI platform / 检测当前平台 |

### Discovery & Creation / 发现与创建

| Command / 命令 | Description / 描述 |
|----------------|-------------------|
| `/petfish search <keyword>` | Search skills across marketplaces / 跨市场搜索skill和MCP server |
| `/petfish mine <repo>` | Analyze repo for extractable skills / 从仓库挖掘候选skill |
| `/petfish create <name>` | Scaffold a new skill / 创建新skill |

### Validation & Quality / 验证与质量

| Command / 命令 | Description / 描述 |
|----------------|-------------------|
| `/petfish lint [path]` | Check skill format quality (100-point score) / 验证skill格式质量（100分制） |
| `/petfish audit <path>` | Security audit (0.0-1.0 risk score) / 安全审计（0.0-1.0风险评分） |
| `/petfish gate <path>` | Full publish gate: lint + security → PASS/FAIL / 完整发布门禁 |

### Optimization & Analytics / 优化与分析

| Command / 命令 | Description / 描述 |
|----------------|-------------------|
| `/petfish optimize <path>` | Analyze and improve skill descriptions / 分析并优化skill描述 |
| `/petfish eval <path>` | Test trigger accuracy with query sets / 测试触发准确率 |
| `/petfish stats` | View skill usage statistics / 查看使用统计 |

### Context-Aware Sensing / 上下文感知

The companion **senses** your conversation context and proactively recommends skills when it detects a capability gap. For example, if you start discussing deployment but don't have the `deploy` pack installed, it will suggest installing it. Each pack is recommended at most once per session to avoid interruption.

胖鱼会**感知**你的对话上下文，在检测到能力缺口时主动推荐skill。例如，当你开始讨论部署但尚未安装`deploy` pack时，它会建议安装。每个pack在每次会话中最多推荐一次，避免打扰。

---

## Companion Internal Skills / 内置Skill体系

The companion pack includes 10 internal skills covering the full skill lifecycle:

companion pack包含10个内置skill，覆盖skill全生命周期：

```
┌─────────────────────────────────────────────────────────┐
│  Skill Lifecycle Pipeline / Skill生命周期流水线          │
│                                                         │
│  mine → author → lint → audit → gate → optimize → eval  │
│    ↓       ↓       ↓      ↓       ↓        ↓       ↓   │
│  发现    创建    格式   安全    门禁     优化    评测   │
│                                                         │
│  + marketplace-connector (跨市场搜索)                    │
│  + skill-usage-tracker   (使用追踪)                      │
│  + petfish-companion     (总控调度)                      │
└─────────────────────────────────────────────────────────┘
```

| Skill | Purpose / 用途 | Script / 脚本 |
|-------|---------------|--------------|
| `petfish-companion` | Orchestration, sensing, routing / 总控调度与感知 | `catalog_query.py`, `check_installed.py`, `detect_platform.py` |
| `marketplace-connector` | Search across 6 sources / 跨6个来源搜索 | `marketplace_search.py` |
| `skill-author` | Scaffold new skills / 创建新skill脚手架 | `generate_skill.py` |
| `skill-lint` | Format & quality check (100-point) / 格式质量检查 | `lint_skill.py` |
| `repo-skill-miner` | Analyze repos for skill candidates / 从仓库挖掘skill | `mine_repo.py` |
| `skill-security-auditor` | Static security analysis / 静态安全分析 | `audit_skill.py` |
| `quality-gate` | Publish decision pipeline / 发布门禁流水线 | `run_gate.py` |
| `skill-description-optimizer` | Improve trigger accuracy / 优化触发准确率 | `optimize_description.py` |
| `skill-trigger-evaluator` | Test trigger precision/recall / 测试触发精度 | `evaluate_triggers.py` |
| `skill-usage-tracker` | Usage analytics & feedback / 使用分析与反馈 | `track_usage.py` |

### Skill Source Priority / Skill来源优先级

When searching for skills, PEtFiSh follows this priority chain:

搜索skill时，胖鱼按以下优先级链查找：

1. **PEtFiSh own repo** / 胖鱼自有仓库 (`packs/`) — highest quality, security audited / 质量最高，安全已审计
2. **Third-party marketplaces** / 三方市场 (SkillKit, Smithery, Glama, anthropics/skills) — community verified / 社区验证
3. **GitHub high-star repos** / GitHub高星仓库 (★ > 1000) — widely used / 广泛使用
4. **GitHub low-star repos** / GitHub低星仓库 — needs review / 需额外审查
5. **Auto-generate** / 自动生成 — created by `skill-author`, validated by `quality-gate` / 由skill-author创建，quality-gate验证

---

## Skill Packs / 技能包

| Alias | Pack | Contents / 内容 | Default / 默认 |
|-------|------|-----------------|---------------|
| `init` | project-initializer-skill | Initializer + wizard + `/initproject` / 初始化器+向导 | **Global / 全局** |
| `companion` | petfish-companion-skill | 10 internal skills + `/petfish` (14 subcommands) / 10个内置skill | **Global / 全局** |
| `course` | opencode-course-skills-pack | 15 skills, 10 commands, 8 agents / 课程开发全套 | Project / 项目级 |
| `testdocs` | opencode-skill-pack-testcases-usage-docs | Test case & doc generation / 测试用例与文档生成 | Project / 项目级 |
| `deploy` | repo-deploy-ops-skill-pack | CI/CD, deploy, ops automation / 部署与运维 | Project / 项目级 |
| `petfish` | petfish-style-skill | 说人话 — engineering writing style / 工程写作风格 | Project / 项目级 |
| `ppt` | opencode-ppt-skills | Slide design & presentation / PPT设计与制作 | Project / 项目级 |
| `calibrate` | anti-sycophancy-calibration-pack | 反迎合决策校准 — anti-sycophancy calibration for reviews / 评审校准 | Project / 项目级 |
| `context` | context-router-skill | 话题治理器 — topic governance, context isolation, contamination scoring / 上下文治理 | Project / 项目级 |

### Profile → Auto-Install Mapping / 项目类型→自动安装映射

When you use `/initproject`, PEtFiSh installs packs based on your project type:

使用`/initproject`时，胖鱼根据项目类型自动安装对应pack：

| Profile / 类型 | Auto-Installed Packs / 自动安装 |
|---------------|-------------------------------|
| minimal | petfish |
| course | course, petfish |
| code | deploy, petfish, testdocs |
| ops | deploy, petfish |
| security | deploy, petfish, testdocs |
| writing | petfish, ppt |
| skills-package | petfish, testdocs |
| comprehensive | course, deploy, petfish, ppt, testdocs, trust, context |

---

## Platform Support / 平台支持

PEtFiSh supports 8 AI coding platforms. Platform configuration is driven by `platforms.json` — the single source of truth for all path conventions and instructions translation.

胖鱼支持8个AI编程平台。平台配置由`platforms.json`驱动 — 所有路径约定和指令翻译的唯一数据源。

| Platform / 平台 | `--platform` | Project Skills | Instructions File | Auto-Detect |
|----------------|-------------|---------------|-------------------|-------------|
| OpenCode | `opencode` (default) | `.opencode/skills/` | `AGENTS.md` | `.opencode/`, `opencode.json` |
| Claude Code | `claude` | `.claude/skills/` | `CLAUDE.md` | `.claude/`, `CLAUDE.md` |
| Codex | `codex` | `.agents/skills/` | `AGENTS.md` | `.codex/` |
| Cursor | `cursor` | `.cursor/skills/` | `.cursor/rules/*.mdc` | `.cursor/`, `.cursorrules` |
| GitHub Copilot | `copilot` | `.github/skills/` | `.github/copilot-instructions.md` | `.github/copilot-instructions.md` |
| Windsurf | `windsurf` | `.windsurf/skills/` | `.windsurfrules` | `.windsurf/`, `.windsurfrules` |
| Antigravity | `antigravity` | `.agents/skills/` | `AGENTS.md` + `GEMINI.md` | `.agents/`, `GEMINI.md` |
| Universal | `universal` | `.agents/skills/` | `AGENTS.md` | (fallback) |

### Platform Groups / 平台组

Batch install across multiple platforms with a single command:

一条命令批量安装到多个平台：

| Group / 组 | Platforms / 平台 |
|------------|-----------------|
| `all` | opencode, claude, codex, cursor, copilot, windsurf, antigravity |
| `primary` | opencode, claude, codex |
| `ide` | cursor, copilot, windsurf |
| `cli` | opencode, claude, codex, antigravity |

**Auto-detection / 自动检测**: Use `--detect` to let PEtFiSh determine the platform from project markers.

使用`--detect`让胖鱼从项目标记自动判断平台。

---

## Install Commands / 安装命令

### Remote Install (no clone needed) / 远程安装（无需clone）

```powershell
# PowerShell
& ([scriptblock]::Create((irm https://raw.githubusercontent.com/kylecui/SKILL_builder/master/remote-install.ps1))) -Pack <alias> [-Target .] [-Platform opencode] [-Detect] [-Force] [-Global]
```

```bash
# Bash
curl -fsSL https://raw.githubusercontent.com/kylecui/SKILL_builder/master/remote-install.sh | bash -s -- --pack <alias> [--target .] [--platform opencode] [--detect] [--force] [--global]
```

### Local Install (cloned repo) / 本地安装（已clone仓库）

```powershell
.\install.ps1 -Pack <alias> [-Target path] [-Platform opencode|claude|codex|cursor|copilot|windsurf|antigravity|all|primary|ide|cli] [-Detect] [-Force] [-Global]
.\install.ps1 -List
```

```bash
./install.sh --pack <alias> [--target path] [--platform <platform|group>] [--detect] [--force] [--global]
./install.sh --list
```

### Private Repos / 私有仓库

```bash
curl -fsSL -H "Authorization: token $GITHUB_TOKEN" \
  https://raw.githubusercontent.com/kylecui/SKILL_builder/master/remote-install.sh \
  | GITHUB_TOKEN=$GITHUB_TOKEN bash -s -- --pack course
```

```powershell
& ([scriptblock]::Create((irm https://raw.githubusercontent.com/kylecui/SKILL_builder/master/remote-install.ps1))) -Pack course -GitHubToken $env:GITHUB_TOKEN
```

### Cross-Platform Examples / 跨平台示例

```bash
# Install for Claude Code / 安装到Claude Code
./install.sh --pack deploy --platform claude --target ~/my-project

# Install for all primary platforms at once / 批量安装到所有主要平台
./install.sh --pack petfish --platform primary --target ~/my-project

# Auto-detect platform and install / 自动检测平台并安装
./install.sh --pack course --detect --target ~/my-project
```

---

## Upgrade / 升级

Already have PEtFiSh installed? Re-run the same install command with `--force` to upgrade to the latest version. The installer automatically detects outdated packs and shows available updates.

已经安装了胖鱼？重新运行安装命令并加上`--force`即可升级到最新版本。安装器会自动检测过时的pack并提示可用更新。

```powershell
# PowerShell — upgrade all packs / 升级全部pack
& ([scriptblock]::Create((irm https://raw.githubusercontent.com/kylecui/SKILL_builder/master/remote-install.ps1))) -Pack all -Force
```

```bash
# Bash — upgrade all packs / 升级全部pack
curl -fsSL https://raw.githubusercontent.com/kylecui/SKILL_builder/master/remote-install.sh | bash -s -- --pack all --force
```

```bash
# Upgrade a single pack / 升级单个pack
curl -fsSL https://raw.githubusercontent.com/kylecui/SKILL_builder/master/remote-install.sh | bash -s -- --pack companion --force
```

**What happens without `--force` / 不加`--force`时的行为：**

- If a pack is already installed and up to date → skipped with `✓ pack is current` message
- If a newer version is available → shows `⬆ UPDATE: pack v0.1.0 → v0.2.0 (use --force to upgrade)`
- New packs that aren't installed yet → installed normally

- 已安装且版本相同 → 跳过，显示`✓ pack is current`
- 有新版本可用 → 显示`⬆ UPDATE: pack v0.1.0 → v0.2.0 (use --force to upgrade)`
- 尚未安装的新pack → 正常安装

---

## Global vs Project Install / 全局安装 vs 项目级安装

- **Global / 全局** (`--global`): Skills + commands installed to user-level directory. Available across all projects. The `init` and `companion` packs default to global.

  全局安装：skill和命令安装到用户级目录，所有项目可用。`init`和`companion` pack默认全局安装。

- **Project / 项目级** (default): Installed to target project's platform-specific directory with instructions merge, config merge, and registry tracking.

  项目级安装（默认）：安装到目标项目的平台特定目录，包括指令合并、配置合并和注册跟踪。

---

## Quality Gate Pipeline / 质量门禁流水线

Every skill must pass the quality gate before publishing to the PEtFiSh registry:

每个skill在发布到胖鱼仓库前必须通过质量门禁：

```
skill目录
  │
  ├─① Lint (skill-lint)
  │   └─ Score ≥ 80/100? → Continue or FAIL
  │
  ├─② Security Audit (skill-security-auditor)
  │   └─ Risk ≤ 0.5? No CRITICAL? → Continue or FAIL
  │
  ├─③ Metadata Validation
  │   └─ name, version, description valid? → Continue or FAIL
  │
  └─④ Decision / 决策
      ├─ ✅ PASS      → Publish allowed / 允许发布
      ├─ ⚠️ CONDITIONAL → Human review needed / 需人工确认
      └─ ❌ FAIL      → Must fix first / 必须先修复
```

Run the gate / 运行门禁：

```bash
# Single skill / 单个skill
uv run .opencode/skills/quality-gate/scripts/run_gate.py --path .opencode/skills/my-skill/

# All skills recursively / 递归扫描所有skill
uv run .opencode/skills/quality-gate/scripts/run_gate.py --path .opencode/skills/ --recursive
```

---

## Prerequisites / 前置条件

- **uv** (recommended / 推荐): Required for Python-based skills. Install from https://docs.astral.sh/uv/getting-started/installation/
- **python3**: Required for platform config parsing and instructions translation / 平台配置解析和指令翻译所需
- The installer warns if uv is not found / 安装器会在uv未安装时发出警告

---

## Adding a New Pack / 添加新Pack

1. Create a directory under `packs/` with your pack name / 在`packs/`下创建pack目录
2. Add `.opencode/` containing `skills/`, `commands/`, and/or `agents/` / 添加`.opencode/`目录
3. Add `pack-manifest.json` for metadata / 添加pack清单文件
4. Pack's `AGENTS.md` → marker-based merge into target project's instructions file / 标记合并到目标指令文件
5. Pack's `opencode.example.json` → deep-merged into target's `opencode.json` (OpenCode only) / 深度合并到目标配置
6. Add an alias in the install scripts and update `platforms.json` if needed / 在安装脚本中添加别名

Or use `/petfish create <name>` to scaffold a new skill interactively / 或使用`/petfish create <name>`交互式创建新skill。

---

## Repo Structure / 仓库结构

```
SKILL_builder/                          # 胖鱼 PEtFiSh repo
├── packs/
│   ├── project-initializer-skill/      ← init (global-default)
│   ├── petfish-companion-skill/        ← companion (global-default)
│   │   └── .opencode/skills/
│   │       ├── petfish-companion/      ← orchestration & sensing / 总控与感知
│   │       ├── marketplace-connector/  ← multi-source search / 跨源搜索
│   │       ├── skill-author/           ← skill scaffolding / skill创建
│   │       ├── skill-lint/             ← format validation / 格式验证
│   │       ├── repo-skill-miner/       ← repo analysis / 仓库分析
│   │       ├── skill-security-auditor/ ← security scanning / 安全扫描
│   │       ├── quality-gate/           ← publish pipeline / 发布流水线
│   │       ├── skill-description-optimizer/ ← description tuning / 描述优化
│   │       ├── skill-trigger-evaluator/    ← trigger testing / 触发测试
│   │       └── skill-usage-tracker/        ← usage analytics / 使用分析
│   ├── opencode-course-skills-pack/    ← course
│   ├── opencode-skill-pack-testcases-usage-docs/ ← testdocs
│   ├── repo-deploy-ops-skill-pack/     ← deploy
│   ├── petfish-style-skill/            ← petfish
│   └── opencode-ppt-skills/            ← ppt
├── platforms.json      ← Platform registry (single source of truth) / 平台注册表
├── install.ps1         ← Local PowerShell installer / 本地安装器
├── install.sh          ← Local Bash installer / 本地安装器
├── remote-install.ps1  ← Remote PowerShell installer / 远程安装器
├── remote-install.sh   ← Remote Bash installer / 远程安装器
└── README.md
```

---

## Version History / 版本历史

### v0.4 — Context Router + Session Management / 上下文治理 + 会话管理

- **v0.4.0**: Context-router pack — topic detection, contamination scoring, context isolation, 18 MCP tools
  - 上下文治理pack — 话题检测、污染评分、上下文隔离、18个MCP工具
- **v0.4.5–v0.4.9**: MCP schema fixes, platform-specific restart hints, CJK detection, trigger evaluation improvements
  - MCP配置修复、平台重启提示、CJK检测、触发评测改进
- **v0.4.10**: Topic-aware session management — 10 new MCP tools (28 total), 3-phase implementation
  - 话题感知会话管理 — 新增10个MCP工具（共28个），3阶段实现
  - Phase 1: SessionStore + session bind/get/list/resume / 会话存储+绑定/查询/列表/恢复
  - Phase 2: Boundary policy + cross-session resume / 边界策略+跨会话恢复
  - Phase 3: Activity query + multi-agent attribution + topic recommendations / 活动查询+多Agent归因+话题推荐
- **v0.4.11–v0.4.12**: Bug fixes — agent-install platform guidance, trigger extraction scoping, deploy_dirs false positives
  - Bug修复 — 安装文档平台指引、触发提取范围、deploy_dirs误报

### v0.3 — Quality & Platform Hardening / 质量与平台加固

- Anti-sycophancy calibration pack / 反迎合校准pack
- Style v4 AI slop detection / 风格v4 AI腔检测
- Release discipline — auto-resolve latest release tag / 发布纪律 — 自动获取最新release tag
- UTF-8 encoding fixes for PowerShell / PowerShell UTF-8编码修复
- Comma-separated multi-pack install / 逗号分隔多pack安装

### v0.2 — Skill Lifecycle Management / Skill全生命周期管理

- **Phase 1**: 8-platform adapter + companion skill with sensing/equip/govern capabilities
  - 8平台适配器 + companion skill（感知/装备/治理能力）
- **Phase 2**: Marketplace search + skill authoring + quality linting
  - 跨市场搜索 + skill创建 + 质量检查
- **Phase 3**: Repo mining + security audit + publish quality gate
  - 仓库挖掘 + 安全审计 + 发布质量门禁
- **Phase 4**: Description optimization + trigger evaluation + usage tracking
  - 描述优化 + 触发评测 + 使用追踪

### v0.1 — Skill Installer / Skill安装器

- Multi-pack installer with remote install support
  - 多pack安装器，支持远程安装
- 7 skill packs (course, deploy, testdocs, petfish, ppt, init, companion)
  - 7个skill pack

---

> **胖鱼 PEtFiSh** — AI工作者的伙伴。发现、创建、验证、优化、安装、追踪 — skill全生命周期，一个伙伴搞定。
>
> Your AI coding companion. Discover, create, validate, optimize, install, track — full skill lifecycle, one companion.
