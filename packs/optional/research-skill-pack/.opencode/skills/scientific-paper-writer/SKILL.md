---
name: scientific-paper-writer
description: 科研论文写作与骨架生成：基于research brief、evidence ledger、synthesis和实验结果产出paper outline与paper draft，强化contribution framing、related work组织与claim↔evaluation闭环。Use when users ask “写论文/paper writing/introduction/论文草稿/paper draft/论文骨架/paper outline/contribution framing/related work”.
compatibility: opencode
license: Apache-2.0
---

## 作用/Purpose

将研究材料系统化转译为可投稿论文结构，确保“主张—证据—评估—结论”闭环成立。该skill不只生成文本，更强调论证边界、贡献定位和评估对应关系。

---

## 触发场景/Trigger Scenarios

- 已有实验与分析结果，需要快速形成论文骨架或初稿
- 需要重构引言、贡献声明与相关工作，避免流水账式写法
- 需要确保evaluation section逐条回应贡献主张
- 需要将evidence ledger中的证据映射到论文叙事结构

---

## 输入/Input

- research brief（问题定义、范围、目标）
- evidence ledger（证据与来源映射）
- synthesis outputs（关键发现、矛盾、边界）
- experiment results（主实验、baseline、ablation、统计结果）
- 可选：目标会议模板与篇幅限制

---

## 输出/Output

- `paper-outline.md`（章节骨架）
- `paper-draft.md`（正文草稿）
- `related-work.md`（分类式相关工作草稿）
- `claim-evaluation-map.md`（贡献-评估映射）

---

## 工作流/Workflow

1. **整理贡献声明** — 将贡献拆解为可验证条目，限制语言强度与证据一致
2. **生成论文骨架** — 按标准CS结构填入每节目标、证据入口和预期结论
3. **组织related work** — 按主题/路线分类，明确与本工作的关系与差异
4. **构建evaluation叙事** — 建立 claim ↔ experiment ↔ result 的一一映射
5. **补充讨论与局限** — 写清适用边界、失败场景、未覆盖问题
6. **压缩摘要** — 在摘要中交代问题、方法、核心结果（含定量或具体发现）
7. **一致性审查** — 检查术语、图表引用、章节逻辑和证据覆盖率

---

## 质量门禁/Quality Gates

- 每条 contribution claim 必须可映射到至少一项 evaluation result
- related work 必须覆盖 evidence ledger 来源的 **≥80%**（按核心来源计）
- limitations 必须是实质性边界，不得伪装成“未来工作”套话
- abstract 必须包含定量结果或具体发现，不能只写“we propose X”

---

## Gotchas/注意事项

- 不要把“方法介绍”写成“贡献证明”；证明在evaluation里
- 不要把related work写成逐篇摘要，应围绕研究问题组织比较
- 不要回避负结果；边界条件通常决定论文可信度
- 不要让contribution口径在标题、摘要、引言、结论中前后漂移
- 不要用空泛形容词（novel, effective, robust）替代可核验证据

---

## 关联资源

- References: `references/paper-writing-rules.md`
- Assets: `assets/paper-outline-template.md`, `assets/related-work-template.md`
