<!-- BEGIN pack: petfish-companion-skill -->
# PEtFiSh Companion Rules

本项目已安装胖鱼PEtFiSh伙伴skill。

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

## 行为边界

- 不自动安装skill，只推荐并提供命令
- 不修改用户项目文件
- 用户拒绝后本次会话不再重复推荐
<!-- END pack: petfish-companion-skill -->
