# Contract Case Studies — done-gate

This file carries what SKILL.md deliberately omits: full lifecycle case studies,
a second-domain sample, and design mistakes that the mechanical checker cannot
catch. Field definitions, tier rules, and trigger phrases live in SKILL.md —
that file is the single source of truth; nothing here repeats it.

---

## Case 1: Bug fix, full lifecycle (contract → failure → amendment → pass)

User request, verbatim: "登录接口偶发超时，修复它，别动其他接口。"

**Round 1 kickoff** — write `.petfish/done/fix-login-timeout/contract.json`:

```json
{
  "revision": 1,
  "amendments": [],
  "critical": false,
  "anchor": {
    "type": "user_request",
    "ref": "登录接口偶发超时，修复它，别动其他接口"
  },
  "outcome": "登录接口在压测脚本下无超时复发，相关测试全绿",
  "constraints": ["只许改src/auth/目录", "数据库schema保持不动"],
  "verifications": [
    {"type": "command", "run": "uv run pytest tests/auth/ -q", "expect": "exit 0"},
    {"type": "artifact", "path": "src/auth/session.py", "contains": "retry_budget"},
    {"type": "judge", "criteria": "超时原因分析落在注释里，能看懂为何这样修"}
  ],
  "blocked_if": ["需要用户提供测试账号"],
  "out_of_scope": ["注册流程的同款问题", "全站超时治理"]
}
```

One judge-type predicate is present → the mechanical signal forces the
independent-verifier tier for this task.

**Round 1 gate: FAIL.** The load script still reproduces the timeout twice.
pytest is green while the reproduction script is red — the predicates never
covered the real failure path. Swapping assertions silently at this point is
forbidden; the change goes through a logged amendment:

```json
{
  "revision": 2,
  "amendments": [
    {
      "reason": "round 1 load-test reproduced the timeout; pytest missed the real path, add a reproduction threshold check",
      "change": "new command predicate: 200-iteration load loop with zero timeouts (expect: exit 0)"
    }
  ]
}
```

Note the direction: this amendment **tightens** (adds a predicate). A loosening
(drop a predicate, lower an expectation) after a failed gate must be announced
to the user inside the verdict — what was loosened, and why.

**Round 2 gate: PASS.** Write `.petfish/done/fix-login-timeout/verdict.json`:

```json
{
  "verdict": "VERIFIED_DONE",
  "revision": 2,
  "round": 2,
  "evidence": [
    "pytest tests/auth/ -q → exit 0 (14 passed)",
    "load loop 200 iterations → exit 0, zero timeouts",
    "src/auth/session.py:47 contains retry_budget = 3",
    "session.py comment block explains the root cause: unbounded retries stacked on missing backoff"
  ],
  "remaining": [],
  "classified_leftovers": {
    "to_backlog": ["registration flow likely has the same timeout (declared out_of_scope)"]
  }
}
```

---

## Case 2: Documentation task (artifact + judge predicates, no test suite)

User request, verbatim: "把这三个模块的接口变化写进docs，评审人要能看懂迁移路径。"

```json
{
  "revision": 1,
  "amendments": [],
  "critical": false,
  "anchor": {
    "type": "user_request",
    "ref": "把这三个模块的接口变化写进docs，评审人要能看懂迁移路径"
  },
  "outcome": "docs/migration.md覆盖全部三个模块的接口变化，读者按文档可独立完成迁移",
  "constraints": ["不改动源码", "不删除docs/migration.md既有章节"],
  "verifications": [
    {"type": "artifact", "path": "docs/migration.md", "contains": "module-a"},
    {"type": "artifact", "path": "docs/migration.md", "contains": "module-c"},
    {"type": "judge", "criteria": "任选一个接口变化，仅凭文档能写出正确的调用改动"}
  ],
  "blocked_if": ["接口变更清单尚未定稿"],
  "out_of_scope": ["旧版本文档回填", "英文翻译"]
}
```

The classic trap for documentation tasks: every predicate is green yet the
content is hollow. `contains: "module-a"` proves the topic was mentioned, not
that it was explained. That is exactly why the judge predicate exists — and why
it forces the verifier tier: an independent checker walks the migration path
using the document alone.

---

## Design mistakes the script cannot catch

`check_contract.py` intercepts tautologies and missing fields. Four mistakes
slip past it and gut the gate anyway — self-review these before locking a
contract:

1. **Activity-shaped outcome.** "写完迁移文档" is an activity; "读者凭文档可独立迁移"
   is a result. An activity outcome paired with file-exists predicates stamps
   existence, not effect.
2. **Predicates aimed at the wrong target.** Outcome says the timeout is gone,
   predicates only check that pytest passes — green tests do not prove the
   failure path was fixed (Case 1 round 1 failed in precisely this way). Each
   predicate must answer: when this passes, which part of the outcome is proven?
3. **Constraints missing the forbidden zone.** If the user's phrase
   "别动其他接口" never lands in constraints, nothing stops a round-2 refactor
   of the registration flow from sneaking in.
4. **blocked_if as a disclaimer.** Putting "如果太难" into blocked_if pre-books a
   surrender. Reserve it for genuine external dependencies — credentials,
   decisions, third parties — never for difficulty expectations.

---

## Independent verifier prompt template (verifier tier only)

Spawn the checker subagent with this template, substituting the bracketed
parts:

```text
You are an independent verifier. You receive only: the contract, the diff,
and the claimed evidence. The executor's self-assessment is not included —
and not needed.

Tasks:
1. Re-run every command-type verification in the contract yourself; record
   exit codes and the decisive output lines
2. Relevance review: for each predicate, does passing it actually support the
   outcome? A predicate that always passes and proves nothing about the
   outcome counts as unverified
3. Output only a conclusion: VERIFIED or NOT_DONE, with per-predicate grounds

Contract: <full contract.json>
Diff: <git diff output>
Evidence: <the executor's claimed evidence[]>

Forbidden: reading the executor's summary; inventing output for commands you
did not run; approving because it "looks about right".
```

Information isolation is the load-bearing wall: nothing the executor concludes
is visible to the checker, so the checker can only take sides with evidence.
