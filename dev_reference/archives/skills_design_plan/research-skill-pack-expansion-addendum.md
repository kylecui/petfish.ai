# Research Skill Pack 补充文档：研究范式扩展设计

> 文档类型：V2计划补充文档  
> 适用对象：`research-skill-pack`后续扩展  
> 主题：在科研研究、产品研究、规划/战略研究之外，如何补充更多通用研究能力  
> 建议状态：**Implemented** — 所有Phase A-E已交付，4个P3 skill在v0.10.9补齐  
> 交付版本：v0.10.0 ~ v0.10.9  
> 最终skill数：54（含4个adapter）  

---

## 0. 核心结论

我们已经完成或正在推进三类核心研究能力：

```text
scientific-research   # 科研研究：求真、证明、实验、论文
product-research      # 产品研究：用户、场景、机会、验证
planning-research     # 规划/战略研究：目标、环境、路径、资源
```

下一步不建议继续按生活领域横向无限拆分，例如：

```text
travel-research
entertainment-research
meeting-research
study-research
shopping-research
...
```

这种方式会导致skill包碎片化、触发混乱、重复逻辑过多。更好的做法是新增几类**通用研究范式**，再通过轻量adapter适配具体领域。

建议形成如下结构：

```text
Core Research Layer
  ├── source discovery
  ├── literature access
  ├── excerpt notes
  ├── insight log
  ├── evidence ledger
  ├── synthesis
  └── quality review

Research Mode Layer
  ├── scientific-research
  ├── product-research
  ├── planning-research
  ├── learning-research
  ├── decision-research
  ├── risk-procurement-research
  └── experience-event-research

Domain Adapter Layer
  ├── travel-adapter
  ├── entertainment-adapter
  ├── conference-adapter
  ├── training-adapter
  ├── tool-selection-adapter
  ├── vendor-selection-adapter
  └── content-selection-adapter
```

最终建议新增四类通用研究包：

| 新增研究范式 | 主要解决的问题 | 优先级 |
|---|---|---|
| `learning-research` | 我该怎么学？如何设计学习路径？ | P1 |
| `decision-research` | 多个选项中我该选哪个？ | P1 |
| `risk-procurement-research` | 某工具、供应商、方案是否可靠、安全、合规、值得引入？ | P2 |
| `experience-event-research` | 如何组织一次旅行、会议、活动、体验？ | P2 |

此外，可以新增一个轻量adapter：

| Adapter | 作用 | 优先级 |
|---|---|---|
| `content-selection-adapter` | 支持电影、书、游戏、展览、演出等娱乐内容选择 | P3 |

---

## 1. 为什么不要按领域无限扩展

### 1.1 领域包容易碎片化

如果为每个领域单独创建完整研究包，会出现：

```text
travel-research
conference-research
entertainment-research
learning-research
shopping-research
restaurant-research
...
```

问题包括：

1. 多数领域都需要相同能力：目标定义、信息搜集、选项比较、风险检查、计划生成。
2. 领域skill之间会大量重复。
3. Agent触发时容易混淆。
4. 维护成本会快速膨胀。
5. 难以沉淀稳定的方法论。
6. 很多场景其实是“决策问题”或“活动组织问题”，不是独立研究问题。

### 1.2 研究范式比领域更稳定

相比之下，研究范式更稳定：

| 用户请求 | 表层领域 | 底层研究范式 |
|---|---|---|
| 帮我选一个旅游目的地 | 旅游 | 决策研究 |
| 帮我规划一次团建 | 活动 | 体验/活动研究 |
| 帮我比较几个AI工具 | 工具 | 决策研究 + 风险采购研究 |
| 帮我设计学习路线 | 学习 | 学习研究 |
| 帮我评估一个供应商 | 采购 | 风险采购研究 |
| 帮我选一部电影 | 娱乐 | 决策研究 + 内容选择adapter |
| 帮我组织一个Workshop | 会议 | 体验/活动研究 + 学习研究 |

因此，建议按照“问题类型”而不是“生活领域”扩展。

---

## 2. 新增研究范式总览

### 2.1 七类研究范式总表

| 研究范式 | 核心问题 | 本质 | 典型产物 |
|---|---|---|---|
| `scientific-research` | 什么是真的？如何证明？ | 求真 | 文献综述、gap、实验方案、论文 |
| `product-research` | 用户需要什么？机会在哪里？ | 造物 | 用户洞察、JTBD、竞品矩阵、MVP |
| `planning-research` | 未来怎么走？资源如何配置？ | 谋划 | 环境扫描、logic model、路线图 |
| `learning-research` | 我该怎么学？如何掌握？ | 学会 | 学习路径、资源清单、练习计划 |
| `decision-research` | 我该选哪个？为什么？ | 选择 | 选项矩阵、权衡分析、推荐 |
| `risk-procurement-research` | 是否值得引入？风险是什么？ | 引入 | 风险评估、供应商尽调、采用建议 |
| `experience-event-research` | 如何组织一次体验或活动？ | 组织 | 行程、活动runbook、后勤与风险预案 |

### 2.2 关系图

```text
                               ┌────────────────────────┐
                               │ Core Research Layer     │
                               │ sources / notes /       │
                               │ insights / evidence /   │
                               │ synthesis / review      │
                               └───────────┬────────────┘
                                           │
        ┌──────────────────────────────────┼──────────────────────────────────┐
        │                                  │                                  │
┌───────▼────────┐                ┌────────▼────────┐              ┌────────▼────────┐
│ Truth-oriented │                │ Creation-oriented│              │ Action-oriented │
│ Research       │                │ Research         │              │ Research        │
├────────────────┤                ├─────────────────┤              ├─────────────────┤
│ scientific     │                │ product          │              │ planning        │
│ learning       │                │ experience-event │              │ decision        │
│                │                │                  │              │ risk-procurement│
└────────────────┘                └─────────────────┘              └─────────────────┘
```

---

## 3. 新增范式一：Learning Research

### 3.1 定位

`learning-research`用于回答：

> 我想学习某个领域、技术、课程、证书或能力，应该如何定义目标、选择资料、设计路径、安排练习并评估进展？

它不是普通的“学习计划生成器”，而是面向研究工作台的学习路径研究能力。它强调：

1. 学习目标清晰化。
2. 当前基础诊断。
3. 先修知识映射。
4. 资源质量筛选。
5. 学习路径设计。
6. 练习任务和反馈机制。
7. 阶段性评估。
8. 学习成果与真实应用连接。

### 3.2 适用场景

- 学习一个技术领域：如XDP、eBPF、LLM Agent、AI安全。
- 准备考试或认证：如CAISP、CAIDCP、云安全认证等。
- 为科研入门设计学习路线。
- 为课程开发收集学习资源。
- 为企业培训设计预学习材料。
- 帮某类学员从零入门复杂主题。
- 设计“从概念到实践”的学习路径。

### 3.3 推荐skills

```text
learning-goal-framer
learning-prerequisite-mapper
learning-resource-discovery
learning-path-designer
learning-practice-planner
learning-progress-reviewer
```

### 3.4 Skill说明

#### `learning-goal-framer`

用途：将模糊学习愿望转化为明确学习目标。

输入示例：

```text
我想系统学习eBPF/XDP，用来支撑rSwitch论文和实现。
```

输出：

```text
learning/00_brief/learning-brief.md
```

核心字段：

| 字段 | 说明 |
|---|---|
| Learning Goal | 学习目标 |
| Target Capability | 最终要具备的能力 |
| Current Baseline | 当前基础 |
| Application Scenario | 学习后用于什么任务 |
| Time Constraint | 时间约束 |
| Output Requirement | 学习成果形式 |
| Assessment Criteria | 如何判断学会 |

#### `learning-prerequisite-mapper`

用途：梳理先修知识和依赖关系。

输出：

```text
learning/01_map/prerequisite-map.md
```

示例结构：

```text
eBPF/XDP
  ├── Linux networking basics
  ├── C programming for kernel constraints
  ├── eBPF verifier model
  ├── BPF maps
  ├── XDP hook and actions
  ├── AF_XDP
  ├── devmap / cpumap / tail calls
  └── performance benchmarking
```

#### `learning-resource-discovery`

用途：发现并筛选学习资源。

资源类型：

| 类型 | 示例 |
|---|---|
| official-doc | 官方文档 |
| textbook | 教材 |
| paper | 论文 |
| tutorial | 教程 |
| course | 课程 |
| code-repo | 代码仓库 |
| lab | 实验材料 |
| talk | 演讲/视频 |
| benchmark | 测试或实验资源 |

输出：

```text
learning/02_resources/resource-list.md
learning/02_resources/resource-index.jsonl
```

#### `learning-path-designer`

用途：设计阶段化学习路径。

输出：

```text
learning/03_path/learning-path.md
```

推荐结构：

| 阶段 | 目标 | 资源 | 练习 | 产出 | 评估 |
|---|---|---|---|---|---|

#### `learning-practice-planner`

用途：设计练习任务和动手实验。

输出：

```text
learning/04_practice/practice-plan.md
```

练习类型：

| 类型 | 示例 |
|---|---|
| Concept Drill | 概念解释 |
| Reading Note | 阅读摘录 |
| Code Lab | 代码实验 |
| Reproduction | 复现实验 |
| Design Exercise | 方案设计 |
| Teaching Back | 反向讲解 |
| Mini Project | 小项目 |

#### `learning-progress-reviewer`

用途：阶段性检查学习效果。

输出：

```text
learning/05_review/progress-review.md
```

检查维度：

| 维度 | 问题 |
|---|---|
| Concept | 是否能解释核心概念 |
| Procedure | 是否能完成关键操作 |
| Transfer | 是否能迁移到新任务 |
| Output | 是否产生可用产物 |
| Weakness | 哪些部分仍不稳 |
| Next Step | 下一阶段怎么学 |

### 3.5 Learning Research目录结构

```text
learning/
  00_brief/
    learning-brief.md
  01_map/
    prerequisite-map.md
    concept-map.md
  02_resources/
    resource-index.jsonl
    resource-list.md
    reading-notes/
  03_path/
    learning-path.md
    weekly-plan.md
  04_practice/
    practice-plan.md
    labs/
  05_review/
    progress-review.md
    assessment-rubric.md
```

### 3.6 与现有研究包关系

| 组合 | 用法 |
|---|---|
| `learning-research` + `scientific-research` | 入门某个科研方向并形成论文选题 |
| `learning-research` + `product-research` | 学习用户研究、设计研究、产品方法 |
| `learning-research` + `planning-research` | 设计人才培养体系、课程体系、学习地图 |
| `learning-research` + `research-note-capture` | 学习过程中保留摘录笔记 |
| `learning-research` + `research-insight-log` | 学习中记录个人理解和灵感 |

---

## 4. 新增范式二：Decision Research

### 4.1 定位

`decision-research`用于回答：

> 面对多个选项，在目标、约束、证据、成本、收益、风险、偏好之间如何权衡，并形成可解释推荐？

它是非常通用的研究范式，可以覆盖：

- 工具选择。
- 技术路线选择。
- 供应商选择。
- 课程选择。
- 旅游目的地选择。
- 会议场地选择。
- 内容娱乐选择。
- 云服务或硬件选择。
- 开源项目引入选择。

### 4.2 适用场景

用户常见表达：

```text
帮我比较一下A和B。
这几个方案哪个好？
我该选哪个？
帮我做一个选型分析。
帮我客观评估几个选择。
这些工具哪个更适合我们的项目？
```

### 4.3 推荐skills

```text
decision-brief-framer
option-discovery
decision-criteria-builder
option-comparison-matrix
tradeoff-analysis
decision-recommendation
```

### 4.4 Skill说明

#### `decision-brief-framer`

用途：明确决策对象、目标、约束和偏好。

输出：

```text
decision/00_brief/decision-brief.md
```

核心字段：

| 字段 | 说明 |
|---|---|
| Decision Question | 要做什么选择 |
| Options | 已知选项 |
| Decision Owner | 谁做决定 |
| Use Case | 使用场景 |
| Constraints | 预算、时间、技术、组织约束 |
| Preferences | 偏好 |
| Must-have | 必须满足 |
| Nice-to-have | 加分项 |
| Deal-breakers | 一票否决项 |

#### `option-discovery`

用途：发现候选选项。

输出：

```text
decision/01_options/options.md
decision/01_options/option-index.jsonl
```

注意事项：

- 如果用户已经给出候选项，应先评估这些候选项。
- 如果候选项不足，再扩展搜索。
- 对当前价格、版本、可用性、开放时间、兼容性等必须核验最新信息。
- 不要把广告宣传直接当作事实。

#### `decision-criteria-builder`

用途：建立决策标准。

输出：

```text
decision/02_criteria/criteria.md
```

示例：

| Criteria | Weight | Why it matters | Must-have |
|---|---:|---|---|
| Cost | 20 | 预算有限 | yes |
| Integration | 25 | 需要接入现有系统 | yes |
| Reliability | 20 | 影响长期使用 | yes |
| Learning curve | 10 | 团队上手速度 | no |
| Ecosystem | 15 | 扩展能力 | no |
| Risk | 10 | 采购和安全风险 | yes |

#### `option-comparison-matrix`

用途：按标准比较选项。

输出：

```text
decision/03_analysis/comparison-matrix.md
```

示例：

| Option | Cost | Capability | Risk | Fit | Evidence | Score |
|---|---:|---:|---:|---:|---|---:|

#### `tradeoff-analysis`

用途：分析权衡，不只给分。

输出：

```text
decision/03_analysis/tradeoff-analysis.md
```

必须回答：

1. 哪个选项综合最好？
2. 哪个选项最稳？
3. 哪个选项风险最大？
4. 哪个选项短期好、长期差？
5. 哪个选项长期好、短期成本高？
6. 哪些判断依赖用户偏好？
7. 哪些结论证据不足？

#### `decision-recommendation`

用途：生成最终推荐。

输出：

```text
decision/04_output/recommendation.md
```

推荐结构：

```markdown
# Decision Recommendation

## Recommended Option
[推荐选项]

## Why
[关键理由]

## Conditions
[在什么条件下成立]

## Alternatives
[备选方案]

## Risks
[风险]

## Validation Before Commitment
[最终决定前还要确认什么]

## Decision Log
[本次选择的依据]
```

### 4.5 Decision Research目录结构

```text
decision/
  00_brief/
    decision-brief.md
  01_options/
    option-index.jsonl
    options.md
  02_criteria/
    criteria.md
    weights.md
  03_analysis/
    comparison-matrix.md
    tradeoff-analysis.md
    sensitivity-analysis.md
  04_output/
    recommendation.md
    decision-log.md
```

---

## 5. 新增范式三：Risk / Procurement Research

### 5.1 定位

`risk-procurement-research`用于回答：

> 某个工具、供应商、服务、数据源、模型、开源项目或技术方案，是否值得引入？有哪些安全、合规、成本、运营和可持续性风险？

它比普通决策研究更强调：

1. 风险识别。
2. 安全审查。
3. 合规检查。
4. 供应商尽调。
5. 总拥有成本。
6. 运营可持续性。
7. 退出机制。
8. 采用建议。

### 5.2 适用场景

- 引入AI工具或Agent平台。
- 采用开源项目。
- 采购SaaS或安全产品。
- 使用第三方数据源。
- 选择培训/认证合作伙伴。
- 引入云服务、API、模型供应商。
- 评估供应商安全与合规风险。
- 评估是否把某个工具用于企业生产环境。

### 5.3 推荐skills

```text
risk-research-brief
vendor-source-diligence
security-risk-review
compliance-check
tco-operational-risk
adoption-recommendation
```

### 5.4 Skill说明

#### `risk-research-brief`

用途：明确评估对象、采用场景和风险边界。

输出：

```text
risk/00_brief/risk-brief.md
```

核心字段：

| 字段 | 说明 |
|---|---|
| Target | 评估对象 |
| Adoption Scenario | 采用场景 |
| Data Involved | 涉及数据 |
| Users | 使用者 |
| Criticality | 关键程度 |
| Deployment Mode | 部署方式 |
| Risk Appetite | 风险接受度 |
| Required Decision | 是否采用、如何采用 |

#### `vendor-source-diligence`

用途：供应商、项目、数据源尽调。

输出：

```text
risk/01_diligence/vendor-profile.md
risk/01_diligence/source-profile.md
```

检查项：

| 维度 | 问题 |
|---|---|
| Identity | 谁提供 |
| Business Stability | 是否稳定 |
| Reputation | 声誉如何 |
| Security Track Record | 是否有安全事件 |
| Maintenance | 是否持续维护 |
| License | 授权是否清晰 |
| Data Policy | 数据如何处理 |
| Support | 支持能力 |
| Lock-in | 是否锁定 |

#### `security-risk-review`

用途：安全风险审查。

输出：

```text
risk/02_security/security-risk.md
```

维度：

| 维度 | 示例问题 |
|---|---|
| Data Exposure | 是否上传敏感数据 |
| Access Control | 权限如何控制 |
| Secrets Handling | 密钥如何保存 |
| Supply Chain | 依赖是否可信 |
| Execution Risk | 是否执行外部代码 |
| Prompt Injection | 是否可能被外部内容污染 |
| Auditability | 是否可审计 |
| Isolation | 是否可隔离 |
| Incident Response | 出事后如何响应 |

#### `compliance-check`

用途：合规风险检查。

输出：

```text
risk/03_compliance/compliance-check.md
```

注意：该skill不应假装提供法律意见。它只能做合规风险研究和问题清单。

检查项：

| 维度 | 示例 |
|---|---|
| Privacy | 个人信息、隐私政策 |
| Data Residency | 数据存储位置 |
| Cross-border Transfer | 跨境传输 |
| License | 开源许可证 |
| Industry Regulation | 行业监管 |
| Contract Terms | 合同限制 |
| IP | 知识产权 |
| Export Control | 出口管制 |
| Procurement Policy | 企业采购政策 |

#### `tco-operational-risk`

用途：评估总拥有成本和运营风险。

输出：

```text
risk/04_operations/tco-operational-risk.md
```

维度：

| 维度 | 示例 |
|---|---|
| Direct Cost | 订阅、授权、服务费 |
| Integration Cost | 接入、开发、迁移 |
| Training Cost | 学习成本 |
| Operation Cost | 运维成本 |
| Switching Cost | 替换成本 |
| Lock-in Risk | 锁定风险 |
| Reliability | SLA、故障风险 |
| Scalability | 扩展能力 |
| Exit Plan | 退出方案 |

#### `adoption-recommendation`

用途：形成采用建议。

输出：

```text
risk/05_output/adoption-recommendation.md
```

推荐类型：

| 推荐 | 含义 |
|---|---|
| Adopt | 可采用 |
| Adopt with Controls | 可采用，但需控制措施 |
| Pilot Only | 仅试点 |
| Defer | 暂缓 |
| Reject | 不建议采用 |
| Need More Evidence | 证据不足 |

### 5.5 Risk / Procurement Research目录结构

```text
risk/
  00_brief/
    risk-brief.md
  01_diligence/
    vendor-profile.md
    source-profile.md
  02_security/
    security-risk.md
    threat-model.md
  03_compliance/
    compliance-check.md
    license-review.md
  04_operations/
    tco-operational-risk.md
    exit-plan.md
  05_output/
    adoption-recommendation.md
    risk-register.md
```

---

## 6. 新增范式四：Experience / Event Research

### 6.1 定位

`experience-event-research`用于回答：

> 如何围绕人、时间、地点、预算、偏好、风险和后勤约束，设计一次可执行的体验或活动？

它覆盖：

- 旅游规划。
- 会议组织。
- 沙龙活动。
- Workshop。
- 培训活动。
- 团建。
- 展会参观。
- 城市体验路线。
- 家庭出行。
- 小型闭门会。

它不只是“生成行程”，而是组织一次体验：目标、参与者、内容、节奏、后勤、风险、应急和复盘。

### 6.2 适用场景

用户常见表达：

```text
帮我安排一次三天两晚旅行。
帮我组织一次AI安全Workshop。
帮我设计一个半天的客户交流活动。
帮我规划一个团队团建。
帮我安排一次会议议程和执行清单。
帮我设计一次展会参观路线。
```

### 6.3 推荐skills

```text
experience-brief-framer
venue-destination-research
schedule-itinerary-planner
participant-experience-designer
logistics-risk-planner
event-runbook-writer
```

### 6.4 Skill说明

#### `experience-brief-framer`

用途：明确活动/体验目标、参与者、约束。

输出：

```text
event/00_brief/event-brief.md
```

核心字段：

| 字段 | 说明 |
|---|---|
| Purpose | 活动目的 |
| Participants | 参与者 |
| Date / Duration | 日期和时长 |
| Location | 地点 |
| Budget | 预算 |
| Preferences | 偏好 |
| Constraints | 约束 |
| Success Criteria | 成功标准 |

#### `venue-destination-research`

用途：研究地点、场地、目的地或路线节点。

输出：

```text
event/01_research/venue-options.md
event/01_research/destination-options.md
```

必须核验：

- 当前开放时间。
- 票务和预约。
- 交通时间。
- 价格。
- 天气。
- 场地可用性。
- 人流和安全风险。
- 签证或证件要求。
- 是否适合参与者画像。

涉及这些当前信息时，必须联网核验，不得只凭记忆。

#### `schedule-itinerary-planner`

用途：形成议程或行程。

输出：

```text
event/02_plan/itinerary.md
event/02_plan/schedule.md
```

设计原则：

1. 不要过度排满。
2. 留出交通和缓冲。
3. 区分必须项和可选项。
4. 考虑参与者体力和注意力。
5. 对会议活动要有节奏设计。
6. 对旅游要有天气备选。
7. 对培训/Workshop要有互动与反馈环节。

#### `participant-experience-designer`

用途：从参与者视角优化体验。

输出：

```text
event/03_experience/participant-journey.md
```

检查点：

| 阶段 | 问题 |
|---|---|
| Before | 参与者是否知道准备什么 |
| Arrival | 到达是否顺畅 |
| Opening | 开场是否清晰 |
| Main Flow | 节奏是否合理 |
| Breaks | 是否有缓冲 |
| Interaction | 是否有参与感 |
| Closing | 是否有收束 |
| After | 是否有后续跟进 |

#### `logistics-risk-planner`

用途：后勤和风险预案。

输出：

```text
event/04_logistics/logistics-plan.md
event/04_logistics/risk-contingency.md
```

后勤项：

- 交通。
- 住宿。
- 餐饮。
- 场地。
- 设备。
- 人员分工。
- 物料。
- 预算。
- 联系方式。
- 应急方案。

风险项：

| 风险 | 示例 |
|---|---|
| Weather | 天气影响 |
| Transport | 延误、堵车 |
| Health | 身体不适 |
| Venue | 场地不可用 |
| Equipment | 投影、网络、音响故障 |
| Attendance | 到场人数变化 |
| Budget | 超预算 |
| Safety | 安全事件 |

#### `event-runbook-writer`

用途：生成执行手册。

输出：

```text
event/05_runbook/event-runbook.md
```

结构：

```markdown
# Event Runbook

## Overview
## Timeline
## Roles and Responsibilities
## Venue and Logistics
## Materials
## Communication Plan
## Risk and Contingency
## Day-of Checklist
## Post-event Follow-up
```

### 6.5 Experience / Event目录结构

```text
event/
  00_brief/
    event-brief.md
    participant-profile.md
  01_research/
    venue-options.md
    destination-options.md
    source-index.jsonl
  02_plan/
    itinerary.md
    schedule.md
    agenda.md
  03_experience/
    participant-journey.md
    interaction-design.md
  04_logistics/
    logistics-plan.md
    risk-contingency.md
    budget.md
  05_runbook/
    event-runbook.md
    day-of-checklist.md
  06_review/
    post-event-review.md
```

---

## 7. 轻量Adapter：Content Selection

### 7.1 定位

`content-selection-adapter`用于娱乐和内容选择，不建议做成完整研究包。

适用场景：

- 选电影。
- 选书。
- 选游戏。
- 选播客。
- 选展览。
- 选演出。
- 选亲子活动。
- 选周末娱乐安排。

它底层主要复用：

```text
decision-research
experience-event-research
```

### 7.2 推荐结构

```text
content/
  preference-profile.md
  candidate-list.md
  comparison.md
  recommendation.md
```

### 7.3 推荐逻辑

1. 明确偏好。
2. 明确限制：时间、地点、年龄、预算、语言、平台。
3. 获取当前可用选项。
4. 对选项按偏好匹配。
5. 给出推荐和备选。
6. 如果涉及当前上映、演出、展览、票务、评分，需要联网核验。

### 7.4 为什么不做完整娱乐研究包

原因：

1. 娱乐选择通常低风险。
2. 多数是偏好匹配，不需要完整证据账本。
3. 当前可用性比深度研究更重要。
4. 可以用decision-research覆盖大部分需求。
5. 不应让主skill包被低价值场景稀释。

---

## 8. 与V2核心底座的关系

新增研究范式都应该复用V2底座：

```text
research-source-discovery
research-literature-access
research-note-capture
research-insight-log
research-evidence-ledger
research-synthesis
research-report-writer
research-quality-reviewer
```

但不同研究范式使用强度不同。

| 研究范式 | Source | Literature Access | Notes | Insights | Evidence | Review |
|---|---:|---:|---:|---:|---:|---:|
| Scientific | 强 | 强 | 强 | 强 | 强 | 强 |
| Product | 强 | 中 | 强 | 强 | 强 | 强 |
| Planning | 强 | 中 | 强 | 强 | 强 | 强 |
| Learning | 强 | 中 | 强 | 强 | 中 | 中 |
| Decision | 强 | 弱/中 | 中 | 中 | 中 | 强 |
| Risk/Procurement | 强 | 中 | 中 | 中 | 强 | 强 |
| Experience/Event | 中 | 弱 | 弱/中 | 中 | 弱/中 | 中 |

说明：

- `learning-research`会大量使用资料和摘录，但不一定总要形成严格证据账本。
- `decision-research`需要证据，但更强调标准、权重和权衡。
- `risk-procurement-research`需要强证据和强审查。
- `experience-event-research`更多依赖实时信息、约束和执行清单。

---

## 9. 推荐新增目录结构

在原`research-skill-pack`中新增：

```text
.opencode/
  skills/
    learning-goal-framer/
      SKILL.md
    learning-prerequisite-mapper/
      SKILL.md
    learning-resource-discovery/
      SKILL.md
    learning-path-designer/
      SKILL.md
    learning-practice-planner/
      SKILL.md
    learning-progress-reviewer/
      SKILL.md

    decision-brief-framer/
      SKILL.md
    option-discovery/
      SKILL.md
    decision-criteria-builder/
      SKILL.md
    option-comparison-matrix/
      SKILL.md
    tradeoff-analysis/
      SKILL.md
    decision-recommendation/
      SKILL.md

    risk-research-brief/
      SKILL.md
    vendor-source-diligence/
      SKILL.md
    security-risk-review/
      SKILL.md
    compliance-check/
      SKILL.md
    tco-operational-risk/
      SKILL.md
    adoption-recommendation/
      SKILL.md

    experience-brief-framer/
      SKILL.md
    venue-destination-research/
      SKILL.md
    schedule-itinerary-planner/
      SKILL.md
    participant-experience-designer/
      SKILL.md
    logistics-risk-planner/
      SKILL.md
    event-runbook-writer/
      SKILL.md

    content-selection-adapter/
      SKILL.md
    travel-adapter/
      SKILL.md
    conference-adapter/
      SKILL.md
    training-event-adapter/
      SKILL.md
```

但实施时不建议一次生成全部。应按优先级逐步增加。

---

## 10. 实施优先级

### P1：优先实现

```text
learning-goal-framer
learning-resource-discovery
learning-path-designer
decision-brief-framer
decision-criteria-builder
option-comparison-matrix
decision-recommendation
```

原因：

- 学习研究和决策研究最通用。
- 与现有课程、人才体系、技术学习、工具选型强相关。
- 能快速复用已有核心底座。

### P2：第二批实现

```text
risk-research-brief
vendor-source-diligence
security-risk-review
compliance-check
tco-operational-risk
adoption-recommendation
experience-brief-framer
venue-destination-research
schedule-itinerary-planner
logistics-risk-planner
event-runbook-writer
```

原因：

- 风险采购对企业和安全场景价值高。
- 活动/会议/旅游可覆盖大量生活和组织场景。
- 但需要更多实时信息核验和安全边界。

### P3：第三批实现

```text
content-selection-adapter
travel-adapter
conference-adapter
training-event-adapter
participant-experience-designer
learning-practice-planner
learning-progress-reviewer
tradeoff-analysis
```

原因：

- Adapter可以后置。
- 一些高级skill需要在基础流程跑通后再完善。
- 娱乐推荐价值较低，不应优先占用架构资源。

---

## 11. 端到端工作流示例

### 11.1 学习研究工作流

```text
User: 我想系统学习eBPF/XDP，用来支撑rSwitch论文和实现。

learning-goal-framer
  ↓
learning-prerequisite-mapper
  ↓
learning-resource-discovery
  ↓
research-literature-access
  ↓
research-note-capture
  ↓
research-insight-log
  ↓
learning-path-designer
  ↓
learning-practice-planner
  ↓
learning-progress-reviewer
```

输出：

```text
learning-brief.md
prerequisite-map.md
resource-list.md
learning-path.md
practice-plan.md
assessment-rubric.md
```

### 11.2 决策研究工作流

```text
User: OpenCode、Codex、Antigravity三者哪个更适合我的项目？

decision-brief-framer
  ↓
option-discovery
  ↓
decision-criteria-builder
  ↓
research-source-discovery
  ↓
option-comparison-matrix
  ↓
tradeoff-analysis
  ↓
decision-recommendation
  ↓
research-quality-reviewer
```

输出：

```text
decision-brief.md
criteria.md
comparison-matrix.md
tradeoff-analysis.md
recommendation.md
```

### 11.3 风险采购研究工作流

```text
User: 我们是否应该在企业内部引入某个AI Agent工具？

risk-research-brief
  ↓
vendor-source-diligence
  ↓
security-risk-review
  ↓
compliance-check
  ↓
tco-operational-risk
  ↓
adoption-recommendation
  ↓
research-quality-reviewer
```

输出：

```text
risk-brief.md
vendor-profile.md
security-risk.md
compliance-check.md
tco-operational-risk.md
adoption-recommendation.md
```

### 11.4 会议活动组织工作流

```text
User: 帮我组织一次半天的AI安全客户Workshop。

experience-brief-framer
  ↓
venue-destination-research
  ↓
schedule-itinerary-planner
  ↓
participant-experience-designer
  ↓
logistics-risk-planner
  ↓
event-runbook-writer
```

如果活动包含教学目标，可叠加：

```text
learning-goal-framer
learning-practice-planner
```

输出：

```text
event-brief.md
agenda.md
participant-journey.md
logistics-plan.md
event-runbook.md
```

### 11.5 旅游规划工作流

```text
User: 帮我安排一次三天两晚的京都旅行。

experience-brief-framer
  ↓
travel-adapter
  ↓
venue-destination-research
  ↓
decision-criteria-builder
  ↓
schedule-itinerary-planner
  ↓
logistics-risk-planner
  ↓
event-runbook-writer
```

必须联网核验：

- 天气。
- 交通。
- 景点开放时间。
- 票务预约。
- 酒店价格。
- 节假日和人流。
- 签证和入境规则。

---

## 12. 新增AGENTS.md建议规则

可以追加到项目级`AGENTS.md`：

```markdown
## Extended Research Mode Rules

When the user asks to learn something, choose a tool, evaluate adoption, organize an event, plan travel, or select entertainment:

1. Do not create a new domain-specific workflow immediately.
2. First classify the request into one of these research modes:
   - learning-research
   - decision-research
   - risk-procurement-research
   - experience-event-research
3. Use domain adapters only after selecting the research mode.
4. For learning tasks, clarify learning goal, baseline, application scenario, resources, path, practice, and assessment.
5. For decision tasks, clarify options, criteria, weights, constraints, deal-breakers, tradeoffs, and recommendation conditions.
6. For risk/procurement tasks, check vendor/source diligence, security risk, compliance risk, TCO, operational risk, and exit plan.
7. For experience/event tasks, check participants, time, location, budget, itinerary, logistics, risks, contingency, and runbook.
8. For travel, venue, events, tickets, weather, pricing, availability, legal requirements, or current schedules, verify up-to-date information.
9. For entertainment/content selection, prefer a lightweight decision workflow unless the user explicitly wants deep research.
10. Always separate evidence, preference, assumption, and recommendation.
```

---

## 13. Trigger设计建议

### 13.1 Learning Research触发

应触发：

```text
我想学X
帮我设计学习路线
我该先学什么
帮我找学习资料
我想准备某个考试/认证
帮我从零入门某领域
```

不应触发：

```text
解释一下这个概念
翻译这段话
帮我改一下PPT
```

### 13.2 Decision Research触发

应触发：

```text
A和B哪个好
帮我比较这些选项
我该选哪个
做一个选型分析
帮我做购买/采用建议
```

不应触发：

```text
告诉我A是什么
把A的文档总结一下
只帮我安装A
```

### 13.3 Risk / Procurement Research触发

应触发：

```text
这个工具能不能引入企业
这个供应商可靠吗
这个开源项目安全吗
这个SaaS合规吗
帮我做供应商尽调
帮我评估采购风险
```

不应触发：

```text
这个工具怎么用
帮我写个demo
帮我改bug
```

### 13.4 Experience / Event Research触发

应触发：

```text
帮我安排旅行
帮我组织会议
帮我做活动方案
帮我设计Workshop
帮我安排团建
帮我做行程
```

不应触发：

```text
今天北京天气如何
帮我写一封会议邀请邮件
帮我翻译日程
```

---

## 14. 输出质量门禁

### 14.1 Learning Research质量门禁

- 是否明确学习目标。
- 是否诊断当前基础。
- 是否列出先修依赖。
- 资源是否分级。
- 路径是否阶段化。
- 是否有练习。
- 是否有评估标准。
- 是否连接真实应用场景。

### 14.2 Decision Research质量门禁

- 是否明确决策问题。
- 是否列出完整候选项。
- 是否定义标准和权重。
- 是否区分must-have和nice-to-have。
- 是否说明一票否决项。
- 是否提供证据。
- 是否做权衡而不只是打分。
- 推荐是否有条件和风险。

### 14.3 Risk / Procurement Research质量门禁

- 是否明确采用场景。
- 是否做供应商/来源尽调。
- 是否检查安全风险。
- 是否检查合规风险。
- 是否分析TCO。
- 是否分析锁定和退出。
- 是否给出控制措施。
- 推荐是否分级。

### 14.4 Experience / Event Research质量门禁

- 是否明确参与者画像。
- 是否明确目标和成功标准。
- 是否核验当前信息。
- 时间安排是否可执行。
- 是否留出缓冲。
- 是否有后勤清单。
- 是否有风险预案。
- 是否有runbook。

---

## 15. 推荐实施路线

### Phase A：扩展计划冻结

目标：确认新增研究范式和边界。

交付物：

```text
本补充文档（research-skill-pack-expansion-addendum.md）经过Momus审查通过即视为Phase A交付。
不另外生成独立设计文档——本文档本身即为设计文档。
```

退出标准：

- 四类新增范式边界清楚。
- 与科研/产品/规划不冲突。
- Adapter不喧宾夺主。

QA验证场景：

```text
工具：人工审查 + Momus review
步骤：将本文档提交 Momus review，确认无 blocking issues
预期结果：Momus verdict = PASS 或 CONDITIONAL（无 REJECT）
```

### Phase B：Learning + Decision MVP

目标：先实现两个最高频通用包。

实现skills：

```text
learning-goal-framer
learning-resource-discovery
learning-path-designer
decision-brief-framer
decision-criteria-builder
option-comparison-matrix
decision-recommendation
```

交付物路径：

```text
packs/optional/research-skill-pack/.opencode/skills/learning-goal-framer/SKILL.md
packs/optional/research-skill-pack/.opencode/skills/learning-resource-discovery/SKILL.md
packs/optional/research-skill-pack/.opencode/skills/learning-path-designer/SKILL.md
packs/optional/research-skill-pack/.opencode/skills/decision-brief-framer/SKILL.md
packs/optional/research-skill-pack/.opencode/skills/decision-criteria-builder/SKILL.md
packs/optional/research-skill-pack/.opencode/skills/option-comparison-matrix/SKILL.md
packs/optional/research-skill-pack/.opencode/skills/decision-recommendation/SKILL.md
packs/optional/research-skill-pack/evals/trigger/learning-trigger-evals.json
packs/optional/research-skill-pack/evals/trigger/decision-trigger-evals.json
```

退出标准：

- 能生成学习路径。
- 能生成选型分析。
- 能与核心notes/evidence/review联动。

QA验证场景：

```text
工具：pytest, uv run
步骤：
  1. 确认7个SKILL.md已创建：glob packs/optional/research-skill-pack/.opencode/skills/{learning-*,decision-*,option-*}/SKILL.md
  2. 确认pack-manifest.json skills数组包含7个新条目，skill_count已更新
  3. 确认test_smoke_research_pack.py::TestFixtureIntegrity::test_all_skills_have_skill_md通过
  4. 确认evals/trigger/learning-trigger-evals.json和decision-trigger-evals.json存在
  5. 运行：uv run pytest tests/test_smoke_research_pack.py -v
  6. 运行：uv run packs/optional/research-skill-pack/scripts/run_trigger_evals.py
预期结果：
  - pytest全部通过
  - trigger eval harness输出total_checks > 0，包含learning和decision相关检查
```

### Phase C：Risk / Procurement MVP

目标：实现企业引入和供应商评估能力。

实现skills：

```text
risk-research-brief
vendor-source-diligence
security-risk-review
compliance-check
tco-operational-risk
adoption-recommendation
```

交付物路径：

```text
packs/optional/research-skill-pack/.opencode/skills/risk-research-brief/SKILL.md
packs/optional/research-skill-pack/.opencode/skills/vendor-source-diligence/SKILL.md
packs/optional/research-skill-pack/.opencode/skills/security-risk-review/SKILL.md
packs/optional/research-skill-pack/.opencode/skills/compliance-check/SKILL.md
packs/optional/research-skill-pack/.opencode/skills/tco-operational-risk/SKILL.md
packs/optional/research-skill-pack/.opencode/skills/adoption-recommendation/SKILL.md
packs/optional/research-skill-pack/evals/trigger/risk-procurement-trigger-evals.json
```

退出标准：

- 能形成采用建议。
- 能列出安全/合规/TCO/退出风险。
- 能给出Adopt / Pilot / Defer / Reject等分级结论。

QA验证场景：

```text
工具：pytest, uv run
步骤：
  1. 确认6个SKILL.md已创建：glob packs/optional/research-skill-pack/.opencode/skills/{risk-*,vendor-*,security-risk-*,compliance-*,tco-*,adoption-*}/SKILL.md
  2. 确认pack-manifest.json skills数组包含6个新条目，skill_count已更新
  3. 确认evals/trigger/risk-procurement-trigger-evals.json存在
  4. 运行：uv run pytest tests/test_smoke_research_pack.py -v
  5. 运行：uv run packs/optional/research-skill-pack/scripts/run_trigger_evals.py
预期结果：
  - pytest全部通过
  - trigger eval harness包含risk/procurement相关检查
```

### Phase D：Experience / Event MVP

目标：支持会议、Workshop、旅游、团建等活动组织。

实现skills：

```text
experience-brief-framer
venue-destination-research
schedule-itinerary-planner
logistics-risk-planner
event-runbook-writer
```

交付物路径：

```text
packs/optional/research-skill-pack/.opencode/skills/experience-brief-framer/SKILL.md
packs/optional/research-skill-pack/.opencode/skills/venue-destination-research/SKILL.md
packs/optional/research-skill-pack/.opencode/skills/schedule-itinerary-planner/SKILL.md
packs/optional/research-skill-pack/.opencode/skills/logistics-risk-planner/SKILL.md
packs/optional/research-skill-pack/.opencode/skills/event-runbook-writer/SKILL.md
packs/optional/research-skill-pack/evals/trigger/experience-event-trigger-evals.json
```

退出标准：

- 能生成可执行活动方案。
- 能生成后勤与风险预案。
- 能区分旅行、会议、培训adapter。

QA验证场景：

```text
工具：pytest, uv run
步骤：
  1. 确认5个SKILL.md已创建
  2. 确认pack-manifest.json已更新
  3. 确认evals/trigger/experience-event-trigger-evals.json存在
  4. 运行：uv run pytest tests/test_smoke_research_pack.py -v
  5. 运行：uv run packs/optional/research-skill-pack/scripts/run_trigger_evals.py
预期结果：
  - pytest全部通过
  - trigger eval harness包含experience/event相关检查
```

### Phase E：Adapter与评测

目标：补充轻量adapter和trigger evals。

实现：

```text
travel-adapter
conference-adapter
training-event-adapter
content-selection-adapter
```

交付物路径：

```text
packs/optional/research-skill-pack/.opencode/skills/travel-adapter/SKILL.md
packs/optional/research-skill-pack/.opencode/skills/conference-adapter/SKILL.md
packs/optional/research-skill-pack/.opencode/skills/training-event-adapter/SKILL.md
packs/optional/research-skill-pack/.opencode/skills/content-selection-adapter/SKILL.md
packs/optional/research-skill-pack/evals/trigger/adapter-trigger-evals.json
```

退出标准：

- Adapter不复制主流程。
- Adapter只补充领域字段、约束和检查清单。
- 每类新增范式至少有3个trigger正例和2个反例。
- 每类新增范式至少有1个端到端output eval。

QA验证场景：

```text
工具：pytest, uv run
步骤：
  1. 确认4个adapter SKILL.md已创建
  2. 确认pack-manifest.json已更新，skill_count反映全部新增
  3. 确认evals/trigger/adapter-trigger-evals.json存在
  4. 运行：uv run pytest tests/test_smoke_research_pack.py -v
  5. 运行：uv run packs/optional/research-skill-pack/scripts/run_trigger_evals.py
  6. 验证每个新增范式（learning/decision/risk/experience）的trigger eval至少有3个正例和2个反例
  7. 验证trigger eval harness total_checks覆盖所有新增范式
预期结果：
  - pytest全部通过
  - trigger eval harness total_checks > 前一个Phase的值
  - 每个范式的trigger precision >= 0.8
```

---

## 16. 与当前V2计划的合并建议

> **合并目标文件**：`dev_reference/skills_design_plan/research-skill-pack-plan-v2.md`
>
> 注意：`.sisyphus/plans/research-skill-pack-implementation.md`是MVP的可执行实施计划，已完成，不再修改。本addendum的内容应作为V2设计文档的扩展章节追加到`dev_reference/skills_design_plan/research-skill-pack-plan-v2.md`末尾。

当前V2计划已经包含：

```text
research-router
research-brief-framer
research-source-discovery
research-literature-access
research-note-capture
research-insight-log
research-evidence-ledger
research-synthesis
research-report-writer
research-quality-reviewer
```

建议在V2计划之后追加一个章节：

```text
## Extended Research Modes
```

新增内容：

```text
learning-research
decision-research
risk-procurement-research
experience-event-research
```

但不要把这些全部塞进MVP。MVP仍然保持核心10个skills。扩展研究范式作为Phase 3之后的能力演进。

推荐最终路线：

```text
MVP Core
  ↓
Scientific / Product / Planning
  ↓
Learning / Decision
  ↓
Risk-Procurement
  ↓
Experience-Event
  ↓
Adapters
```

---

## 17. 最终建议

新增领域研究能力时，应坚持三个原则：

### 原则一：先抽象范式，再做领域adapter

不要直接做旅游、娱乐、会议等独立大包。先判断它属于：

```text
learning
decision
risk-procurement
experience-event
```

再用adapter补充字段。

### 原则二：高价值、高复用优先

优先顺序：

```text
learning-research
decision-research
risk-procurement-research
experience-event-research
content-selection-adapter
```

### 原则三：所有研究都复用核心底座

无论哪类研究，都尽量复用：

```text
source discovery
literature access
note capture
insight log
evidence ledger
synthesis
quality review
```

只是使用强度不同。

最终结论：

> 我们不应该把research-skill-pack做成“无数领域模板集合”，而应该把它做成“少数高复用研究范式 + 轻量领域adapter”的研究工作台。学习、决策、风险采购、体验活动这四类，是科研、产品、规划之后最值得补充的通用研究能力。
