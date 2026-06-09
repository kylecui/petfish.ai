# GPT Creation Plan Review

Review target:

```text
online-gpt/GPT-CREATION-PLAN.md
```

Review result:

```text
BLOCKED: secret exposure in GPT-CREATION-PLAN.md
```

The plan is structurally good, but it must not be used for GPT Builder operation until the security issue below is fixed.

## Blocker 1: API keys are committed in plaintext

`GPT-CREATION-PLAN.md` currently includes concrete staging and production API key values in the Authentication section.

This is a release blocker and a credential incident.

## Required immediate actions

1. Rotate both staging and production Gateway API keys.
2. Update the Gateway secret store / environment configuration.
3. Update GPT Builder Actions auth using the new staging key only when ready for staging tests.
4. Replace plaintext keys in `GPT-CREATION-PLAN.md` with placeholders only:

```text
<STAGING_GATEWAY_API_KEY>
<PRODUCTION_GATEWAY_API_KEY>
```

5. Add an explicit rule: real keys must never appear in repository docs, GPT Knowledge, Instructions, local notes, or screenshots.
6. Review recent commits and local team notes for the same leaked values.
7. Treat old keys as compromised even if the repository is private.

## Required wording for the Authentication section

Use this pattern:

```text
Auth Type: API Key
Header: Authorization
Value: Bearer <STAGING_GATEWAY_API_KEY>
```

For production:

```text
Value: Bearer <PRODUCTION_GATEWAY_API_KEY>
```

The actual values must be stored only in the deployment secret store and the GPT Builder Actions secret field.

## Non-blocking observations

The plan correctly preserves these points:

- GPT Builder Instructions must come from `petfish-companion.gpt-builder.instructions.md`.
- Canonical instructions must not be pasted directly into GPT Builder.
- Knowledge upload list includes files 00-06 and 08-11.
- `knowledge/07-remote-control-model.md` is excluded.
- First-release Actions use `openapi.gateway-only.yaml` only.
- `/v1/remote/*` endpoints are excluded from first-release Actions.
- P0/P1/P2 testing order is preserved.
- Final state is marked as READY FOR RC REVIEW, not READY FOR PUBLICATION.

## Additional recommended cleanup

The plan includes deployment host and server details. This may be acceptable for an internal operational document, but for any public or semi-public release package, move host/IP/systemd details to a private deployment note.

## Re-review criteria

Mark this review as resolved only when:

- plaintext keys are removed from `GPT-CREATION-PLAN.md`;
- both leaked keys have been rotated;
- GPT Builder / Gateway deployment uses the rotated keys;
- the plan says placeholders only;
- no Knowledge or Instructions file contains secrets;
- P0/P1/P2 preview tests are rerun after key rotation if Actions auth changed.

## Current decision

```text
NO-GO for GPT Builder operation until credential rotation and document redaction are complete.
```
