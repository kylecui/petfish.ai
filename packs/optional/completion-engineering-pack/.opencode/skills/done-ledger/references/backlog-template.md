# Backlog Examples & Workflows — done-ledger

SKILL.md owns the rules; this file owns the practice. Two complete backlog
examples from different domains, the workflow that turns a leftover into the
anchor of a follow-up contract, and a session-level rollup pattern.

---

## Example 1: Bug-fix task (gate cap + waiting-on-user mixed)

Scenario: the login-timeout fix passed on round 2, but load-test coverage
analysis and a registration-flow sweep were blocked by the 3-round cap.

`.petfish/done/fix-login-timeout/backlog.md`:

```markdown
# Backlog — fix-login-timeout

> 任务：登录接口偶发超时修复 · verdict：VERIFIED_DONE（round 2/3） · 2026-09-20

## 等待用户

- [ ] 测试账号权限未开通——压测报告的生成命令写在verdict.json evidence[1]，拿到账号即可复跑

## Gate触顶遗留

- [ ] 压测覆盖率分析未做（round 3额度让位给了复现阈值核对）——下个迭代排期
- [ ] flaky用例test_login_4321待重跑——CI侧观察一周再定，不阻塞本任务关闭

## 范围外建议

- [ ] 注册流程疑似同款超时（契约out_of_scope声明过）——单开任务，勿顺手修
- [ ] 连接池框架替换构想——记录备查，无行动承诺

## 已归档

- [x] 会话过期阈值硬编码——round 2改为配置项——2026-09-20
```

---

## Example 2: Research task (dominated by out-of-scope suggestions)

Scenario: a competitor-scan report was delivered on round 1; the research
process itself surfaced a pile of "while we were there" findings.

`.petfish/done/competitor-scan-q3/backlog.md`:

```markdown
# Backlog — competitor-scan-q3

> 任务：Q3竞品扫描报告 · verdict：VERIFIED_DONE（round 1/3） · 2026-09-20

## 等待用户

（无）

## Gate触顶遗留

（无——一轮过门）

## 范围外建议

- [ ] 厂商B的定价页改版信号——不在本次扫描维度内，但对Q4定价策略有参考价值
- [ ] 两家厂商的招聘动向暗示新产品线——证据链弱，仅存疑
- [ ] 报告第四章可独立扩写成白皮书——需用户判断投入产出

## 已归档

- [x] 厂商A数据源口径不一致——round 1中已换源重跑——2026-09-20
```

Research-style leftovers are mostly out-of-scope suggestions: their value is
in being recorded, not executed. Resist the "might as well also" reflex —
each suggestion deserves its own contract with its own predicates, not a
sneaky extension of a task that just closed.

---

## Workflow: a backlog item becomes the anchor of the next contract

The backlog is not a landfill; it is the staging area for future work. Two
legitimate paths forward:

1. **Promotion to a new task.** The user green-lights one out-of-scope
   suggestion → the new contract's anchor cites the entry verbatim
   (`"type": "todo"`, ref pointing at `backlog:<task-slug>` plus the entry
   line). Tick the old entry into 已归档 with a note: "handed over to
   `<new-task-slug>`".
2. **Cross-session resumption.** For 等待用户 entries, when the user returns,
   restate the waiting condition and the resume path (read the remaining[]
   array from verdict.json). Continued work still goes through done-gate —
   the original contract is reusable within its 14-day TTL; after expiry,
   write a fresh contract citing the old backlog entry as the anchor.

Forbidden path: moving backlog entries into the todo queue. A pending todo
wakes the platform's auto-continuation machinery; the historical incident was
one "commit after user confirmation" pending todo triggering 200+ empty
continuation rounds.

---

## Multi-task session rollup

When one session closes several tasks (e.g. a PR carrying three fixes), each
task keeps its own backlog, and the closing message gives the user a one-line
rollup:

```text
本session收尾3个任务：
- fix-login-timeout → VERIFIED_DONE（2轮）· backlog 4条
- docs-migration-guide → VERIFIED_DONE（1轮）· backlog 1条
- fix-typo-config → SKIPPED（用户要求跳过流程）· 留痕1条
```

The rollup lets the user see, at session granularity, which work was truly
finished, which landed degraded, and which bypassed the process — instead of
excavating three directories to reconstruct the picture.

---

## Writing discipline

- One line per entry, three elements: description, source (waiting / gate cap /
  out-of-scope), suggested timing
- Waiting-on-user entries must also be spoken aloud in the conversation; the
  backlog line exists for cross-session recovery only
- Never delete archived entries — this file ships with the repo, and its
  history lines are the audit trail of "what was left, and how it later went
  away"
