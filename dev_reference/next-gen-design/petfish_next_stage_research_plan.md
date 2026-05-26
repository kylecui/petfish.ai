# PEtFiSh下一阶段研发方向、设计与实施方案

> 阶段主题：**Runtime Hardening & Evidence Phase**  
> 中文：**运行时硬化与证据化阶段**  
> 目标：将PEtFiSh从“skills-first项目”升级为“面向AI Agent工作区的Companion Gateway与Skill Pack Lifecycle Runtime”。

---

## 1. 核心判断

PEtFiSh当前不再缺少单点功能。它已经具备项目初始化、skills安装、Companion Gateway、context治理、quality gate、research/deploy/course/testdocs等pack，以及多平台适配意识。

下一阶段的核心问题不是“还要加什么skill”，而是：

1. Gateway是否稳定、低成本、可控？
2. PEtFiSh是否可以脱离OMO/oh-my-opencode独立证明自身有效？
3. skills、plugin、MCP、policy之间的职责是否清晰？
4. PEtFiSh是否能用评估报告证明自己减少了上下文污染、失败、返工和无效调用？

因此，下一阶段应从：

```text
skills-first
```

升级为：

```text
runtime-first
```

从：

```text
prompt discipline
```

升级为：

```text
plugin-enforced discipline
```

从：

```text
implicit context
```

升级为：

```text
MCP-backed state
```

从：

```text
OMO-assisted development
```

升级为：

```text
OMO-decoupled evaluation
```

从：

```text
feature-rich
```

升级为：

```text
evidence-backed
```

---

## 2. 项目重新定位

建议将PEtFiSh正式定位为：

> **PEtFiSh is a companion gateway and skill-pack lifecycle runtime for AI-agent workspaces.**

中文：

> **PEtFiSh是面向AI Agent工作区的伴随式网关与技能包生命周期运行时。**

这个定位比“skills仓库”更准确，也比“完整Agent平台”更收敛。

PEtFiSh不应试图替代OpenCode、Claude Code、Cursor、Codex或OMO。它应该成为这些环境之上的：

- 工作区初始化层；
- Companion Gateway层；
- skills/pack生命周期层；
- topic/context治理层；
- 成本与权限策略层；
- 质量门禁与评估层。

---

## 3. 总体架构

### 3.1 目标架构

```text
PEtFiSh Runtime
├── Core Semantics
│   ├── Companion Gateway
│   ├── Skill / Pack Lifecycle
│   ├── Project Mode
│   ├── Rigor Policy
│   ├── Topic Governance
│   ├── Anti-Sycophancy Policy
│   └── Release / Quality Discipline
│
├── Policy Layer
│   ├── gateway-policy.yaml
│   ├── model-routing-policy.yaml
│   ├── cost-policy.yaml
│   ├── permission-policy.yaml
│   ├── rigor-policy.yaml
│   └── adapter-policy.yaml
│
├── Execution Layer
│   ├── Skills
│   ├── Plugins
│   ├── MCP Servers
│   └── Platform Adapters
│
├── State Layer
│   ├── topic graph
│   ├── installed packs registry
│   ├── skill catalog
│   ├── usage / cost log
│   ├── quality gate results
│   └── evaluation reports
│
└── Evaluation Layer
    ├── gateway eval
    ├── trigger eval
    ├── install E2E
    ├── cost eval
    ├── safety eval
    └── cross-platform eval
```

---

## 4. 技术职责边界

### 4.1 Skill：知识与流程

Skill继续保留，但不再承担强制控制职责。

Skill适合表达：

- 什么时候使用；
- 怎么做；
- 输入输出格式；
- 质量标准；
- 工作流；
- 领域知识；
- 检查清单。

适合继续保留为skill的模块：

| 类型 | 示例 |
|---|---|
| 方法论 | research、reflect、calibrate |
| 工作流 | course、deploy、testdocs |
| 文风规则 | petfish-style |
| 领域模板 | ppt、writing、security review |
| 检查清单 | release checklist、pack checklist |

Skill回答的是：

```text
什么时候用？
怎么做？
产物格式是什么？
质量标准是什么？
```

---

### 4.2 Plugin：强制控制与事件驱动

Plugin负责“必须发生”的事情。

适合迁移到plugin的能力：

| 能力 | 迁移原因 |
|---|---|
| Companion Gateway前置检查 | 每轮自动执行，不能靠agent记忆 |
| cost guard | 控制高价模型调用、循环、token预算 |
| secret guard | 拦截`.env`、key、token等敏感文件 |
| release guard | 监听release/git命令，提醒发布纪律 |
| rigor trigger | 根据风险自动触发plan/review |
| quality gate trigger | 在发布/pack变更前自动触发 |
| compaction hook | 控制上下文压缩与保留摘要 |

Plugin回答的是：

```text
什么时候强制触发？
什么时候阻止？
什么时候升级？
什么时候记录？
```

---

### 4.3 MCP：状态服务与外部工具

MCP负责长期状态和结构化查询。

适合做成MCP的能力：

| MCP | 作用 |
|---|---|
| `context-state` | topic graph、session状态、context污染分数 |
| `skill-registry` | 已安装pack、skill catalog、profile映射 |
| `usage-cost` | 模型调用、token估算、任务成本记录 |
| `quality-gate` | 查询lint/audit/gate结果 |
| `repo-state` | repo inventory、文件摘要、变更状态 |
| `release-state` | release/tag/checklist状态 |

MCP回答的是：

```text
当前状态是什么？
历史记录是什么？
这个pack是否安装？
上次质量门禁结果是什么？
这个topic是否已经漂移？
```

---

### 4.4 Policy：策略真值源

Policy是PEtFiSh自己的规则源，不应散落在OMO配置、agent prompt或平台特定文件里。

建议新增目录：

```text
.opencode/
  petfish/
    policy/
      gateway-policy.yaml
      model-routing-policy.yaml
      cost-policy.yaml
      permission-policy.yaml
      rigor-policy.yaml
      adapter-policy.yaml
```

Policy回答的是：

```text
PEtFiSh认为什么任务该用什么模型？
什么情况需要review？
什么情况禁止继续？
什么情况需要用户确认？
```

---

## 5. OMO与PEtFiSh的边界

### 5.1 基本原则

OMO/oh-my-opencode可以用于开发加速和OpenCode高级集成，但不能成为PEtFiSh核心评测的依赖。

建议写入项目原则：

```text
PEtFiSh may use OMO for development acceleration and OpenCode integration,
but PEtFiSh core evaluation must run without OMO by default.
OMO is an adapter, not a dependency of truth.
```

中文：

```text
PEtFiSh可以使用OMO加速开发和增强OpenCode集成，
但PEtFiSh核心评测默认不得依赖OMO。
OMO是适配器，不是真值依赖。
```

### 5.2 三套运行Profile

#### Profile A：Core Baseline

用于证明PEtFiSh自身有效。

```text
- OpenCode原生
- PEtFiSh skills
- PEtFiSh plugin / MCP
- 不加载oh-my-opencode
- 不加载OMO agent / category / fallback
```

#### Profile B：OpenCode + OMO Integration

用于证明PEtFiSh与OMO兼容。

```text
- OpenCode
- PEtFiSh
- OMO / oh-my-opencode
- PEtFiSh cost guard约束OMO
```

#### Profile C：Cross-Platform Degraded

用于证明PEtFiSh语义可迁移。

```text
- Claude / Cursor / Codex / Windsurf / Universal
- 只使用PEtFiSh instructions + skills + scripts
- 不依赖OMO
- plugin / MCP能力降级
```

---

## 6. Cost-Aware Gateway设计

### 6.1 设计原则

```text
规则优先
轻模型默认
高端模型低频
状态服务辅助
严禁高端模型进入循环
```

### 6.2 模型层级

```yaml
model_tiers:
  gateway:
    default: deepseek/deepseek-v4-flash
    purpose: "每轮Gateway检查、分类、skill sense、topic初判"

  worker:
    default: deepseek/deepseek-v4-flash
    fallback: siliconflow/Qwen/Qwen3-Coder-480B-A35B-Instruct
    purpose: "文件摘要、简单修改、草稿生成"

  deep_coding:
    default: deepseek/deepseek-v4-pro
    purpose: "多文件实现、长上下文、复杂debug"

  critic:
    default: siliconflow/Pro/zai-org/GLM-5.1
    fallback: deepseek/deepseek-v4-pro
    purpose: "计划批判、架构裁决、发布审查"

  multimodal:
    default: siliconflow/Pro/moonshotai/Kimi-K2.5
    purpose: "截图、PPT、视觉材料"
```

### 6.3 升级规则

```yaml
upgrade_rules:
  use_deep_coding_when:
    - task_touches_3_or_more_files
    - long_context_required
    - ci_failure_analysis
    - multi_file_refactor
    - security_sensitive_code

  use_critic_when:
    - rigor_true
    - release_change
    - installer_change
    - pack_manifest_change
    - security_policy_change
    - destructive_operation
    - final_review_required

  use_multimodal_when:
    - image_input
    - ppt_or_slide_task
    - diagram_review
```

### 6.4 限制规则

```yaml
limits:
  max_gateway_model_calls_per_turn: 1
  max_critic_calls_per_task: 2
  max_high_model_calls_per_task: 3
  max_failed_iterations: 2
  max_diff_lines_without_review: 500
  max_files_without_plan: 3
  max_steps_without_checkpoint: 8
```

---

## 7. Plugin设计方案

### 7.1 `petfish-gateway-plugin`

职责：

- 每轮读取project mode；
- 检查topic风险；
- 检查failure signal；
- 检查skill gap；
- 触发anti-sycophancy；
- 决定是否继续、提醒、升级或暂停。

输入：

```text
user_message
session_id
project_mode
installed_packs
active_topic
previous_assistant_output
```

输出：

```json
{
  "action": "proceed | warn | pause | recommend_pack | fork_topic",
  "risk_level": "low | medium | high",
  "recommended_pack": "deploy",
  "model_tier": "gateway",
  "reason": "topic drift detected"
}
```

---

### 7.2 `petfish-cost-guard-plugin`

职责：

- 统计每任务调用次数；
- 限制高端模型调用；
- 防止Agent循环；
- 检测重复失败；
- 检测diff过大；
- 输出成本报告。

触发点：

```text
before model call
after model call
before tool execution
after tool execution
on task checkpoint
```

拦截条件：

```text
high_model_calls > limit
failed_iterations > limit
diff_lines > threshold
tool_loop_detected
```

---

### 7.3 `petfish-safety-guard-plugin`

职责：

- 阻止读取`.env`、密钥、token；
- 对危险bash命令要求确认；
- 对跨仓库写操作拦截；
- 对release、tag、publish操作触发检查清单。

规则示例：

```yaml
deny_read:
  - ".env"
  - ".env.*"
  - "*secret*"
  - "*token*"
  - "id_rsa"
  - "credentials.json"

ask_before_bash:
  - "rm -rf*"
  - "git push*"
  - "gh release create*"
  - "npm publish*"
  - "docker compose down*"

deny_cross_repo_write: true
```

---

### 7.4 `petfish-quality-hook-plugin`

职责：

- pack变更后自动提醒运行lint/audit/gate；
- release前强制检查；
- 新pack引入时检查九触点；
- quality gate失败时阻止发布流程。

---

## 8. MCP设计方案

### 8.1 `context-state-mcp`

职责：

```text
topic_detect
topic_update
topic_get_active
topic_fork
topic_switch
topic_report
contamination_score
```

数据文件：

```text
.petfish/state/topics.json
.petfish/state/sessions.json
.petfish/state/topic-events.jsonl
```

---

### 8.2 `skill-registry-mcp`

职责：

```text
list_installed_packs
list_available_packs
suggest_packs
search_skills
get_skill_metadata
get_profile_mapping
```

数据来源：

```text
installed-packs.json
pack-manifest.json
catalog_query.py
README/profile mapping
```

---

### 8.3 `usage-cost-mcp`

职责：

```text
record_model_call
record_tool_call
get_task_cost
get_session_cost
get_high_model_call_ratio
detect_cost_anomaly
```

数据文件：

```text
.petfish/state/usage.jsonl
.petfish/state/cost-summary.json
```

---

### 8.4 `quality-gate-mcp`

职责：

```text
run_lint
run_audit
run_gate
get_last_gate_result
check_pack_touchpoints
check_trigger_coverage
```

---

## 9. Evaluation体系设计

### 9.1 评测目标

PEtFiSh必须证明：

```text
是否减少上下文污染？
是否减少失败？
是否减少返工？
是否降低成本？
是否提高skill触发质量？
是否提升发布可靠性？
```

### 9.2 目录结构

```text
benchmarks/
├── README.md
├── datasets/
│   ├── gateway-topic-drift.jsonl
│   ├── skill-sense.jsonl
│   ├── failure-signal.jsonl
│   ├── anti-sycophancy.jsonl
│   ├── cost-routing.jsonl
│   ├── install-e2e.jsonl
│   └── pack-touchpoint.jsonl
├── scripts/
│   ├── run_gateway_eval.py
│   ├── run_skill_sense_eval.py
│   ├── run_failure_signal_eval.py
│   ├── run_cost_routing_eval.py
│   ├── run_install_e2e.py
│   └── generate_eval_report.py
└── reports/
    └── v0.12-evaluation.md
```

### 9.3 指标

| 模块 | 指标 | 目标 |
|---|---|---|
| Topic Check | precision / recall | >80% |
| Skill Sense | precision / recall | >85% / >80% |
| Failure Signal | recovery suggestion accuracy | >85% |
| Anti-Sycophancy | counterargument detection rate | >80% |
| Cost Routing | high-model call ratio | <20% |
| Gateway | avg calls per turn | ≤1 |
| Install | fresh install success | >95% |
| Pack Lifecycle | 9-touchpoint coverage | 100% |
| Quality Gate | false pass rate | <5% |
| OMO Integration | behavior divergence | 可解释 |

### 9.4 Evaluation Report模板

```markdown
# PEtFiSh v0.12 Evaluation Report

## 1. Summary
- Version:
- Date:
- Profile:
  - Core Baseline
  - OpenCode + OMO Integration
  - Cross-platform degraded

## 2. Gateway Evaluation
| Metric | Score | Target | Pass |
|---|---:|---:|---|

## 3. Skill Sense Evaluation

## 4. Failure Signal Evaluation

## 5. Anti-Sycophancy Evaluation

## 6. Cost Routing

## 7. Install E2E

## 8. Quality Gate

## 9. OMO Comparison
| Metric | Core | With OMO | Delta | Interpretation |
|---|---:|---:|---:|---|

## 10. Known Failures

## 11. Next Fixes
```

---

## 10. 版本路线图

### v0.12：Cost-Aware Gateway

目标：让Gateway成本可控，GLM/高端模型不进入高频路径。

交付物：

```text
.opencode/petfish/policy/model-routing-policy.yaml
.opencode/petfish/policy/cost-policy.yaml
.opencode/plugins/petfish-gateway.ts
.opencode/plugins/petfish-cost-guard.ts
benchmarks/datasets/cost-routing.jsonl
benchmarks/scripts/run_cost_routing_eval.py
```

验收标准：

```text
- Core Baseline下Gateway每轮最多1次模型调用
- 普通消息不触发GLM-5.1
- 复杂任务GLM-5.1默认最多2次
- cost-routing eval通过率≥85%
```

---

### v0.13：Plugin-Enforced Runtime

目标：把关键纪律从AGENTS.md迁移到plugin强制执行。

交付物：

```text
.opencode/plugins/petfish-safety-guard.ts
.opencode/plugins/petfish-quality-hook.ts
.opencode/petfish/policy/permission-policy.yaml
.opencode/petfish/policy/release-policy.yaml
```

验收标准：

```text
- secret read test 100%拦截
- release command触发release checklist
- 新pack缺少触点时quality hook报错
- 跨仓库写操作被拦截
```

---

### v0.14：MCP-backed State

目标：把状态服务化，减少prompt记忆依赖。

交付物：

```text
.opencode/skills/fish-trail/mcp/context-state/
.opencode/skills/petfish-companion/mcp/skill-registry/
.opencode/skills/petfish-companion/mcp/usage-cost/
.opencode/skills/quality-gate/mcp/quality-gate/
```

验收标准：

```text
- context-state MCP可独立启动
- skill-registry MCP可返回pack/profile映射
- usage-cost MCP可输出session/task cost
- quality-gate MCP可返回最近一次gate结果
```

---

### v0.15：Evaluation & Proof

目标：建立PEtFiSh证明体系。

交付物：

```text
benchmarks/
tests/e2e-install/
reports/v0.15-evaluation.md
.github/workflows/petfish-eval.yml
```

验收标准：

```text
- 每次release附带evaluation report
- Core Baseline和With OMO分开报告
- install E2E成功率≥95%
- trigger precision≥85%
```

---

### v0.16：Adapter Decoupling

目标：让PEtFiSh核心语义独立于OMO和OpenCode。

交付物：

```text
petfish-core-policy.yaml
adapters/opencode-native/
adapters/opencode-omo/
adapters/claude/
adapters/cursor/
adapters/codex/
```

验收标准：

```text
- Core Baseline不依赖OMO
- OMO adapter可选启用
- Cross-platform degraded profile可通过基础测试
```

---

## 11. 实施顺序

### 阶段1：冻结横向扩展

时间：1周

任务：

- 暂停新增pack；
- 整理现有pack清单；
- 确认core与optional；
- 建立架构文档。

产物：

```text
docs/architecture/petfish-runtime-architecture.md
docs/architecture/omo-boundary.md
docs/architecture/cost-aware-gateway.md
```

---

### 阶段2：Policy先行

时间：1–2周

任务：

新增：

```text
.opencode/petfish/policy/
  gateway-policy.yaml
  model-routing-policy.yaml
  cost-policy.yaml
  permission-policy.yaml
  rigor-policy.yaml
```

验收：

- 能用policy解释当前所有模型路由；
- 能生成oh-my-openagent配置；
- 能解释什么时候触发GLM-5.1。

---

### 阶段3：Core Baseline测试环境

时间：1周

任务：

建立三套profile：

```text
profiles/core-baseline/
profiles/opencode-omo-integration/
profiles/cross-platform-degraded/
```

验收：

- Core Baseline不加载OMO；
- OMO Integration加载OMO；
- 两者可以跑同一组benchmark。

---

### 阶段4：Gateway与Cost Guard

时间：2–3周

任务：

实现：

```text
petfish-gateway-plugin
petfish-cost-guard-plugin
```

并接入：

```text
run_gateway_eval.py
run_cost_routing_eval.py
```

验收：

- 普通任务不调用高端模型；
- 复杂任务只在边界调用critic；
- 失败循环会停止；
- 生成cost summary。

---

### 阶段5：MCP状态服务

时间：3–4周

任务：

优先实现三个MCP：

```text
context-state
skill-registry
usage-cost
```

验收：

- Gateway从MCP读取状态；
- Skill Sense从registry查询；
- cost guard写入usage-cost；
- topic drift可复现评测。

---

### 阶段6：评估报告与发布集成

时间：2周

任务：

- evaluation report自动生成；
- release前自动运行install E2E；
- quality gate接入release checklist；
- README展示当前评测摘要。

验收：

- 每个release有评估报告；
- master merge后release流程有证据；
- 外部用户能看到PEtFiSh是否真的有效。

---

## 12. v0.12最小可行版本

如果不想一次做太大，v0.12只做MVP：

```text
1. petfish-cost-policy.yaml
2. petfish-model-routing-policy.yaml
3. Core Baseline profile
4. OMO Integration profile
5. cost-routing benchmark
6. Gateway benchmark
7. 生成oh-my-openagent配置的脚本
```

目录建议：

```text
.opencode/
  petfish/
    policy/
      cost-policy.yaml
      model-routing-policy.yaml
      gateway-policy.yaml
    adapters/
      opencode-native/
      opencode-omo/
    generated/
      oh-my-openagent.generated.json

benchmarks/
  datasets/
    cost-routing.jsonl
    gateway-basic.jsonl
  scripts/
    run_cost_routing_eval.py
    run_gateway_eval.py
```

MVP验收：

```text
- 同一任务在Core Baseline和OMO Integration下可对比
- 能输出每个任务应使用的模型tier
- 能证明GLM-5.1不会进入Gateway高频路径
- 能生成oh-my-openagent配置但不依赖它
```

---

## 13. 风险与避免事项

### 13.1 不要继续疯狂加pack

现在不是缺pack，而是已有pack如何稳定触发、低成本运行、可证明有效。

### 13.2 不要把OMO变成PEtFiSh核心

OMO可以帮助开发，但不能成为评测真值依赖。PEtFiSh core必须能在无OMO环境下独立运行。

### 13.3 不要把所有Gateway逻辑都交给LLM

Gateway应该规则优先、轻模型兜底。高端模型只做低频裁决。

### 13.4 不要默认启用大量MCP

MCP会增加上下文和复杂度。默认只启用：

```text
context-state
skill-registry
usage-cost
quality-gate
```

其它外部MCP按需启用。

### 13.5 不要把plugin写得太重

plugin应先做强制边界和日志，不要一开始做复杂AI判断。复杂判断留给policy+轻模型+MCP状态。

---

## 14. 最终路线总结

PEtFiSh下一阶段的核心路线是：

```text
从skills-first升级为runtime-first
从prompt discipline升级为plugin-enforced discipline
从implicit context升级为MCP-backed state
从OMO-assisted development升级为OMO-decoupled evaluation
从feature-rich升级为evidence-backed
```

一句话总结：

> **PEtFiSh下一步要证明的不是“我有很多skills”，而是“我能让AI Agent工作区更稳定、更少污染、更少失败、更低成本、更可审计”。**

建议将下一阶段正式命名为：

```text
PEtFiSh v0.12–v0.15: Runtime Hardening & Evidence Phase
```

中文：

```text
PEtFiSh v0.12–v0.15：运行时硬化与证据化阶段
```
