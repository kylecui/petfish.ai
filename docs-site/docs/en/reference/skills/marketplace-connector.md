# marketplace-connector

> Pack: **companion**

>

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
| 2 | Glama (glama.ai) | MCP server | 无需 |
| 3 | Smithery (smithery.ai) | MCP server | 需API key |
| 4 | SkillKit (localhost:3737) | Aggregated skills | 无需（本地） |
| 5 | anthropics/skills | Official Claude skills | 无需 |
| 6 | GitHub搜索 | SKILL.md repos | 无需（有限速） |

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

*... (40 more lines in full SKILL.md)*
