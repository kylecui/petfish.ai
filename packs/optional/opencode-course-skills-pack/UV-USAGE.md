# uv使用说明

本包现在默认采用 **uv管理的仓库级Python环境** 来运行辅助脚本，而不是直接调用系统 `python3`。

## 推荐方式

先在项目根目录执行：

```bash
uv sync
```

然后用 `uv run` 调用脚本：

```bash
uv run .opencode/skills/course-directory-structure/scripts/bootstrap_course_tree.py --root . --mode full --with-placeholders
uv run .opencode/skills/course-directory-structure/scripts/check_course_tree.py --root .
uv run .opencode/skills/course-quality-control-reporting/scripts/render_qc_report.py --input findings.json --output docs/07-qc/qc-report.md
```

## 设计原则

-仓库根目录提供 `pyproject.toml` 与 `.python-version`
-默认使用项目级 `.venv`
-所有文档示例统一使用 `uv run`
-当前内置脚本仅依赖Python标准库，但仍建议通过uv保持执行入口一致

## 何时需要额外依赖

当前无需额外依赖。如果后续为QA、文件解析、课程检查等脚本增加第三方库，直接把依赖写入根目录 `pyproject.toml`，再执行：

```bash
uv sync
```

即可把新依赖同步进项目虚拟环境。
