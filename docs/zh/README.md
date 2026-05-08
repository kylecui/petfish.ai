<p align="center">
  <img src="../../assets/petfish-logo.png" alt="胖鱼 PEtFiSh logo" width="360" />
</p>

# 胖鱼 PEtFiSh

**你的AI伙伴**

[English](../../README.md)

<p align="center">
  <img src="../../assets/petfish-icon-256.png" alt="胖鱼 PEtFiSh icon" width="128" />
</p>

---

## 胖鱼是什么

从项目第一行代码到最终交付，胖鱼始终相伴。不是你想起来才调用的工具集，是每一轮交互都参与的AI伙伴。

```
┌─────────────────────────────────────────────────────┐
│  ><(((^>  胖鱼 PEtFiSh v0.8                        │
│                                                     │
│  常伴  每一轮交互都在                                │
│  守护  感知缺口、守护上下文、阻断污染                │
│  可信  Lint + 审计 + 红线 = 验证出的信任             │
│  秉正  不迎合、标准不降格                            │
│                                                     │
│  /petfish — 你的常驻伙伴                             │
└─────────────────────────────────────────────────────┘
```

支持8个AI编程平台，一条命令完成安装。

---

## 快速开始

```bash
# macOS / Linux / WSL
curl -fsSL https://raw.githubusercontent.com/kylecui/petfish.ai/master/remote-install.sh \
  | bash -s -- --pack init,companion --detect
```

```powershell
# Windows PowerShell
& ([scriptblock]::Create((irm https://raw.githubusercontent.com/kylecui/petfish.ai/master/remote-install.ps1))) -Pack "init,companion" -Detect
```

装完输入 `/initproject`——胖鱼问你项目类型，自动装上匹配的能力包。

> 安装脚本自动获取最新稳定release，不用指定版本号。

---

## 四个承诺

### 常伴 — 每一轮交互都在

Companion Gateway在每条消息前自动执行话题检测和能力感知。不需要你主动调用。从`/initproject`那一刻起，胖鱼就是你工作流的一部分。

### 守护 — 在你掉坑之前拦住

三层感知模型：关键词白名单匹配已知领域 → 意图级缺口检测 → 无缺口静默通过。上下文污染超过60分？主动拦截。每个领域每session最多提醒一次，不打扰。

### 可信 — 信任是验证出来的

每个Skill都过质量门禁：Lint 100分制打分、安全审计0.0–1.0风险评分、四条红线命中即deny。TrustSkills引擎六维风险评估、五级动作裁决。信任不是宣称的，是审计出来的。

### 秉正 — 标准不因便利而降格

反迎合校准：先中性化问题再给结论，至少补一个反方。质量门禁不放水，红线命中即deny。推你往更高标准走。

---

## /petfish 命令

| 命令 | 说明 |
|------|------|
| `/petfish` | 查看已装skill状态 |
| `/petfish catalog` | 浏览全量技能目录 |
| `/petfish suggest` | 基于项目特征推荐skill |
| `/petfish install <alias>` | 获取安装命令 |
| `/petfish search <keyword>` | 跨市场搜索skill和MCP server |
| `/petfish create <name>` | 创建新skill |
| `/petfish mine <repo>` | 从仓库挖掘候选skill |
| `/petfish lint [path]` | 验证skill格式质量（100分制） |
| `/petfish audit <path>` | 安全审计（0.0-1.0风险评分） |
| `/petfish gate <path>` | 完整发布门禁 |
| `/petfish optimize <path>` | 分析并优化skill描述 |
| `/petfish eval <path>` | 测试触发准确率 |
| `/petfish stats` | 查看使用统计 |
| `/petfish detect` | 检测当前平台 |

---

## 10个能力包

| 别名 | 定位 | 规模 |
|------|------|------|
| `companion` | 胖鱼本体——常伴核心 + 生命周期管理 | 10 skills, 1 cmd |
| `context` | 话题治理器——守护核心 | 1 skill, 31 MCP |
| `calibrate` | 反迎合校准——秉正核心 | 1 skill |
| `trust` | Skill可信度治理——可信核心 | 1 skill |
| `init` | 项目初始化向导 | 1 skill, 1 cmd |
| `course` | 课程开发全套 | 15 skills, 10 cmds, 8 agents |
| `deploy` | 部署与运维 | 7 skills |
| `petfish` | 工程写作风格 | 1 skill |
| `testdocs` | 测试用例与文档 | 2 skills |
| `ppt` | PPT设计 | 2 skills |

---

## 平台支持

| 平台 | Skills目录 | 指令文件 |
|------|-----------|----------|
| OpenCode | `.opencode/skills/` | `AGENTS.md` |
| Claude Code | `.claude/skills/` | `CLAUDE.md` |
| Codex | `.agents/skills/` | `AGENTS.md` |
| Cursor | `.cursor/skills/` | `.cursor/rules/*.mdc` |
| GitHub Copilot | `.github/skills/` | `copilot-instructions.md` |
| Windsurf | `.windsurf/skills/` | `.windsurfrules` |
| Antigravity | `.agents/skills/` | `AGENTS.md` + `GEMINI.md` |
| Universal | `.agents/skills/` | `AGENTS.md` |

用 `--detect` 自动检测平台，或 `--platform <name>` 手动指定。

---

## 升级

重跑安装命令加 `--force`：

```bash
curl -fsSL https://raw.githubusercontent.com/kylecui/petfish.ai/master/remote-install.sh \
  | bash -s -- --pack all --force
```

或者让AI帮你：

```
Upgrade PEtFiSh by following: https://raw.githubusercontent.com/kylecui/petfish.ai/master/docs/agent-upgrade.md
```

---

## 环境要求

- **`uv`** — 所有带外部依赖的Python skill、MCP server和脚本都通过uv管理虚拟环境。MCP server用 `uv run` 启动，独立脚本用PEP 723 inline metadata或pack级 `pyproject.toml` 声明依赖。项目中不使用 `pip install`。安装器在uv未安装时会发出警告。
- `python3` — 安装器中仅用于stdlib级JSON解析和指令文件翻译（无需虚拟环境）

---

## 更多文档

- [安装指南](petfish-install-prompt.md)
- [Companion Gateway 技术文档](companion-gateway.md)
- [网站](https://petfish.ai)

---

## 版本历史

### v0.8 — 多平台生成 & Agent纪律

- **v0.8.1**: 通用agent纪律（跨仓库保护、网络重试）；完整ops项目模板（11段）；code项目经验沉淀（Development Gotchas, Architecture Decisions）；部署skill参考文档（私有仓库访问、本地补丁管理）。关闭 #66, #67, #68, #69。
- **v0.8.0**: 多平台指令文件生成（#63）——`detect_all_platforms()`、token受限平台内容压缩、Claude Code hook脚本、uv优先Python策略。

### v0.7 — 稳定性 & Pack版本化

- **v0.7.2**: 修复#57根因（`grep -qF`替换`echo | grep`）；修复#65（topic_detector.py缺失8条QA双语术语）。
- **v0.7.1**: 修复#57 legacy名称识别；fish-trail和companion升级至1.0.0（#64）；修复AGENTS.md标记损坏；更新全部4个安装脚本。

### v0.6 — Companion Gateway

- **v0.6.4**: 网站和文档双语化，归档过时v0.2文档
- **v0.6.3**: 伙伴叙事重塑，修复#57 --force升级bug
- **v0.6.2**: 修复companion pack技能感知、安装器去重、catalog回退、universal平台检测
- **v0.6.1**: 修复topic_graph持久化、validate schema对齐、意图感知技能推荐
- **v0.6.0**: Companion Gateway——每条消息自动话题检测 + 三层能力感知 + 开发者调试模式

### v0.5 — Fish Trail

- **v0.5.0–v0.5.4**: 仓库重命名petfish.ai，fish-trail pack（31个MCP工具），话题路由/报告/验证脚本

### v0.4 — 上下文治理

- **v0.4.0–v0.4.12**: 上下文治理pack，话题感知会话管理（31个MCP工具），bug修复

### v0.3 — 质量加固

- 反迎合校准pack，AI腔检测，发布纪律，PowerShell UTF-8修复

### v0.2 — Skill生命周期

- 8平台适配器，跨市场搜索，安全审计，发布质量门禁

### v0.1 — Skill安装器

- 多pack安装器，7个skill pack

---

> **胖鱼 PEtFiSh** — 你的AI伙伴。从init到交付，胖鱼始终相伴。
