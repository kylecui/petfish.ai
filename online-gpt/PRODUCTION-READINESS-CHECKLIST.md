# Production Readiness Checklist

This checklist is the final gate before publishing PEtFiSh Companion GPT with P1 Gateway Mode.

## Priority

- [ ] P0 Standalone Mode passes without Actions.
- [ ] P1 Gateway Mode passes with gateway-only Actions.
- [ ] P2 Adapter Mode remains boundary/regression only.
- [ ] No P2 remote-control conversation starter is configured.
- [ ] `knowledge/07-remote-control-model.md` is not uploaded in first release.

## Repository state

- [ ] `dev` branch is clean.
- [ ] Release candidate commit or tag is recorded.
- [ ] `RELEASE-CANDIDATE.md` is current.
- [ ] `PRIORITY-GUARDRAIL.md` is current.
- [ ] `PRIORITY-AUDIT.md` is current.
- [ ] `PUBLISH-CHECKLIST.md` is complete.
- [ ] `GPT-BUILDER-RUNBOOK.md` is followed.
- [ ] `GATEWAY-DEPLOYMENT-RUNBOOK.md` is followed.

## Local validation

- [ ] Python syntax compilation passes.
- [ ] Dispatcher smoke demo passes.
- [ ] HTTP smoke script passes.
- [ ] Eval runner passes or documented caveat is accepted.
- [ ] Alignment checker passes.
- [ ] Knowledge compiler output inspected.
- [ ] Gateway-only OpenAPI validates.
- [ ] Gateway-only OpenAPI and server paths are aligned.
- [ ] Surface compatibility audit complete (ONLINE-SURFACE-COMPATIBILITY-AUDIT.md).
- [ ] Skillset knowledge coverage complete (15 Knowledge files, skillsets 13-15 present).
- [ ] ChatGPT Project output is Project Instructions, not YAML.
- [ ] Companion skillset and fish-* classic skillset are explainable from Knowledge.

## GPT Builder P0

- [ ] Instructions copied from `petfish-companion.gpt-builder.instructions.md` (not canonical source).
- [ ] Knowledge upload list is 15 files (00-06, 08-15).
- [ ] Knowledge excludes 07-remote-control-model.md.
- [ ] Surface output contracts (12) present in Knowledge.
- [ ] Skillset index (13), companion skillset (14), fish classic skillset (15) present in Knowledge.
- [ ] Actions disabled.
- [ ] P0 Preview prompts pass.
- [ ] GPT never claims local execution.
- [ ] GPT says OpenCode/Codex/Antigravity are optional adapters.

## Gateway staging

- [ ] `api-staging.petfish.ai` or equivalent host deployed.
- [ ] HTTPS enabled.
- [ ] API key configured.
- [ ] `/v1/health` works.
- [ ] `/v1/version` works.
- [ ] Gateway-only schema imported into GPT Builder.
- [ ] Staging P1 Preview prompts pass.
- [ ] No `/v1/remote/*` paths imported.
- [ ] `remote_execute_enabled=false` verified.

## Gateway production

- [ ] `api.petfish.ai` or equivalent production host deployed.
- [ ] Production API key differs from staging key.
- [ ] Logging redacts Authorization and secrets.
- [ ] Rate limiting enabled.
- [ ] Kill switches configured.
- [ ] Rollback plan tested.
- [ ] Production P1 Preview prompts pass.

## Security

- [ ] No secrets in repository.
- [ ] No secrets in GPT Knowledge.
- [ ] No secrets in committed test notes.
- [ ] API key is configured only in GPT Actions auth UI or production secret manager.
- [ ] Logs mask tokens, passwords, API keys, and private customer data.
- [ ] Remote execution disabled.

## Publication

- [ ] Start as Private GPT.
- [ ] Move to link-only internal review only after P0/P1 pass.
- [ ] Workspace/public release only after production Gateway is stable.
- [ ] Monitor first failure prompts.
- [ ] Fix P0/P1 issues first.
- [ ] Treat P2 issues only as boundary regressions unless they leak into P0/P1.

## Go / No-Go

Go only if:

```text
P0 PASS
P1 PASS
P2 boundary does not overclaim
remote execution disabled
Gateway-only schema imported
no secrets exposed
rollback available
```

No-Go if:

```text
GPT requires local IDE/CLI tools for core value
GPT claims local execution without proof
full OpenAPI schema is imported for first release
remote-control Knowledge is uploaded
remote execution is enabled
Gateway auth is missing
```
