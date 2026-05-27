# 安装说明

## 直接安装到项目

把本包中的 `.opencode/` 目录复制到你的项目根目录。

同时把 `pyproject.toml` 和 `.python-version` 复制到项目根目录（如果项目根目录还没有这两个文件）。

## 初始化uv环境

```bash
uv sync
```

## 检查点

确认以下路径存在：

```text
.opencode/skills/generate-test-cases/SKILL.md
.opencode/skills/generate-usage-docs/SKILL.md
pyproject.toml
.python-version
```

## 调用建议

在OpenCode中，直接以自然语言触发：

- “根据当前项目生成test cases”
- “根据当前项目生成使用文档”

## 后续建议

1. 先在一个真实仓库上试跑
2. 记录代理的误判、漏判和空泛输出
3. 把这些问题补充回各自skill的 `Gotchas`、`references/` 和 `evals/`
