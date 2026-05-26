# Marketplace API Reference

本文件记录胖鱼支持的各marketplace API端点和响应格式，供marketplace_search.py使用。

## 1. Glama (glama.ai)

免费公开API，无需认证。

```
GET https://glama.ai/api/mcp/v1/servers?query=<keyword>&limit=20
```

响应字段：
```json
{
  "servers": [{
    "id": "string",
    "name": "string",
    "namespace": "string",
    "slug": "string",
    "description": "string",
    "attributes": ["hosting:hybrid"],
    "repository": {"url": "https://github.com/..."},
    "spdxLicense": {"name": "MIT License"},
    "tools": [{"name": "string", "description": "string"}]
  }],
  "pageInfo": {"hasNextPage": true, "endCursor": "string"}
}
```

单个server详情：
```
GET https://glama.ai/api/mcp/v1/servers/{namespace}/{slug}
```

## 2. Smithery (smithery.ai)

需要API key（`SMITHERY_API_KEY`环境变量）。

```
GET https://registry.smithery.ai/servers?q=<keyword>&pageSize=20
Authorization: Bearer <API_KEY>
```

响应字段：
```json
{
  "servers": [{
    "qualifiedName": "string",
    "displayName": "string",
    "description": "string",
    "verified": true,
    "useCount": 4638,
    "remote": true,
    "isDeployed": true
  }],
  "pagination": {"totalCount": 148, "currentPage": 1}
}
```

## 3. SkillKit (本地)

需要先运行`skillkit serve`启动本地REST server。

```
GET http://localhost:3737/search?q=<keyword>&limit=20&include_content=true
```

响应字段：
```json
{
  "skills": [{
    "name": "string",
    "description": "string",
    "source": "anthropics/skills",
    "tags": ["string"],
    "score": 87
  }],
  "total": 42
}
```

## 4. anthropics/skills (GitHub)

通过GitHub Contents API枚举官方skill列表。

```
GET https://api.github.com/repos/anthropics/skills/contents/skills
```

返回目录列表，每个条目代表一个skill：
```json
[{"name": "pdf", "type": "dir", "path": "skills/pdf"}]
```

获取单个skill的SKILL.md：
```
GET https://api.github.com/repos/anthropics/skills/contents/skills/{name}/SKILL.md
```

限速：60次/小时（无token），5000次/小时（有token）。

## 5. GitHub Code Search

搜索包含SKILL.md的仓库：
```
GET https://api.github.com/search/code?q=filename:SKILL.md+<keyword>
```

搜索高星仓库：
```
GET https://api.github.com/search/repositories?q=<keyword>+topic:ai-skills&sort=stars
```
