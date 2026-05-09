---
name: planning-environment-scanner
description: 环境扫描与外部趋势分析（PESTLE、趋势雷达、信号识别），将外部变量转化为战略研究输入。Use when the user says "环境扫描", "PESTLE", "趋势分析", "trend analysis", "external scanning", "macro environment", "趋势雷达", "trend radar", "信号识别", "weak signals", "外部风险", or "外部机会".
compatibility: opencode
license: Apache-2.0
---

## 作用/Purpose

将宏观环境中的政治、经济、社会、技术、法律、环境变量系统化扫描，并沉淀为可用于后续情景规划与政策研究的输入证据。该skill必须覆盖：
1) PESTLE维度下的关键趋势与驱动因素识别；
2) 弱信号、早期变化与潜在拐点记录；
3) 对战略问题的相关性筛选与优先级排序。

输出应支持后续规划链路，而不是停留在“信息汇总”。

---

## 触发场景/Trigger Scenarios

- 用户要求“环境扫描 / PESTLE / macro environment / external scanning”
- 需要建立趋势雷达并识别未来3-5年的外部变化
- 需要从政策、市场、技术与社会变化中提取战略信号
- 团队需要为情景规划提供可信的外部变量输入
- 需要构建规划前的外部风险与机会基线

---

## 输入/Input

- planning brief（规划目标、时间跨度、决策边界）
- scope definition（行业、地域、政策边界、目标群体）
- baseline assumptions（当前战略假设与已知约束）
- 可选：既有研究笔记、行业报告、历史环境扫描文档

---

## 输出/Output

- `environment-scan.md`
- `trend-radar.md`
- `signal-register.md`

---

## 工作流/Workflow

1. 定义扫描边界：时间跨度、地理范围、行业范围与决策问题映射。
2. 按PESTLE建立扫描框架，并明确每个维度的观察指标。
3. 调用`research-source-discovery`收集多源材料，建立来源清单与可信度分层。
4. 抽取趋势、驱动因素与弱信号，记录变化方向、速度与影响对象。
5. 使用`research-evidence-ledger`登记关键证据，区分事实、推断与不确定性。
6. 构建趋势雷达并对信号进行优先级排序，标注触发条件与监测频率。
7. 输出对后续`planning-scenario-planner`与`planning-policy-researcher`可直接复用的外部变量包。

---

## 质量门禁/Quality Gates

- PESTLE六个维度必须全部覆盖，不得缺维。
- 每条关键趋势必须有来源与证据编号可追溯。
- 必须显式区分“确定趋势”与“弱信号/待验证变化”。
- 趋势评估需包含影响方向、影响范围与时间窗口。
- 至少识别3条与战略决策直接相关的高优先级外部变量。
- 输出需包含可供后续情景规划复用的标准化变量列表。

---

## Gotchas/注意事项

- 不要把短期新闻波动误判为长期结构性趋势。
- 不要只关注技术维度，忽略法律与社会变量的约束。
- 不要在证据不足时给出确定性判断，应标记不确定性。
- 不要把“信息量大”误当成“战略相关性高”。
- 不要跳过信号监测机制，否则无法持续更新扫描结论。

---

## 关联资源

- `research-source-discovery`
- `research-evidence-ledger`
- `research-synthesis`
- `planning-stakeholder-analyst`
- `planning-scenario-planner`
