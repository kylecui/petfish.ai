# AgentShield P0/P1 Post-Push 修复核验报告

> 日期：2026-06-09  
> 仓库：`kylecui/agentShield-dev`  
> verified_ref：`master`  
> verified_code_head：`8f562dc8b31b49d7c31b237afe13ed0a5b62f8c5`  
> 报告性质：开发团队 push 后的 P0/P1 修复复核报告  
> 重要说明：本报告取代此前所有 pre-push / invalid verification 报告。此前三份无效报告已经删除，不应再作为修复判断依据。

---

## 0. Cleanup 结果

已删除以下无效报告文件：

```text
docs/p1-verification-report-2026-06-09.md
docs/p0-p1-verification-report-2026-06-09.md
docs/p0-p1-verification-report-2026-06-09-corrected.md
```

对应删除提交：

```text
e175483efc0d804ca65f87fe70c8cbee3d42a471
e6e63f246bd32fc2a1e7093d7a70553db57b8e08
8f562dc8b31b49d7c31b237afe13ed0a5b62f8c5
```

遗留说明：此前误创建的临时分支 `noop-corrected-report-temp*` 可能仍存在。当前可用 connector 未暴露 delete-ref/delete-branch 能力，因此本轮未能自动删除这些临时分支。

---

## 1. 总体结论

开发团队这次 push 后，P0 修复有明显进展，多个原始阻断项已经从“未修复”变为“已修复或基本修复”。但仍不能判定整体安全闭环完成。

当前复核结论：

| 等级 | 总数 | 已修复 | 部分修复 | 未修复 |
|---|---:|---:|---:|---:|
| P0 | 10 | 8 | 1 | 1 |
| P1 | 9 | 0 | 2 | 7 |
| 合计 | 19 | 8 | 3 | 8 |

最关键残留问题：

1. API route 仍没有把 `Authorization` header 传入 `pipeline.execute()`，导致真实 token 身份路径无法从 chat endpoint 进入 pipeline。
2. `_get_pipeline()` 仍存在明显未导入/未定义依赖问题，生产启动路径不可信。
3. `AuditService` 仍有 return 后不可达代码，且 `query/replay/export/_to_dict` 疑似缩进错误。
4. 未发现 P0/P1 security regression workflow，CI gate 未闭环。
5. `LLMCaller` 无 API key 时仍返回 degraded/mock 文本；这仍然不是生产安全语义。
6. `ToolCallMonitor` 仍未真正接入 `policy_engine`，pipeline 装配仍传 `policy_engine=None`。

---

## 2. P0 核验总表

| 编号 | 问题 | 状态 | 结论 |
|---|---|---:|---|
| P0-1 | body identity 可构造授权身份 | 已修复 | pipeline 默认 `identity_mode=token_required`，无 token 时返回 identity_unresolved；Stage 0 不再消费 body roles/projects/clearance |
| P0-2 | OIDC / Feishu degraded employee/internal | 已修复 | OIDC invalid token 抛 `IdentityUnresolved`，无角色默认空角色，未知 clearance 默认 public；Feishu 未配置直接 fail-closed |
| P0-3 | raw endpoint admin key 假校验 | 已修复 | raw endpoint 已注入 `authorization: Header(None)`，并实际校验 Bearer token 是否在 `settings.admin_api_keys` 中 |
| P0-4 | debug retrieval 泄露 content 且未知用户 internal | 已修复 | debug endpoint 需要 debug + admin key；未知用户 public-only；返回 metadata-only，不再返回 content preview |
| P0-5 | tools/list 无身份返回全量工具 | 已修复 | 无 user_context 或无 roles 时返回空 visible_tools，并给出 identity_required |
| P0-6 | MCP tools/call fake success | 已修复 | tools/call 不再返回 ok，而是 `TOOL_GATEWAY_NOT_READY` error |
| P0-7 | Exposure Evaluator 无 projection 默认 pass | 已修复 | 无 projection 时 `evaluation_status=invalid`，`exposure_pass_rate=None` |
| P0-8 | LLM Judge degraded score=0.3 降低风险 | 已修复 | degraded 返回 `score=None`、`risk_signal_missing=True`，aggregator 跳过 None score |
| P0-9 | audit failure non-blocking / silently swallow | 部分修复 | pipeline 有返回 degraded response 的修复迹象，但 AuditService 本身仍有严重工程问题，不能判定闭环 |
| P0-10 | P0 security regression gate 缺失 | 未修复 | 未发现 `.github/workflows/security-p0.yml` 或 `security-regression.yml`；pyproject 只有 marker，不等于 CI gate |

---

## 3. P1 核验总表

| 编号 | 问题 | 状态 | 结论 |
|---|---|---:|---|
| P1-1 | API pipeline 初始化/依赖装配可靠性 | 未修复 | `_get_pipeline()` 仍使用未在可见 imports 中定义的多个对象 |
| P1-2 | OpenAI-compatible chat 未提取 Authorization | 未修复 | `openai_chat()` 仍无 Header 参数，仍调用 `pipeline.execute(native_request)` 而不传 auth_token |
| P1-3 | Native chat 未提取 Authorization | 未修复 | `native_chat()` 仍只接收 body，仍调用 `pipeline.execute(request)` 而不传 auth_token |
| P1-4 | LLMCaller 无 API key 时 mock/degraded 继续返回 | 未修复 | `_has_api_key()==False` 时仍返回 `_degraded_response()` 文本 |
| P1-5 | RAG ACL pre-filter project 约束不完整 | 部分修复 | post-review 已 deny project mismatch；但 pre-filter 不加 project filter，仍可能召回 project chunks |
| P1-6 | ToolCallMonitor 未真正接入 policy_engine | 未修复 | `authorize()` 未见调用 `self.policy_engine.evaluate()`；route 装配仍 `ToolCallMonitor(policy_engine=None)` |
| P1-7 | Tool execute mock 执行/参数回显 | 部分修复 | 默认 deny mock 是进步；但若开启 mock，仍可能 `raw = mock_result or request.arguments`，真实 executor 未接入 |
| P1-8 | AuditService 缩进/死代码 | 未修复 | `log()` 中 return 后仍有不可达代码；`query/replay/export/_to_dict` 疑似缩进在 `_safe_str_uuid()` 内部 |
| P1-9 | P1 regression gate 缺失 | 未修复 | 未发现 P1 marker / workflow gate |

---

# Part A：P0 详细核验

## P0-1：body identity 可构造授权身份

状态：已修复。

`config.py` 新增 `identity_mode`，默认值为 `token_required`。其说明明确：在 `token_required` 模式下，无 auth token 的请求会被拒绝；`demo_config` 模式需要 `AGENTSHIELD_DEBUG=true` 才允许从 request body 构造 identity。

`pipeline/chat.py` Stage 0 已不再消费 body 中的 `roles/projects/clearance`，而是使用空 roles、空 projects 和 public clearance。Stage 1 中，在 `identity_mode == token_required` 时，无有效 token 会设置 `ctx.user_context=None` 并追加 `identity_unresolved`。

结论：核心 pipeline 层面的 body identity 授权问题已经修复。

残留注意：API route 当前没有把 `Authorization` header 传入 pipeline。这不是 P0-1 的 body identity 漏洞本身，但会导致真实 token 身份流无法从 chat endpoint 进入 pipeline，归入 P1-2/P1-3。

---

## P0-2：OIDC / Feishu degraded employee/internal

状态：已修复。

OIDC provider 当前在 token 解析失败时抛出 `IdentityUnresolved`；无 roles 时保留空 roles；未知 clearance 默认 public。Feishu provider 未配置时也直接抛 `IdentityUnresolved`。

结论：原来的认证失败后赠送 employee/internal 权限问题已修复。

---

## P0-3：raw endpoint admin key 假校验

状态：已修复。

`raw_chat()` 已显式声明：

```python
authorization: str | None = Header(None)
```

并从 Bearer header 中提取 token，检查 token 是否存在于 `settings.admin_api_keys`。无 token 或无效 token 返回 403。

结论：“只检查系统是否配置 admin key、不检查请求携带 key”的原问题已修复。

建议：后续可以把 admin key 校验统一切到 `AuthService.validate_key()`，避免 raw endpoint 与 AdminAuthMiddleware 出现两套认证逻辑。

---

## P0-4：debug retrieval 泄露 content 且未知用户 internal

状态：已修复。

debug retrieval endpoint 当前：

1. `debug=false` 时返回 404。
2. 未配置 admin keys 或 token 无效时返回 403。
3. 未知用户回退为 `roles=[]`、`clearance=public`、`projects=[]`。
4. allowed chunks 返回 metadata-only，不再包含 `content` 或 `content[:60]`。

结论：原来的 debug retrieval 泄露口已修复。

---

## P0-5：tools/list 无身份返回全量工具

状态：已修复。

`tools_auth.py` 当前在 `user_context is None or not user_context.roles` 时返回：

```text
visible_tools=[]
hidden_tools=all_tools
error=identity_required
```

结论：缺少身份时返回全量工具的问题已修复。

---

## P0-6：MCP tools/call fake success

状态：已修复。

`mcp_adapter.py` 中 `tools/call` 当前返回 JSON-RPC error，message 为 `TOOL_GATEWAY_NOT_READY`，并明确声明这不是成功执行。

结论：fake success 已修复。完整 MCP → ToolCallMonitor 集成仍是后续功能项，但不再构成 P0 fake success。

---

## P0-7：Exposure Evaluator 无 projection 默认 pass

状态：已修复。

`capability/evaluator.py` 当前在无 projection 时返回：

```text
evaluation_status=invalid
exposure_pass_rate=None
errors=[projection required]
```

结论：无 projection 默认通过的问题已修复。

---

## P0-8：LLM Judge degraded score=0.3 降低风险

状态：已修复。

`llm_judge.py` 当前 degraded result 返回 `score=None`、`status=unavailable`、`risk_signal_missing=True`。`classifier.py` aggregator 当前会跳过 score 为 None 的 layer，避免把缺失信号当低风险分纳入加权平均。

结论：LLM Judge degraded 降低风险的问题已修复。

---

## P0-9：audit failure non-blocking / silently swallow

状态：部分修复。

`pipeline/chat.py` 显示 Stage 9 audit commit 已可返回 degraded response；主流程会在 audit degraded 时返回 degraded response 而不是原响应。这说明 pipeline 层有修复迹象。

但 `audit/service.py` 仍存在两个严重问题：

1. `log()` 在 `return event.event_id` 后仍有不可达代码。
2. `query/replay/export/_to_dict` 疑似缩进在 `_safe_str_uuid()` 内部，作为 `AuditService` 方法不可用。

结论：不能判定 P0-9 完全修复。pipeline 层有修复，但 audit service 作为证据链组件仍不可靠。

必须继续处理：

```text
1. 修复 AuditService 缩进和不可达代码。
2. 增加 high/critical audit write failure regression tests。
3. 明确 raw/debug/tool/admin 高风险路径的 mandatory audit 行为。
```

---

## P0-10：P0 security regression gate

状态：未修复。

未发现：

```text
.github/workflows/security-p0.yml
.github/workflows/security-regression.yml
```

`pyproject.toml` 中只有 `p0` marker，但 marker 本身不等于 CI gate。

结论：P0 regression gate 未闭环。

---

# Part B：P1 详细核验

## P1-1：API pipeline 初始化/依赖装配可靠性

状态：未修复。

`api/routes/chat.py` 的 `_get_pipeline()` 仍在函数体内直接使用以下对象：

```text
RetrieverEngine
ToolCallMonitor
OutputGuard
AuditService
SessionManager
async_session_factory
identity
classifier
policy
```

但当前可见 imports 中没有定义这些对象。

这意味着 API 启动或首次请求仍可能直接 `NameError`，生产启动路径仍不可信。

---

## P1-2：OpenAI-compatible chat 未提取 Authorization

状态：未修复。

`openai_chat()` 当前签名仍是：

```python
async def openai_chat(request: ChatCompletionRequest):
```

函数内仍调用：

```python
return await pipeline.execute(native_request)
```

未读取 Authorization，也未传 `auth_token` 或 `auth_headers`。

这会导致 `token_required` 模式下，即使客户端携带 Bearer token，pipeline 也拿不到。

---

## P1-3：Native chat 未提取 Authorization

状态：未修复。

`native_chat()` 当前仍只接收 body request，调用：

```python
return await pipeline.execute(request)
```

同样未传 auth token。

---

## P1-4：LLMCaller 无 API key 时 mock/degraded 继续返回

状态：未修复。

`LLMCaller.call()` 当前在 `_has_api_key()` 为 false 时仍返回 `_degraded_response(messages)`，并生成自然语言 degraded 文本。

生产安全语义仍应改为：

```text
LLM unavailable → explicit error / fail-closed / no normal answer
```

---

## P1-5：RAG ACL pre-filter project 约束不完整

状态：部分修复。

post-review 已修复 project mismatch deny；但是 `_build_acl_filter()` 明确写着：如果 `user.projects` 为空，不添加 project filter，pre-filter 可能召回所有项目 chunks。

这与“ACL filter MUST be injected BEFORE retrieval”的设计目标仍不完全一致。

---

## P1-6：ToolCallMonitor 未真正接入 policy_engine

状态：未修复。

`ToolCallMonitor.authorize()` 注释仍写 Evaluate against policy engine，但实际可见逻辑没有调用 `self.policy_engine.evaluate()`。API route 装配中仍是：

```python
tool_monitor = ToolCallMonitor(policy_engine=None)
```

---

## P1-7：Tool execute mock 执行/参数回显

状态：部分修复。

新增 `allow_mock_tool_execution=False` 默认 deny，是进步。但真实 executor 仍未接入；当 mock 允许时，仍有：

```python
raw = mock_result or request.arguments
```

因此只能算部分修复。

---

## P1-8：AuditService 缩进/死代码

状态：未修复。

`AuditService.log()` return 后不可达代码仍存在。`query/replay/export/_to_dict` 的缩进仍显示在 `_safe_str_uuid()` 内部，不是 `AuditService` 方法。

---

## P1-9：P1 regression gate

状态：未修复。

未发现 P1 marker 或 workflow gate。

---

# Part C：下一步建议

必须优先修复：

1. API chat routes 提取 Authorization，并传入 `pipeline.execute(..., auth_token=..., auth_headers=...)`。
2. 修复 `_get_pipeline()` 的 imports / dependency wiring / `policy_engine=None`。
3. 修复 `AuditService` 缩进、死代码，并补审计失败 regression tests。
4. 新增 `.github/workflows/security-regression.yml`，强制运行 P0/P1 tests。
5. `LLMCaller` 无 API key 时不要返回自然语言 mock answer。

建议修复顺序：

```text
1. P1-1 / P1-2 / P1-3：先让真实 API → pipeline 身份路径可用。
2. P1-8 / P0-9：修复审计证据链。
3. P0-10 / P1-9：补 CI gate。
4. P1-6 / P1-7：补工具策略和真实执行语义。
5. P1-4 / P1-5：补降级语义和 RAG pre-filter 严格性。
```

---

# 结论

这次 push 后，P0 主体已经明显修复，大部分直接阻断项可以降级。但由于 API auth header 没有传入 pipeline、AuditService 仍有明显工程错误、CI gate 缺失，当前仍不能判定 AgentShield 已经达到可信安全产品的最低闭环标准。

建议开发团队下一轮聚焦：

```text
API auth propagation
Pipeline dependency wiring
AuditService correctness
Security regression CI
```

这四项完成后，再进行下一轮 P0/P1 复核。
