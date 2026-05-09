---
name: research-literature-access
description: 文献全文合法获取与访问审计：处理付费墙、版本差异（published/accepted/preprint/tech report）、全文缺失与授权访问确认，优先free-first并记录access-attempts。Use when users ask “文献全文/论文打不开/付费墙/合法获取/check版本/source access”, needing legal full-text, user-authorized access, and audit logs.
compatibility: opencode
license: Apache-2.0
---

## 作用/Purpose

在合规前提下获取可用全文，并沉淀访问过程与版本信息，确保研究可复现、可审计。

## 触发场景/Trigger Scenarios

- 目标文献在付费墙后。
- 同一作品存在多个来源与版本。
- 需要确认 published / accepted manuscript / preprint / tech report。
- 用户要求阅读某论文但暂无全文。
- 需要向用户确认合法授权访问方式。

## 输入/Input

- 文献标识信息（title、DOI、authors、venue、year）。
- 用户可用授权方式（机构订阅、个人购买、手动登录等）。

## 输出/Output

- `literature-access.json`
- `access-attempts.jsonl`
- `updated source-index.jsonl`

## 工作流/Workflow

1. 识别作品并归一化元信息（title/DOI 等）。
2. 按 free-first 顺序检索合法来源：用户上传 → 官方开放版 → 预印本 → 作者主页 → 机构仓储 → 开放数据库 → 机构订阅 → 个人购买。
3. 若找到合法全文，记录来源与可访问性并继续。
4. 若未找到，询问用户授权访问选项，不做未授权操作。
5. 将所有尝试写入 `access-attempts.jsonl`。
6. 记录版本类型及差异风险，更新 `source-index.jsonl`。
7. 使用 `literature_access_record.py` 完成记录结构检查；参考 `legal-access-policy.md`、`credential-safety.md` 与 `literature-access-template.json`。

## 质量门禁/Quality Gates

- 必须有完整访问尝试日志。
- 必须标注 `full_text_available` 状态。
- 使用非正式出版版本时，必须记录版本类型与差异风险。
- 仅允许合法访问路径，严禁盗版与绕过。

## Gotchas/注意事项

- 不得存储明文凭据；仅记录 `secret_ref`（如 `os-keychain:name`、`env:VAR`、`manual-login`）。
- 摘要信息可登记，但不得冒充全文证据。
- 访问失败也要记录，避免重复无效尝试。
- 合规优先于速度。
