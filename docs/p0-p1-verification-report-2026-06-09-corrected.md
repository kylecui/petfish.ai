# AgentShield P0/P1 修复核验完整报告（Corrected）

> 日期：2026-06-09  
> 仓库：`kylecui/agentShield-dev`  
> 报告性质：P0/P1 修复状态复核报告  
> 更正说明：本报告取代 `docs/p0-p1-verification-report-2026-06-09.md`。上一版误将 P0 统计为 8 项；实际 P0 应为 10 项。  
> 基线来源：`docs/code-critical-review.md` 与当前源码复核。

---

## 0. 总体结论

当前修复没有闭环。

- P0：10 项核验，0 项完全修复，1 项部分修复，9 项未修复。
- P1：9 项核验，0 项完全修复，1 项部分修复，8 项未修复。
- 合计：19 项核验，0 项完全修复，2 项部分修复，17 项未修复。

当前代码仍不应宣称 “rescue 成功”，也不应作为可信安全产品展示或交付。核心问题仍集中在：

1. 身份边界仍可被 request body 击穿。
2. 身份源失败时仍存在 employee/internal fail-open。
3. raw/debug endpoint 仍存在绕过或泄露路径。
4. 工具投影、MCP、Exposure Evaluator 存在 fake success / fake pass。
5. LLM Judge 与 LLMCaller 降级路径仍会弱化安全语义。
6. Audit 写入失败和 AuditService 工程质量仍不能支撑安全产品证据链。
7. P0/P1 regression gate 缺失。

---

## 1. P0 阻断项核验总表

| 编号 | 问题 | 状态 | 结论 |
|---|---|---:|---|
| P0-1 | 身份路径仍然允许 request body 构造授权身份 | 未修复 | body.user 仍进入 `ctx.user_context`，Stage 0 也读取 body roles/projects/clearance |
| P0-2 | OIDC / Feishu degraded identity 仍返回 employee/internal | 未修复 | IdP 失败仍赠送内部员工权限 |
| P0-3 | raw endpoint admin key 校验是假的 | 部分修复 | 增加 enable/debug gate，但仍未验证请求头 Authorization |
| P0-4 | debug retrieval endpoint 泄露 chunk 内容且未知用户回退 internal | 未修复 | 仍返回 `content[:60]`，未知用户仍 employee/internal |
| P0-5 | tools/list 无 user_context 时返回所有工具 | 未修复 | 缺少身份时仍 `visible_tools=all_tools` |
| P0-6 | MCP tools/call 返回 ok，属于 fake success | 未修复 | 未接 ToolCallMonitor，却返回成功 |
| P0-7 | Tool Exposure Evaluator 没有 projection 时默认 pass | 未修复 | 无 projection 时仍 `exposure_pass_rate=1.0` |
| P0-8 | LLM Judge degraded score=0.3 会降低风险 | 未修复 | 检测器不可用仍返回低风险分 |
| P0-9 | Audit write failure non-blocking / silently swallow 风险 | 未修复 | pipeline 注释写高风险审计失败不能吞，但当前审计链路未形成 fail-closed 证据 |
| P0-10 | P0 security regression gate 缺失 | 未修复 | 未见可阻断合并的 P0 安全回归 workflow |

---

## 2. P1 高优先级项核验总表

| 编号 | 问题 | 状态 | 结论 |
|---|---|---:|---|
| P1-1 | API pipeline 初始化/依赖装配可靠性 | 未修复 | `_get_pipeline()` 存在明显缩进、未定义依赖和装配不可信问题 |
| P1-2 | OpenAI-compatible chat 未提取 Authorization | 未修复 | `/v1/chat/completions` 未把 auth token 传入 pipeline |
| P1-3 | Native chat 未提取 Authorization | 未修复 | `/api/v1/chat` 同样未提取 Header 身份凭证 |
| P1-4 | LLMCaller 无 API key 时 mock/degraded 继续返回 | 未修复 | 生产路径不应以 mock/degraded answer 继续执行 |
| P1-5 | RAG ACL pre-filter 对 project 约束仍不完整 | 部分修复 | post-review 修复，但 pre-filter 对空 projects 未显式限制 project |
| P1-6 | ToolCallMonitor 未真正接入 policy_engine | 未修复 | 注释写 policy evaluation，但代码未调用 policy_engine |
| P1-7 | Tool execute 仍是 mock 执行/参数回显 | 未修复 | `execute_and_sanitize()` 仍以 request.arguments/mock_result 作为 raw result |
| P1-8 | AuditService 方法缩进/死代码导致查询能力不可用 | 未修复 | `query/replay/export` 疑似缩进错误；`log()` 后存在不可达代码 |
| P1-9 | P1 security regression gate 缺失 | 未修复 | 只有 pytest marker 不等于 CI gate，未见 P1 release-blocking workflow |

---

# Part A：P0 阻断项详细核验

## P0-1：身份路径仍然允许 request body 构造授权身份

状态：未修复。

当前 `pipeline/chat.py` 的 Stage 1 仍在无 `auth_token` 且 body 有 `user_id` 时，从 request body 构造 `ctx.user_context`。Stage 0 preflight 在身份解析之前已经从 request body user 中读取 `user_id`、`tenant_id`、`roles`、`projects`、`clearance`。

### 风险

攻击者可以伪造 body.user，使请求获得伪造身份上下文。后续 RAG、policy、tool projection、tool authorization 都可能基于该伪造身份做判断。

### 必须修复

```text
no auth token → identity_unresolved → deny
body.user 只能作为 correlation/audit hint，不得进入 UserContext 或 PreflightContext 授权字段。
```

### 必补测试

```text
test_chat_without_auth_token_denies_in_fail_closed_mode.py
test_body_user_cannot_become_authorization_identity.py
test_preflight_does_not_consume_body_roles_projects_clearance.py
test_demo_config_identity_requires_debug_mode.py
test_demo_identity_marks_response_and_audit_as_not_production.py
```

---

## P0-2：OIDC / Feishu degraded identity 仍返回 employee/internal

状态：未修复。

OIDC token 解析失败后仍返回 degraded user；OIDC claims 没有 roles 时默认 `employee`，clearance 无法识别时默认 `internal`。Feishu provider 当前无条件返回 degraded UserContext，同样是 employee/internal。

### 风险

这是典型认证失败后的权限赠送。IdP 不可用、token invalid、provider 未配置时，系统不应假定调用者是内部员工。

### 必须修复

```text
IdP unavailable / invalid token / provider unconfigured → raise IdentityUnresolved
```

或者最多返回：

```text
roles=[]
projects=[]
clearance=public
auth_source=<provider>_unresolved
identity_confidence=0
```

### 必补测试

```text
test_oidc_invalid_token_does_not_return_employee.py
test_oidc_missing_roles_does_not_default_employee.py
test_oidc_unknown_clearance_does_not_default_internal.py
test_feishu_unconfigured_does_not_return_internal.py
test_identity_provider_degraded_denies_internal_resource.py
```

---

## P0-3：raw endpoint admin key 校验仍不合格

状态：部分修复。

`/v1/chat/raw` 已增加 `AGENTSHIELD_ENABLE_RAW_LLM=true` 与 `AGENTSHIELD_DEBUG=true` gate，但仍没有从 FastAPI 参数注入 Authorization header，也没有校验调用者提交的 admin API key。当前逻辑只是检查系统是否配置了 admin_api_keys。

### 风险

一旦 raw endpoint 被 enable 且 debug 打开，只要系统配置了 admin key，调用者可能不需要携带 admin key 即可访问 raw LLM，绕过安全管线。

### 必须修复

```python
async def raw_chat(
    request: dict,
    authorization: str | None = Header(None),
):
    verify_admin_key_or_raise(authorization)
```

同时 raw endpoint 必须纳入 AdminAuthMiddleware 或独立 raw endpoint auth guard，并写 audit。

### 必补测试

```text
test_raw_endpoint_disabled_by_default.py
test_raw_endpoint_enabled_without_authorization_denies.py
test_raw_endpoint_invalid_admin_key_denies.py
test_raw_endpoint_valid_admin_key_allows_only_in_debug.py
test_raw_endpoint_audits_every_call.py
```

---

## P0-4：debug retrieval endpoint 仍泄露内容且未知用户回退 internal

状态：未修复。

`/api/v1/debug/retrieval` 仍然存在：未知 user fallback 到 employee/internal、返回 allowed chunk 的 `content[:60]`、未看到 debug gate、未看到 admin auth、未看到 localhost-only 或环境隔离。

### 风险

这是直接数据泄露 endpoint。攻击者可以传入任意 user，触发 internal employee fallback，并看到 retrieval allowed content preview。

### 必须修复

```text
AGENTSHIELD_DEBUG_RETRIEVAL=false 默认
debug=true + valid admin key + localhost/internal allowlist 才可启用
未知用户必须 public-only
返回 metadata-only，禁止 content/content_preview/raw_text
```

### 必补测试

```text
test_debug_retrieval_disabled_by_default.py
test_debug_retrieval_requires_admin.py
test_debug_retrieval_requires_debug_mode.py
test_debug_retrieval_does_not_return_content.py
test_debug_retrieval_unknown_user_public_only.py
```

---

## P0-5：tools/list 无 user_context 时仍返回所有工具

状态：未修复。

`/tools/list` 在 `user_context is None` 或 `not user_context.roles` 时，仍返回 `visible_tools = all_tools`。

### 风险

缺少可信身份时，LLM 或调用方不应该看到完整工具清单。这违反工具最小暴露原则。

### 必须修复

```text
user_context missing → visible_tools=[]
user_context missing → hidden_tools=all_tools
reason=identity_required
```

或者直接 403。

### 必补测试

```text
test_tools_list_without_identity_returns_no_tools.py
test_tools_list_empty_roles_returns_no_tools_or_public_only.py
test_tools_list_does_not_return_all_tools_by_default.py
test_tools_list_requires_trusted_identity.py
```

---

## P0-6：MCP tools/call 仍返回 fake success

状态：未修复。

MCP adapter 明确写着 ToolCallMonitor 尚未完整集成，但 `tools/call` 仍返回 `ok`。

### 风险

调用方会以为工具调用成功，但实际上没有经过 Tool Projection、Tool Authorization、Argument Guard、Credential Broker、Result Sanitizer、Audit。

### 必须修复

```json
{
  "error": {
    "code": "TOOL_GATEWAY_NOT_READY",
    "message": "MCP tools/call is disabled until ToolCallMonitor integration is complete"
  }
}
```

### 必补测试

```text
test_mcp_call_without_tool_monitor_returns_error.py
test_mcp_call_never_returns_fake_ok.py
test_mcp_tools_list_uses_projection.py
test_mcp_call_goes_through_tool_monitor.py
test_mcp_call_audits_decision.py
```

---

## P0-7：Tool Exposure Evaluator 没有 projection 时默认 pass

状态：未修复。

`ToolExposureEvaluator` 在未配置 projection 时仍返回 `exposure_pass_rate=1.0`。

### 风险

Evaluator 的职责是证明工具暴露是否正确。没有 projection，就没有评价对象，不应通过。当前行为等价于门禁系统未接入门禁策略时默认放行。

### 必须修复

```text
evaluation_status=invalid
exposure_pass_rate=0.0 或 null
errors=["projection_required"]
publish_gate=false
```

### 必补测试

```text
test_exposure_evaluator_requires_projection.py
test_exposure_evaluator_missing_projection_fails_gate.py
test_exposure_evaluator_invalid_status_blocks_publish.py
```

---

## P0-8：LLM Judge degraded score=0.3 仍会降低风险

状态：未修复。

LLM Judge 在 LLM 不可用或异常时返回 `score=0.3`、`confidence=0.0`、`enabled=True`。

### 风险

Judge 不可用不是低风险，而是风险信号缺失。如果聚合器把 `score=0.3` 纳入平均或加权汇总，整体风险会被降低。

### 必须修复

方案 A：fail-closed 高风险：

```text
score=1.0
confidence=0.0
risk_types=["detector_unavailable"]
enabled=False
degraded=True
```

方案 B：unknown-risk，不参与降低风险：

```text
score=None
confidence=0.0
risk_types=["detector_unavailable"]
enabled=False
degraded=True
aggregation_effect="no_lowering"
```

### 必补测试

```text
test_llm_judge_degraded_does_not_lower_risk.py
test_llm_judge_degraded_marks_detector_unavailable.py
test_prompt_classifier_detector_failure_is_fail_closed_or_unknown.py
test_risk_aggregation_ignores_degraded_low_score_for_lowering.py
```

---

## P0-9：Audit write failure non-blocking / silently swallow 风险

状态：未修复。

`pipeline/chat.py` 顶部 fail-closed invariant 明确写着：`audit write failure for high-risk event → log alert, don't silently swallow`。但从当前可见代码和审计服务质量看，审计链路还没有形成高风险事件审计失败时的强制阻断/告警闭环：

1. pipeline 中 audit failure 的强约束没有看到对应 regression test。
2. `AuditService.log()` 自身存在不可达代码和后续方法缩进疑点，审计服务可靠性不足。
3. raw/debug/tool 等关键路径也没有看到完整 audit 保障。

### 风险

安全产品的审计链路不是可选日志。高风险事件如果因为 DB、schema、session、序列化等问题无法写入，而请求仍继续成功返回，就会形成不可追溯的安全绕过。

### 必须修复

```text
high/critical risk event audit write failure → fail closed or explicit security alert
raw/debug/tool/admin sensitive action → mandatory audit
AuditService failure must propagate to pipeline security decision for high-risk events
```

建议区分：

```text
low-risk audit failure → degrade with alert
high/critical audit failure → block or require admin override
```

### 必补测试

```text
test_high_risk_audit_write_failure_blocks_response.py
test_critical_risk_audit_write_failure_blocks_response.py
test_raw_endpoint_audit_failure_blocks_or_alerts.py
test_tool_call_audit_failure_blocks_high_risk_tool.py
test_audit_failure_never_silently_swallowed.py
```

---

## P0-10：P0 security regression gate 缺失

状态：未修复。

当前没有看到可阻断合并的 P0 security regression workflow。`pyproject.toml` 中虽有 `p0` marker，但 marker 不是 CI gate，也不能证明每次合并前会运行 P0 安全回归测试。

### 风险

P0 修复如果没有 regression gate，后续提交会反复引入 body identity、debug bypass、fake MCP success、tool full exposure、LLM judge soft-fail、audit non-blocking 等已知高危问题。

### 必须修复

新增：

```text
.github/workflows/security-p0.yml
```

最低执行：

```bash
ruff check src tests
mypy src
pytest -m p0
pytest tests/security/p0
```

必须禁止：

```text
xfail P0 tests
skip P0 tests
只测 happy path
```

### 必补测试/门禁

```text
test_security_p0_workflow_exists.py
test_p0_marker_runs_in_ci.py
test_p0_tests_are_not_skipped_or_xfailed.py
test_p0_regression_suite_covers_all_10_items.py
```

---

# Part B：P1 高优先级项详细核验

## P1-1：API pipeline 初始化/依赖装配可靠性

状态：未修复。

`_get_pipeline()` 存在明显工程问题：多个核心对象在可见代码片段中未导入或未定义；初始化块显示为额外缩进；`ToolCallMonitor(policy_engine=None)` 意味着工具授权链路未接入策略引擎。

### 必补测试

```text
test_pipeline_factory_imports_all_dependencies.py
test_pipeline_factory_fails_when_policy_engine_missing.py
test_pipeline_factory_fails_when_audit_service_missing.py
test_pipeline_factory_does_not_silently_use_mock_vector_store_in_prod.py
```

---

## P1-2：OpenAI-compatible chat 未提取 Authorization

状态：未修复。

`/v1/chat/completions` 只接收 request body，没有读取 `Authorization`，也没有向 `pipeline.execute()` 传入 `auth_token` 或 `auth_headers`。

### 必补测试

```text
test_openai_chat_extracts_bearer_token.py
test_openai_chat_passes_auth_token_to_pipeline.py
test_openai_chat_without_auth_denies_in_fail_closed.py
```

---

## P1-3：Native chat 未提取 Authorization

状态：未修复。

`/api/v1/chat` 同样没有读取请求头，也没有向 pipeline 传入 `auth_token` 或 `auth_headers`。

### 必补测试

```text
test_native_chat_extracts_bearer_token.py
test_native_chat_passes_auth_headers_to_pipeline.py
test_native_chat_body_user_not_authoritative.py
```

---

## P1-4：LLMCaller 无 API key 时 mock/degraded 继续返回

状态：未修复。

`LLMCaller.call()` 在 `_has_api_key()` 为 false 时，会返回 `_degraded_response(messages)`。

### 必补测试

```text
test_llm_no_api_key_fails_closed_in_prod.py
test_llm_degraded_response_requires_debug_or_demo.py
test_pipeline_does_not_treat_degraded_llm_as_normal_answer.py
```

---

## P1-5：RAG ACL pre-filter 对 project 约束仍不完整

状态：部分修复。

post-retrieval review 已经修复 project mismatch deny；但 `_build_acl_filter()` 在 `user.projects` 为空时没有追加 project empty/null 条件，pre-filter 与注释不一致。

### 必补测试

```text
test_retriever_pre_filter_limits_project_when_user_has_no_projects.py
test_retriever_pre_filter_allows_only_user_projects_and_public.py
test_retriever_post_review_denies_project_mismatch.py
```

---

## P1-6：ToolCallMonitor 未真正接入 policy_engine

状态：未修复。

`ToolCallMonitor.authorize()` 注释写了 evaluate policy engine，但实际未看到 `self.policy_engine.evaluate()` 调用；pipeline 装配时还传入 `policy_engine=None`。

### 必补测试

```text
test_tool_monitor_requires_policy_engine_in_prod.py
test_tool_monitor_invokes_policy_engine.py
test_tool_monitor_policy_exception_denies.py
test_tool_monitor_records_policy_hits.py
```

---

## P1-7：Tool execute 仍是 mock 执行/参数回显

状态：未修复。

`ToolCallMonitor.execute_and_sanitize()` 中 `raw = mock_result or request.arguments`，生产路径仍可能把输入参数作为工具结果回显。

### 必补测试

```text
test_tool_execute_without_executor_returns_not_ready.py
test_tool_mock_execution_requires_debug_mode.py
test_tool_execution_never_echoes_arguments_as_result_in_prod.py
test_tool_execution_audits_authorize_execute_sanitize.py
```

---

## P1-8：AuditService 方法缩进/死代码导致查询能力不可用

状态：未修复。

`AuditService.log()` 在 `return event.event_id` 后存在不可达代码。`query/replay/export/_to_dict` 疑似缩进错误，可能不在 `AuditService` 类内。

### 必补测试

```text
test_audit_service_log_returns_event_id.py
test_audit_service_query_is_class_method.py
test_audit_service_replay_is_class_method.py
test_audit_service_export_is_class_method.py
test_audit_service_no_unreachable_dead_code.py
```

---

## P1-9：P1 security regression gate 缺失

状态：未修复。

P0 需要 release-blocking gate；P1 也需要 hardening gate。当前仅有 pytest marker 不足以证明合并前会执行 P1 安全回归。

### 必补测试/门禁

```text
test_security_p1_workflow_exists.py
test_p1_marker_runs_in_ci.py
test_p1_tests_are_not_skipped_or_xfailed.py
test_p1_regression_suite_covers_all_9_items.py
```

---

# Part C：开发处理路线图

## 第一阶段：先封住 P0 直接绕过路径

1. P0-1：body identity。
2. P0-2：IdP degraded employee/internal。
3. P0-3：raw endpoint admin key 校验。
4. P0-4：debug retrieval 泄露口。
5. P0-5：tools/list 全量工具暴露。

## 第二阶段：修复工具网关、评估门禁和审计门禁

1. P0-6：MCP fake success。
2. P0-7：Exposure Evaluator fake pass。
3. P0-9：Audit failure non-blocking。
4. P1-6：ToolCallMonitor 接入 policy engine。
5. P1-7：Tool execution 禁止 mock 回显。

## 第三阶段：修复降级语义和 RAG pre-filter

1. P0-8：LLM Judge degraded 不能降低风险。
2. P1-4：LLMCaller 无 key 不得 mock 正常回答。
3. P1-5：RAG ACL project pre-filter 完整注入。

## 第四阶段：修复工程可靠性和 CI 门禁

1. P1-1：pipeline factory。
2. P1-2/P1-3：API auth token extraction。
3. P1-8：AuditService。
4. P0-10：P0 security regression CI。
5. P1-9：P1 security regression CI。

---

# Part D：合并/发布门禁建议

在 P0/P1 全部闭环前，不建议合并到可展示分支。

建议新增：

```text
.github/workflows/security-regression.yml
.github/workflows/security-p0.yml
```

最低执行：

```bash
ruff check src tests
mypy src
pytest -m p0
pytest -m p1
pytest tests/security
```

建议新增 pytest markers：

```toml
markers = [
    "p0: P0 security invariant tests — must always pass",
    "p1: P1 security hardening tests — must pass before release",
]
```

合并标准：

```text
1. 10 个 P0 regression tests 全部通过。
2. 9 个 P1 regression tests 全部通过。
3. 不允许 xfail/skip 关键安全测试。
4. 不允许生产路径出现 demo/mock/fake-success/fake-pass。
5. 不允许未认证路径访问 internal/confidential/secret 数据或全量工具清单。
6. 不允许 high/critical 审计失败被静默吞掉。
```

---

# Part E：最终结论

当前 AgentShield 代码仍处于“开始具备安全产品形状，但安全执行闭环没有成立”的状态。

P0/P1 均未闭环意味着：

```text
身份不可信；
调试口未封；
raw 绕过仍危险；
工具投影和执行不可信；
检测器与模型降级语义不安全；
审计与 CI 门禁不足。
```

开发团队应暂停继续堆叠 showcase 功能，优先完成 P0/P1 hardening 与 regression gate。

在 P0/P1 全部修复并通过自动化测试前，不建议宣称 AgentShield 已达到可信 Runtime Access Control Execution Plane 的最低工程标准。
