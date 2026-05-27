# uv使用说明

本包默认采用 **uv管理的仓库级Python环境** 来运行辅助脚本。

## 推荐方式

先在项目根目录执行：

```bash
uv sync
```

然后用 `uv run` 调用脚本：

```bash
uv run .opencode/skills/repo-runtime-discovery/scripts/repo_inventory.py --root . --output -
uv run .opencode/skills/target-host-readiness/scripts/host_probe.py --local --output -
uv run .opencode/skills/target-host-readiness/scripts/host_probe.py --ssh user@host --output -
uv run .opencode/skills/deployment-verifier/scripts/verify_http.py --spec smoke-matrix.json --output -
uv run .opencode/skills/service-operations/scripts/release_state.py init --state .deploy/releases.json
```

## 设计原则

-仓库根目录提供 `pyproject.toml` 与 `.python-version`
-默认使用项目级 `.venv`
-所有文档示例统一使用 `uv run`
-内置脚本同时支持 `#!/usr/bin/env -S uv run` shebang和PEP 723 inline metadata，可直接执行

## 何时需要额外依赖

当前无需额外依赖。如果后续增加第三方库，直接写入根目录 `pyproject.toml`，再执行：

```bash
uv sync
```
