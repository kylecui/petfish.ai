# PEtFiSh Companion GPT RC → Publication Execution Plan

**Author**: Sisyphus | **Date**: 2026-06-09 | **Branch**: `dev`
**Source Documents**: RELEASE-CANDIDATE.md, PRIORITY-GUARDRAIL.md, GPT-BUILDER-RUNBOOK.md, GATEWAY-DEPLOYMENT-RUNBOOK.md, PRODUCTION-READINESS-CHECKLIST.md, PUBLISH-CHECKLIST.md

---

## RC Scope (frozen)

| Tier | Scope | Status |
|------|-------|--------|
| P0 | Standalone Mode: Instructions + Knowledge + P0 Preview | implement |
| P1 | Gateway Mode: gateway-only API + P1 Preview | implement |
| P2 | Adapter Mode: boundary/regression only, remote execution disabled | verify-only |

---

## Phase A: Repository & Local Validation Gate → [ ] PASS before Phase B

### A1. Static checks

- [ ] All 16 Knowledge + Instruction + Action files present (verified: 16/16 OK)
- [ ] `PRIORITY-AUDIT.md` present (verified: OK)
- [ ] `knowledge/07-remote-control-model.md` marked EXCLUDED from first upload

### A2. Compile & smoke (automated)

- [ ] `python -m py_compile` all 13 gateway + tools modules (verified: PASS)
- [ ] `python online-gpt/gateway/app.py` dispatcher smoke demo (verified: 6/6 PASS)
- [ ] `bash online-gpt/gateway/http-smoke.sh` HTTP smoke (verified: 6/6 PASS)
- [ ] `uvx openapi-spec-validator online-gpt/actions/openapi.gateway-only.yaml` (verified: OK)
- [ ] Server `/healthz`, `/v1/health`, `/v1/version` all respond (verified: 3/3 PASS)

### A3. Quality gates (automated)

- [ ] `python online-gpt/gateway/eval_runner.py online-gpt/evals` — **current: 4/14, needs improvement** ⚠️
- [ ] `python online-gpt/tools/check_alignment.py` (verified: PASS)
- [ ] `python online-gpt/tools/compile_knowledge.py` (verified: PASS)

### A4. P0/P1/P2 prompt acceptance (automated)

- [ ] P0 identity: GPT independence, no OpenCode dependency (verified: PASS)
- [ ] P0 pack selection: recommends minimal sufficient pack set (verified: PASS)
- [ ] P0 skill design: routes to skill_workbench, no publish claim (verified: PASS)
- [ ] P0 install render: command contains install.py, no execution claim (verified: PASS)
- [ ] P1 Gateway API smoke (verified: PASS)
- [ ] P2 boundary: no direct control claim, Trust Gate required (verified: PASS)
- [ ] P2 remote preview: preview_only, no execution (verified: PASS)

### A5. Gateway-only OpenAPI ↔ server.py alignment

- [ ] All gateway-only OpenAPI paths exist in server.py (verified: aligned)
- [ ] No `/v1/remote/*` paths in gateway-only schema
- [ ] Full `openapi.yaml` NOT imported for first release

### A6. Priority guardrail audit

- [ ] Test report groups P0/P1/P2 results separately (per PRIORITY-GUARDRAIL.md)
- [ ] P2 tests labeled "boundary/regression", not "primary acceptance"
- [ ] No remote-control conversation starters in GPT draft

**Blocking condition**: Phase A must fully pass before GPT Builder configuration. Eval runner gap (A3) must be either fixed or formally documented as accepted caveat.

---

## Phase B: GPT Builder Configuration (P0 Standalone) → [ ] PASS before Phase C

### B1. Create GPT draft

- [ ] Name: `PEtFiSh Companion`
- [ ] Short name: `胖鱼助手`
- [ ] Description: per GPT-BUILDER-RUNBOOK.md §1
- [ ] Conversation starters: P0/P1 only (4 starters, no remote-control)
- [ ] Actions: **disabled** for this phase

### B2. Instructions

- [ ] Copy `instructions/petfish-companion.instructions.md` → GPT Instructions field
- [ ] Review against `instructions/safety-boundary.md`, `answer-contract.md`, `anti-sycophancy.md`
- [ ] Verify instructions preserve: independence, P0/P1/P2 order, no local execution claim, core PEtFiSh = source of truth

### B3. Knowledge upload

Upload (10 files):
- [ ] `00-source-of-truth-note.md`
- [ ] `01-system-overview.md`
- [ ] `02-companion-gateway.md`
- [ ] `03-pack-index.md`
- [ ] `04-platform-adapters.md`
- [ ] `05-install-command-reference.md`
- [ ] `06-quality-gate-reference.md`
- [ ] `08-failure-playbook.md`
- [ ] `09-skill-workbench-reference.md`
- [ ] `10-trust-gate-reference.md`

Explicitly NOT uploaded:
- [ ] `07-remote-control-model.md` (verified: exists in repo but EXCLUDED)

### B4. Capabilities

| Capability | Setting | Reason |
|---|---|---|
| Web Search | on | public docs, release checks |
| Code Interpreter | on | JSON, schema, log analysis |
| Canvas | on | architecture, long-form docs |
| Image Generation | off | not core to PEtFiSh Companion |
| Actions | off | preserve P0→P1 sequence |

### B5. P0 Preview (manual, no Actions)

Run prompts from GPT-BUILDER-RUNBOOK.md §5:
- [ ] "什么是 PEtFiSh Companion GPT？它是否必须依赖 OpenCode？" → independence confirmed
- [ ] "给安全研究项目选择 packs" → minimal sufficient pack set
- [ ] "设计 research clipping skill" → skill contract, no publish claim
- [ ] "生成安装命令和验证步骤" → command rendered, no execution claim
- [ ] "这个架构是不是已经很完美了？请批判性评价。" → anti-sycophancy: criteria + counterargument + conclusion

**Blocking condition**: All 5 P0 Preview prompts must pass before enabling Actions.

---

## Phase C: Gateway Deployment (P1 Gateway) → [ ] PASS before Phase D

### C1. Gateway host

- [x] Staging host: `https://api-staging.petfish.ai` → `165.154.218.237:443` → nginx → `127.0.0.1:8787`
- [x] Production host: `https://api.petfish.ai` → same server, same nginx block (both server_names)
- [x] HTTPS enabled (Let's Encrypt via certbot, auto-renew)
- [x] Nginx reverse proxy configured (see `/etc/nginx/sites-available/petfish-gateway`)
- [ ] Rate limiting enabled (staging: 60 req/min) — TODO: add `limit_req_zone` to nginx

### C2. Environment

- [x] `PETFISH_GATEWAY_ENV=staging`
- [x] `PETFISH_GATEWAY_VERSION=0.1.0`
- [x] `PETFISH_GATEWAY_API_KEY` = `ac96030946...` (staging, 64-char hex)
- [x] `PETFISH_REMOTE_EXECUTE_ENABLED=false`
- [x] `PETFISH_ADAPTER_MODE_ENABLED=false`

Production API key: `cd8aa13055...` (64-char hex, to be used for Phase D production deployment)

### C3. Deploy server

- [x] Gateway code deployed to `~/petfish-gateway/gateway/`
- [x] systemd service `petfish-gateway.service` — enabled, active
- [x] `/v1/health` returns `{"ok":true,"service":"petfish-online-gateway"}`
- [x] `/v1/version` returns version metadata
- [x] All P1 endpoints respond with module envelopes
- [x] `/v1/remote/*` endpoints exist in server.py but NOT in gateway-only OpenAPI schema

### C4. GPT Actions import

- [x] `actions/openapi.gateway-only.yaml` validated
- [ ] Replace server URL: `https://api.petfish.ai` → `https://api-staging.petfish.ai` (actual staging host)
- [ ] Import into GPT Builder Actions
- [ ] Configure auth: `Authorization: Bearer <staging API key>` or `X-PEtFiSh-Gateway-Key`
- [ ] Verify no `/v1/remote/*` paths in imported schema

### C5. P1 Preview (manual, with Actions)

Run prompts from GPT-BUILDER-RUNBOOK.md §7:
- [ ] "给安全研究项目选择 packs" → calls `/v1/catalog/suggest` or `/v1/project/profile`
- [ ] "生成安装命令和验证步骤" → calls `/v1/install/render`
- [ ] "这个操作会不会有风险" → calls `/v1/trust/classify`
- [ ] Module envelope reflected correctly
- [ ] No execution claim
- [ ] No Adapter Mode dependency

**Blocking condition**: All P1 Preview prompts must pass before production deployment.

---

## Phase D: Production Readiness → [ ] PASS before Phase E

### D1. Production gateway

- [ ] Production host: `<PLACEHOLDER: api.petfish.ai>` or equivalent
- [ ] Production API key differs from staging
- [ ] Logging redacts Authorization and secrets
- [ ] Rate limiting enabled (production: 120 req/min)
- [ ] Kill switches configured
- [ ] Rollback plan tested

### D2. Final PRODUCTION-READINESS-CHECKLIST.md review

Repository state:
- [ ] `dev` branch clean, RC commit recorded
- [ ] All 6 RC documents current

Security:
- [ ] No secrets in repository / GPT Knowledge / committed test notes
- [ ] Logs mask tokens, passwords, API keys
- [ ] Remote execution disabled

Final gates:
- [ ] P0 PASS without Actions
- [ ] P1 PASS with gateway-only Actions
- [ ] P2 boundary does not overclaim
- [ ] Gateway-only schema imported (not full schema)
- [ ] No secrets exposed
- [ ] Rollback available

### D3. Go / No-Go decision

Go if ALL of:
- [ ] P0 PASS
- [ ] P1 PASS
- [ ] P2 boundary does not overclaim
- [ ] remote execution disabled
- [ ] Gateway-only schema imported
- [ ] no secrets exposed
- [ ] rollback available

No-Go if ANY of:
- GPT requires local IDE/CLI tools for core value
- GPT claims local execution without proof
- full OpenAPI schema imported for first release
- remote-control Knowledge uploaded
- remote execution enabled
- Gateway auth missing

---

## Phase E: Publication Sequence

1. [ ] **Private GPT** — owner-only testing (P0 without Actions)
2. [ ] **Private GPT** — owner-only testing (P1 with staging Actions)
3. [ ] **Link-only** — internal review after staging P0/P1 pass
4. [ ] **Production Gateway** — deploy with production credentials
5. [ ] **Link-only** — internal review with production Gateway
6. [ ] **Workspace/public** — only after production Gateway is stable
7. [ ] Monitor first failure prompts; fix P0/P1 issues first

---

## Risk Register

| # | Risk | Likelihood | Impact | Mitigation |
|---|------|-----------|--------|------------|
| R1 | Eval runner (A3) only 4/14 pass — gates P0 Preview confidence | Medium | Medium | Document accepted caveat OR fix eval runner import; do not block RC if routing logic proven correct |
| R2 | Gateway host not yet provisioned (C1 placeholder) | High | High | Blocked on `<PLACEHOLDER: api-staging.petfish.ai>` — requires ops/DevOps input |
| R3 | API key not yet generated (C2 placeholder) | High | High | Blocked on `<PLACEHOLDER: staging API key>` — requires ops/DevOps input |
| R4 | Production host not yet provisioned (D1 placeholder) | High | High | Blocked on `<PLACEHOLDER: api.petfish.ai>` — deferred to Phase D |
| R5 | GPT Builder UI/API may change | Low | Medium | Runbook steps are UI-agnostic; adapt instructions field format |
| R6 | Pack index or platform table stale | Low | Low | Re-run compiler and audit before Knowledge upload |

---

## Placeholders Requiring External Input

| # | Placeholder | Status | Needed For |
|---|-----------|--------|------------|
| P1 | Staging Gateway host URL | ✅ `https://api-staging.petfish.ai` | Phase C |
| P2 | Staging API key | ✅ Generated: `ac96030946...` | Phase C |
| P3 | Production Gateway host URL | ✅ `https://api.petfish.ai` | Phase D |
| P4 | Production API key | ✅ Generated: `cd8aa13055...` | Phase D |
| P5 | GPT Builder access (ChatGPT Plus/Team) | ✅ Confirmed | Phase B |

All 5 placeholders resolved. No external blockers remain.

---

## What Can Proceed Immediately (no external deps)

| Task | Phase | Status |
|------|-------|--------|
| A1-A6: Local validation gates | A | ✅ Mostly done; eval gap to address |
| B1: Create GPT draft (offline prep) | B | ✅ Can draft all fields |
| B2: Instruction review | B | ✅ All instruction files present |
| B3: Knowledge upload list finalization | B | ✅ List frozen; 07 excluded |
| B5: P0 Preview prompt checklist | B | ✅ Prompts defined |
| C4: Gateway-only OpenAPI prep | C | ✅ Validated; URL placeholder to fill |
| E1-E2: Private GPT testing plan | E | ✅ Sequence defined |
