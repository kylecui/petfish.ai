# trustskills Pack

`trustskills` pack wraps the external `kylecui/trustskills` Python governance engine as a standalone OpenCode skill pack for petfish.ai.

`trustskills` pack把外部 `kylecui/trustskills` Python治理引擎封装成一个可独立安装的OpenCode skill pack，用于petfish.ai中的skill可信度评估与治理决策。

## What this pack does / 这个pack做什么

- Provides one skill: `skill-trust-governance`
- Ships a thin wrapper script: `trust_scan.py`
- Calls the external `trustskills` CLI instead of vendoring engine source code
- Supports single-skill scan, root scan, manifest generation, manifest verification, and JSON-ready integration output

- 提供一个skill：`skill-trust-governance`
- 附带一个薄封装脚本：`trust_scan.py`
- 通过外部 `trustskills` CLI运行，不内置引擎源码
- 支持单skill扫描、根目录批量扫描、manifest生成、manifest校验，以及可接入quality-gate的JSON输出

## Installation / 安装

### 1) Install the external engine / 安装外部引擎

```bash
uv add git+https://github.com/kylecui/trustskills.git
```

Or:

```bash
uv pip install git+https://github.com/kylecui/trustskills.git
```

`trustskills` requires Python >= 3.12 and depends on `pydantic>=2.13.3` and `pyyaml>=6.0`.

`trustskills` 依赖 Python >= 3.12，运行时依赖 `pydantic>=2.13.3` 与 `pyyaml>=6.0`。

### 2) Install this pack / 安装本pack

Copy `packs/trustskills/` into the target project pack registry, or install it through your normal PEtFiSh pack workflow.

将 `packs/trustskills/` 放入目标项目的pack目录，或通过你现有的PEtFiSh pack安装流程安装。

## Usage / 用法

### Scan a single skill / 扫描单个skill

```bash
uv run packs/trustskills/.opencode/skills/skill-trust-governance/scripts/trust_scan.py --path .opencode/skills/skill-lint --detail
```

### Scan all skills under a root / 扫描根目录下全部skill

```bash
uv run packs/trustskills/.opencode/skills/skill-trust-governance/scripts/trust_scan.py --root .opencode/skills --output reports/trustskills-scan.md
```

### Emit machine-readable JSON / 输出机器可解析JSON

```bash
uv run packs/trustskills/.opencode/skills/skill-trust-governance/scripts/trust_scan.py --root .opencode/skills --json
```

### Generate manifests / 生成manifest

```bash
uv run packs/trustskills/.opencode/skills/skill-trust-governance/scripts/trust_scan.py --path .opencode/skills/skill-lint --manifest
```

### Verify manifests / 校验manifest

```bash
uv run packs/trustskills/.opencode/skills/skill-trust-governance/scripts/trust_scan.py --root .opencode/skills --verify --json
```

### Use a custom policy / 使用自定义策略

```bash
uv run packs/trustskills/.opencode/skills/skill-trust-governance/scripts/trust_scan.py --root .opencode/skills --policy policy/trustskills.yaml --json
```

## Integration with /petfish / 与`/petfish`集成

This pack does not add new commands or agents. It is designed to work alongside the `petfish-companion-skill` pack:

- Use `/petfish audit <path>` for static skill security review
- Use this pack's `trust_scan.py` for governance scoring and redline decisions
- Feed `--json` output into internal CI, release checks, or quality-gate style workflows

本pack不会新增commands或agents。它适合与 `petfish-companion-skill` 配合使用：

- 用 `/petfish audit <path>` 做静态安全审计
- 用本pack的 `trust_scan.py` 做治理分级与红线判定
- 将 `--json` 输出接入内部CI、发布门禁或quality-gate风格流程

## Notes / 说明

- The engine source code is intentionally not copied into this pack.
- The wrapper uses relative paths and `Path` objects only.
- No `__pycache__` or `.pyc` artifacts are included.

- 本pack不会复制治理引擎源码。
- 封装脚本仅使用相对路径与 `Path` 对象。
- 不包含 `__pycache__` 或 `.pyc` 产物。
