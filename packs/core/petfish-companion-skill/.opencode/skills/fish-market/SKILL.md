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

## 2. 搜索来源与优先级（2026市场调研版：市场优先，GitHub垫底）

按以下顺序搜索，结果合并后统一排序。**原则：现成市场结果（秒级）永远优先于GitHub挖掘（分钟级慢路径）**：

| 优先级 | 来源 | 类型 | 认证 |
|--------|------|------|------|
| 1 | PEtFiSh自有仓库 | Skill pack | 无需 |
| 2 | PEtFiSh Market (社区) | Community skill | 无需 |
| 3 | PEtFiSh Community注册表 | Community | 无需 |
| 4 | ClaudSkills | **SKILL.md聚合 69K+**（每日2刷，含中文内容） | 无需（24h本地缓存） |
| 5 | PulseMCP | MCP server（策展、日更） | 无需 |
| 6 | MCP Official Registry | MCP server（官方权威源） | 无需 |
| 7 | Glama | MCP server（最大索引48K） | `GLAMA_API_KEY`（2026起401） |
| 8 | Smithery | MCP server | `SMITHERY_API_KEY` |
| 9 | SkillKit | 本地聚合器（需本地:3737运行） | 本地 |
| 10 | anthropics/skills | 官方参考skill（30个精选） | 无需 |
| 11 | **GitHub搜索（最后手段）** | SKILL.md repos | 无需（限速） |

## 2.5 无结果时的升级梯子（强制顺序）

市场全部为空时，按此顺序逐级升级，**不得跳级直奔GitHub挖掘**：

1. **英文关键词重试**——中文查询零结果时先翻译重试（甘特图→gantt chart、题库→question bank）。脚本会在零结果时输出此提示。
2. **skills.sh CLI**（vercel-labs，73+agent支持含OpenCode）：`npx skills find <keyword>`
3. **GitHub挖掘**（repo-skill-miner）——仅当以上全空。明确告知用户这是慢路径（分钟级）。
4. **`/petfish create`**——从零创建。GitHub挖掘与create是"最后手段二人组"，GitHub仅排create之前。

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
uv run .opencode/skills/fish-market/scripts/marketplace_search.py --query "<用户关键词>" --json
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
