# Alignment Evals

Alignment evals protect `online-gpt/` from drifting away from core PEtFiSh.

They should be added whenever online-gpt introduces:

- a new module name;
- a new adapter behavior;
- a new Action;
- a new Knowledge file;
- a new remote-control path;
- a new pack/profile recommendation rule.

## What to test

Alignment evals should ensure:

- core PEtFiSh remains the source of truth;
- GPT behavior wraps existing semantics instead of replacing them;
- online-gpt does not invent official pack aliases;
- command rendering preserves local installer semantics;
- remote execution remains a controlled adapter concern.

## Related tools

```bash
python online-gpt/tools/check_alignment.py
python online-gpt/tools/compile_knowledge.py
```
