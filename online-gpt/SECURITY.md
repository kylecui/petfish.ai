# Security Model

This document defines the security posture for PEtFiSh Companion GPT.

## Security objective

The online GPT shell must improve project coordination without becoming an uncontrolled command execution channel.

## Assets

| Asset | Protection goal |
|---|---|
| local project files | prevent unapproved modification or deletion |
| credentials and tokens | prevent exposure, logging, or Knowledge upload |
| remote daemon | prevent unauthorized execution |
| GPT Knowledge | prevent secret inclusion and stale policy drift |
| Actions gateway | prevent confused-deputy execution |
| audit logs | preserve traceability without leaking sensitive content |

## Trust boundaries

```text
User conversation
  boundary: prompt injection and unclear intent
GPT instructions / knowledge
  boundary: retrieval and instruction hierarchy
GPT Actions
  boundary: external API call
Online Gateway
  boundary: policy and module dispatch
Remote daemon
  boundary: local machine authority
Runtime adapter
  boundary: filesystem and agent execution
```

## Threats

| Threat | Mitigation |
|---|---|
| GPT claims unverified execution | execution truth labels and adapter proof rule |
| prompt asks to bypass policy | Trust Gate and safety-boundary instructions |
| secret pasted into chat | mask, refuse storage, avoid Knowledge inclusion |
| destructive command without scope | deny or require second confirmation |
| remote daemon abused | disabled-by-default execution, approval token, audit trace |
| stale Knowledge causes wrong command | branch-aware fallback and verification steps |
| module route drift | eval runner and regression cases |

## Policy controls

- Default remote execution mode: disabled.
- Default install behavior: command rendering only.
- Default destructive behavior: deny if scope is unclear.
- Default secret behavior: mask and do not persist.
- Default publish behavior: require release discipline and explicit approval.

## Audit requirements

Any real execution adapter should log:

- trace ID;
- user-visible task summary;
- module and operation ID;
- risk classification;
- approval decision;
- target project alias;
- result status;
- redacted logs summary.

Audit logs must not include raw tokens or private keys.

## Security acceptance

The subsystem is not ready for remote execution until:

- Trust Gate is tested;
- approval token flow exists;
- daemon registration is scoped;
- logs are redacted;
- execution results include trace IDs;
- remote execute can be disabled centrally.
