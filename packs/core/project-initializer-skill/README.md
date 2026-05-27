# Project Initializer Skill Package

这是一个可直接放入OpenCode项目的`project-initializer` Skill包。它把项目初始化拆成两个层级：

1. `SKILL.md`负责向导式澄清、风险判断、初始化计划、用户确认和输出规范。
2. `tools/init_project.py`负责确定性创建目录、写入模板、处理冲突、生成初始化报告。

## 安装位置

推荐复制到项目目录：

```text
.opencode/skills/project-initializer/
```

也可以放入OpenCode支持的全局skills目录。

## 快速试运行

```bash
cd .opencode/skills/project-initializer
uv run python tools/init_project.py --profile comprehensive --target /path/to/project --with-opencode --with-mcp-template --no-overwrite --dry-run
```

确认计划后执行：

```bash
uv run python tools/init_project.py --profile comprehensive --target /path/to/project --with-opencode --with-mcp-template --no-overwrite
```

## 典型用法

在OpenCode中说：

```text
使用project-initializer。按综合项目初始化当前目录，允许创建文件，但不要覆盖已有文件。需要MCP模板和uv开发环境说明。
```

