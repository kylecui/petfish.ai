---
name: research-supervisor-bridge
description: 上游导师技能桥：指导按需获取并运行 HKUSTDial/Supervisor-Skills 与 yinwu01/Ducktor（原版博导经验技能），含许可证告知（Supervisor为CC BY-NC-SA 4.0，商用需上游授权）、运行时装载步骤、与 PEtFiSh 自研 research-mentor-cards 的逐能力对照表。用于 Supervisor-Skills、Ducktor、原版导师技能、上游对比、mentor对比、博导经验原版。不向上游仓库提交内容，不将其内容并入本pack。
metadata:
  version: 1.0.0
  author: PEtFiSh
---

# Research Supervisor Bridge — 上游导师技能桥

PEtFiSh 自研的 `research-mentor-cards` 与上游原版是**两个可选项**：本 skill 负责"想用原版时"的合规获取路径与逐能力对照。**本 pack 不收录、不改编、不重分发上游任何内容**。

## 上游仓库与许可证（使用前必读）

| 仓库 | 内容 | 许可证 | 商用 |
|---|---|---|---|
| HKUSTDial/Supervisor-Skills | 12个skill（idea-evaluator、deep-research、figure-designer、paper-writer 等）+ 博导经验 handbook（双语） | **CC BY-NC-SA 4.0**（README徽章明确） | 非商业用途按许可条款使用；**商用需向上游获得授权**（上游已与百度/豆包有授权合作先例，联系其官方渠道） |
| yinwu01/Ducktor | 把 Supervisor-Skills 包装为导师卡片插件（多平台：Claude/Codex/Cursor） | 混合（仓库内 LICENSES/ 分文件：MIT、CC-BY-4.0、CC-BY-NC-SA-4.0） | **逐文件自查许可证**后再用于对应用途 |

## 运行时装载步骤（不并入 PEtFiSh packs）

1. 征得用户确认（告知 NC 许可证含义：非商业可用、需署名、以相同方式共享、商用需授权）
2. 克隆到用户目录（**禁止**克隆进任何 packs/ 或 .opencode/skills/ 仓库目录）。跨平台两步走——目录创建用 uv 一行命令，克隆用 git（任意 shell 通用）：
   ```bash
   uv run python -c "from pathlib import Path; p = Path.home() / '.local' / 'share' / 'opencode' / 'upstream'; p.mkdir(parents=True, exist_ok=True); print(p)"
   git clone https://github.com/HKUSTDial/Supervisor-Skills.git <上一步打印的绝对路径>/supervisor-skills
   git clone https://github.com/yinwu01/Ducktor.git <上一步打印的绝对路径>/ducktor
   ```
3. 按上游自己的 INSTALL.md/插件说明接入平台（Ducktor 提供 claude/codex/cursor 插件清单）
4. 引用其内容产出时遵守 CC BY-NC-SA：署名 HKUSTDial/Supervisor-Skills、注明许可、以相同许可共享衍生文本

## 与 PEtFiSh 自研能力的逐能力对照

| 能力 | 上游 skill | PEtFiSh 对应 | 差异 |
|---|---|---|---|
| 综述级文献调研 | deep-research | research-router→…→research-synthesis 全链路 + scientific-literature-review | 上游单技能含 self-adversarial/hedge-calibration 参考；PEtFiSh 按证据链拆分且证据结构化（JSONL账本） |
| Idea 评估 | idea-evaluator | research-mentor-cards I 卡组（部分覆盖）+ scientific-gap-finder | 上游有独立评估器；PEtFiSh 以 I 系列对抗式提问覆盖部分场景 |
| 论文正文写作 | paper-writer / intro-drafter | scientific-paper-writer | 上游证据门控写作；PEtFiSh 走 evidence-ledger→report 链 |
| 论文润色 | paper-polish | petfish-style-rewriter（风格向） | 上游面向学术忠实润色；PEtFiSh 面向风格人格化，学术场景功能部分重叠 |
| 投稿前审查/审稿回复 | pre-submission-reviewer / rebuttal-guidance | scientific-review-rebuttal | 功能对应 |
| 论文模板 | tech-paper-template / benchmark-paper-template | scientific-paper-writer 的 paper-outline/related-work 模板 | 上游模板粒度更细（分论文类型） |
| 科研绘图 | figure-designer | **无对应（真实缺口）** | 想用选上游；想贡献自研实现欢迎提 issue |
| 图重建为Draw.io | drawio-reconstruction | drawio-course-diagrams（课程域） | 领域不同，能力部分重叠 |
| 导师经验卡 | Ducktor cards（W01-W14 等，博导经验） | research-mentor-cards（14张原创卡，方法论文献引用） | 上游卡源=博导实战经验；PEtFiSh 卡源=公开方法论文献+内部实践，分级体系不同（见对照模式） |
| Vibe research 流程 | vibe-research-workflow | **无独立对应** | 上游独有概念 |

## 对照模式使用建议

- 同一问题分别用两侧跑一遍（例：都用各自的 idea 评估路径），对比输出结构后择优固化到自己的工作流
- 对比结论若沉淀为改进建议：PEtFiSh 侧提 issue；上游侧按其 CONTRIBUTING.md 走，**不要**在本仓库 issue 里指挥上游
- 永远不要为了"对齐上游"把 NC 内容搬进 PEtFiSh pack——机制可学，内容须原创

## MUST DO

- 装载前必须向用户复述 NC 许可证的三条含义（署名/非商业/相同方式共享）
- 克隆目标目录必须是用户目录下的 upstream 区，不得进任何被安装的 pack 路径

## MUST NOT DO

- 禁止把上游 SKILL.md/handbook 内容复制进本 pack 或任何 PEtFiSh 产物
- 禁止代表用户接受许可证条款——用户必须自行确认商用授权问题
- 禁止向上游仓库提交任何内容（跨仓库保护：反馈走上游自己的 issue/CONTRIBUTING 流程）
