# Unified Python Installer v2.0 — Migration Plan

## Goal

Replace 4 shell installers (~10,500 lines) with a single Python script (~1,000-1,500 lines) executed via `uv run`.

## Why

- 4 installers = 4x maintenance burden, divergent behavior, PS 5.1 incompatibilities
- Already calling Python internally (dozens of `python3 -c` inline)
- `uv run <url>` enables single-command distribution without npm/pip publishing
- Python stdlib covers all needs: pathlib, json, shutil, subprocess, urllib, argparse

## Architecture

```
install.py  (single file, PEP 723 metadata, stdlib only)
├── CLI layer (argparse)
├── Platform detection & config
├── Pack resolution (alias → core/optional/community/market)
├── Download module (urllib for tarballs, GitHub API)
├── Install pipeline
│   ├── AGENTS.md merge (marker sections)
│   ├── L1 rules file split
│   ├── Instruction translation (rename_with_header / wrap_as_mdc)
│   ├── opencode.json deep merge (3-level, atomic L2 mcp)
│   ├── Claude settings conversion
│   ├── Plugin deployment
│   ├── MCP server deployment
│   ├── Skill/agent/command copy
│   ├── Claude hooks deployment
│   └── Registry update (installed-packs.json)
├── Version management (semver compare, upgrade detection)
├── Migration (v0.9 → v1.4)
├── Uninstall
└── Market/community pack handling
```

## Phases

### Phase 0: Foundation (est. 1 day)
**Goal**: Skeleton that can run and parse args

- [ ] Create `install.py` with PEP 723 metadata (stdlib only)
- [ ] CLI argument parsing (14 params via argparse)
- [ ] UTF-8 setup (`sys.stdout.reconfigure(encoding='utf-8')`)
- [ ] Logging with colors (cross-platform)
- [ ] uv binary detection + auto-install + PATH refresh
- [ ] Platform detection logic (scan for .opencode/, .claude/, CLAUDE.md, etc.)

**Deliverable**: `uv run install.py --detect` works on all platforms

### Phase 1: Core Pipeline (est. 2-3 days)
**Goal**: Install a core pack from local filesystem

- [ ] Pack alias registry (~30 mappings)
- [ ] Core vs optional pack classification
- [ ] `platforms.json` read + validate + fallback generation
- [ ] Platform config lookup (skills_dir, agents_dir, commands_dir, instructions_file, config_file)
- [ ] Pack directory resolution (`find_pack_dir`)
- [ ] `pack-manifest.json` parsing (skills, commands, agents, version, legacy_names)
- [ ] Skill/agent/command directory copy (with skip-if-exists + force logic)
- [ ] Registry update (`installed-packs.json` read/write, array→dict normalization)
- [ ] Version comparison (semver: read installed + manifest → same/newer/not-installed)
- [ ] "all" pack expansion (scan packs/core/ + packs/optional/)

**Deliverable**: `uv run install.py --pack course --target .` installs a core pack locally

### Phase 2: File Merging (est. 2-3 days)
**Goal**: AGENTS.md and config merging work correctly

- [ ] AGENTS.md marker section merge (<!-- pack-name-start/end -->, legacy name awareness)
- [ ] L1 rules file split (write standalone .md files, backup old ones)
- [ ] L1 pack list (hardcoded map: which packs are L1)
- [ ] Extra agents-rules/*.md deployment
- [ ] Instruction content compression (token-limited condensation)
- [ ] Instruction translation: `rename_with_header` (copy + prepend header)
- [ ] Instruction translation: `wrap_as_mdc` (Cursor .mdc format)
- [ ] GEMINI.md dual-write (antigravity platform)
- [ ] `opencode.json` deep merge (3-level, atomic L2 mcp, SkillsDir rewrite)
- [ ] `opencode.example.json` → Claude settings conversion
- [ ] Plugin deployment (copy .ts files + register in opencode.json)
- [ ] MCP server file deployment

**Deliverable**: Full AGENTS.md + opencode.json merge for OpenCode and Claude platforms

### Phase 3: Distribution (est. 2 days)
**Goal**: Remote install from GitHub + community + market

- [ ] GitHub tarball download (urllib, 3 retries, 429/403 backoff)
- [ ] Tarball extraction (tarfile stdlib)
- [ ] Extract directory detection (find <owner>-<repo>-<sha>/ pattern)
- [ ] Community pack: parse `community/owner/repo[/ref]` spec
- [ ] Community pack: download (tarball with retry → git clone fallback)
- [ ] Community pack: manifest validation
- [ ] Market index query (fetch index.json, match by alias/name)
- [ ] Market pack download (external repo tarball)
- [ ] Market path resolution (nested repo layout)
- [ ] Branch/repo override (--branch, --repo params)
- [ ] GitHub auth token support
- [ ] Mirror fallback for China market (ghfast.top → ghproxy.com)
- [ ] Version compatibility check (`min_petfish_version` field)

**Deliverable**: `uv run install.py --pack course` works from URL (no local clone)

### Phase 4: Hooks + Uninstall + Migration (est. 1-2 days)
**Goal**: Feature parity with shell installers

- [ ] Claude hooks: copy scripts, set executable bit (chmod on Unix)
- [ ] Claude hooks: merge into `.claude/settings.json` (UserPromptSubmit, PreCompact, PostCompact)
- [ ] Hook deduplication (skip already-registered commands)
- [ ] Uninstall: skill/agent/command directory removal
- [ ] Uninstall: AGENTS.md marker section removal
- [ ] Uninstall: AGENTS.md rules table row removal
- [ ] Uninstall: opencode.json key cleanup (cross-check other installed packs)
- [ ] Uninstall: registry entry removal
- [ ] Migration: v0.9.x registry key rename (old names → new names)
- [ ] Migration: skill directory rename
- [ ] Migration: rules file rename
- [ ] Migration: opencode.json MCP path update (context-router → fish-trail)
- [ ] Migration: v0.10.x inline section removal
- [ ] Global install mode (install to ~/.config/opencode/skills, skip AGENTS.md merge)

**Deliverable**: `--uninstall`, `--global`, and migration work

### Phase 5: Deprecation + Documentation (est. 1-2 days)
**Goal**: Users migrate to new installer

- [ ] Add deprecation notice to shell installers (warning, not error)
- [ ] Update README.md: replace all 4 installer commands with `uv run` command
- [ ] Update website/index.html: replace installer commands
- [ ] Update docs/agent-install.md, docs/agent-upgrade.md
- [ ] Update docs/zh/README.md (Chinese translation)
- [ ] Update archive docs
- [ ] Create `uv run` bootstrap script (curl uv + run install.py in one line)
- [ ] Test: `uv run https://raw.githubusercontent.com/.../install.py` from clean machine
- [ ] Test: offline mode (`uv run ./install.py`)

**Deliverable**: Users can install via single `uv run` command

## Estimated Total: 8-12 days

## Risk Register

### 7.1 Original Risks

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| AGENTS.md merge logic divergence | High | Medium | Extract merge logic into testable functions; diff output against shell installer for same input |
| platforms.json format changes | Medium | Low | Parse defensively, validate schema |
| Windows long paths (>260 chars) | Medium | Medium | Use `\\?\` prefix on Windows |
| Windows encoding (GBK terminals) | High | Medium | Force UTF-8 at script start; same approach as v1.4.20 shell fix |
| `uv run <url>` caching stale scripts | Medium | Medium | Document `--refresh` flag; or use commit SHA URLs |
| Community pack download failure | Medium | Medium | Same retry chain: urllib → subprocess git clone |
| Breaking installed-packs.json format | High | Low | Read both array and dict formats; write dict format |
| Shell installers diverge during transition | Medium | High | Freeze shell installers after Python version is stable; don't maintain both in parallel |

### 7.2 Risks Identified by Expert Review (CRITICAL — Must Address)

| # | Risk | Severity | Mitigation |
|---|------|----------|------------|
| M1 | **Migration state corruption** — mid-migration failure leaves registry half-converted | CRITICAL | Backup registry before migration; try/except with restore on failure |
| M2 | **opencode.json atomic L2 merge** — `mcp` entries must be replaced atomically, NOT recursively merged | HIGH | Explicit `ATOMIC_L2_KEYS = {'mcp'}` logic; unit test with real MCP configs |
| M3 | **AGENTS.md legacy name handling** — multiple legacy sections, position tracking, blank line cleanup | HIGH | Port regex carefully; test coexisting `<!-- BEGIN pack: old-name -->` + `<!-- BEGIN pack: new-name -->` |
| M4 | **Download→Install ordering** — downloading during install loop causes missing file refs | HIGH | Strict two-phase: Phase A downloads ALL packs, Phase B installs from local copies |
| M5 | **Registry update must be LAST** — files without registry = invisible pack | HIGH | Files first → configs second → registry last (roll-forward) |
| M6 | **Uninstall cross-pack dependency** — opencode.json key deletion requires checking ALL other packs | HIGH | Before deleting key, scan all installed packs' manifests for same key |
| M7 | **Market metadata two-phase query** — network failure between resolve and download = broken state | MEDIUM | Download index once, cache to temp file; re-download if stale |
| M8 | **Windows shutil.rmtree PermissionError** | MEDIUM | Use `onerror=force_remove` handler that chmod + retry |
| M9 | **trust_scan.py invocation** — nested `uv run` within `uv run` | MEDIUM | Use `subprocess.run([sys.executable, trust_scan_path])` — avoids nesting |
| M10 | **Plugin exclusion** — `topic-detector.ts` MUST NOT deploy (constructor crash) | MEDIUM | Hard-coded exclusion list in plugin deploy function |
| M11 | **Global install split logic** — `init` installs globally AND locally when target is `.` | MEDIUM | Port exact split logic; reference issue #215 |
| M12 | **Content condensation** — token-limited platforms (Windsurf 6000, Cursor 8000) | LOW | Char-based approximation (1 token ≈ 4 chars) |

### 7.3 Mandatory Implementation Directives (NON-NEGOTIABLE)

1. **Error messages = shell-style** — no Python stack traces exposed to users. Top-level try/except formats friendly errors.
2. **Market index queried ONCE** before download phase — never per-pack.
3. **ALL packs downloaded BEFORE install phase** — staged in temp directory.
4. **Migration runs ONCE** before install loop — never per-pack.
5. **Registry update is LAST** per pack — files first, config second, registry third.
6. **stdlib ONLY** — no external deps.
7. **UTF-8 enforcement** at script start.
8. **Parity diff test** mandatory before merge.

## Testing Strategy

1. **Unit tests** for pure functions (merge logic, semver compare, path expansion)
2. **Integration test** with a mock pack directory (full install → verify file tree)
3. **Diff test**: Run both shell installer and Python installer on same input → diff output (MANDATORY before merge)
4. **Platform smoke test**: Docker containers for all 9 platforms on single machine
5. **Remote test**: `uv run <url>` from clean environment
6. **Edge case tests**: corrupted JSON, conflicting markers, empty packs, concurrent installs, Ctrl+C mid-install
7. **Network resilience tests**: mock 429/403, verify retry + mirror fallback

## Not in Scope (Deferred)

- npm/npx distribution (not needed with `uv run <url>`)
- Interactive TUI (keep CLI simple)
- Auto-update mechanism (users re-run the same command)
- Signing/verification of the Python script itself

## Review Log

- **Momus** (plan review): [OKAY] — All references valid, all phases executable, timeline reasonable. QA scenarios could be more specific but not blocking.
- **Metis** (risk analysis): Identified 12 hidden risks (M1-M12). Most critical: migration state corruption (M1), opencode.json atomic merge (M2), AGENTS.md legacy names (M3), download ordering (M4). All mitigations incorporated into §7.2-7.3.
- **Decision**: Full Python rewrite (not hybrid). Metis's hybrid proposal retains 4 shell files, which doesn't solve the core maintenance problem.
