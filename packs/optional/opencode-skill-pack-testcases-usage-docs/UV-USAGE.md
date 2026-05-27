# uv使用说明

本包默认采用 **uv管理的仓库级Python环境** 来运行辅助脚本，而不是直接调用系统 `python3`。

## 推荐方式

先在项目根目录执行：

```bash
uv sync
```

然后用 `uv run` 调用脚本：

```bash
uv run .opencode/skills/generate-test-cases/scripts/project_inventory.py .
uv run .opencode/skills/generate-test-cases/scripts/validate_test_case_json.py path/to/test-cases.json
uv run .opencode/skills/generate-usage-docs/scripts/project_inventory.py .
uv run .opencode/skills/generate-usage-docs/scripts/validate_docset.py path/to/docset-root
```

## 设计原则

-仓库根目录提供 `pyproject.toml` 与 `.python-version`
-默认使用项目级 `.venv`
-所有文档示例统一使用 `uv run`
-当前内置脚本仅依赖Python标准库，但仍建议通过uv保持执行入口一致

## 何时需要额外依赖

当前无需额外依赖。如果后续为校验、解析等脚本增加第三方库，直接把依赖写入根目录 `pyproject.toml`，再执行：

```bash
uv sync
```

即可把新依赖同步进项目虚拟环境。
