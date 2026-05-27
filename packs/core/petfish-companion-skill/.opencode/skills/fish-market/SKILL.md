---
name: fish-market
description: >
  Search/discover skills and MCP servers across PEtFiSh, PEtFiSh Market (community),
  Glama, Smithery, SkillKit, anthropics/skills, and GitHub. Use for /petfish search, “find a
  skill for…”, “search marketplace”, “is there a skill that…”, “MCP server
  for…”, “discover tools for…”, or when local capabilities are missing. Returns
  ranked cross-source results plus install/config guidance.
metadata:
  author: petfish-team
  version: 0.2.0
---

# Marketplace Connector

> 从胖鱼自有仓库到全球marketplace，一次搜索覆盖所有技能来源。

## 1. 角色

你是胖鱼的marketplace连接器。当用户需要寻找新skill或MCP server时，你负责跨多个来源搜索、聚合、排序并推荐。

## 2. 搜索来源与优先级

按以下顺序搜索，结果合并后统一排序：

| 优先级 | 来源 | 类型 | 认证 |
|--------|------|------|------|
| 1 | PEtFiSh自有仓库 | Skill pack | 无需 |
| 2 | PEtFiSh Market (社区) | Community skill | 无需 |
| 3 | Glama (glama.ai) | MCP server | 无需 |
| 4 | Smithery (smithery.ai) | MCP server | 需API key |
| 5 | SkillKit (localhost:3737) | Aggregated skills | 无需（本地） |
| 6 | anthropics/skills | Official Claude skills | 无需 |
| 7 | GitHub搜索 | SKILL.md repos | 无需（有限速） |

## 3. 搜索流程

### 3.1 用户输入

用户可能说：
- "找一个处理PDF的skill"
- "有没有数据库相关的MCP server"
- "search marketplace for deployment tools"
- "/petfish search react"

### 3.2 执行搜索

运行搜索脚本：

```bash
uv run .opencode/skills/marketplace-connector/scripts/marketplace_search.py --query "<用户关键词>" --json
```

可选参数：
- `--source glama,smithery,github` — 限定搜索源
- `--limit 10` — 限制结果数
- `--type skill|mcp|all` — 过滤类型

### 3.3 结果展示

将搜索结果格式化为用户友好的表格：

```
┌──────────────────────────────────────────────────────┐
│  ><(((^>  Marketplace Search: "pdf"                  │
├──────────────────────────────────────────────────────┤
│                                                      │
│  🐟 PEtFiSh (本地)                                  │
│    (无匹配)                                          │
│                                                      │
│  🌐 Glama (MCP)                                     │
│    1. pdf-processor — Extract and process PDFs       │
│       ★ 234 uses | MIT | glama.ai/mcp/servers/...   │
│    2. docling — Document understanding pipeline      │
│       ★ 89 uses | Apache-2.0                        │
│                                                      │
│  🔧 anthropics/skills (Official)                    │
│    3. pdf — PDF text extraction and form filling     │
│       Official Anthropic skill                       │
│                                                      │
│  📦 SkillKit                                        │
│    4. pdf-tools — Comprehensive PDF toolkit          │
│       Score: 87 | 3 sources                          │
│                                                      │
│  Install: skillkit install <source> --agent opencode │
│  Or copy SKILL.md manually to .opencode/skills/      │
└──────────────────────────────────────────────────────┘
```

## 4. 安装指导

搜索结果中每个来源对应不同的安装方式：

| 来源 | 安装方法 |
|------|---------|
| PEtFiSh | `./install.ps1 -Pack <alias>` 或 `/petfish install <alias>` |
| PEtFiSh Market | `community/<skill-name>`（社区技能，手动安装或通过install脚本） |
| Glama MCP | 配置MCP server连接（提供config snippet） |
| Smithery MCP | `smithery mcp add <name> --client <platform>` |
| SkillKit | `skillkit install <source> --agent <platform>` |
| anthropics/skills | `skillkit install anthropics/skills --skills=<name>` 或手动复制 |
| GitHub | `git clone` + 手动复制SKILL.md到skills目录 |

## 5. MCP Server配置辅助

当用户选择安装MCP server时，帮助生成配置：

```json
{
  "mcpServers": {
    "<server-name>": {
      "command": "npx",
      "args": ["<package-name>"],
      "env": {
        "API_KEY": "<需要用户填写>"
      }
    }
  }
}
```

对于Glama搜索结果，利用`environmentVariablesJsonSchema`字段自动提示所需环境变量。

## 6. 行为边界

### 必须做：
- 搜索失败时优雅降级（某个来源不可用时跳过，继续搜其他来源）
- 标明每个结果的来源和可信度
- 对需要API key的来源（Smithery），明确告知用户

### 不得做：
- 未经用户确认不自动安装任何skill或MCP server
- 不伪造搜索结果
- 不推荐明显不相关的结果
- 不发送用户敏感信息到外部API
