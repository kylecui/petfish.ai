# Implementation Notes

## Design Decision

This package deliberately separates the skill and the script.

- `SKILL.md` handles judgment: intent clarification, risk classification, confirmation gates, and output standards.
- `tools/init_project.py` handles deterministic execution: directory creation, file generation, conflict handling, and report generation.

## Safety Model

Default behavior is no-overwrite. Existing files are preserved. If a target file exists, the script writes a `.new` version unless `--overwrite` is explicitly set.

The script refuses dangerous target paths such as filesystem roots, home directory roots, and obvious system paths.

## Extension Points

- Add profile-specific directories and files in `PROFILES` inside `tools/init_project.py`.
- Add external repository installation by implementing a separate, confirmation-gated script.
- Add `--copy-skill` support for local skills only after adding path traversal checks.
- Add rollback by persisting a machine-readable manifest of all created files.

## Recommended OpenCode Invocation

```text
使用project-initializer。按综合项目初始化当前目录，允许创建文件，但不要覆盖已有文件。需要MCP模板和uv开发环境说明。先dry-run，再给我确认清单。
```

## Manual Script Invocation

```bash
python tools/init_project.py --profile comprehensive --target . --with-opencode --with-mcp-template --with-uv --no-overwrite --dry-run
python tools/init_project.py --profile comprehensive --target . --with-opencode --with-mcp-template --with-uv --no-overwrite
```
