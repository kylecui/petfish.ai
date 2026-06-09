# Online GPT Tools

This directory contains stdlib-only helper tools for keeping `online-gpt/` aligned with core PEtFiSh.

## Tools

```text
tools/
├── README.md
├── check_alignment.py
└── compile_knowledge.py
```

## Design rule

Tools should prefer reading core PEtFiSh sources instead of hardcoding online-only facts.

## Alignment check

```bash
python online-gpt/tools/check_alignment.py
```

Checks:

- known pack aliases in online knowledge;
- platform names in online knowledge;
- source-of-truth marker presence;
- forbidden drift phrases.

## Knowledge compilation

```bash
python online-gpt/tools/compile_knowledge.py
```

This script is a scaffold for regenerating selected `knowledge/*.md` files from core repository sources.

It should be expanded before online-gpt is published widely.
