# context

**话题治理器 + Tiered Memory v2 — 在项目内维护topic边界、继承策略和切换记录，降低跨话题上下文污染。v2新增：4态生命周期 (active/warm/cold/archived)、压实感知状态转换、token预算感知分层保留、功能开关系统。三层架构：AGENTS.md always-on感知 + MCP server状态管理 + SKILL.md深度治理方法论**

| 字段 | 值 |
|---|---|
| 包名 | `fish-trail` |
| 别名 | `context` |
| 版本 | 1.1.0 |
| 技能数 | 1 |
| 命令数 | 0 |
| 代理数 | 0 |
| 兼容性 | opencode |

## 技能列表

- [`fish-trail`](../skills/fish-trail.md) — topic_detect is high risk, users ask to 整理/切换/合并/归档话题 or 清空上下文, or mention topic governance/上下文污染/继承隔离/session resume. I...

## 安装

```bash
uv run https://raw.githubusercontent.com/kylecui/petfish.ai/master/install.py --pack context --detect
```
