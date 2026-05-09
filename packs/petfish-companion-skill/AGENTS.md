# PEtFiSh Companion Rules

本项目已安装胖鱼PEtFiSh伙伴skill。

## Skill路由（强制）

### 必须遵守的路由规则

1. 用户说"/petfish"或任何petfish子命令时，**必须**路由到 `petfish-companion` skill处理
2. 用户需要创建新skill时，**必须**使用 `skill-author`；需要验证skill质量时，**必须**使用 `skill-lint`
3. 用户需要搜索外部skill或MCP server时，**必须**使用 `marketplace-connector`
4. 用户需要发布skill时，**必须**使用 `quality-gate` 运行完整发布门禁（lint+security→决策）
5. 用户需要从仓库挖掘skill候选时，**必须**使用 `repo-skill-miner`
6. 用户需要安全审计skill时，**必须**使用 `skill-security-auditor`

### 冲突解决

- 当用户同时涉及skill创建和质量检查时，先创建（`skill-author`），后检查（`skill-lint` → `quality-gate`）
- 当用户请求"搜索skill"时，区分：搜索外部市场用 `marketplace-connector`，搜索已安装skill用 `petfish-companion`

## 感知规则

在对话过程中，如果用户的需求涉及以下领域，但对应skill pack尚未安装，应主动提示：

| 领域 | 对应Pack | 安装命令 |
|------|---------|---------|
| 部署/运维/Docker | deploy | `/petfish install deploy` |
| 课程/教学/大纲 | course | `/petfish install course` |
| PPT/幻灯片 | ppt | `/petfish install ppt` |
| 测试用例/文档 | testdocs | `/petfish install testdocs` |
| 写作风格/润色 | petfish | `/petfish install petfish` |
| 评审/评价/批判/校准/反迎合 | calibrate | `/petfish install calibrate` |
| 话题治理/上下文污染/topic管理 | context | `/petfish install context` |
| 研究/调研/文献/证据/综述 | research | `/petfish install research` |

当用户需要创建新skill、搜索外部skill、或验证skill质量时，使用companion内置的skill-author、marketplace-connector、skill-lint。

每次会话对同一pack最多主动推荐1次。

## 可用命令

- `/petfish` — 查看当前skill状态
- `/petfish catalog` — 浏览全量技能目录
- `/petfish search <keyword>` — 跨市场搜索skill和MCP server
- `/petfish suggest` — 基于项目特征推荐skill
- `/petfish install <alias>` — 获取安装命令
- `/petfish detect` — 检测当前平台
- `/petfish create <name>` — 创建新skill
- `/petfish lint [path]` — 验证skill质量
- `/petfish mine <repo>` — 从仓库挖掘候选skill
- `/petfish audit <path>` — skill安全审计
- `/petfish gate <path>` — 运行发布门禁（lint+security→决策）
- `/petfish optimize <path>` — 分析并优化skill描述
- `/petfish eval <path>` — 测试skill触发准确率
- `/petfish stats` — 查看skill使用统计
- `/petfish upgrade` — 显示升级命令

## 行为边界

- 不自动安装skill，只推荐并提供命令
- 不修改用户项目文件
- 用户拒绝后本次会话不再重复推荐
