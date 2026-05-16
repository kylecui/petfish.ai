# context

**话题治理器 — 在项目内维护topic边界、继承策略和切换记录，降低跨话题上下文污染。三层架构：AGENTS.md always-on感知 + MCP server状态管理 + SKILL.md深度治理方法论**

| Field | Value |
|---|---|
| Pack name | `fish-trail` |
| Alias | `context` |
| Version | 1.0.1 |
| Skills | 1 |
| Commands | 0 |
| Agents | 0 |
| Compatibility | opencode |

## Skills

- [`fish-trail`](../skills/fish-trail.md) — topic_detect is high risk, users ask to 整理/切换/合并/归档话题 or 清空上下文, or mention topic governance/上下文污染/继承隔离/session resume. I...

## Install

=== "PowerShell"

    ```powershell
    & ([scriptblock]::Create((irm https://raw.githubusercontent.com/kylecui/petfish.ai/master/remote-install.ps1))) -Pack "context"
    ```

=== "Bash"

    ```bash
    curl -fsSL https://raw.githubusercontent.com/kylecui/petfish.ai/master/remote-install.sh | bash -s -- --pack context
    ```
