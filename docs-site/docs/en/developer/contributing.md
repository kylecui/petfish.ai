# Contributing to PEtFiSh

How to contribute skills, packs, and improvements to the PEtFiSh project.

---

## Development Setup

### Prerequisites

- **Git** — for version control
- **uv** — Python environment manager (required for all Python scripts)
- **Python 3.11+** — for skill scripts and MCP servers

### Clone and Branch

```bash
git clone https://github.com/kylecui/petfish.ai.git
cd petfish.ai
git checkout dev
```

All development happens on the `dev` branch. Never commit directly to `master`.

---

## Branching Strategy

```text
master ← dev ← feature branches
  │
  └── Every merge to master = a GitHub Release (vX.Y.Z)
```

- **`dev`**: Active development branch
- **`master`**: Stable release branch — every merge gets a release tag
- **Feature branches**: Branch from `dev`, PR back to `dev`

### Version Numbers

| Change Type | Version Bump | Examples |
|---|---|---|
| Breaking changes | Major (X) | Pack structure change, installer API change |
| New features | Minor (Y) | New pack, new skill, new platform |
| Bug fixes | Patch (Z) | Fix, docs correction, small optimization |

---

## Adding a New Skill

1. Create the skill directory under the appropriate pack
2. Write `SKILL.md` with proper frontmatter
3. Add scripts, references, and schemas as needed
4. Add trigger evaluation tests
5. Run the quality gate: `/petfish gate path/to/skill/`
6. Fix any FAIL or CONDITIONAL issues

See the [Skill Authoring Guide](skill-authoring.md) for detailed instructions.

---

## Adding a New Pack

A new pack requires updating **9 touchpoints**. Missing any one causes silent installation failures for users.

### The 9-Touchpoint Checklist

| # | Touchpoint | File(s) | What to Do |
|---|---|---|---|
| 1 | Local installer aliases | `install.ps1`, `install.sh` | Register pack alias in the pack mapping |
| 2 | Remote installer arrays | `remote-install.ps1`, `remote-install.sh` | **Manually add** to `$AllPacks` / `ALL_PACKS` static array |
| 3 | Companion catalog | `catalog_query.py` PROFILES dict | Add to relevant profiles (at minimum `comprehensive`) |
| 4 | Project initializer | `project-initializer/SKILL.md` + `init_project.py` | Associate with profiles or add new profile |
| 5 | README | `README.md` | Update Pack list and Profile → Auto-Install table |
| 6 | Website | `website/index.html`, `pitch.html`, `blog.html` | Update pack cards, tables, counts |
| 7 | Install/upgrade docs | `docs/agent-install.md`, `docs/agent-upgrade.md` | Update examples and pack lists |
| 8 | Chinese translation | `docs/zh/README.md` | Sync Chinese version |
| 9 | Archive docs | `docs/archive/` | Update pack counts and lists |

!!! danger "Local vs Remote installer architecture"
    **Local installers** (`install.ps1`, `install.sh`) dynamically scan the `packs/` directory — new packs are auto-discovered, but aliases still need registration.

    **Remote installers** (`remote-install.ps1`, `remote-install.sh`) use **hardcoded static arrays**. If you don't manually add the pack name, `--pack all` will silently skip it.

    This asymmetry has caused real incidents. Always test both install paths.

### Verification

After adding a new pack:

1. Search for the pack name across all 9 touchpoint files
2. Test `--pack all` with both local and remote installers
3. Verify `/petfish catalog` lists the new pack
4. Verify `/initproject` profile selection includes it

---

## The 4 Installers

PEtFiSh has 4 installer scripts that must stay synchronized:

| Script | Type | Architecture |
|---|---|---|
| `install.ps1` | Local, PowerShell | Dynamic `packs/` scan |
| `install.sh` | Local, Shell | Dynamic `packs/` scan |
| `remote-install.ps1` | Remote, PowerShell | Static array |
| `remote-install.sh` | Remote, Shell | Static array |

Any logic change must be evaluated for all 4 scripts. The implementation may differ (dynamic vs. static), but the functional behavior must be identical.

---

## Testing

### Smoke Tests

Pack-level smoke tests live in `tests/` within each pack:

```bash
uv run pytest packs/my-pack/tests/ -v
```

### Trigger Evaluation

Test skill trigger accuracy:

```bash
uv run python .opencode/skills/skill-trigger-evaluator/scripts/evaluate_triggers.py \
  --path packs/my-pack/.opencode/skills/my-skill/evals/trigger/my-skill.json
```

### Quality Gate

Run the full publish gate before any PR:

```bash
uv run python .opencode/skills/quality-gate/scripts/run_gate.py \
  --path packs/my-pack/.opencode/skills/ --recursive
```

---

## Pull Request Process

1. Branch from `dev`
2. Make changes
3. Run quality gate on affected skills
4. Run smoke tests if applicable
5. Update CHANGELOG if the pack has one
6. Create PR to `dev`
7. After merge to `dev` and testing, create PR from `dev` to `master`
8. After merge to `master`, **immediately create a GitHub Release**:

```bash
gh release create vX.Y.Z --target master \
  --title "vX.Y.Z - Brief description" \
  --notes "Changelog summary"
```

---

## Code Conventions

### Python

- Use `uv` for all virtual environment management — no `pip install`
- Scripts with external dependencies use PEP 723 inline metadata
- MCP servers launch via `["uv", "run", "python", "server.py"]`
- Stdlib-only inline code (`python3 -c`) is fine without uv

### SKILL.md

- Frontmatter `description` must cover ≥80% of body trigger keywords
- Include both Chinese and English trigger phrases
- Keep description under 500 characters
- Schema field names must match SKILL.md field descriptions exactly

### Naming

- Directories and files: lowercase `kebab-case`
- Skill names must match their directory names
- Avoid `final`, `new`, `v2` in names

### Bash in Scripts

When embedding Python in bash strings (`python3 -c "..."`), use `chr()` instead of escaped literals:

```python
# Good — immune to shell escaping layers
sep = chr(47)  # forward slash
bs = chr(92)   # backslash

# Bad — breaks across SSH, PowerShell, and other proxy shells
sep = "/"
bs = "\\"
```

---

## What Not to Do

- Don't commit directly to `master`
- Don't merge to `master` without creating a release tag
- Don't use `pip install` anywhere
- Don't modify other repositories' code — file issues instead
- Don't delete published releases (unless security vulnerability)
- Don't skip the quality gate before PRs
