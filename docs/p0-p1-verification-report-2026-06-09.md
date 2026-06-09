# AgentShield P0/P1 修复核验完整报告

> 日期：2026-06-09  
> 仓库：`kylecui/agentShield-dev`  
> 报告性质：P0/P1 修复状态复核报告  
> 基线来源：`docs/code-critical-review.md` 与当前源码复核  
> 说明：P0 条目按原审计文档可见 P0-1～P0-8 逐项核验；P1 条目因 GitHub connector 对长审计文档返回内容在 P0 后截断，按当前仓库中与 P1 级高优先级风险对应的 9 个验证点进行源码侧核验。

---

## 0. 总体结论

当前修复没有闭环。

- P0：8 项核验，0 项完全修复，1 项部分修复，7 项未修复。
- P1：9 项核验，0 项完全修复，1 项部分修复，8 项未修复。
- 合计：17 项核验，0 项完全修复，2 项部分修复，15 项未修复。

当前代码仍不应宣称 “rescue 成功”，也不应作为可信安全产品展示或交付。主要问题仍集中在：

1. 身份边界仍可被 request body 击穿。
2. 身份源失败时仍存在 employee/internal fail-open。
3. raw/debug endpoint 仍存在绕过或泄露路径。
4. 工具投影、MCP、Exposure Evaluator 存在 fake success / fake pass。
5. LLM Judge 与 LLMCaller 降级路径仍会弱化安全语义。
6. ToolCallMonitor 没有真正接入 policy engine。
7. AuditService 存在明显工程可靠性问题。
8. CI/security regression gate 缺失。

---

## 1. P0 阻断项核验总表

| 编号 | 问题 | 状态 | 结论 |
|---|---|---:|---|
| P0-1 | 身份路径仍然允许 request body 构造授权身份 | 未修复 | body.user 仍进入 `ctx.user_context`，Stage 0 也读取 body roles/projects/clearance |
| P0-2 | OIDC / Feishu degraded identity 仍返回 employee/internal | 未修复 | IdP 失败仍赠送内部员工权限 |
| P0-3 | raw endpoint admin key 校验是假的 | 部分修复 | 增加 enable/debug gate，但仍未验证请求头中的 Authorization |
| P0-4 | debug retrieval endpoint 泄露 chunk 内容且未知用户回退 internal | 未修复 | 仍返回 `content[:60]`，未知用户仍 employee/internal |
| P0-5 | tools/list 无 user_context 时返回所有工具 | 未修复 | 缺少身份时仍 `visible_tools=all_tools` |
| P0-6 | MCP tools/call 返回 ok，属于 fake success | 未修复 | 未接 ToolCallMonitor，却返回成功 |
| P0-7 | Tool Exposure Evaluator 没有 projection 时默认 pass | 未修复 | 无 projection 时仍 `exposure_pass_rate=1.0` |
| P0-8 | LLM Judge degraded score=0.3 会降低风险 | 未修复 | 检测器不可用仍返回低风险分 |

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
| P1-9 | CI/security regression gate 缺失 | 未修复 | 未见实际 `.github/workflows/security-regression.yml` 或等效门禁 |

---

# Part A：P0 阻断项详细核验

---

## P0-1：身份路径仍然允许 request body 构造授权身份

状态：未修复。

### 当前问题

`pipeline/chat.py` 的 Stage 1 仍然在无 `auth_token` 且 body 中存在 `user_id` 时，从 request body 构造 `ctx.user_context`。

同时，Stage 0 preflight 在身份解析之前已经从 request body user 中读取：

- `user_id`
- `tenant_id`
- `roles`
- `projects`
- `clearance`

这意味着即使注释声称 body user 是 correlation-only，实际执行路径仍然消费了 body 中的授权属性。

### 风险

攻击者可以伪造 body.user，使请求获得伪造身份上下文。后续 RAG、policy、tool projection、tool authorization 都可能基于该伪造身份做判断。

### 必须修复

生产/默认路径必须改为：

```text
no auth token → identity_unresolved → deny
```

body.user 只能作为：

```text
correlation_id / display hint / audit hint
```

不得进入：

```text
UserContext
PreflightContext.roles
PreflightContext.projects
PreflightContext.clearance
```

Demo/showcase 必须显式隔离：

```text
AGENTSHIELD_IDENTITY_MODE=demo_config
AGENTSHIELD_DEBUG=true
AGENTSHIELD_DEMO_FAIL_OPEN=true
```

并且 response/audit 必须标记：

```text
identity_mode=demo_config
not_production_identity=true
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

### 当前问题

OIDC token 解析失败后仍返回 degraded user，且该 degraded user 仍是：

```text
roles=["employee"]
clearance="internal"
projects=[]
```

OIDC claims 没有 roles 时也默认 `employee`，clearance 无法识别时默认 `internal`。

Feishu provider 当前无条件返回 degraded UserContext，同样是 employee/internal。

### 风险

这是典型认证失败后的权限赠送。IdP 不可用、token invalid、provider 未配置时，系统不应假定调用者是内部员工。

### 必须修复

IdP 不可用、token invalid、provider unconfigured 时必须：

```text
raise IdentityUnresolved
```

或者最多返回：

```text
roles=[]
projects=[]
clearance=public
auth_source=<provider>_unresolved
identity_confidence=0
```

并确保该身份默认不能访问 internal/confidential/secret 资源。

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

### 已有进步

`/v1/chat/raw` 已增加：

```text
AGENTSHIELD_ENABLE_RAW_LLM=true
AGENTSHIELD_DEBUG=true
```

这比完全裸奔有进步。

### 当前问题

raw endpoint 仍然没有从 FastAPI 参数注入 Authorization header，也没有校验调用者提交的 admin API key。

当前逻辑仍然只是检查：

```text
系统是否配置了 admin_api_keys
```

而不是检查：

```text
本次请求是否携带了有效 admin key
```

另外，AdminAuthMiddleware 只保护：

```text
/api/v1/admin
/api/v1/capabilities
/api/v1/profiles
```

`/v1/chat/raw` 不在这些前缀内。

### 风险

一旦 raw endpoint 被 enable 且 debug 打开，只要系统配置了 admin key，调用者可能不需要携带 admin key 即可访问 raw LLM，绕过安全管线。

### 必须修复

应改为独立 guard：

```python
async def raw_chat(
    request: dict,
    authorization: str | None = Header(None),
):
    verify_admin_key_or_raise(authorization)
```

并建议将 raw endpoint 纳入统一受保护前缀或扩展 AdminAuthMiddleware：

```text
/v1/chat/raw → admin protected
```

同时 raw 调用必须写 audit。

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

### 当前问题

`/api/v1/debug/retrieval` 仍然存在以下问题：

1. 未知 user fallback 到 employee/internal。
2. 返回 allowed chunk 的 `content[:60]`。
3. 未看到 debug gate。
4. 未看到 admin auth。
5. 未看到 localhost-only 或环境隔离。

### 风险

这是直接数据泄露 endpoint。攻击者可以传入任意 user，触发 internal employee fallback，并看到 retrieval allowed content preview。

即使只返回 60 字，也足以泄露敏感业务信息、项目名称、内部事实、客户数据或策略文档片段。

### 必须修复

生产默认禁用：

```text
AGENTSHIELD_DEBUG_RETRIEVAL=false
```

启用条件必须同时满足：

```text
AGENTSHIELD_DEBUG=true
valid admin key
localhost only 或 explicit internal network allowlist
```

未知用户必须：

```text
roles=[]
clearance=public
projects=[]
```

返回内容必须改为 metadata-only：

```text
chunk_id
doc_id
classification
project
score
decision
reason
```

禁止返回：

```text
content
content_preview
raw_text
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

### 当前问题

`/tools/list` 在 `user_context is None` 或 `not user_context.roles` 时，仍返回：

```text
visible_tools = all_tools
hidden_tools = []
```

### 风险

这违反工具最小暴露原则。缺少可信身份时，LLM 或调用方不应该看到完整工具清单。

### 必须修复

改成：

```text
user_context missing → visible_tools=[]
user_context missing → hidden_tools=all_tools
reason=identity_required
```

或者直接返回 403。

注意：`roles=[]` 不等于“可见所有工具”，应代表匿名/public/未授权上下文。

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

### 当前问题

MCP adapter 明确写着 ToolCallMonitor 尚未完整集成，但 `tools/call` 仍返回：

```json
{"content": [{"type": "text", "text": "ok"}]}
```

### 风险

这是 fake success。调用方会以为工具调用成功，但实际上没有经过：

```text
Tool Projection
Tool Authorization
Argument Guard
Credential Broker
Result Sanitizer
Audit
```

安全产品中 fake success 比 NotImplemented 更危险，因为它会掩盖安全控制缺失。

### 必须修复

在完整接入 ToolCallMonitor 之前，必须改为：

```json
{
  "error": {
    "code": "TOOL_GATEWAY_NOT_READY",
    "message": "MCP tools/call is disabled until ToolCallMonitor integration is complete"
  }
}
```

`tools/list` 也必须使用 projection 后的可见工具列表，而不是空列表或静态列表。

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

### 当前问题

`ToolExposureEvaluator` 在未配置 projection 时仍返回：

```text
exposure_pass_rate=1.0
errors=["No projection configured — using default pass"]
```

### 风险

Evaluator 的职责是证明工具暴露是否正确。没有 projection，就没有评价对象，不应通过。

当前行为等价于“门禁系统未接入门禁策略时默认放行”。

### 必须修复

无 projection 时必须返回 invalid/fail：

```text
evaluation_status=invalid
exposure_pass_rate=0.0 或 null
errors=["projection_required"]
publish_gate=false
```

建议扩展结果结构：

```python
evaluation_status: Literal["pass", "fail", "invalid"]
gate_passed: bool
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

### 当前问题

LLM Judge 在 LLM 不可用或异常时返回：

```text
score=0.3
confidence=0.0
enabled=True
```

### 风险

Judge 不可用不是低风险，而是风险信号缺失。如果聚合器把 `score=0.3` 纳入平均或加权汇总，整体风险会被降低。

### 必须修复

建议改成以下任一方案。

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

聚合器必须保证 detector unavailable 不会降低最终风险。

### 必补测试

```text
test_llm_judge_degraded_does_not_lower_risk.py
test_llm_judge_degraded_marks_detector_unavailable.py
test_prompt_classifier_detector_failure_is_fail_closed_or_unknown.py
test_risk_aggregation_ignores_degraded_low_score_for_lowering.py
```

---

# Part B：P1 高优先级项详细核验

---

## P1-1：API pipeline 初始化/依赖装配可靠性

状态：未修复。

### 当前问题

`src/agent_shield/api/routes/chat.py` 的 `_get_pipeline()` 存在明显工程问题：

1. `RetrieverEngine`、`ToolCallMonitor`、`OutputGuard`、`AuditService`、`async_session_factory`、`identity`、`classifier`、`policy` 等对象在可见代码片段中未导入或未定义。
2. `_get_pipeline()` 中 `retriever = RetrieverEngine(_vector_store)` 之后的 ToolMonitor、OutputGuard、AuditService、SessionManager、PreflightGateway、SecureChatPipeline 初始化块显示为额外缩进，疑似会导致运行时或语法级错误。
3. 即使忽略缩进问题，`tool_monitor = ToolCallMonitor(policy_engine=None)` 也意味着工具授权链路没有接入策略引擎。

### 风险

pipeline 是执行平面入口。如果初始化路径不稳定，则所有后续身份、策略、检索、工具、审计都无法形成可信闭环。

### 处理建议

- 将 `_get_pipeline()` 拆成显式 factory，所有组件通过清晰 import 和 dependency wiring 完成装配。
- 任何核心组件缺失时必须 fail-fast，而不是 silent fallback。
- 禁止在生产路径中吞掉 `_vector_store.enable_real()` 异常后继续 mock。
- 为 `_get_pipeline()` 增加启动级测试。

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

### 当前问题

`/v1/chat/completions` 的 `openai_chat(request: ChatCompletionRequest)` 只接收 request body，没有 `Request`、`Header` 或 dependency 注入，也没有读取 `Authorization`。

随后它调用：

```python
pipeline.execute(native_request)
```

没有传入：

```python
auth_token=...
auth_headers=...
```

### 风险

即使 pipeline 支持 token-based identity resolution，OpenAI-compatible API 入口也不会把 token 传进去。实际身份仍会退化到 body/correlation/demo 路径。

### 处理建议

改成：

```python
async def openai_chat(
    request: ChatCompletionRequest,
    authorization: str | None = Header(None),
    fastapi_request: Request = None,
):
    auth_token = extract_bearer_token(authorization)
    return await pipeline.execute(native_request, auth_token=auth_token, auth_headers=dict(fastapi_request.headers))
```

### 必补测试

```text
test_openai_chat_extracts_bearer_token.py
test_openai_chat_passes_auth_token_to_pipeline.py
test_openai_chat_without_auth_denies_in_fail_closed.py
```

---

## P1-3：Native chat 未提取 Authorization

状态：未修复。

### 当前问题

`/api/v1/chat` 的 `native_chat(request: SecureChatRequest)` 同样没有读取请求头，也没有向 pipeline 传入 `auth_token` 或 `auth_headers`。

### 风险

Native API 虽然宣称是 full security context，但实际仍依赖 body 中的 `SecureChatRequest.user`，继续放大 P0-1 的 body identity 问题。

### 处理建议

- Native endpoint 与 OpenAI-compatible endpoint 使用统一 auth extraction helper。
- 未携带 token 时默认 fail-closed。
- body.user 只能作为 correlation/audit hint。

### 必补测试

```text
test_native_chat_extracts_bearer_token.py
test_native_chat_passes_auth_headers_to_pipeline.py
test_native_chat_body_user_not_authoritative.py
```

---

## P1-4：LLMCaller 无 API key 时 mock/degraded 继续返回

状态：未修复。

### 当前问题

`src/agent_shield/pipeline/llm.py` 文档说明：无 API key 时 graceful degrade to mock。`call()` 中如果 `_has_api_key()` 为 false，会返回 `_degraded_response(messages)`。

### 风险

对安全产品来说，LLM 调用失败或 API key 缺失不应自动生成 mock 回答。否则安全管线可能把非真实模型输出当作正常响应写入审计/展示/评估路径。

### 处理建议

- 生产模式：无 API key → fail-closed 或返回明确 `LLM_UNAVAILABLE`，不得生成自然语言 mock answer。
- demo 模式：必须显式标记 `degraded=true`、`not_production=true`。
- pipeline 下游不得把 degraded LLM response 当作正常模型输出。

### 必补测试

```text
test_llm_no_api_key_fails_closed_in_prod.py
test_llm_degraded_response_requires_debug_or_demo.py
test_pipeline_does_not_treat_degraded_llm_as_normal_answer.py
```

---

## P1-5：RAG ACL pre-filter 对 project 约束仍不完整

状态：部分修复。

### 已修方向

`RetrieverEngine._evaluate_access()` 中已经修复了一个重要问题：如果 chunk 有 project 且该 project 不在 user.projects 中，会 deny。这修复了 post-retrieval review 层的空项目绕过。

### 残留问题

`_build_acl_filter()` 中对项目过滤仍不完整：

```python
if user.projects:
    filter_conditions.append({"key": "project", "values": user.projects})
# If user has no projects, only match chunks with no project
```

注释说 “user has no projects 时只匹配无 project 的 chunks”，但代码没有追加任何 project empty/null 条件。

### 风险

向量库 pre-filter 没有显式限制 project 时，仍可能召回不该进入候选集的项目文档。虽然 post-review 可以二次拦截，但这违反了“ACL filter MUST be injected BEFORE retrieval”的原始设计目标。

### 处理建议

- user.projects 非空时，应允许 `project in user.projects` 加上明确 public/unassigned 条件。
- user.projects 为空时，应显式限制为 `project is null / project == "" / no project`。
- 过滤条件需要与具体 vector store filter dialect 对齐，不要只写注释。

### 必补测试

```text
test_retriever_pre_filter_limits_project_when_user_has_no_projects.py
test_retriever_pre_filter_allows_only_user_projects_and_public.py
test_retriever_post_review_denies_project_mismatch.py
```

---

## P1-6：ToolCallMonitor 未真正接入 policy_engine

状态：未修复。

### 当前问题

`ToolCallMonitor.authorize()` 的注释写了 “Evaluate against policy engine”，但实际可见代码没有调用 `self.policy_engine.evaluate()` 或等效策略判断。

同时在 `_get_pipeline()` 装配中，`ToolCallMonitor(policy_engine=None)` 被显式传入。

### 风险

工具授权只剩本地字段检查和 risk_level 判断，无法执行统一策略、租户策略、会话风险策略、用户/角色/资源策略。

### 处理建议

- `policy_engine` 在生产路径必须 required。
- `authorize()` 必须先做 policy decision，再进入 field-level pruning。
- policy evaluation 异常必须 deny。
- `policy_hits` 应真实记录命中的策略，而不是空数组。

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

### 当前问题

`ToolCallMonitor.execute_and_sanitize()` 中：

```python
raw = mock_result or request.arguments
```

这意味着工具执行仍是 placeholder/mock，甚至可能把输入参数作为 raw result 回显。

### 风险

这不是可信工具网关执行路径。缺少：

- executor registry
- credential broker
- backend isolation
- timeout/retry/circuit breaker
- result schema enforcement
- tool execution audit

### 处理建议

- 在真实 executor 接入前，生产路径必须返回 `TOOL_EXECUTOR_NOT_READY`。
- mock 执行只能在 debug/demo 显式开启。
- 工具执行结果必须经过 output schema validation 和 sanitizer。
- 工具调用必须写审计。

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

### 当前问题

`src/agent_shield/audit/service.py` 中：

1. `log()` 在 `return event.event_id` 后还有不可达代码：

```python
await session.commit()
await session.execute(stmt)
await session.commit()
return event.event_id
```

2. `_safe_str_uuid()` 定义后，`query()`、`replay()`、`export()`、`_to_dict()` 的缩进显示疑似仍在 `_safe_str_uuid()` 函数体内，而不是 `AuditService` 类方法。

### 风险

Audit service 是安全产品的不可篡改证据链。如果查询/回放/导出方法不可用，审计闭环不成立。死代码也说明该文件没有经过基础静态检查。

### 处理建议

- 修复缩进：`query/replay/export/_to_dict` 应为 `AuditService` 类方法。
- 删除 `log()` 中 return 后不可达代码。
- 为 audit service 增加单元测试和类型检查。
- CI 必须运行 ruff/mypy/pytest。

### 必补测试

```text
test_audit_service_log_returns_event_id.py
test_audit_service_query_is_class_method.py
test_audit_service_replay_is_class_method.py
test_audit_service_export_is_class_method.py
test_audit_service_no_unreachable_dead_code.py
```

---

## P1-9：CI/security regression gate 缺失

状态：未修复。

### 当前问题

未能读取到：

```text
.github/workflows/security-p0.yml
.github/workflows/ci.yml
```

`pyproject.toml` 中虽然定义了 pytest marker：

```toml
markers = [
    "p0: P0 security invariant tests — must always pass",
]
```

但仅有 marker 不等于 CI gate。当前没有看到强制执行 P0/P1 安全回归测试的 workflow。

### 风险

没有 CI gate，安全修复会退化为人工口头约束，后续提交很容易重新引入 fail-open / fake-success / debug bypass 问题。

### 处理建议

新增 GitHub Actions：

```text
.github/workflows/security-regression.yml
```

最低 gate：

```bash
ruff check src tests
mypy src
pytest -m p0
pytest tests/security
```

P1 完成后建议新增 marker：

```toml
"p1: P1 security hardening tests — must pass before release"
```

### 必补测试/门禁

```text
test_security_workflow_exists.py
test_p0_marker_runs_in_ci.py
test_p1_marker_runs_in_ci.py
```

---

# Part C：开发处理路线图

## 第一阶段：先封住 P0 直接绕过路径

必须优先处理：

1. P0-1：body identity。
2. P0-2：IdP degraded employee/internal。
3. P0-3：raw endpoint admin key 校验。
4. P0-4：debug retrieval 泄露口。
5. P0-5：tools/list 全量工具暴露。

目标：任何未认证/未授权/调试路径都不能获得内部身份、内部数据或全量工具视图。

---

## 第二阶段：修复工具网关和评估门禁

处理：

1. P0-6：MCP fake success。
2. P0-7：Exposure Evaluator fake pass。
3. P1-6：ToolCallMonitor 接入 policy engine。
4. P1-7：Tool execution 禁止 mock 回显。

目标：工具相关链路必须形成 Projection → Authorization → Execution → Sanitization → Audit 的闭环。

---

## 第三阶段：修复降级语义和 RAG pre-filter

处理：

1. P0-8：LLM Judge degraded 不能降低风险。
2. P1-4：LLMCaller 无 key 不得 mock 正常回答。
3. P1-5：RAG ACL project pre-filter 完整注入。

目标：任何检测器/模型/向量库降级都不能变成 fail-open。

---

## 第四阶段：修复工程可靠性和 CI 门禁

处理：

1. P1-1：pipeline factory。
2. P1-2/P1-3：API auth token extraction。
3. P1-8：AuditService。
4. P1-9：security regression CI。

目标：让安全语义能够通过自动测试和 CI 持续保持。

---

# Part D：合并/发布门禁建议

在 P0/P1 全部闭环前，不建议合并到可展示分支。

建议新增：

```text
.github/workflows/security-regression.yml
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
1. P0 regression tests 全部通过。
2. P1 regression tests 全部通过。
3. 不允许 xfail/skip 关键安全测试。
4. 不允许生产路径出现 demo/mock/fake-success/fake-pass。
5. 不允许未认证路径访问 internal/confidential/secret 数据或全量工具清单。
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

因此，开发团队应暂停继续堆叠 showcase 功能，优先完成 P0/P1 hardening 与 regression gate。

在 P0/P1 全部修复并通过自动化测试前，不建议宣称 AgentShield 已达到可信 Runtime Access Control Execution Plane 的最低工程标准。
