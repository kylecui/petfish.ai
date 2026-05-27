# Petfish Fix Verification — Fish-Trail Plugin/MCP

Date: 2026-05-23
Branch under test: `feat/fish-trail-tiered-memory-v2`
Workspaces: `/tmp/opencode/petfish_eval_manual`, `/tmp/opencode/petfish_eval_fresh`, `/tmp/opencode/petfish_eval_158`, `/tmp/opencode/petfish_eval_159_latest`

## Scope

Verify Petfish team fixes for issues #149-#159, then run a limited performance/quality smoke evaluation.

## Verdict

Status: **DISK MODE VERIFIED; realtime architecturally blocked by OpenCode plugin API limitation**.

The MCP audit logging work passes direct functional testing. After branch update to `20a0b29`, fresh install and disk-mode topic injection pass smoke validation. After `6d86386`, realtime option propagation is fixed: runtime plugin logs report `detectionMode=realtime` and inject realtime context. After `94f6004`, #159 source changes are present. After `b96432e`, #161 is fixed (TopicDetector inlined). However, Discovered at `13b66c5`: `client.available=true` and `serverUrl` provides a REST API (`/session/{id}/message`), but `client.messages()` is not a function — client is a plain HTTP client, not an OpenAPI SDK. REST API workaround successfully retrieves messages, but **only from completed turns** — the current user message is not yet persisted when `system.transform` runs. This means Scheme D with REST API is one turn behind, equivalent to disk mode. Filed analysis as comment on #163.

## Issue Status Checked

| Issue | Upstream status | Verification result |
|---|---|---|
| #149 dual disk/realtime plugin modes | Closed | Source contains both modes, but realtime did not inject metadata in OpenCode smoke test; see #157 |
| #150 Tier 2 stays MCP-side | Closed | Source confirms plugin has no ONNX/embedding imports; accepted |
| #151 Bun transpiler workaround | Closed | Source avoids `(x || "").method()` in inspected paths; accepted |
| #152 branch/install path | Closed | Remote installer points to prerelease branch; acceptable for prerelease validation, not master release |
| #153 v2 registry fallback | Closed | Source has fallback chain, but topic detail lookup has prefix collision; see #156 |
| #154 audit log identifiers | Closed | Direct MCP test passed; accepted |
| #155 invalid fish-trail opencode.example.json | Closed | Fresh install now passes after `20a0b29` |
| #156 wrong topic detail from 8-char prefix | Closed | Same-prefix disk-mode smoke test now passes after `20a0b29` |
| #157 realtime input extraction | Closed | Code exists, but runtime cannot verify due to #158 |
| #158 realtime option propagation | Closed | Runtime logs confirm `detectionMode=realtime` after `6d86386` |
| #159 `Forget everything` reset metadata | Closed | Static source fix present in `94f6004`, but runtime verification fails because user message extraction is empty |

## New Issues Filed

| Issue | Severity | Summary |
|---|---|---|
| #155 | Blocker | `packs/core/fish-trail/opencode.example.json` invalid JSON; fresh install fails |
| #156 | High | Plugin topic detail lookup uses 8-char prefix, causing wrong topic title/scope injection |
| #157 | High | `realtime` mode does not receive user text via `input.content`; no detection metadata injected |
| #158 | Blocker | Runtime plugin option remains `disk mode` despite `opencode.json` setting `detectionMode: "realtime"` |
| #159 | Medium | `Forget everything` does not surface realtime reset metadata, while `Start over`, `Reset context`, and `fresh start` do |
| #160 realtime user message extraction | Closed (commit) | Input shape `keys=[sessionID,model]` — no user text available; architecturally blocked by OpenCode API |
| #161 TopicDetector auto-load | Closed (commit) | `topic-detector.ts` removed from `.opencode/plugin/`; class inlined into `system-prompt-context-inject.ts` |
+| #162 topic_validate schema | Open | `MISSING_REQUIRED_FIELD` for all nodes |
+| #163 OpenCode hook API limitation | Open | `experimental.chat.system.transform` does not expose user messages; realtime detection architecturally blocked |
+| #163 OpenCode hook API limitation | Open | `experimental.chat.system.transform` does not expose user messages; realtime detection architecturally blocked |

## Second Verification Round After #155-#157

Branch updated to `20a0b29`.

### Fresh Install Retest

Command:

```bash
bash ./install.sh --pack context --platform opencode --target /tmp/opencode/petfish_eval_fresh --force
```

Result: **PASS**.

Installed assets include:

- `.opencode/plugin/system-prompt-context-inject.ts`
- `.opencode/plugin/system-prompt-rules.ts`
- `.opencode/plugin/topic-detector.ts`
- `.opencode/skills/fish-trail/...`
- `opencode.json` with MCP and plugin config

### Disk Mode Same-Prefix Topic Retest

Test topics:

```text
topic_20260523_aaaa — QA Audit Topic
topic_20260523_bbbb — API Monitoring Setup
```

Active topic: `topic_20260523_aaaa`.

Observed response:

```text
Active topic: topic_20260523_aaaa — "QA Audit Topic"
Scope: Verify mutation audit logging
```

Result: **PASS**. This confirms #156 is fixed for disk-mode detail lookup.

### Realtime Mode Runtime Option Retest

Config:

```json
[".opencode/plugin/system-prompt-context-inject.ts", {
  "maxTopics": 5,
  "maxSummaryLen": 200,
  "detectionMode": "realtime"
}]
```

Observed plugin log:

```text
[system-prompt-context-inject] Injected topic context (disk mode): active=topic_20260523_aaaa, related=1
```

Result: **FAIL / BLOCKED**. The model can sometimes answer `switch -> topic_20260523_bbbb`, but this is not sufficient evidence of realtime metadata because it can infer relation/target from prompt and related topic list. The plugin's own log still says `disk mode`.

## Third Verification Round After #158

Branch updated to `6d86386`.

### Realtime Option Propagation Retest

Workspace: `/tmp/opencode/petfish_eval_158`.

Observed plugin log:

```text
[system-prompt-context-inject] options resolved: maxTopics=5, maxSummaryLen=200, detectionMode=realtime
[system-prompt-context-inject] Injected topic context (realtime mode): active=topic_20260523_aaaa, related=1
```

Result: **PASS** for #158. OpenCode still does not pass tuple plugin options as a second function argument, but the plugin now resolves config from `opencode.json`, so runtime behavior is correct.

### Realtime Relation Smoke Tests

Observed:

| Prompt | Observed result | Result |
|---|---|---|
| `Switch to API Monitoring Setup...` | `switch topic_20260523_bbbb` | PASS |
| `By the way, separately evaluate dashboard alerts...` | `fork` | PASS |
| `Start over...` | `reset` | PASS |
| `Reset context...` | `reset` | PASS |
| `fresh start...` | `reset` | PASS |
| `Forget everything...` | no realtime reset metadata surfaced | FAIL; filed #159 |

Conclusion: realtime mode is no longer blocked by option propagation. It is suitable for targeted switch/fork/reset smoke testing, but release-quality reset coverage should wait for #159 or explicitly exclude `Forget everything` as a reset phrase.

## Fourth Verification Round After #159

Branch updated to `94f6004`.

Fresh install source:

```bash
git archive origin/feat/fish-trail-tiered-memory-v2 | tar -x -C /tmp/opencode/petfish_src_159
cd /tmp/opencode/petfish_src_159
bash ./install.sh --pack context --platform opencode --target /tmp/opencode/petfish_eval_159_latest --force
```

Static source check: **PASS**.

Evidence:

```text
.opencode/plugin/topic-detector.ts: "forget everything"
.opencode/plugin/system-prompt-context-inject.ts: "Reset requested"
```

Runtime check: **FAIL / NOT VERIFIED**.

CLI command:

```bash
opencode run --print-logs --log-level INFO "Forget everything. Answer only relation if realtime metadata exists."
```

Observed plugin output:

```text
[system-prompt-context-inject] options resolved: maxTopics=5, maxSummaryLen=200, detectionMode=realtime
[system-prompt-context-inject] Realtime detection input: userMsg.length=0, first60=null
[system-prompt-context-inject] Injected topic context (realtime mode): active=topic_20260523_bbbb, related=1
[system-prompt-context-inject] Realtime detection input: userMsg.length=0, first60=null
[system-prompt-context-inject] Injected topic context (realtime mode): active=topic_20260523_bbbb, related=1
```

Expected plugin output:

```text
[system-prompt-context-inject] Realtime detection input: userMsg.length>0, first60="Forget everything..."
[system-prompt-context-inject] Realtime detection result: relation=reset, confidence=0.95, target=none
```

Additional runtime signal:

```text
ERROR service=plugin path=file:///tmp/opencode/petfish_eval_159_latest/.opencode/plugin/topic-detector.ts error=Cannot call a class constructor TopicDetector without |new| failed to load plugin
```

Interpretation: #159 fixed the detector phrase table and reset-context formatting, but realtime runtime verification still fails because the plugin transform input does not expose the current user text in the fields currently inspected by `extractUserMessage()`. Model answers such as `reset` are not sufficient evidence unless plugin logs include `Realtime detection result: relation=reset`.

Follow-up issue filed as #160: `fish-trail realtime still cannot extract current user message in OpenCode runtime`.

### Disk Mode Quality Regression (N=7)

Workspace: `/tmp/opencode/petfish_eval_159_latest`, disk mode.

Active topic: `topic_20260523_aaaa` — QA Audit Topic.
Related: `topic_20260523_bbbb` — API Monitoring Setup.

| Check | Result | Notes |
|---|---|---|
| Active topic recall | 6/7 | All but one prompt correctly referenced QA Audit Topic |
| Scope quote accuracy | PASS | "Verify mutation audit logging" quoted exactly |
| Contamination: API monitoring prompt | PASS | Answered "No" — did not confuse with related topic |
| Contamination: dashboard alerts prompt | PASS | Answered "No" — did not confuse with related topic |
| Avg wall time | 4.83s | N=7 |
| Avg input tokens | 1,925 | Includes system prompt |
| Avg output tokens | 43 |  |

Artifact: `experiments/plugin-context-inject/results/disk-quality-regression.json`

### MCP Audit Trail Coverage

All 6 mutation tools tested and verified in `decisions/decision-log.json`:

| Tool | Audit entry | Fields verified |
|---|---|---|
| topic_create | Yes | action, target_topic, timestamp |
| topic_update | Yes | action, source_topic, timestamp |
| topic_archive | Yes | action, source_topic, timestamp |
| topic_link | Yes | action, source_topic, target_topic, payload.relation, timestamp |
| topic_unlink | Yes | action, source_topic, target_topic, timestamp |
| session_bind | Yes | action, source_topic, timestamp |
| session_close | Yes | action, source_topic, timestamp |

Additional tools tested:

| Tool | Result | Notes |
|---|---|---|
| topic_detect | PASS | Returns relation=switch, confidence=0.85, risk=40 |
| topic_search | PASS | Returns matching topics |
| topic_graph | PASS | Returns full graph |
| topic_validate | FAIL | Reports MISSING_REQUIRED_FIELD; filed #162 |
| contamination_score | PASS | Returns score/level/dimensions |
| session_list | PASS | Returns session array |
| get_memory_context | PASS | Returns context_block (empty for minimal setup) |
| decision_log | PASS | Writes entry; returns timestamp |
| decision_history | PASS | Returns filtered entries by topic |

Note: `topic_validate` always fails due to schema mismatch between validator and `topic_graph.json` format; see #162.

Note: First disk QA run had wrong active topic (`topic_20260523_bbbb`) because realtime probes flipped the registry. After resetting to `topic_20260523_aaaa`, all results correct.

Artifact: `experiments/plugin-context-inject/results/mcp-audit-trail.json`

### Multi-Topic Contamination Test

Workspace: `/tmp/opencode/petfish_eval_159_latest`, disk mode.

4 same-date topics (all sharing `topic_20260523_` prefix):

| Topic ID | Title | Status |
|---|---|---|
| topic_20260523_aaaa | QA Audit Topic | active (current) |
| topic_20260523_bbbb | API Monitoring Setup | active |
| topic_20260523_cccc | Performance Benchmarking | active |
| topic_20260523_ed99 | Temp Archive Test | archived |

Contamination probe results (6 prompts):

| Check | Result | Notes |
|---|---|---|
| Active scope recall | PASS | "Verify mutation audit logging" |
| Negative: latency probe | PASS | Correctly said No |
| Negative: dashboard alerts probe | PASS | Correctly said No |
| Tag recall | PASS | qa, audit |
| Scope quote | PASS | Exact quote correct |
| Topic list | PASS | All 4 topics listed with correct titles and IDs |

**Contamination failures: 0/6**. Disk mode does not mix scope/title across same-date topics.

Artifact: `experiments/plugin-context-inject/results/multi-topic-contamination.json`

### Upgrade Install Test

Install over existing workspace (`/tmp/opencode/petfish_eval_fresh`):

```bash
bash install.sh --pack context --platform opencode --target /tmp/opencode/petfish_eval_fresh --force
```

Result: **PASS**.

- `opencode.json` merged correctly (preserves existing schema, adds MCP + plugin config)
- `installed-packs.json` updated with version `1.1.0`
- All plugin files, skills, and agents-rules installed
- No data loss or corruption

### System-Prompt-Rules Injection Verification

Prompt asking model to list system prompt headings mentioning fish-trail, topic governance, or safety:

Model response:

```text
1. ## Active Topic Context (auto-injected by plugin)
2. # Fish Trail — 话题治理器
3. # Safety Guard Rules
```

Result: **PASS**. All three expected rules sections are injected into the system prompt at runtime.

## Functional Results

### Install Path

Command:

```bash
bash ./install.sh --pack context --platform opencode --target /tmp/opencode/petfish_eval --force
```

First-round result: **FAIL**. After `20a0b29`: **PASS**.

Error:

```text
json.decoder.JSONDecodeError: Extra data: line 18 column 3 (char 456)
```

Original root cause: `packs/core/fish-trail/opencode.example.json` contained a duplicated trailing JSON fragment. Fixed in `20a0b29`.

### MCP Mutation Audit

Direct MCP JSONL test operations:

- `topic_create`
- `topic_update`
- `session_bind`
- `session_close`

Result: **PASS**.

Evidence from `decision-log.json`:

```json
{"action":"topic_create","target_topic":"topic_20260523_5dfe"}
{"action":"topic_update","source_topic":"topic_20260523_5dfe"}
{"action":"session_bind","session_id":"oc_eval-session-001"}
{"action":"session_close","session_id":"oc_eval-session-001"}
```

stderr logging also emitted `tool_call` and `tool_done` with durations.

### Disk Mode Plugin Injection

First-round manual install workaround was used because #155 blocked normal install. After `20a0b29`, fresh install succeeds.

Disk mode smoke result after `20a0b29`: **PASS**.

- Plugin loads in OpenCode server
- Context is injected
- No routine MCP calls required for basic topic recall
- Same-prefix topic detail lookup now returns the correct title/scope.

First-round incorrect output:

```text
Active topic: topic_20260523_5dfe — API Monitoring Setup
```

Actual active ID `topic_20260523_5dfe` was `QA Audit Topic`; `API Monitoring Setup` belonged to `topic_20260523_01f8`.

### Realtime Mode Plugin Injection

Realtime mode smoke result: **FAIL for zero-turn detection metadata**.

Prompt:

```text
Switch to API Monitoring Setup. State relation/target only if realtime metadata exists.
```

Observed model answer:

```text
Injected realtime detection metadata does not exist in the current context.
```

After #157, code includes `extractUserMessage()`. Runtime initially still logged `disk mode`; #158 fixed option propagation in `6d86386`. After #159, source contains the reset phrase and reset-optimized formatting, but runtime still logs `userMsg.length=0`, so realtime detection is not verified.

## Performance Smoke Data

These are not release-quality benchmarks. First and second-round realtime samples were invalidated by #158. After #158, a small targeted probe verified mode propagation. After #159, source-level reset handling exists, but runtime user-message extraction remains empty, so realtime detection is still blocked for release benchmarking.

Artifacts:

- `experiments/plugin-context-inject/results/petfish-fix-verification-disk.json`
- `experiments/plugin-context-inject/results/petfish-fix-verification-realtime.json`

### Disk Mode Smoke Sample

| N | Avg input | Avg output | Avg wall time | Notes |
|---:|---:|---:|---:|---|
| 3 | 169 | 46 | 4.70s | Token accounting appears to exclude cached/system prompt content; context recall worked but was polluted by #156 |

### Realtime Mode Smoke Sample

| N | Avg input | Avg output | Avg wall time | Notes |
|---:|---:|---:|---:|---|
| 3 | 7,614 | 84 | 13.49s | No realtime metadata observed; user-triggered topic actions still reached MCP and were audited |

### Second-Round Smoke Sample After `20a0b29`

Artifact:

- `experiments/plugin-context-inject/results/petfish-final-regression.json`

| Mode | N | Avg input | Avg output | Avg wall time | Tools | Notes |
|---|---:|---:|---:|---:|---:|---|
| disk | 3 | 198 | 37 | 5.80s | 0 | Correct active topic and related topic recall |
| realtime | 3 | 3,085 | 10 | 15.22s | 0 | Historical sample; invalid as realtime benchmark because plugin log still said `disk mode` before #158 fix |

### Third-Round Realtime Probe After `6d86386`

Artifact updated:

- `experiments/plugin-context-inject/results/petfish-final-regression.json`

| Check | Result | Notes |
|---|---|---|
| Runtime mode | PASS | Plugin log reports `detectionMode=realtime` |
| Switch | PASS | Returned `switch topic_20260523_bbbb` |
| Fork | PASS | Returned `fork` |
| Reset controls | PASS | `Start over`, `Reset context`, and `fresh start` returned `reset` |
| Reset edge phrase | FAIL | `Forget everything` did not surface reset metadata; filed #159 |

## Quality Assessment

| Area | Result | Evidence |
|---|---|---|
| MCP mutation audit | PASS | Correct topic/session IDs in decision log |
| Disk mode quality + contamination | PASS | 6/7 recall, 0/2 contamination in 2-topic; 0/6 contamination in 4-topic |
| MCP audit trail | PASS | All 6 mutation tools write decision-log entries with correct fields |
| Upgrade install | PASS | Merges opencode.json, updates installed-packs registry |
| System-prompt-rules injection | PASS | All three rules sections visible in model context |
| Realtime detection | BLOCKED | OpenCode hook API does not expose user messages; architecturally impossible until OpenCode fixes; see #163 |
| Fresh install | PASS | Installer now completes and installs plugins + skill + opencode.json |
| Tier 2 architecture | PASS | Plugin excludes embedding/ONNX; MCP remains semantic path |
| Bun workaround | PASS | Inspected TypeScript avoids known bad pattern |

## Recommendation

Realtime benchmarking is **architecturally blocked** — OpenCode 1.15.7's `experimental.chat.system.transform` hook only provides `{sessionID, model}`, no user messages. Plugin-side realtime detection cannot work until OpenCode exposes user text to this hook (filed #163). Three options:

1. Request OpenCode to add user messages to system transform hook input
2. Accept disk mode as the only viable plugin approach and deprecate `realtime`
3. Move Tier 1 detection back to MCP server (re-introduces per-turn MCP cost)

Meanwhile, all disk-mode and MCP testing is complete:

1. Fresh install and upgrade install: PASS
2. Disk mode quality/performance regression (N=7): PASS, 0 contamination
3. MCP audit trail (6/6 mutation tools): PASS
4. Multi-topic contamination (4 same-date topics): PASS, 0 contamination
5. System-prompt-rules injection: PASS

The positive parts: fresh install works, disk mode works with zero contamination, same-prefix topic lookup is fixed, realtime option propagation is fixed, #159 source changes and #161 fix are present, audit trail is complete and useful, upgrade install is safe, and rules injection is verified. The remaining blocker is the OpenCode platform limitation for realtime detection.
