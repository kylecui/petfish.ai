# uv Usage for project-initializer-skill

## Setup

```bash
cd packs/core/project-initializer-skill
uv sync
```

## Run init_project.py

```bash
uv run python .opencode/skills/project-initializer/tools/init_project.py --profile comprehensive --target /path/to/project --dry-run
```

## Notes

- All Python scripts in this pack should be invoked via `uv run` to ensure correct virtual environment.
- If uv is not installed, see https://docs.astral.sh/uv/getting-started/installation/
