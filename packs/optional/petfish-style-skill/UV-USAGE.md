# uv Usage for petfish-style-skill

This pack uses [uv](https://docs.astral.sh/uv/) to manage Python environments and run scripts.

## Quick start

```bash
# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Run the style checker
uv run .opencode/skills/petfish-style-rewriter/scripts/check_style.py output.md
```

## Why uv?

- Creates an isolated virtual environment automatically
- No manual `pip install` or `venv` setup needed
- Reproducible across machines
- Scripts declare their own dependencies via PEP 723 inline metadata
