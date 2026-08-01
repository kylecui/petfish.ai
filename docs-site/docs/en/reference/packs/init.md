# init

**项目初始化器 — 创建标准目录结构、自动安装推荐skill、运行post-init wizard**

| Field | Value |
|---|---|
| Pack name | `project-initializer-skill` |
| Alias | `init` |
| Version | 1.1.0 |
| Skills | 1 |
| Commands | 1 |
| Agents | 0 |
| Compatibility | opencode |

## Skills

- [`project-initializer`](../skills/project-initializer.md) — Initialize/scaffold/bootstrap AI-agent workspaces, generate AGENTS.md/README/.opencode/docs/tasks/qa/mcp templates, run ...

## Install

```bash
uv run https://raw.githubusercontent.com/kylecui/petfish.ai/master/install.py --pack init --detect
```
