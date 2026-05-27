---
name: petfish
description: >
  胖鱼PEtFiSh伙伴入口。查看已装skill状态、搜索技能目录、
  跨市场搜索skill、创建新skill、验证skill质量、
  获取安装建议、检测当前平台。
  Trigger: /petfish [subcommand]
  Subcommands: status, catalog, suggest, install <alias>, detect, search <keyword>, create <name>, lint [path], mine <repo>, audit <path>, gate <path>, optimize <path>, eval <path>, stats
---

# /petfish — 胖鱼PEtFiSh Companion

根据用户输入的子命令执行对应操作。如果没有子命令，默认显示status。

## 子命令路由

### /petfish 或 /petfish status

运行以下脚本获取当前项目的skill安装状态：

```bash
uv run .opencode/skills/petfish-companion/scripts/check_installed.py --target .
```

将输出格式化为状态卡片展示：
- 当前检测到的平台
- 已安装的pack列表（含版本）
- 未安装但可用的pack列表
- 安装提示

### /petfish catalog

运行以下脚本列出全量技能目录：

```bash
uv run .opencode/skills/petfish-companion/scripts/catalog_query.py --list
```

### /petfish search <keyword>

搜索技能目录：

```bash
uv run .opencode/skills/petfish-companion/scripts/catalog_query.py --search "<keyword>"
```

### /petfish suggest

1. 运行`detect_platform.py`检测当前平台
2. 运行`check_installed.py`获取已装状态
3. 分析当前项目的文件结构（检查是否有课程目录、Dockerfile、测试文件等）
4. 基于项目特征推荐缺失的skill pack

推荐逻辑：
- 存在`docs/01-outline/`或`docs/02-content/` → 推荐`course`
- 存在`Dockerfile`、`docker-compose.yml`、`deploy/` → 推荐`deploy`
- 存在`tests/`、`__tests__/`、`*.test.*` → 推荐`testdocs`
- 存在`*.pptx`或`slides/` → 推荐`ppt`

### /petfish install <alias>

提示用户运行安装命令：

```bash
# 本地安装
./install.ps1 -Pack <alias> -Target .   # PowerShell
./install.sh --pack <alias> --target .   # Bash

# 远程安装
& ([scriptblock]::Create((irm https://raw.githubusercontent.com/kylecui/petfish.ai/master/remote-install.ps1))) -Pack <alias>
curl -fsSL https://raw.githubusercontent.com/kylecui/petfish.ai/master/remote-install.sh | bash -s -- --pack <alias>
```

注意：companion自身不直接执行安装，而是生成并展示正确的安装命令让用户执行。

### /petfish detect

运行平台检测：

```bash
uv run .opencode/skills/petfish-companion/scripts/detect_platform.py --target .
```

## 行为规则

1. 所有输出使用用户的对话语言（中文对话→中文输出，英文→英文）
2. 技术术语保持紧凑混排（`Docker部署`而非`Docker 部署`）
3. 不自动执行安装，只提供命令
4. 遇到错误时给出明确的排查建议

## 新增子命令

### /petfish search \<keyword\>

跨多个来源搜索skill和MCP server：

```bash
uv run .opencode/skills/marketplace-connector/scripts/marketplace_search.py --query "<keyword>"
```

搜索按优先级展示结果：
1. 胖鱼自有仓库匹配
2. 三方市场（SkillKit/Smithery/Glama）
3. GitHub高星仓库
4. GitHub低星仓库

### /petfish create \<name\>

使用skill-author创建新skill：

```bash
uv run .opencode/skills/skill-author/scripts/generate_skill.py --name "<name>" --type automation --output .opencode/skills/
```

创建完成后自动运行lint验证：

```bash
uv run .opencode/skills/skill-lint/scripts/lint_skill.py --path .opencode/skills/<name>/
```

支持的模板类型：`automation`（默认）、`workflow`、`knowledge`。

### /petfish lint \[path\]

验证skill质量，默认扫描当前项目所有skill：

```bash
# 扫描单个skill
uv run .opencode/skills/skill-lint/scripts/lint_skill.py --path <path>

# 递归扫描所有skill
uv run .opencode/skills/skill-lint/scripts/lint_skill.py --path .opencode/skills/ --recursive

# 预览修复建议
uv run .opencode/skills/skill-lint/scripts/lint_skill.py --path <path> --fix

# 自动修复
uv run .opencode/skills/skill-lint/scripts/lint_skill.py --path <path> --fix-apply
```

输出100分制评分和具体问题列表。

### /petfish mine \<repo\>

从GitHub仓库或本地仓库挖掘可提取为skill的工作流：

```bash
# 分析本地仓库
uv run .opencode/skills/repo-skill-miner/scripts/mine_repo.py --repo <local-path>

# 分析GitHub仓库
uv run .opencode/skills/repo-skill-miner/scripts/mine_repo.py --repo <github-url>

# 深度扫描
uv run .opencode/skills/repo-skill-miner/scripts/mine_repo.py --repo <repo> --depth deep
```

输出mining报告，包括候选skill、工具需求、安全风险和优先级排名。

### /petfish audit \<path\>

对skill进行安全审计：

```bash
# 审计单个skill
uv run .opencode/skills/skill-security-auditor/scripts/audit_skill.py --path <skill-path>

# 递归审计所有skill
uv run .opencode/skills/skill-security-auditor/scripts/audit_skill.py --path .opencode/skills/ --recursive
```

输出风险评分(0.0-1.0)和安全发现列表。

### /petfish gate \<path\>

运行完整发布门禁（lint + security audit + metadata验证 → 发布决策）：

```bash
# 单个skill门禁
uv run .opencode/skills/quality-gate/scripts/run_gate.py --path <skill-path>

# 批量门禁
uv run .opencode/skills/quality-gate/scripts/run_gate.py --path .opencode/skills/ --recursive
```

输出PASS/CONDITIONAL/FAIL决策及详细报告。

### /petfish optimize \<path\>

分析skill描述质量并建议优化：

```bash
uv run .opencode/skills/skill-description-optimizer/scripts/optimize_description.py --path <skill-path> --suggest --verbose

# 含兄弟skill重叠分析
uv run .opencode/skills/skill-description-optimizer/scripts/optimize_description.py --path <skill-path> --siblings .opencode/skills/ --suggest
```

### /petfish eval \<path\>

测试skill触发准确率：

```bash
# 自动生成测试集
uv run .opencode/skills/skill-trigger-evaluator/scripts/evaluate_triggers.py --path <skill-path> --verbose

# 使用自定义测试集
uv run .opencode/skills/skill-trigger-evaluator/scripts/evaluate_triggers.py --path <skill-path> --test-file tests.json

# 含跨触发冲突检测
uv run .opencode/skills/skill-trigger-evaluator/scripts/evaluate_triggers.py --path <skill-path> --siblings .opencode/skills/
```

### /petfish stats

查看当前项目的skill使用统计：

```bash
uv run .opencode/skills/skill-usage-tracker/scripts/track_usage.py --action report --target .
```
