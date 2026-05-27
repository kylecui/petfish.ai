# uv Usage for opencode-ppt-skills

This pack uses [uv](https://docs.astral.sh/uv/) to manage Python environments and run scripts.

## Quick start

```bash
# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Build a deck from spec
uv run .opencode/skills/ppt-writer/scripts/build_deck.py deck_spec.json --out output.pptx

# QA a deck
uv run .opencode/skills/ppt-writer/scripts/qa_deck.py output.pptx --out qa.json

# Extract content from PPTX
uv run .opencode/skills/ppt-reader/scripts/pptx_extract.py input.pptx --out inventory.json --markdown summary.md
```

## Why uv?

- Creates an isolated virtual environment automatically
- No manual `pip install` or `venv` setup needed
- Reproducible across machines
- Scripts declare their own dependencies via PEP 723 inline metadata
