---
name: product-validation-planner
description: 设计产品验证计划，围绕假设清单、最小MVP、量化成功标准与决策树，降低投入前不确定性。Use when the user says "验证计划", "validation plan", "MVP", "假设验证", "hypothesis testing", "产品验证", "product validation", "success metrics", "go/pivot/kill", "决策树", "decision tree", or "怎么验证这个想法".
compatibility: opencode
license: Apache-2.0
---

## 作用/Purpose

将“想法可不可行”转为可执行验证路径，优先验证高风险假设而非直接开发。该skill必须输出：
1) 可检验假设清单；
2) 最小化验证实验与MVP范围；
3) 含 proceed/pivot/kill 的决策规则。

输出应支持阶段性投入决策，而不是泛化“先做再看”。

---

## 触发场景/Trigger Scenarios

- 用户提出“验证计划 / validation plan / 假设验证”
- 需要定义MVP并控制试错成本
- 需要设计 hypothesis testing 与 success metrics
- 需要回答“怎么验证这个想法”并给出具体实验路径
- 需要建立 go/pivot/kill 的决策树用于里程碑评审

---

## 输入/Input

- opportunity map（机会地图与优先级）
- product hypotheses（产品假设与风险假设）
- resource constraints（时间、人力、预算、技术约束）
- 可选：历史实验结果、现有指标基线

---

## 输出/Output

- `hypothesis-list.md`
- `mvp-plan.md`
- `validation-experiments.md`
- `decision-tree.md`

---

## 工作流/Workflow

1. 识别最风险假设（价值、可用性、可行性、增长等）。
2. 将假设改写为可测试、可证伪的验证命题。
3. 设计最小实验（原型、landing page、手动服务、A/B等）。
4. 定义成功/失败标准，要求可量化且可在窗口期观测。
5. 规划MVP最小范围，剔除非关键能力与过度实现。
6. 构建决策树：达到阈值则 proceed，未达阈值则 pivot/kill。
7. 估算资源消耗与执行顺序，明确关键依赖。
8. 输出验证节奏与复盘机制，约束决策漂移。

---

## 质量门禁/Quality Gates

- 必须至少包含1条可测试假设（testable hypothesis）。
- 每条核心假设必须配套量化成功标准（非定性口号）。
- MVP范围必须满足“最小可验证”，不得夹带大规模功能。
- 决策树必须包含 kill/pivot 分支，不能仅有“继续推进”。
- 实验设计必须说明采样窗口、数据来源与判定阈值。

---

## Gotchas/注意事项

- 不要把“上线后看数据”当作验证方案。
- 不要把MVP做成v1.0，应优先验证关键不确定性。
- 量化指标需防止虚荣指标（vanity metrics）误导决策。
- 失败实验不是失败项目，关键是是否快速收敛认知。
- 决策树应预先冻结阈值，避免事后解释偏差。

---

## 关联资源

- None (standalone)
