# AgentShield P1 修复核验报告

> 日期：2026-06-09  
> 仓库：`kylecui/agentShield-dev`  
> 核验范围：`docs/code-critical-review.md` 中 P1 级别问题的源码侧复核；由于 GitHub connector 对原审计文档返回内容在 P0 后发生截断，本报告按当前仓库中与 P1 级别风险对应的 9 个高优先级验证点进行逐项核验。  
> 结论：P1 修复未闭环，不建议进入展示/交付分支。

---

## 0. 总结结论

本轮核验共覆盖 9 个 P1 级别验证点：

| 编号 | 验证点 | 状态 | 结论 |
|---|---|---:|---|
| P1-1 | API pipeline 初始化/依赖装配可靠性 | 未修复 | `_get_pipeline()` 存在明显缩进/未导入/未定义依赖风险，运行路径不可信 |
| P1-2 | OpenAI-compatible chat 未提取 Authorization | 未修复 | `/v1/chat/completions` 仍只从 body.user 构造请求，不传 auth_token |
| P1-3 | Native chat 未提取 Authorization | 未修复 | `/api/v1/chat` 也未从 Header 提取身份凭证 |
| P1-4 | LLMCaller 无 API key 时 mock/degraded 继续返回 | 未修复 | 生产安全产品不应以 mock 回答替代 fail-closed |
| P1-5 | RAG ACL pre-filter 对 project 约束仍不完整 | 部分修复 | post-review 修了空项目绕过，但 pre-filter 在 user.projects 为空时没有显式限制 project |
| P1-6 | ToolCallMonitor 未真正接入 policy_engine | 未修复 | 注释写 evaluate policy，但代码未调用 policy_engine，且装配时传入 None |
| P1-7 | Tool execute 仍是 mock 执行/参数回显 | 未修复 | `execute_and_sanitize()` 仍以 request.arguments/mock_result 作为 raw result |
| P1-8 | AuditService 方法缩进/死代码导致查询能力不可用 | 未修复 | `query/replay/export/_to_dict` 疑似缩进进 `_safe_str_uuid()` 内；`log()` 后存在不可达代码 |
| P1-9 | CI/security regression gate 缺失 | 未修复 | 未发现 `.github/workflows/security-p0.yml` 或 `ci.yml`；pyproject 只有 marker，无 CI 门禁 |

整体判断：当前 P1 级问题仍会影响 AgentShield 作为 Runtime Access Control Execution Plane 的工程可信度。P0 仍未闭环的情况下，P1 问题进一步说明当前代码不能作为安全产品交付版本。

---

## P1-1：API pipeline 初始化/依赖装配可靠性

状态：未修复。

### 发现

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

### 发现

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

### 发现

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

### 发现

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

### 发现

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

### 发现

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

### 发现

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

### 发现

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

## 10. 处理优先级建议

### 第一优先级：让系统能可靠启动并走真实安全链路

1. P1-1 `_get_pipeline()` 装配修复
2. P1-2 / P1-3 API auth token extraction
3. P1-8 AuditService 缩进/死代码修复

### 第二优先级：消除 mock/fake 安全路径

1. P1-4 LLM degraded mock response
2. P1-6 ToolCallMonitor policy_engine 接入
3. P1-7 Tool mock execution 禁用生产路径

### 第三优先级：补齐数据面与工程门禁

1. P1-5 RAG project pre-filter
2. P1-9 security regression CI

---

## 11. 最终结论

P1 修复没有闭环。

当前仓库在 P0 未闭环的基础上，P1 仍存在执行链路、API 身份传递、RAG pre-filter、工具策略接入、工具执行、审计服务、CI 门禁等工程可靠性问题。

开发团队应暂停继续堆叠 showcase 功能，先完成以下硬性目标：

```text
1. 所有 P0 修复闭环。
2. 本报告列出的 9 项 P1 验证点全部修复。
3. 新增 P0/P1 regression tests。
4. CI 中强制运行安全回归测试。
5. 禁止生产路径出现 demo/mock/fake-success/fake-pass。
```

在上述目标完成前，不建议宣称 AgentShield 已达到可信安全产品的最低工程标准。
