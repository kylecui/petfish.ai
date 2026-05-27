# PEtFiSh Project Landscape

> **强制文档** — 所有涉及跨仓库变更的开发者必须遵守本文档定义的同步规则。
> 上次更新: 2026-05-27 (v1.3)

---

## 1. 仓库清单

| # | 仓库 | 可见性 | 角色 | 维护关系 |
|---|------|--------|------|---------|
| 1 | **[kylecui/petfish.ai](https://github.com/kylecui/petfish.ai)** | Public | 主单仓库 — 所有源码、13 packs、96 skills、文档、网站、CI/CD | 核心仓库，所有变更起点 |
| 2 | **[kylecui/petfish-market](https://github.com/kylecui/petfish-market)** | Public | Community skill marketplace — 提交→CI验证→发布index.json | 依赖 #1 的 gate 工具链 |
| 3 | **[kylecui/petfish_remote](https://github.com/kylecui/petfish_remote)** | Public | 胖鱼遥控器 — 通过IM操作opencode的连接器（飞书/Slack/Telegram/企微/Web） | 依赖 #1 的安装器分发 skills |
| 4 | **[kylecui/petfish_tester](https://github.com/kylecui/petfish_tester)** | Private | 测试与评估工具 — benchmark、A/B test、实验 | 引用 #1 的评估数据 |
| 5 | **[kylecui/opencode](https://github.com/kylecui/opencode)** | Public | OpenCode fork — 本地patch（上游PR [anomalyco/opencode#28993](https://github.com/anomalyco/opencode/pull/28993)） | 上游独立，我们维护patch分支 |
| 6 | **[kylecui/trustskills](https://github.com/kylecui/trustskills)** | Public | 外部Python治理引擎 — `uv add trustskills` 安装 | 被 fish-guard (trust pack) 引用 |

---

## 2. 核心仓库结构

### 2.1 petfish.ai (主仓库)

```
petfish.ai/
├── packs/                                    # ★ Pack源码（用户安装的内容来源）
│   ├── petfish-companion-skill/              # companion — 2 skills + 2 MCPs + 1 cmd
│   │   └── .opencode/
│   │       ├── skills/fish-brain/            # 鱼伴 — 传感、路由、registry查询
│   │       ├── skills/fish-market/           # 鱼市 — 外部skill搜索
│   │       ├── commands/petfish.md           # /petfish 命令
│   │       ├── mcp/skill-registry/           # MCP: pack查询
│   │       └── mcp/usage-cost/               # MCP: token用量追踪
│   │
│   ├── petfish-toolchain-skill/              # toolchain — 8 skills (v1.3新增)
│   │   └── .opencode/skills/
│   │       ├── skill-author/                 #   新skill脚手架
│   │       ├── skill-lint/                   #   质量检查
│   │       ├── repo-skill-miner/             #   仓库挖掘
│   │       ├── skill-security-auditor/       #   安全审计
│   │       ├── quality-gate/                 #   发布门禁
│   │       ├── skill-description-optimizer/  #   描述优化
│   │       ├── skill-trigger-evaluator/      #   触发测试
│   │       └── skill-usage-tracker/          #   使用统计
│   │
│   ├── project-initializer-skill/            # init — 1 skill (fish-init 鱼启) + /initproject
│   ├── research-skill-pack/                  # research — 54 skills (7领域)
│   ├── opencode-course-skills-pack/          # course — 15 skills + 8 agents + 10 cmds
│   ├── repo-deploy-ops-skill-pack/           # deploy — 7 skills
│   ├── opencode-ppt-skills/                  # ppt — 2 skills
│   ├── opencode-skill-pack-testcases-usage-docs/ # testdocs — 2 skills
│   ├── petfish-style-skill/                  # petfish — 1 skill (fish-style 鱼言)
│   ├── anti-sycophancy-calibration-pack/     # calibrate — 1 skill (fish-calibrate 鱼准)
│   ├── fish-trail/                           # context — 1 skill + 1 MCP (context-state)
│   ├── trustskills-governance-pack/          # trust — 1 skill (fish-guard 鱼卫)
│   └── fish-reflection-pack/                 # reflect — 1 skill (fish-reflection)
│
├── install.ps1 / install.sh                  # ★ 本地安装器（动态扫描packs/）
├── remote-install.ps1 / remote-install.sh    # ★ 远程安装器（静态ALL_PACKS数组）
├── platforms.json                            # 8平台注册表
├── community-packs.json                      # 社区pack注册表（空，有schema）
├── connector.yaml                            # 远程连接器: wss://remote.petfish.ai
│
├── lib/plugin/                               # OpenCode插件源码 (TypeScript)
├── .opencode/plugin/                         # 编译后的插件 (4个)
├── .opencode/agents-rules/                   # pack规则注入文件 (8个)
│
├── .github/workflows/                        # CI/CD
│   ├── ci.yml                                #   测试 + manifest校验 + installer校验
│   ├── docs.yml                              #   MkDocs → GitHub Pages
│   ├── website.yml                           #   静态站 → SCP /var/www/petfish.ai/
│   └── petfish-eval.yml                      #   评估 + benchmark
│
├── docs/                                     # 项目文档 (EN)
├── docs/zh/                                  # 项目文档 (ZH)
├── docs-site/                                # MkDocs文档站源码
├── website/                                  # 静态营销网站
├── scripts/                                  # 辅助脚本
├── tests/                                    # Python测试套件
├── evals/                                    # 评估数据与报告
├── research/                                 # 活跃研究项目
├── dev_reference/                            # 开发参考与设计文档（草案）
├── AGENTS.md                                 # 根项目规则 (~1200行)
└── opencode.json                             # OpenCode配置
```

### 2.2 petfish-market (社区市场)

```
petfish-market/
├── .github/
│   ├── workflows/
│   │   ├── validate-submission.yml           # PR触发: clone → lint → audit → gate
│   │   └── publish-index.yml                 # merge触发: 重建index.json
│   ├── scripts/
│   │   ├── rebuild_index.py                  # 扫描skills/*.json → 生成index
│   │   └── write_gate_result.py              # gate结果写入PR comment
│   └── PULL_REQUEST_TEMPLATE/
│       └── skill_submission.md
├── skills/
│   ├── .gitkeep
│   └── community--test-skill.json            # 测试skill
├── CONTRIBUTING.md                           # 提交指南
├── index.json                                # marketplace索引
└── README.md
```

### 2.3 petfish_remote (胖鱼遥控器)

```
petfish_remote/
├── src/
│   ├── main.ts                               # 入口
│   ├── server/                               # ConnectorGateway + 注册 + 认证
│   ├── connector/                            # ConnectorClient + SessionBridge + Daemon
│   │   └── bridges/                          # OpenCode/Codex/Gemini bridge
│   ├── adapters/                             # IM适配器
│   │   ├── feishu/                           #   飞书
│   │   ├── slack/                            #   Slack
│   │   ├── telegram/                         #   Telegram
│   │   ├── wecom/                            #   企业微信
│   │   └── web/                              #   Web界面
│   ├── core/                                 # SessionManager, TaskManager, PolicyEngine
│   ├── render/                               # MessageRenderer, ApprovalRenderer
│   ├── runtime/                              # Local/Remote/SSH/WSL runtime
│   └── plugin/                               # petfish-plugin installer
├── config/                                   # adapters.yaml, policies.yaml, etc.
├── .opencode/skills/                         # 安装后的skills（通过petfish.ai安装器）
├── tests/
└── docs/
```

---

## 3. 依赖关系

### 3.1 依赖图

```
                    petfish.ai (主仓库)
                    ┌────────────────┐
                    │ packs/ (13)     │
                    │ installers (4)  │
                    │ CI/CD (4)       │
                    └──┬─────┬───────┘
                       │     │
          ┌────────────┘     └──────────────┐
          ▼                                  ▼
  petfish-market                    petfish_remote
  ┌─────────────────┐               ┌─────────────────┐
  │ CI clone #1     │               │ 安装器从 #1      │
  │ run_gate.py     │◄──────────────│ 分发skills       │
  │ index.json ─────┼──┐            └─────────────────┘
  └─────────────────┘  │
                       │    ┌─────────────────────┐
                       └───►│ fish-market (鱼市)   │
                            │ marketplace_search.py│
                            │ 查询 index.json      │
                            └─────────────────────┘

  petfish_tester (Private)        kylecui/opencode (Fork)
  ┌──────────────────┐            ┌──────────────────┐
  │ benchmark数据     │            │ 本地patch         │
  │ A/B test          │            │ 上游PR #28993     │
  └──────────────────┘            └──────────────────┘

  kylecui/trustskills (Python包)
  ┌──────────────────┐
  │ uv add trustskills│
  │ fish-guard 引用   │
  └──────────────────┘
```

### 3.2 具体依赖清单

| 依赖方向 | 依赖内容 | 文件位置 |
|---------|---------|---------|
| market → petfish.ai | CI clone latest release tag 的 `quality-gate/scripts/run_gate.py` | market: `.github/workflows/validate-submission.yml` L54-62 |
| market → petfish.ai | CI clone latest release tag 的 `skill-lint/scripts/lint_skill.py` | market: `.github/workflows/validate-submission.yml` (via gate) |
| petfish.ai → market | `marketplace_search.py` 查询 `petfish-market/main/index.json` | ai: `packs/.../fish-market/scripts/marketplace_search.py` L159 |
| petfish.ai → market | `marketplace_search.py` 查询 `petfish.ai/master/community-packs.json` | ai: `packs/.../fish-market/scripts/marketplace_search.py` L120 |
| remote → petfish.ai | 通过 `install.ps1/sh` 安装 skills 到 `.opencode/skills/` | remote: `opencode.json`, `.opencode/installed-packs.json` |
| ai → opencode fork | `patch_opencode.py` 构建本地patch | ai: `scripts/patch_opencode.py` L50 |
| ai → trustskills | `fish-guard` 通过 `uv add trustskills` 引用 | ai: `packs/trustskills-governance-pack/README.md` |
| ai → petfish_tester | eval benchmark数据源 | ai: `dev_reference/eval-handoff-extracted/` |
| remote → connector.yaml | `wss://remote.petfish.ai/ws/connector` 连接器配置 | ai: `connector.yaml` → remote 的 server |

---

## 4. 同步维护规则（强制）

### 4.1 petfish.ai release 后必须检查

每次 petfish.ai 发布新 release 后，必须检查以下 cross-repo 影响：

| 检查项 | 影响仓库 | 检查方法 |
|-------|---------|---------|
| gate 工具链路径是否变化 | petfish-market | market CI 引用 `packs/.../quality-gate/scripts/run_gate.py`，确认该路径仍然有效 |
| skill 目录是否迁移/重命名 | petfish-market | market 的 `skills/*.json` 中 `path` 字段指向的路径是否仍存在 |
| 安装器别名是否变化 | petfish_remote | remote 通过安装器分发 skills，确认旧别名仍有效 |
| community-packs.json schema 是否变化 | petfish-market | 确认 `community-packs.json` 的 `_schema` 与 market 的 CONTRIBUTING.md 一致 |
| fish-market 的搜索源 URL 是否变化 | petfish.ai | 确认 `marketplace_search.py` 中的 URL 仍可访问 |

### 4.2 petfish-market 变更后必须检查

| 检查项 | 影响仓库 | 检查方法 |
|-------|---------|---------|
| index.json schema 是否变化 | petfish.ai | 确认 `marketplace_search.py` 的解析逻辑兼容新 schema |
| CI 验证流程是否变化 | petfish.ai | 确认 gate 工具链的 CLI 接口未变化 |

### 4.3 禁止事项

- **禁止**在 petfish.ai 中移动/重命名被 market CI 引用的脚本路径，而不更新 market 的 CI 配置
- **禁止**在 petfish.ai 中修改 `community-packs.json` 的 schema，而不同步更新 market 的 CONTRIBUTING.md
- **禁止**在 market 中修改 `index.json` 的结构，而不同步更新 `marketplace_search.py` 的解析逻辑
- **禁止**在 petfish.ai 中删除被 remote 的 `connector.yaml` 引用的连接器协议

---

## 5. 当前已知问题

### 5.1 petfish-market CI 已断

**问题**: v1.3 将 `quality-gate` 从 `companion` pack 迁移到 `toolchain` pack。market CI 的 `validate-submission.yml` 引用的路径是：
```
petfish-ai/packs/petfish-companion-skill/.opencode/skills/quality-gate/scripts/run_gate.py
```
该路径在 v1.3 后已不存在，实际路径变为：
```
petfish-ai/packs/petfish-toolchain-skill/.opencode/skills/quality-gate/scripts/run_gate.py
```

**影响**: 社区提交 PR 时 CI 会因找不到 `run_gate.py` 而失败。

**修复**: 更新 market 的 `validate-submission.yml` 中的 `GATE_SCRIPT` 路径。

### 5.2 petfish-market 测试 skill 指向过时路径

**问题**: `skills/community--test-skill.json` 中 `"path": "packs/petfish-companion-skill/.opencode/skills/skill-lint"`。v1.3 后 `skill-lint` 已迁移到 `petfish-toolchain-skill/`。

**修复**: 更新 `community--test-skill.json` 的 `path` 字段。

### 5.3 petfish_remote 使用旧 skill 名称

**问题**: remote 仓库的 `.opencode/skills/` 中仍是 v1.3 之前的目录名（`petfish-companion`、`marketplace-connector`、`skill-trust-governance` 等）。

**影响**: 功能不受影响（安装器通过 legacy_names 兼容），但下次重新安装时目录名会变化。

**建议**: 下次 remote 更新 skills 时，使用 `--force` 重新安装以获取新名称。

---

## 6. Pack 总览

| Alias | Pack目录 | Skills | MCPs | Cmds | 中文品牌 |
|-------|---------|--------|------|------|---------|
| `companion`, `fish-brain`, `fish-core` | petfish-companion-skill | 2 | 2 | 1 | 鱼伴 |
| `toolchain` | petfish-toolchain-skill | 8 | 0 | 0 | 鱼具 |
| `init`, `fish-init` | project-initializer-skill | 1 | 0 | 1 | 鱼启 |
| `research` | research-skill-pack | 54 | 0 | 0 | — |
| `course` | opencode-course-skills-pack | 15 | 0 | 10 | — |
| `deploy` | repo-deploy-ops-skill-pack | 7 | 0 | 0 | — |
| `ppt` | opencode-ppt-skills | 2 | 0 | 0 | — |
| `testdocs` | opencode-skill-pack-testcases-usage-docs | 2 | 0 | 0 | — |
| `petfish`, `fish-style` | petfish-style-skill | 1 | 0 | 0 | 鱼言 |
| `calibrate`, `fish-calibrate` | anti-sycophancy-calibration-pack | 1 | 0 | 0 | 鱼准 |
| `context` | fish-trail | 1 | 1 | 0 | 鱼迹 |
| `trust`, `fish-guard` | trustskills-governance-pack | 1 | 0 | 0 | 鱼卫 |
| `reflect` | fish-reflection-pack | 1 | 0 | 0 | — |
| **Total** | **13 packs** | **96** | **3** | **12** | |

---

## 7. CI/CD 流水线

| Workflow | 触发条件 | 作用 |
|----------|---------|------|
| `ci.yml` | push/PR to dev/master | pytest + manifest校验 + installer校验 |
| `docs.yml` | push to dev/master | MkDocs build → GitHub Pages |
| `website.yml` | push to master | SCP → /var/www/petfish.ai/ |
| `petfish-eval.yml` | PR comment / schedule | fish-trail MCP测试 + 4项benchmark |

---

## 8. 变更记录

| 日期 | 变更 | 作者 |
|------|------|------|
| 2026-05-27 | 初始版本 — 6个仓库全景图 + 同步维护规则 + 已知问题 | v1.3 module decomposition |
