# Upgrade

PEtFiSh upgrades by re-running the installer with `--force`. Your project files, MCP state, and configuration are preserved.

## Check for Updates

Run `/petfish upgrade` in your AI assistant. It queries the latest GitHub release and shows the upgrade command if a newer version is available.

You can also check manually:

```bash
# See latest release
gh release view --repo kylecui/petfish.ai --json tagName -q .tagName
```

## Upgrade All Packs

```bash
uv run https://raw.githubusercontent.com/kylecui/petfish.ai/master/install.py --pack all --force --detect
```

!!! tip "What `--force` does"
    Re-installs all packs even if they appear current. Without `--force`, existing packs are skipped and only missing packs are installed.

## Upgrade Specific Packs

Replace `all` with a comma-separated list:

```bash
# Only upgrade companion and research
uv run https://raw.githubusercontent.com/kylecui/petfish.ai/master/install.py --pack companion,research --force
```

## After Upgrading

!!! warning "Restart Required"
    After upgrading, **restart your AI coding tool** for new skills to load.

    | Platform | How to Restart |
    |---|---|
    | OpenCode | `Ctrl+C` then re-launch. Resume: `opencode -s <session_id>` |
    | Claude Code | `/exit` or `Ctrl+C`. Resume: `claude --continue` |
    | Codex | `Ctrl+C` and re-launch |
    | Cursor | `Ctrl+Shift+P` → "Reload Window" |
    | Copilot | `Ctrl+Shift+P` → "Reload Window" |
    | Windsurf | `Ctrl+Shift+P` → "Reload Window" |
    | Antigravity | `Ctrl+C` and re-launch |

Then verify:

```
/petfish
```

This shows updated pack versions and skill counts.

## Version-Specific Notes

### From v0.4.x or earlier → v0.5+

Major changes:

- Repo renamed `SKILL_builder` → `petfish.ai` (install URLs changed automatically)
- Pack renamed `context-router-skill` → `fish-trail`
- State directory moved `.ai-context/` → `.petfish/fish-trail/` (auto-migrated)

The `--force` upgrade handles all renames. After upgrading, clean up legacy directories:

=== "macOS / Linux / WSL"

    ```bash
    rm -rf .opencode/skills/context-router/ .opencode/skills/context-router-skill/
    ```

=== "Windows PowerShell"

    ```powershell
    Remove-Item -Recurse -Force .opencode\skills\context-router\, .opencode\skills\context-router-skill\ -ErrorAction SilentlyContinue
    ```

### From v0.5.x → v0.6+

- Companion Gateway introduced (3-step flow)
- No breaking changes; `--force` picks up new features

### From v0.10.x → v0.11+

- Gateway expanded to 6 steps (Mode Read, Failure Signal Detection, Anti-Sycophancy Check added)
- No breaking changes; `--force` picks up new AGENTS.md content

## Troubleshooting

| Problem | Solution |
|---|---|
| "Pack already installed" | Use `--force` to re-install |
| Legacy directories remain | Delete old skill dirs manually (see above) |
| MCP server won't start | Check `uv` is installed and paths in config point to new `fish-trail/` directory |
| AGENTS.md has duplicate markers | Remove old `context-router-skill` markers manually |
| Skills not loading after upgrade | Restart your AI tool (see table above) |

See also: [FAQ & Troubleshooting](faq.md)
