---
name: done-ledger
description: 任务收尾后的遗留分流与待办整理。Use when 遗留分流、还有下一步吗、收尾整理、遗留事项、待办整理、任务收尾清单, backlog, leftover triage, wrap up, end-of-task leftovers, remaining work triage. gate触顶与范围外的遗留只进backlog.md永不进todo（防无限循环）；等用户的项todo标completed并在对话明示等待；范围内未完成回done-gate过门。
compatibility: opencode
metadata:
  version: "1.0.0"
  author: "Petfish"
---

# Done Ledger — 遗留分流与待办整理

## Purpose

任务收尾时"还可以做X"的冲动是无限的，todo队列不是垃圾桶。done-ledger在任务结束时把所有遗留强制分流：该回门的回门，该记的记backlog，等用户的明说等待。核心规则一条：**gate触顶后的遗留与范围外建议永不进todo**——pending待办会喂给平台的自动继续机制，造成无限循环。

## Triggers

触发短语：遗留分流、还有下一步吗、收尾整理、遗留事项、待办整理、任务收尾清单、backlog、leftover triage、wrap up、end-of-task leftovers、remaining work triage

触发判定只认上述组合词——裸词done与单独的完成二字因误报风险被消毒。

## 适用边界

任务临近结束或已过done-gate门时，用本skill处理遗留的归宿。开工建契约与过门判定归done-gate管——本skill只管剩下的怎么放。纯翻译与简单问答类请求无遗留可分流，不触发。

## 遗留分流表（唯一真值）

| 遗留类型 | 去向 | 禁止 |
|---|---|---|
| in-scope未完成（gate循环内） | 回done-gate Phase B继续过门 | 不得绕门直接宣称 |
| gate触顶（3轮用尽）后的所有遗留 | backlog.md或对话明示 | **永不进todo** |
| out-of-scope建议 | backlog.md | **禁建todo** |
| blocked-on-user | todo标completed+对话明示等待项 | 禁止留pending todo |

### 为什么触顶遗留不进todo

外部todo continuation hook对pending状态无限触发——本仓库曾因一个"用户确认后提交"的pending todo触发200+次无效自动继续。遗留进todo等于重新点燃循环。分流到backlog.md既不丢信息，也不喂给自动机制。

## blocked-on-user处理（todo语义：blocked≠pending）

等用户的项（缺部署凭证、等A/B决策等）：

1. 对应todo**标completed**——agent能自主完成的部分已做完，剩余部分agent无法推进
2. 回复中明示等待：等什么、用户回来后从哪继续（引用verdict.json的remaining[]）
3. 需跨session跟进的，在backlog.md的"等待用户"段落记一行留档

## backlog.md规范

位置：`.petfish/done/<task-slug>/backlog.md`，与contract.json、verdict.json同目录。格式模板、条目生命周期与写作规则见 `references/backlog-template.md`。硬规则重申一条：触顶遗留与范围外建议的归宿是backlog，不是todo。

## State Files（状态文件）

与done-gate共用 `.petfish/done/<task-slug>/` 目录：contract.json与verdict.json由done-gate写入，backlog.md由本skill维护。verdict的remaining[]是分流的输入清单。

## 已知边界（诚实声明）

F2的典型形态是agent从不宣称任务完成、只在行文里无限"还可以做X"——此时gate和本skill都不会被触发。这是已知残余风险，接受并记录（gateway的开放契约提醒部分缓解）。

## Must do

- 任务收尾时逐项过分流表，每条遗留有明确去向
- 等用户的项：todo标completed+回复明示等待内容与恢复条件
- backlog条目带来源与建议处理时机

## Must not do

- 禁止把gate触顶遗留或范围外建议写成todo（新建pending不行，转pending也不行）
- 禁止用"顺便再做一下"处理范围外建议
- 禁止把backlog当成绕过gate的通道——in-scope未完成必须回gate
- 禁止删除已归档条目（审计留痕）
