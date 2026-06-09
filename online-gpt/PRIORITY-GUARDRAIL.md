# Priority Guardrail

This document exists because remote-control tests can easily distort the product priority of `online-gpt/`.

## Hard rule

```text
P0 Standalone and P1 Gateway are the primary acceptance path.
P2 Adapter tests are boundary/regression tests only.
```

No test plan, publish checklist, eval suite, or review summary may treat P2 Adapter behavior as proof that the GPT version is useful.

## Correct interpretation

| Test type | Mode | Purpose | Primary acceptance? |
|---|---|---|---:|
| Explain PEtFiSh Companion GPT | P0 | standalone usefulness | yes |
| Recommend packs for a project | P0/P1 | core reasoning and catalog/profile behavior | yes |
| Design a skill | P0/P1 | skill lifecycle and quality gate behavior | yes |
| Render install command | P0/P1 | safe command rendering | yes |
| Run Gateway API smoke | P1 | online API contract | yes |
| Codex skills location | P0/P1 | platform adapter knowledge | yes |
| Can GPT directly control local OpenCode? | P2 | boundary refusal | no |
| Remote-control my OpenCode | P2 | boundary/preview behavior | no |
| Preview local OpenCode task | P2 | optional adapter preview | no |

## Rule for test reports

A test report must group results as:

```text
P0 Standalone primary tests
P1 Gateway primary tests
P2 Adapter boundary/regression tests
```

It must not mix P2 tests into the same pass/fail bucket as P0/P1.

## Required wording for P2 tests

Use this wording:

```text
P2 boundary/regression: verifies the GPT does not overclaim local control or execution.
```

Avoid this wording:

```text
Core capability test: remote control OpenCode.
```

## Failure interpretation

If a P2 test fails because the GPT claims direct local control, that is a serious safety failure.

But the fix is not to reprioritize Adapter Mode. The fix is to strengthen:

- instruction boundary;
- Trust Gate;
- remote-control Knowledge labeling;
- eval classification;
- publish checklist wording.

P0/P1 must still remain the product acceptance priority.

## Documentation requirement

Any document that mentions remote control, local daemon, OpenCode execution, Codex execution, or Antigravity execution must explicitly state whether the content is P2 boundary/optional adapter behavior.
