# skill-lint rules

This document defines the lint rules used by `scripts/lint_skill.py`.

## Frontmatter rules

### FM001 — ERROR

**Description:** `name` field missing or empty.

**Good**

```yaml
---
name: skill-lint
---
```

**Bad**

```yaml
---
description: Validate skills
---
```

### FM002 — ERROR

**Description:** `name` exceeds 64 chars.

**Good**

```yaml
name: skill-lint
```

**Bad**

```yaml
name: this-is-a-very-long-skill-name-that-keeps-going-past-the-limit-and-breaks-style
```

### FM003 — ERROR

**Description:** `name` contains chars other than lowercase letters, digits, hyphens.

**Good**

```yaml
name: skill-lint
```

**Bad**

```yaml
name: Skill_Lint
```

### FM004 — WARN

**Description:** `name` doesn't match parent directory name.

**Good**

```text
skill directory: skill-lint/
frontmatter name: skill-lint
```

**Bad**

```text
skill directory: skill-lint/
frontmatter name: skill-checker
```

### FM005 — ERROR

**Description:** `description` field missing or empty.

**Good**

```yaml
description: Use this skill when the user asks to validate skill quality.
```

**Bad**

```yaml
description:
```

### FM006 — WARN

**Description:** `description` exceeds 1024 chars.

**Good**

```yaml
description: Use this skill when the user wants to lint a skill before release.
```

**Bad**

```yaml
description: <very long description over 1024 chars>
```

### FM007 — WARN

**Description:** `description` doesn't describe WHEN to use the skill (no trigger phrases).

**Good**

```yaml
description: Use this skill when the user asks to lint skill or validate skill quality.
```

**Bad**

```yaml
description: A helpful linter for skills.
```

### FM008 — INFO

**Description:** missing `metadata.version`.

**Good**

```yaml
metadata:
  version: 0.2.0
```

**Bad**

```yaml
metadata:
  author: petfish-team
```

### FM009 — INFO

**Description:** missing `metadata.author`.

**Good**

```yaml
metadata:
  author: petfish-team
```

**Bad**

```yaml
metadata:
  version: 0.2.0
```

## Structure rules

### ST001 — ERROR

**Description:** SKILL.md not found.

**Good**

```text
my-skill/
└── SKILL.md
```

**Bad**

```text
my-skill/
└── README.md
```

### ST002 — WARN

**Description:** no `references/` directory.

**Good**

```text
my-skill/
├── SKILL.md
└── references/
```

**Bad**

```text
my-skill/
└── SKILL.md
```

### ST003 — WARN

**Description:** no `scripts/` directory.

**Good**

```text
my-skill/
├── SKILL.md
└── scripts/
```

**Bad**

```text
my-skill/
└── SKILL.md
```

### ST004 — INFO

**Description:** empty `evals/` directory.

**Good**

```text
evals/
└── prompt-01.md
```

**Bad**

```text
evals/
```

### ST005 — WARN

**Description:** files in skill root besides `SKILL.md` and `README.md`.

**Good**

```text
my-skill/
├── SKILL.md
├── README.md
├── references/
└── scripts/
```

**Bad**

```text
my-skill/
├── SKILL.md
├── notes.txt
└── scripts/
```

## Content rules

### CT001 — WARN

**Description:** SKILL.md body is empty (no instructions after frontmatter).

**Good**

```markdown
---
name: my-skill
description: Use this skill when...
---

## Workflow

1. Do X.
```

**Bad**

```markdown
---
name: my-skill
description: Use this skill when...
---
```

### CT002 — WARN

**Description:** SKILL.md body exceeds 5000 tokens (may impact loading performance).

**Good**

```text
Short, focused instructions with references for long details.
```

**Bad**

```text
Massive inline handbook with thousands of tokens duplicated from reference docs.
```

### CT003 — INFO

**Description:** no "must do" / "must not do" section in SKILL.md.

**Good**

```markdown
## Must do
- Run the checker first.

## Must not do
- Do not edit files silently.
```

**Bad**

```markdown
## Notes
- Be helpful.
```

### CT004 — WARN

**Description:** `references/` files duplicate SKILL.md content (>50% overlap).

**Good**

```text
SKILL.md: short operating rules
references/: detailed rule catalog and examples
```

**Bad**

```text
references/usage.md repeats most of SKILL.md word-for-word.
```

## Security rules

### SC001 — WARN

**Description:** `scripts/` contains `subprocess.call` with `shell=True`.

**Good**

```python
subprocess.run(["uv", "run", "tool.py"], check=True)
```

**Bad**

```python
subprocess.call("uv run tool.py", shell=True)
```

### SC002 — WARN

**Description:** `scripts/` contains `eval()` or `exec()`.

**Good**

```python
json.loads(payload)
```

**Bad**

```python
result = eval(user_input)
exec(script_text)
```

### SC003 — WARN

**Description:** `scripts/` contains hardcoded credentials patterns (API key, password, token).

**Good**

```python
api_key = os.environ.get("API_KEY")
```

**Bad**

```python
API_KEY = "sk-live-1234567890"
PASSWORD = "super-secret"
```

### SC004 — INFO

**Description:** `scripts/` makes network requests (`urllib`, `requests`, `httpx`, `curl`).

**Good**

```python
from pathlib import Path
```

**Bad**

```python
import requests
response = requests.get(url)
```
