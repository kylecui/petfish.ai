# 胖鱼 PEtFiSh 技术白皮书

> v0.2 | 2026-05

---

## A. 问题与定位

OpenCode、Claude Code、Cursor、Copilot、Windsurf、Codex、Antigravity——7个AI编程平台，每个都有自己的skill格式、路径约定和配置文件。

这导致三个工程问题：

1. **碎片化**：同一组织的skill要为不同平台手工维护多份副本
2. **无治理**：skill从"某人写了个SKILL.md"到"进入生产项目"之间，没有格式检查、安全审计、发布门禁
3. **无追踪**：没人知道哪些skill被真正使用、触发准确率多少、哪些已过时

胖鱼在skill层做统一管理：一套skill多平台安装，一套流水线从创建到发布全覆盖。不替代任何AI平台。

---

## B. 架构总览

```
┌──────────────────────────────────────────────────────────┐
│                    用户 / CI / CD                          │
│                                                          │
│   /petfish (14 subcommands)    install.ps1 / install.sh  │
│   ─────────────────────────    ─────────────────────────  │
│                    │                      │               │
│            ┌───────┴───────┐      ┌───────┴───────┐      │
│            │  Companion    │      │   Installer   │      │
│            │  (10 skills)  │      │   (4 scripts) │      │
│            └───────┬───────┘      └───────┬───────┘      │
│                    │                      │               │
│            ┌───────┴──────────────────────┴───────┐      │
│            │         Pack Layer (8 packs)          │      │
│            │  pack-manifest.json 统一schema        │      │
│            └───────────────────┬──────────────────┘      │
│                                │                          │
│            ┌───────────────────┴──────────────────┐      │
│            │     Platform Adapter Layer            │      │
│            │     platforms.json (8 platforms)       │      │
│            │     路径映射 + 指令翻译 + 配置合并     │      │
│            └──────────────────────────────────────┘      │
└──────────────────────────────────────────────────────────┘
```

核心分层：

| 层 | 职责 | 关键文件 |
|---|---|---|
| 用户接口层 | `/petfish` 14个子命令 + 4个install脚本 | `petfish.md`, `install.ps1/sh`, `remote-install.ps1/sh` |
| Companion层 | 10个内置skill，覆盖skill全生命周期 | `packs/petfish-companion-skill/.opencode/skills/` |
| Pack层 | 8个skill pack，按领域组织 | `packs/*/pack-manifest.json` |
| 平台适配层 | 8平台路径映射、指令翻译、配置合并 | `platforms.json` |

---

## C. 平台适配层

### 核心数据源：platforms.json

`platforms.json`是平台适配的唯一数据源。每个平台定义：

```json
{
  "opencode": {
    "display_name": "OpenCode",
    "project": {
      "skills_dir": ".opencode/skills",
      "commands_dir": ".opencode/commands",
      "agents_dir": ".opencode/agents",
      "config_file": "opencode.json",
      "instructions_file": "AGENTS.md"
    },
    "global": { ... },
    "skill_format": "SKILL.md",
    "detect_markers": [".opencode", "opencode.json"],
    "instructions_merge_strategy": "marker_based"
  }
}
```

### 8平台路径映射

| 平台 | Skills目录 | 指令文件 | 检测标记 |
|---|---|---|---|
| OpenCode | `.opencode/skills/` | `AGENTS.md` | `.opencode/`, `opencode.json` |
| Claude Code | `.claude/skills/` | `CLAUDE.md` | `.claude/`, `CLAUDE.md` |
| Codex | `.agents/skills/` | `AGENTS.md` | `.codex/` |
| Cursor | `.cursor/skills/` | `.cursor/rules/*.mdc` | `.cursor/`, `.cursorrules` |
| GitHub Copilot | `.github/skills/` | `.github/copilot-instructions.md` | `.github/copilot-instructions.md` |
| Windsurf | `.windsurf/skills/` | `.windsurfrules` | `.windsurf/`, `.windsurfrules` |
| Antigravity | `.agents/skills/` | `AGENTS.md` + `GEMINI.md` | `.agents/`, `GEMINI.md` |
| Universal | `.agents/skills/` | `AGENTS.md` | (fallback) |

### 指令翻译机制

不同平台的指令文件格式不同，胖鱼通过三种翻译方法处理：

| 方法 | 适用平台 | 行为 |
|---|---|---|
| `marker_based` | OpenCode, Codex, Copilot, Windsurf, Antigravity, Universal | 用`<!-- BEGIN/END pack -->`标记合并，不覆盖用户已有内容 |
| `rename_with_header` | Claude Code, Copilot, Windsurf | 复制AGENTS.md内容，必要时加平台特定头部 |
| `wrap_as_mdc` | Cursor | 将AGENTS.md内容包装为`.mdc`前置元数据格式 |

### 平台组

支持批量安装：

| 组 | 包含平台 |
|---|---|
| `all` | opencode, claude, codex, cursor, copilot, windsurf, antigravity |
| `primary` | opencode, claude, codex |
| `ide` | cursor, copilot, windsurf |
| `cli` | opencode, claude, codex, antigravity |

### 自动检测

安装时传入`--detect`，胖鱼按`detect_markers`逐一匹配目标项目中的文件/目录，自动判断当前平台。

---

## D. Pack体系

### pack-manifest.json统一schema

每个pack必须包含`pack-manifest.json`，遵循统一schema：

```json
{
  "name": "petfish-companion-skill",
  "version": "0.2.0",
  "description": "AI Worker's Companion...",
  "compatibility": "opencode, claude, codex, cursor, copilot, windsurf, antigravity, universal",
  "skill_count": 10,
  "command_count": 1,
  "agent_count": 0,
  "skills": ["petfish-companion", "marketplace-connector", "skill-author", ...],
  "commands": ["petfish"],
  "agents": []
}
```

必填字段：`name`, `version`, `description`, `compatibility`, `skill_count`, `command_count`, `agent_count`, `skills`, `commands`, `agents`。

### 8个Pack的定位

| Pack | Alias | 定位 | Skills | Cmds | Agents |
|---|---|---|---:|---:|---:|
| project-initializer-skill | `init` | 项目初始化向导 | 1 | 1 | 0 |
| petfish-companion-skill | `companion` | skill生命周期管理内核 | 10 | 1 | 0 |
| opencode-course-skills-pack | `course` | 课程开发全套 | 15 | 10 | 8 |
| repo-deploy-ops-skill-pack | `deploy` | 部署与运维 | 7 | 0 | 0 |
| opencode-skill-pack-testcases-usage-docs | `testdocs` | 测试用例与文档生成 | 2 | 0 | 0 |
| petfish-style-skill | `petfish` | 工程写作风格 | 1 | 0 | 0 |
| opencode-ppt-skills | `ppt` | PPT设计与制作 | 2 | 0 | 0 |
| trustskills-governance-pack | `trust` | skill可信度治理 | 1 | 0 | 0 |

### 项目类型→自动安装映射

`/initproject`根据项目类型自动选择pack组合：

| 类型 | 自动安装 |
|---|---|
| minimal | petfish |
| course | course, petfish |
| code | deploy, petfish, testdocs |
| ops | deploy, petfish |
| security | deploy, petfish, testdocs |
| writing | petfish, ppt |
| skills-package | petfish, testdocs |
| comprehensive | course, deploy, petfish, ppt, testdocs |

---

## E. Companion内核：10个内置Skill

### 生命周期流水线

```
mine → author → lint → audit → gate → optimize → eval
  ↓       ↓       ↓      ↓       ↓        ↓       ↓
发现    创建    格式   安全    门禁     优化    评测

+ marketplace-connector (跨市场搜索)
+ skill-usage-tracker   (使用追踪)
+ petfish-companion     (总控调度)
```

### 各Skill详解

| Skill | 脚本 | 输入 | 输出 | 核心逻辑 |
|---|---|---|---|---|
| **petfish-companion** | `catalog_query.py`, `check_installed.py`, `detect_platform.py` | 用户命令 | 路由到对应skill | 动态读取`packs/*/pack-manifest.json`，运行时发现所有pack |
| **marketplace-connector** | `marketplace_search.py` | 关键词 | 跨源搜索结果 | 对接6个来源：胖鱼仓库、SkillKit、Smithery、Glama、anthropics/skills、GitHub |
| **skill-author** | `generate_skill.py` | skill名称+描述 | 完整skill目录 | 生成SKILL.md + scripts/ + references/ 脚手架 |
| **skill-lint** | `lint_skill.py` | skill目录 | 100分制评分+findings | 40+规则，覆盖结构、前置元数据、内容质量、安全模式 |
| **repo-skill-miner** | `mine_repo.py` | GitHub仓库 | 候选skill列表 | 分析仓库结构、README、代码模式，提取可skill化的模块 |
| **skill-security-auditor** | `audit_skill.py` | skill目录 | 0.0-1.0风险评分 | 5级severity，检测shell注入、硬编码凭证、网络访问、eval/exec |
| **quality-gate** | `run_gate.py` | skill目录 | PASS/CONDITIONAL/FAIL | 编排lint+security audit，通过`find_sibling_script()`发现同级skill脚本 |
| **skill-description-optimizer** | `optimize_description.py` | skill目录 | 优化建议 | 分析description的触发准确率、覆盖面、歧义度 |
| **skill-trigger-evaluator** | `evaluate_triggers.py` | skill+测试集 | precision/recall | 用query集合测试skill触发条件的准确率与召回率 |
| **skill-usage-tracker** | `track_usage.py` | 使用事件 | 统计报告 | JSON schema记录使用频率、反馈评分、推荐衰减 |

### Catalog动态加载

`catalog_query.py`不使用硬编码的pack列表。它通过`_find_packs_root()`从脚本位置向上查找`packs/`目录，然后遍历所有子目录的`pack-manifest.json`：

```python
def _find_packs_root():
    """Walk up from script location to find packs/ directory."""
    current = Path(__file__).resolve().parent
    for _ in range(10):
        candidate = current / "packs"
        if candidate.is_dir():
            return candidate
        current = current.parent
    return None
```

新pack只需放入`packs/<name>/pack-manifest.json`，不需要修改任何代码。

---

## F. 质量门禁体系

### 三级流水线

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
  └─④ Decision
      ├─ ✅ PASS       → 允许发布
      ├─ ⚠️ CONDITIONAL → 需人工确认
      └─ ❌ FAIL       → 必须先修复
```

### Lint评分规则 (100分制)

起始100分，按finding扣分：

| Severity | 每项扣分 | 含义 |
|---|---:|---|
| error | -10 | 结构缺陷、必填字段缺失 |
| warn | -5 | 质量问题、最佳实践违反 |
| info | -1 | 建议性改进 |

最低0分。主要检查类别：

| 规则前缀 | 检查内容 |
|---|---|
| ST0xx | 结构完整性 — SKILL.md存在、scripts/目录、references/目录 |
| FM0xx | 前置元数据 — name, description, version, author, triggers |
| CT0xx | 内容质量 — 长度、标题层级、trigger提示、与references的重叠度 |
| SC0xx | 安全模式 — subprocess shell=True、eval/exec、硬编码凭证、网络访问 |
| PY0xx | Python脚本质量 — 语法正确性(py_compile)、shebang、PEP inline metadata |

### Security Audit评分

风险分 = Σ(finding severity weight)，归一化到0.0-1.0：

| Severity | 权重 |
|---|---:|
| info | 0.0 |
| low | 0.1 |
| medium | 0.3 |
| high | 0.6 |
| critical | 1.0 |

检测类别：

| 类别 | 检测内容 |
|---|---|
| code_execution | `subprocess.call(shell=True)`, `eval()`, `exec()`, `os.system()` |
| credentials | 硬编码API key、password、token、secret |
| network | `urllib`, `requests`, `httpx`, `curl` 调用 |
| file_system | 敏感路径读写 |
| markdown_injection | SKILL.md中的可执行代码块(bash/python/powershell) |

### Quality Gate编排逻辑

`run_gate.py`不直接包含lint和audit逻辑，而是通过`find_sibling_script()`动态发现同级skill的脚本：

```python
def find_sibling_script(script_name: str) -> str | None:
    this_dir = Path(__file__).resolve().parent      # quality-gate/scripts/
    skills_dir = this_dir.parent.parent              # skills/
    parts = script_name.split("/")
    candidate = skills_dir / parts[0] / "scripts" / parts[1]
    return str(candidate) if candidate.exists() else None
```

这意味着：
- lint脚本更新后，gate自动使用最新版本
- 可以独立运行lint或audit，也可以通过gate统一编排
- 如果lint脚本不存在，gate会fallback到内置基本检查

---

## G. TrustSkills治理引擎

`trustskills-governance-pack`封装了外部`trustskills` Python引擎，提供基于行为分析（而非文案分析）的skill可信度评估。

### 六个风险维度

| 维度 | 权重 | 含义 |
|---|---:|---|
| `shell` | 0.25 | shell执行、子进程调用、高权限工具声明 |
| `network` | 0.25 | 网络访问、外部域名、远程通信范围 |
| `file_write` | 0.15 | 文件写入能力、批量写路径、宽范围写入 |
| `sensitive_data` | 0.15 | 接触密钥、凭证、敏感系统路径、隐私数据 |
| `script_risk` | 0.10 | 脚本内的file IO、subprocess、network等行为证据 |
| `persistence` | 0.10 | 持久化副作用，如服务安装、长期状态写入、配置驻留 |

### 五级治理动作

| 级别 | 阈值 | 含义 |
|---|---:|---|
| `allow` | ≥ 0.00 | 直接放行 |
| `allow_with_ask` | ≥ 0.15 | 允许执行，先征得用户确认 |
| `sandbox_required` | ≥ 0.35 | 需要沙箱隔离执行 |
| `manual_review_required` | ≥ 0.55 | 必须进入人工复核 |
| `deny` | 红线命中 | 硬拒绝，不走阈值计算 |

### 四条红线规则

| 红线 | 含义 |
|---|---|
| `subprocess-network-combo` | script同时具备subprocess与network，可能形成download-and-exec路径 |
| `dangerous-system-paths` | 读写`/etc/passwd`、`/etc/shadow`、`/root/.ssh`、`~/.ssh/id_*`等敏感路径 |
| `sudo-without-approval` | 声明sudo/su，但没有显式approval_required |
| `subprocess-os-combo` | script同时具备subprocess与os级操作，表明任意命令/高破坏面行为 |

命中任何一条红线，治理结果直接进入`deny`，不走分数阈值。

### 策略自定义

通过`--policy`传入YAML文件，可覆盖：

- `weights` — 调整各维度权重
- `thresholds` — 调整各级别触发阈值
- `disabled_redlines` — 在受控环境中禁用特定红线
- `disabled_indicators` — 禁用特定指标
- `extra_indicators` — 添加领域特有风险信号

### 与Companion的协作

`trustskills`与companion的security auditor是互补关系：

| 工具 | 分析方法 | 适用场景 |
|---|---|---|
| skill-security-auditor | 静态模式匹配（正则+AST） | 快速扫描，CI集成 |
| trustskills | 行为维度加权+红线规则 | 深度治理，发布决策 |

---

## H. 可扩展性

### 添加新Pack

1. 在`packs/`下创建目录
2. 放入`.opencode/`目录（包含`skills/`, `commands/`, `agents/`）
3. 创建`pack-manifest.json`（遵循统一schema）
4. 如需AGENTS.md合并，使用`<!-- BEGIN/END pack: <name> -->`标记
5. 如需opencode.json合并，放入`opencode.example.json`
6. 在install脚本中添加alias

`catalog_query.py`会自动发现新pack，无需修改代码。

### 添加新平台

1. 在`platforms.json`的`platforms`对象中添加新平台定义
2. 指定`skills_dir`, `instructions_file`, `detect_markers`, `instructions_merge_strategy`
3. 如需指令翻译，定义`instructions_translation`（source → target → method）
4. 安装脚本会自动读取platforms.json，无需修改安装逻辑

### 添加新Skill

对现有pack添加skill：
1. 在pack的`.opencode/skills/`下创建skill目录
2. 创建`SKILL.md`（含前置元数据：name, description, version）
3. 可选创建`scripts/`, `references/`
4. 更新`pack-manifest.json`的`skills`数组和`skill_count`
5. 运行lint验证：`uv run lint_skill.py --path <skill-dir>`

或使用`/petfish create <name>`自动生成脚手架。

---

## I. 安全模型

胖鱼的安全体系分三层：

### 第一层：静态分析 (skill-security-auditor)

在skill安装或发布前，对SKILL.md和scripts/目录做静态扫描：

- 正则匹配危险模式（subprocess shell=True, eval/exec, 硬编码凭证）
- Python AST分析（import检查、函数调用检查）
- SKILL.md中可执行代码块的语言白名单检查
- 输出：0.0-1.0风险评分 + findings列表

### 第二层：行为分析 (trustskills)

对skill的可执行行为做六维度加权评估：

- 不依赖文案描述，而是分析实际代码行为
- 红线规则提供硬拒绝能力
- 治理等级映射到具体运行策略（放行/确认/沙箱/人审/拒绝）
- 支持自定义策略覆盖默认规则

### 第三层：质量门禁 (quality-gate)

编排前两层的结果，加上元数据验证，给出综合发布决策：

- lint ≥ 80分 且 risk ≤ 0.5 且 无CRITICAL finding → PASS
- 部分条件未满足但无硬性阻断 → CONDITIONAL（需人工确认）
- 任一硬性条件失败 → FAIL

三层之间的关系：

```
静态分析 (快速, CI友好)
    ↓
行为分析 (深度, 治理决策)
    ↓
质量门禁 (编排, 发布决策)
```

每一层都可独立使用，也可通过quality-gate统一编排。

---

## 附录：关键技术决策记录

| 决策 | 选择 | 理由 |
|---|---|---|
| 平台配置 | `platforms.json`单一数据源 | 避免多处硬编码，新平台只改一个文件 |
| Pack发现 | 运行时遍历`packs/*/pack-manifest.json` | 新pack零代码接入 |
| 安装脚本 | PowerShell + Bash双版本 | 覆盖Windows + macOS/Linux |
| 远程安装 | `curl | bash` / `irm | scriptblock` | 零依赖，一条命令 |
| 指令合并 | marker-based merge | 不覆盖用户已有内容 |
| 质量门禁编排 | `find_sibling_script()` | 松耦合，各skill可独立更新 |
| trustskills集成 | subprocess调用外部CLI | 不vendoring引擎源码，版本独立升级 |
| Lint JSON输出 | `findings`字段（非`issues`） | 与security audit统一命名 |
| Security JSON输出 | `{"results": [...]}` | 便于gate解包和聚合 |
