# 我给 AI 编程助手写了个"技能管家"

> TL;DR: 胖鱼 PEtFiSh 是一个 AI Skill 生命周期管理工具。一条命令安装，支持 8 个 AI 编程平台，内置质量门禁和安全审计。开源，免费，欢迎 PR。

---

## 起因

我日常用好几个 AI 编程工具——OpenCode、Claude Code、Cursor，偶尔还用 Copilot。

每个工具都有自己的"规则文件"格式：Cursor 用 `.cursorrules` 和 `.mdc`，Claude Code 用 `CLAUDE.md`，OpenCode 用 `AGENTS.md`，Copilot 用 `.github/copilot-instructions.md`……

同一套规则，我要维护好几个版本。改了一处，其他地方忘了同步，AI 在不同平台表现不一致。

更头疼的是——我写了一堆 skill（给 AI 的结构化指令），但完全不知道：

- 这些 skill 的触发准确率是多少？
- 里面有没有安全问题（比如不小心写了 `subprocess.call(shell=True)`）？
- 哪些 skill 其实从来没被触发过？

于是我搞了胖鱼。

---

## 胖鱼是什么

**胖鱼 PEtFiSh**（谐音"朋友"）是一个 AI Skill 的全生命周期管理工具：

```
发现 → 创建 → 检查 → 安全审计 → 发布门禁 → 优化 → 追踪
mine → author → lint → audit → gate → optimize → track
```

### 核心特性

**1. 一套 skill，8 个平台**

写一次 `SKILL.md`，胖鱼自动翻译成各平台格式并安装到正确路径：

| 平台 | Skill目录 | 指令文件 |
|---|---|---|
| OpenCode | `.opencode/skills/` | `AGENTS.md` |
| Claude Code | `.claude/skills/` | `CLAUDE.md` |
| Cursor | `.cursor/skills/` | `.cursor/rules/*.mdc` |
| Copilot | `.github/skills/` | `.github/copilot-instructions.md` |
| Windsurf | `.windsurf/skills/` | `.windsurfrules` |
| Codex | `.agents/skills/` | `AGENTS.md` |
| Antigravity | `.agents/skills/` | `AGENTS.md` + `GEMINI.md` |
| Universal | `.agents/skills/` | `AGENTS.md` |

**2. 质量门禁**

skill 也是代码，应该有 CI：

- **Lint**：100 分制，检查结构、元数据、内容质量、安全模式
- **Security Audit**：0.0-1.0 风险评分，检测 shell 注入、硬编码凭证、危险网络调用
- **Quality Gate**：编排 lint + audit，给出 PASS / CONDITIONAL / FAIL

```bash
# 跑一个 skill 的完整门禁
uv run .opencode/skills/quality-gate/scripts/run_gate.py --path .opencode/skills/my-skill/
```

**3. 上下文感知**

胖鱼会"听"你和 AI 的对话。当你开始讨论部署但没装 deploy pack，它会提醒一次——不多不少。

**4. trustskills 治理引擎**

不是看 skill 的文案"像不像安全"，而是分析实际代码行为：

- 6 个风险维度（shell、network、file_write、sensitive_data、script_risk、persistence）
- 4 条红线规则（subprocess+network combo、敏感路径、sudo without approval、subprocess+os combo）
- 5 级治理动作（allow → allow_with_ask → sandbox_required → manual_review_required → deny）

---

## 怎么用

**30 秒上手：**

```bash
# macOS / Linux / WSL
curl -fsSL https://raw.githubusercontent.com/kylecui/petfish.ai/master/remote-install.sh | bash -s -- --pack init,companion

# Windows PowerShell
& ([scriptblock]::Create((irm https://raw.githubusercontent.com/kylecui/petfish.ai/master/remote-install.ps1))) -Pack "init,companion"
```

> 安装脚本自动获取最新稳定release版本，无需手动指定版本号。

装完后输入 `/initproject`，胖鱼会问你项目类型，然后自动装上匹配的 skill pack。

**日常使用 `/petfish` 命令：**

```
/petfish              → 查看已装 skill 状态
/petfish catalog      → 浏览全量技能目录
/petfish suggest      → 基于项目结构推荐 skill
/petfish lint [path]  → 质量打分
/petfish audit <path> → 安全审计
/petfish gate <path>  → 完整发布门禁
/petfish search <kw>  → 跨市场搜索 skill
/petfish mine <repo>  → 从仓库挖掘候选 skill
/petfish create <n>   → 创建新 skill
```

---

## 8 个 Skill Pack

| Alias | 干嘛的 | Skills数 |
|---|---|---:|
| `init` | 项目初始化向导 | 1 |
| `companion` | 胖鱼本体，10 个管理类 skill | 10 |
| `course` | 课程开发全套 | 15 |
| `deploy` | 部署与运维 | 7 |
| `testdocs` | 测试用例与文档生成 | 2 |
| `petfish` | 工程写作风格（"说人话"） | 1 |
| `ppt` | PPT 设计 | 2 |
| `trust` | skill 可信度治理 | 1 |

---

## 技术选型

- **Python 3.9+**（脚本层，零外部依赖）
- **PowerShell + Bash** 双版本安装器
- **platforms.json** 单一数据源驱动 8 平台适配
- **pack-manifest.json** 统一 schema
- **marker-based merge** 避免覆盖用户已有指令
- **trustskills** 外部引擎（Python ≥ 3.12, pydantic + pyyaml）

---

## 现状与计划

当前版本 **v0.2**，在 `dev` 分支。

已完成：
- 8 平台适配器
- 10 个 companion 内置 skill
- 质量门禁流水线
- trustskills 治理引擎集成
- 远程一键安装（PowerShell + Bash）

后续方向：
- 更多三方市场对接（SkillKit, Smithery, Glama）
- skill 自动生成 + 自动推送到胖鱼仓库
- 更完善的触发准确率评测
- 社区贡献的 skill pack

---

## 链接

- **GitHub**: https://github.com/kylecui/petfish.ai
- **安装**: `curl -fsSL https://raw.githubusercontent.com/kylecui/petfish.ai/master/remote-install.sh | bash -s -- --pack init,companion`
- **License**: 开源

欢迎 Star ⭐，更欢迎 PR。

如果你也受够了在多个 AI 工具之间手动同步规则，试试胖鱼。

---

*><(((^> 胖鱼 PEtFiSh — AI Worker's Companion*
