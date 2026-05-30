#!/usr/bin/env bash
#
# Install 胖鱼 PEtFiSh skill packs into a target project or global skills directory.
#
# Usage:
#   ./install.sh --pack course --target ~/my-project
#   ./install.sh --pack all --platform antigravity
#   ./install.sh --pack petfish --platform all
#   ./install.sh --pack init --global
#   ./install.sh --list
#   ./install.sh --pack testdocs --force
#
set -euo pipefail

# --- uv availability check & auto-install ---
if ! command -v uv &>/dev/null; then
    echo "[胖鱼 PEtFiSh] uv not found. Installing uv (required for Python-based skills)..."
    if curl -LsSf https://astral.sh/uv/install.sh | sh 2>/dev/null; then
        # Source the env to make uv available in this session
        [ -f "$HOME/.local/bin/env" ] && . "$HOME/.local/bin/env" 2>/dev/null
        export PATH="$HOME/.local/bin:$PATH"
        if command -v uv &>/dev/null; then
            echo "[胖鱼 PEtFiSh] ✅ uv installed successfully: $(uv --version)"
        else
            echo "[胖鱼 PEtFiSh] WARNING: uv install completed but not found in PATH."
            echo "         You may need to restart your shell or add ~/.local/bin to PATH."
        fi
    else
        echo "[胖鱼 PEtFiSh] WARNING: Failed to install uv automatically."
        echo "         Install manually: https://docs.astral.sh/uv/getting-started/installation/"
    fi
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PACKS_DIR="$SCRIPT_DIR/packs"
PLATFORMS_JSON="$SCRIPT_DIR/platforms.json"

# Fallback: if platforms.json is missing (e.g. standalone download), use hardcoded defaults
if [[ ! -f "$PLATFORMS_JSON" ]]; then
    PLATFORMS_TEMP="$(mktemp)"
    PLATFORMS_JSON="$PLATFORMS_TEMP"
    cat > "$PLATFORMS_JSON" <<'PLATFORMSEOF'
{
  "platforms": {
    "opencode": {
      "display_name": "OpenCode",
      "project": {
        "skills_dir": ".opencode/skills",
        "commands_dir": ".opencode/commands",
        "agents_dir": ".opencode/agents",
        "config_file": "opencode.json",
        "instructions_file": "AGENTS.md",
        "rules_dir": null
      },
      "global": {
        "skills_dir": "~/.config/opencode/skills",
        "commands_dir": "~/.config/opencode/commands",
        "agents_dir": null,
        "config_file": null,
        "instructions_file": null
      },
      "skill_format": "SKILL.md",
      "detect_markers": [".opencode", "opencode.json"],
      "instructions_merge_strategy": "marker_based",
      "notes": "Primary development platform for PEtFiSh."
    },
    "claude": {
      "display_name": "Claude Code",
      "project": {
        "skills_dir": ".claude/skills",
        "commands_dir": ".claude/commands",
        "agents_dir": ".claude/agents",
        "config_file": ".claude/settings.json",
        "instructions_file": "CLAUDE.md",
        "rules_dir": ".claude/rules"
      },
      "global": {
        "skills_dir": "~/.claude/skills",
        "commands_dir": "~/.claude/commands",
        "agents_dir": "~/.claude/agents",
        "config_file": "~/.claude/settings.json",
        "instructions_file": "~/.claude/CLAUDE.md"
      },
      "skill_format": "SKILL.md",
      "detect_markers": [".claude", "CLAUDE.md"],
      "instructions_merge_strategy": "marker_based",
      "instructions_translation": {
        "source": "AGENTS.md",
        "target": "CLAUDE.md",
        "method": "rename_with_header"
      },
      "notes": "SKILL.md format is fully compatible with OpenCode."
    },
    "codex": {
      "display_name": "Codex",
      "project": {
        "skills_dir": ".agents/skills",
        "commands_dir": null,
        "agents_dir": ".codex/agents",
        "config_file": ".codex/config.toml",
        "instructions_file": "AGENTS.md",
        "rules_dir": null
      },
      "global": {
        "skills_dir": "~/.agents/skills",
        "commands_dir": null,
        "agents_dir": "~/.codex/agents",
        "config_file": "~/.codex/config.toml",
        "instructions_file": "~/.codex/AGENTS.md"
      },
      "skill_format": "SKILL.md",
      "detect_markers": [".codex"],
      "instructions_merge_strategy": "marker_based",
      "notes": "Uses AGENTS.md natively."
    },
    "cursor": {
      "display_name": "Cursor",
      "project": {
        "skills_dir": ".cursor/skills",
        "commands_dir": null,
        "agents_dir": null,
        "config_file": null,
        "instructions_file": null,
        "rules_dir": ".cursor/rules"
      },
      "global": {
        "skills_dir": null,
        "commands_dir": null,
        "agents_dir": null,
        "config_file": null,
        "instructions_file": null
      },
      "skill_format": "SKILL.md",
      "detect_markers": [".cursor", ".cursorrules"],
      "instructions_merge_strategy": "mdc_rules",
      "instructions_translation": {
        "source": "AGENTS.md",
        "target": ".cursor/rules/petfish-agents.mdc",
        "method": "wrap_as_mdc"
      },
      "condense": {
        "max_tokens": 8000
      },
      "notes": "Supports SKILL.md natively."
    },
    "copilot": {
      "display_name": "GitHub Copilot",
      "project": {
        "skills_dir": ".github/skills",
        "commands_dir": null,
        "agents_dir": null,
        "config_file": null,
        "instructions_file": ".github/copilot-instructions.md",
        "rules_dir": ".github/instructions"
      },
      "global": {
        "skills_dir": null,
        "commands_dir": null,
        "agents_dir": null,
        "config_file": null,
        "instructions_file": null
      },
      "skill_format": "SKILL.md",
      "detect_markers": [".github/copilot-instructions.md", ".github/skills"],
      "instructions_merge_strategy": "marker_based",
      "instructions_translation": {
        "source": "AGENTS.md",
        "target": ".github/copilot-instructions.md",
        "method": "rename_with_header"
      },
      "notes": "Supports SKILL.md under .github/skills/."
    },
    "windsurf": {
      "display_name": "Windsurf",
      "project": {
        "skills_dir": ".windsurf/skills",
        "commands_dir": null,
        "agents_dir": null,
        "config_file": null,
        "instructions_file": ".windsurfrules",
        "rules_dir": ".windsurf/rules"
      },
      "global": {
        "skills_dir": null,
        "commands_dir": null,
        "agents_dir": null,
        "config_file": "~/.codeium/windsurf/config.json",
        "instructions_file": "~/.codeium/windsurf/memories/global_rules.md"
      },
      "skill_format": "SKILL.md",
      "detect_markers": [".windsurf", ".windsurfrules"],
      "instructions_merge_strategy": "marker_based",
      "instructions_translation": {
        "source": "AGENTS.md",
        "target": ".windsurfrules",
        "method": "rename_with_header"
      },
      "condense": {
        "max_tokens": 6000
      },
      "notes": "Supports SKILL.md under .windsurf/skills/."
    },
    "antigravity": {
      "display_name": "Antigravity",
      "project": {
        "skills_dir": ".agents/skills",
        "commands_dir": ".agents/workflows",
        "agents_dir": ".agents/rules",
        "config_file": null,
        "instructions_file": "AGENTS.md",
        "rules_dir": null
      },
      "global": {
        "skills_dir": "~/.gemini/antigravity/skills",
        "commands_dir": "~/.gemini/antigravity/workflows",
        "agents_dir": null,
        "config_file": null,
        "instructions_file": null
      },
      "skill_format": "SKILL.md",
      "detect_markers": [".agents", "GEMINI.md"],
      "instructions_merge_strategy": "marker_based",
      "notes": "Google Gemini-based platform."
    },
    "universal": {
      "display_name": "Universal (cross-platform)",
      "project": {
        "skills_dir": ".agents/skills",
        "commands_dir": null,
        "agents_dir": null,
        "config_file": null,
        "instructions_file": "AGENTS.md",
        "rules_dir": null
      },
      "global": {
        "skills_dir": "~/.agents/skills",
        "commands_dir": null,
        "agents_dir": null,
        "config_file": null,
        "instructions_file": null
      },
      "skill_format": "SKILL.md",
      "detect_markers": [],
      "instructions_merge_strategy": "marker_based",
      "notes": "Fallback cross-platform path."
    }
  },
  "platform_groups": {
    "all": ["opencode", "claude", "codex", "cursor", "copilot", "windsurf", "antigravity"],
    "primary": ["opencode", "claude", "codex"],
    "ide": ["cursor", "copilot", "windsurf"],
    "cli": ["opencode", "claude", "codex", "antigravity"]
  }
}
PLATFORMSEOF
fi

# --- Merge helpers ---

merge_agents_md() {
    local src_file="$1" dst_file="$2" pack_name="$3" force="$4" manifest_file="${5:-}"
    local begin_marker="<!-- BEGIN pack: $pack_name -->"
    local end_marker="<!-- END pack: $pack_name -->"
    local src_content
    src_content="$(cat "$src_file")"
    # Strip existing markers from source if present (safety net)
    src_content="$(echo "$src_content" | sed "s|^${begin_marker}$||" | sed "s|^${end_marker}$||" | sed '/./,$!d' | sed -e :a -e '/^\n*$/{$d;N;ba}' )"
    local wrapped="${begin_marker}
${src_content}
${end_marker}"

    if [[ ! -f "$dst_file" ]]; then
        printf '%s\n' "$wrapped" > "$dst_file"
        echo "created"
        return
    fi

    if [[ ! -f "$dst_file" ]]; then
        printf '%s\n' "$wrapped" > "$dst_file"
        echo "created"
        return
    fi

    # Also check for legacy pack names that should be replaced
    local legacy_names_json="[]"
    if [[ -n "$manifest_file" && -f "$manifest_file" ]]; then
        legacy_names_json="$(python3 -c "
import json, sys
with open(sys.argv[1], 'r', encoding='utf-8') as f:
    m = json.load(f)
print(json.dumps(m.get('legacy_names', [])))
" "$manifest_file" 2>/dev/null || echo '[]')"
    fi

    # Check if current name OR any legacy name exists in the file
    local found_marker=false
    if grep -qF "$begin_marker" "$dst_file"; then
        found_marker=true
    else
        # Check legacy names
        local has_legacy
        has_legacy="$(python3 -c "
import json, sys
names = json.loads(sys.argv[1])
text = open(sys.argv[2], 'r', encoding='utf-8').read()
for name in names:
    if '<!-- BEGIN pack: ' + name + ' -->' in text:
        print('yes')
        sys.exit(0)
print('no')
" "$legacy_names_json" "$dst_file" 2>/dev/null || echo 'no')"
        if [[ "$has_legacy" == "yes" ]]; then
            found_marker=true
        fi
    fi

    if $found_marker; then
        if ! $force; then
            echo "exists"
            return
        fi
        # Replace current name and all legacy name sections
        python3 -c "
import re, json, sys

pack_name = sys.argv[1]
replacement = sys.argv[2]
dst_file = sys.argv[3]
legacy_names = json.loads(sys.argv[4])

text = open(dst_file, 'r', encoding='utf-8').read()

# Collect all names to search for (current + legacy)
all_names = [pack_name] + legacy_names

# Remove ALL sections matching any name
first_pos = len(text)  # track where to insert replacement
found_any = False

for name in all_names:
    begin = '<!-- BEGIN pack: ' + name + ' -->'
    end = '<!-- END pack: ' + name + ' -->'
    pattern = re.escape(begin) + r'.*?' + re.escape(end)
    matches = list(re.finditer(pattern, text, flags=re.DOTALL))
    if matches:
        if matches[0].start() < first_pos:
            first_pos = matches[0].start()
        found_any = True
        # Remove all occurrences of this name
        text = re.sub(pattern, '', text, flags=re.DOTALL)

if found_any:
    text = text.strip()
    first_pos = min(first_pos, len(text))
    text = text[:first_pos].rstrip() + '\n\n' + replacement + '\n\n' + text[first_pos:].lstrip()

# Clean up multiple blank lines
text = re.sub(r'\n{3,}', '\n\n', text).strip() + '\n'
open(dst_file, 'w', encoding='utf-8').write(text)
" "$pack_name" "$wrapped" "$dst_file" "$legacy_names_json"
        echo "updated"
        return
    fi

    # Append
    printf '\n\n%s\n' "$wrapped" >> "$dst_file"
    echo "merged"
}

write_pack_rules_file() {
    local src_file="$1" target_dir="$2" pack_name="$3"
    local l1_name=""

    case "$pack_name" in
        opencode-course-skills-pack)       l1_name="course-skills.md" ;;
        repo-deploy-ops-skill-pack)        l1_name="deploy-ops.md" ;;
        petfish-style-skill)               l1_name="petfish-style.md" ;;
        petfish-companion-skill)           l1_name="petfish-companion.md" ;;
        petfish-toolchain-skill)           l1_name="petfish-companion.md" ;;
        anti-sycophancy-calibration-pack)  l1_name="anti-sycophancy.md" ;;
        fish-trail)                        l1_name="fish-trail.md" ;;
        research-skill-pack)               l1_name="research.md" ;;
        fish-reflection-pack)              l1_name="fish-reflection.md" ;;
        series-style-governor-pack)          l1_name="series-style-governor.md" ;;
        *) return ;;
    esac

    local rules_dir="$target_dir/.opencode/agents-rules"
    mkdir -p "$rules_dir"

    local content
    content="$(cat "$src_file")"
    # Remove BEGIN/END markers
    content="$(echo "$content" | sed "/^<!-- BEGIN pack: $pack_name -->$/d" | sed "/^<!-- END pack: $pack_name -->$/d")"
    # Trim leading/trailing whitespace and ensure trailing newline
    content="$(echo "$content" | sed -e 's/^[[:space:]]*//' -e '/./,$!d' | sed -e :a -e '/^[[:space:]]*$/{ $d; N; ba; }')"

    # Backup existing rules file before overwriting (timestamped to preserve history)
    if [ -f "$rules_dir/$l1_name" ]; then
        cp "$rules_dir/$l1_name" "$rules_dir/$l1_name.$(date +%Y%m%d%H%M%S).bak"
    fi
    printf '%s\n' "$content" > "$rules_dir/$l1_name"
    echo "    + .opencode/agents-rules/$l1_name" >&2
}

# Install plugin files to .opencode/plugin/ (v0.11.0+)
# Only for OpenCode platform when L1 packs are present.
install_plugin_file() {
    local source_root="$1" target_dir="$2"
    local plugin_dir="$target_dir/.opencode/plugin"
    mkdir -p "$plugin_dir"

    # Copy all plugin files from lib/plugin/
    local src_plugin_dir="$source_root/lib/plugin"
    if [[ -d "$src_plugin_dir" ]]; then
        for src_plugin in "$src_plugin_dir"/*.ts; do
            [[ -f "$src_plugin" ]] || continue
            local plugin_name="$(basename "$src_plugin")"
            # topic-detector.ts is inlined into system-prompt-context-inject.ts (#160/#161)
            # and must NOT be deployed as a standalone plugin (causes constructor crash)
            [[ "$plugin_name" == "topic-detector.ts" ]] && continue
            cp "$src_plugin" "$plugin_dir/$plugin_name"
            echo "    + .opencode/plugin/$plugin_name" >&2
        done
    fi
}

# Register plugin tuple in opencode.json (idempotent)
register_plugin_in_config() {
    local config_file="$1"
    [[ -f "$config_file" ]] || return 0

    python3 -c "
import json, sys

config_file = sys.argv[1]

plugins_to_register = [
    ('.opencode/plugin/system-prompt-rules.ts', {'mode': 'all'}),
    ('.opencode/plugin/system-prompt-context-inject.ts', {'maxTopics': 5, 'maxSummaryLen': 200}),
]

with open(config_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

if 'plugin' not in data:
    data['plugin'] = []

changed = False
for plugin_path, plugin_opts in plugins_to_register:
    plugin_tuple = [plugin_path, plugin_opts]
    already_exists = any(
        isinstance(entry, list) and len(entry) >= 1 and entry[0] == plugin_path
        for entry in data['plugin']
    )
    if not already_exists:
        data['plugin'].append(plugin_tuple)
        changed = True

if changed:
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write(chr(10))
    print('    + opencode.json (plugins registered)')
" "$config_file" >&2
}

# v0.10.x → v0.11.x migration: remove old inline pack section from AGENTS.md
remove_inline_pack_section() {
    local agents_file="$1" pack_name="$2" manifest_file="${3:-}"
    [[ -f "$agents_file" ]] || return 0

    # Collect all names to remove: current + legacy names from manifest
    local names_to_try=("$pack_name")
    if [[ -n "$manifest_file" && -f "$manifest_file" ]]; then
        local legacy
        legacy="$(python3 -c "
import json, sys
with open(sys.argv[1], 'r', encoding='utf-8') as f:
    m = json.load(f)
for n in m.get('legacy_names', []):
    print(n)
" "$manifest_file" 2>/dev/null)" || true
        while IFS= read -r name; do
            [[ -n "$name" ]] && names_to_try+=("$name")
        done <<< "$legacy"
    fi

    local removed=false
    for name in "${names_to_try[@]}"; do
        local begin_marker="<!-- BEGIN pack: $name -->"
        local end_marker="<!-- END pack: $name -->"

        grep -qF "$begin_marker" "$agents_file" || continue

        # Use awk to remove section between markers (inclusive), no python3 dependency
        local tmp_file="${agents_file}.tmp.$$"
        awk -v bm="$begin_marker" -v em="$end_marker" '
            index($0, bm) { skip=1; next }
            skip && index($0, em) { skip=0; next }
            !skip { print }
        ' "$agents_file" > "$tmp_file"

        if [[ -s "$tmp_file" ]]; then
            mv "$tmp_file" "$agents_file"
            removed=true
            echo "    - AGENTS.md (removed inline section for $name)" >&2
        else
            rm -f "$tmp_file"
        fi
    done

    # Collapse triple+ blank lines to one blank line
    if $removed; then
        local tmp_file="${agents_file}.tmp.$$"
        awk 'NF {blank=0} !NF {blank++} blank<=1' "$agents_file" > "$tmp_file"
        if [[ -s "$tmp_file" ]]; then
            mv "$tmp_file" "$agents_file"
        else
            rm -f "$tmp_file"
        fi
    fi
}

# v0.9.x → v1.4 migration: clean up renamed packs, skills, and MCP paths
migrate_legacy_v0_9() {
    local target="$1" skills_dir="$2" config_file="$3" rules_dir="$4"
    [[ -d "$target" ]] || return 0

    python3 -c "
import json, os, sys, shutil

target = sys.argv[1]
skills_dir = sys.argv[2]
config_file = sys.argv[3]
rules_dir = sys.argv[4]

PACK_RENAMES = {
    'context-router-skill': 'fish-trail',
    'companion': 'petfish-companion-skill',
    'toolchain': 'petfish-toolchain-skill',
    'project-initializer': 'project-initializer-skill',
    'anti-sycophancy-calibration': 'anti-sycophancy-calibration-pack',
    'petfish-style-rewriter': 'petfish-style-skill',
    'skill-trust-governance': 'trustskills-governance-pack',
}

SKILL_RENAMES = {
    'context-router': 'fish-trail',
    'petfish-companion': 'fish-brain',
    'marketplace-connector': 'fish-market',
    'project-initializer': 'fish-init',
    'anti-sycophancy-calibration': 'fish-calibrate',
    'petfish-style-rewriter': 'fish-style',
    'skill-trust-governance': 'fish-guard',
}

RULES_RENAMES = {
    'context-router.md': 'fish-trail.md',
}

migrated = False

def find_registry_file(base):
    for candidate in [
        os.path.join(base, '.opencode', 'installed-packs.json'),
        os.path.join(base, '.claude', 'installed-packs.json'),
        os.path.join(base, '.agents', 'installed-packs.json'),
    ]:
        if os.path.isfile(candidate):
            return candidate
    return None

for base_dir in [target, os.path.expanduser('~')]:
    reg_file = find_registry_file(base_dir)
    if not reg_file or not os.path.isfile(reg_file):
        continue
    try:
        with open(reg_file, 'r', encoding='utf-8') as f:
            reg = json.load(f)
    except (json.JSONDecodeError, IOError):
        continue

    packs = reg.get('packs')
    if packs is None:
        continue
    if isinstance(packs, list):
        packs = {p: {} for p in packs if isinstance(p, str)}
        reg['packs'] = packs

    changed = False
    for old_key, new_key in PACK_RENAMES.items():
        if old_key in packs and new_key not in packs:
            packs[new_key] = packs.pop(old_key)
            print('    ' + chr(8635) + ' Registry: {} -> {}'.format(old_key, new_key), file=sys.stderr)
            changed = True
            migrated = True
        elif old_key in packs and new_key in packs:
            del packs[old_key]
            print('    ' + chr(8635) + ' Registry: removed stale {}'.format(old_key), file=sys.stderr)
            changed = True
            migrated = True

    if changed:
        with open(reg_file, 'w', encoding='utf-8') as f:
            json.dump(reg, f, indent=2, ensure_ascii=False)
            f.write(chr(10))

abs_skills = os.path.join(target, skills_dir) if not os.path.isabs(skills_dir) else skills_dir
if os.path.isdir(abs_skills):
    for old_dir, new_dir in SKILL_RENAMES.items():
        old_path = os.path.join(abs_skills, old_dir)
        new_path = os.path.join(abs_skills, new_dir)
        if os.path.isdir(old_path):
            if os.path.isdir(new_path):
                shutil.rmtree(old_path)
                print('    ' + chr(8635) + ' Removed stale skill dir: {}/'.format(old_dir), file=sys.stderr)
                migrated = True
            else:
                os.rename(old_path, new_path)
                print('    ' + chr(8635) + ' Renamed skill dir: {}/ -> {}/'.format(old_dir, new_dir), file=sys.stderr)
                migrated = True

abs_rules = os.path.join(target, rules_dir) if rules_dir and not os.path.isabs(rules_dir) else (rules_dir or '')
if abs_rules and os.path.isdir(abs_rules):
    for old_file, new_file in RULES_RENAMES.items():
        old_path = os.path.join(abs_rules, old_file)
        new_path = os.path.join(abs_rules, new_file)
        if os.path.isfile(old_path):
            if os.path.isfile(new_path):
                os.remove(old_path)
                print('    ' + chr(8635) + ' Removed stale rules file: {}'.format(old_file), file=sys.stderr)
            else:
                os.rename(old_path, new_path)
                print('    ' + chr(8635) + ' Renamed rules file: {} -> {}'.format(old_file, new_file), file=sys.stderr)
            migrated = True

abs_config = os.path.join(target, config_file) if config_file and not os.path.isabs(config_file) else (config_file or '')
if abs_config and os.path.isfile(abs_config):
    with open(abs_config, 'r', encoding='utf-8') as f:
        content = f.read()

    new_content = content
    replacements = [
        ('context-router/mcp', 'fish-trail/mcp'),
        ('context-router' + chr(47), 'fish-trail' + chr(47)),
    ]
    for old_str, new_str in replacements:
        if old_str in new_content:
            new_content = new_content.replace(old_str, new_str)

    try:
        config = json.loads(new_content)
        mcp = config.get('mcp', {})
        if 'context-state' in mcp:
            srv = mcp['context-state']
            if isinstance(srv, dict):
                for field in ['command', 'args']:
                    val = srv.get(field, '')
                    if isinstance(val, str) and 'context-router' in val:
                        srv[field] = val.replace('context-router', 'fish-trail')
                    elif isinstance(val, list):
                        srv[field] = [a.replace('context-router', 'fish-trail') if isinstance(a, str) and 'context-router' in a else a for a in val]
                for env_key in ['cwd', 'PETFISH_STATE_DIR']:
                    env_val = srv.get(env_key, '')
                    if isinstance(env_val, str) and 'context-router' in env_val:
                        srv[env_key] = env_val.replace('context-router', 'fish-trail')
                env = srv.get('env', {})
                if isinstance(env, dict):
                    for k, v in env.items():
                        if isinstance(v, str) and 'context-router' in v:
                            env[k] = v.replace('context-router', 'fish-trail')
        updated = json.dumps(config, indent=2, ensure_ascii=False)
        if updated != new_content:
            new_content = updated + chr(10)
    except (json.JSONDecodeError, KeyError):
        pass

    if new_content != content:
        with open(abs_config, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print('    ' + chr(8635) + ' Updated MCP paths in {}'.format(config_file), file=sys.stderr)
        migrated = True
" "$target" "$skills_dir" "$config_file" "$rules_dir"
}

merge_opencode_json() {
    local src_file="$1" dst_file="$2" force="$3" skills_dir="${4:-.opencode/skills}"

    python3 -c "
import json, os, sys

force = sys.argv[3] == 'true'
skills_dir = sys.argv[4] if len(sys.argv) > 4 else '.opencode/skills'
with open(sys.argv[1], 'r', encoding='utf-8') as f:
    src = json.load(f)

normalized_skills_dir = skills_dir.rstrip('/' + chr(92)) or '.opencode/skills'
src_str = json.dumps(src, ensure_ascii=False)
src_str = src_str.replace('.opencode/skills/', normalized_skills_dir + '/')
src = json.loads(src_str)

if not os.path.isfile(sys.argv[2]):
    with open(sys.argv[2], 'w', encoding='utf-8') as f:
        json.dump(src, f, indent=2, ensure_ascii=False)
        f.write('\n')
    print('created')
    sys.exit(0)

with open(sys.argv[2], 'r', encoding='utf-8') as f:
    dst = json.load(f)

# Keys whose level-2 entries should be replaced atomically (not deep-merged)
ATOMIC_L2 = {'mcp'}

def deep_merge(s, d, force_flag, parent_key=''):
    for k, v in s.items():
        if k not in d:
            d[k] = v
        elif parent_key in ATOMIC_L2 and force_flag:
            # Replace entire entry (e.g. mcp.context-state) atomically
            d[k] = v
        elif isinstance(v, dict) and isinstance(d[k], dict):
            deep_merge(v, d[k], force_flag, parent_key=k)
        elif force_flag:
            d[k] = v

deep_merge(src, dst, force)
with open(sys.argv[2], 'w', encoding='utf-8') as f:
    json.dump(dst, f, indent=2, ensure_ascii=False)
    f.write('\n')
print('merged')
" "$src_file" "$dst_file" "$force" "$skills_dir"
}

get_restart_hint() {
    case "$1" in
        opencode)
            printf '%s\n' '⚠️  Restart needed. Exit: Ctrl+C | Resume: opencode -s <session_id>'
            ;;
        claude)
            printf '%s\n' '⚠️  Restart needed. Exit: /exit or Ctrl+C | Resume: claude --continue'
            ;;
        codex)
            printf '%s\n' '⚠️  Restart needed. Exit: Ctrl+C'
            ;;
        cursor|copilot|windsurf)
            printf '%s\n' '⚠️  Restart needed. Reload window: Ctrl+Shift+P → "Reload Window"'
            ;;
        antigravity)
            printf '%s\n' '⚠️  Restart needed. Exit: Ctrl+C'
            ;;
    esac
}

update_installed_packs() {
    local registry_dir="$1" pack_name="$2" manifest_file="$3"
    local reg_file="$registry_dir/installed-packs.json"

    mkdir -p "$registry_dir"

    python3 -c "
import json, sys, os
from datetime import datetime, timezone

registry_dir = sys.argv[1]
pack_name = sys.argv[2]
manifest_file = sys.argv[3]
reg_file = os.path.join(registry_dir, 'installed-packs.json')

entry = {'installed_at': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}

if os.path.isfile(manifest_file):
    with open(manifest_file, 'r') as f:
        m = json.load(f)
    for key in ('version', 'skills', 'commands', 'agents', 'description', 'skill_count', 'command_count', 'agent_count'):
        if key in m:
            entry[key] = m[key]
    if 'skill_count' not in entry and 'skills' in m:
        entry['skill_count'] = len(m['skills'])

if os.path.isfile(reg_file):
    with open(reg_file, 'r') as f:
        reg = json.load(f)
else:
    reg = {'packs': {}}

# v0.4.x-v0.9.x used array format: normalize to dict
packs = reg.get('packs') or {}
if isinstance(packs, list):
    packs = {p: {} for p in packs if isinstance(p, str)}
    reg['packs'] = packs

reg['packs'][pack_name] = entry
with open(reg_file, 'w') as f:
    json.dump(reg, f, indent=2, ensure_ascii=False)
    f.write('\n')
" "$registry_dir" "$pack_name" "$manifest_file"
}

read_installed_pack_version() {
    local registry_dir="$1" pack_name="$2"

    python3 - "$registry_dir" "$pack_name" <<'PY'
import json
import os
import sys

registry_dir, pack_name = sys.argv[1:3]
reg_file = os.path.join(registry_dir, 'installed-packs.json')

if not os.path.isfile(reg_file):
    sys.exit(0)

with open(reg_file, 'r', encoding='utf-8') as f:
    reg = json.load(f)

packs = reg.get('packs') or {}
# v0.4.x-v0.9.x used array format: normalize to dict
if isinstance(packs, list):
    packs = {p: {} for p in packs if isinstance(p, str)}
version = (packs.get(pack_name) or {}).get('version')
if version:
    print(version)
PY
}

read_manifest_pack_version() {
    local manifest_file="$1"

    python3 - "$manifest_file" <<'PY'
import json
import os
import sys

manifest_file = sys.argv[1]
if not os.path.isfile(manifest_file):
    sys.exit(0)

with open(manifest_file, 'r', encoding='utf-8') as f:
    manifest = json.load(f)

version = manifest.get('version')
if version:
    print(version)
PY
}

check_pack_version() {
    local registry_dir="$1" pack_name="$2" manifest_file="$3"

    python3 - "$registry_dir" "$pack_name" "$manifest_file" <<'PY'
import json
import os
import sys

registry_dir, pack_name, manifest_file = sys.argv[1:4]

if not registry_dir or not os.path.isfile(manifest_file):
    print('unknown')
    sys.exit(0)

with open(manifest_file, 'r', encoding='utf-8') as f:
    manifest = json.load(f)

source_version = manifest.get('version')
if not source_version:
    print('unknown')
    sys.exit(0)

reg_file = os.path.join(registry_dir, 'installed-packs.json')
if not os.path.isfile(reg_file):
    print('not-installed')
    sys.exit(0)

with open(reg_file, 'r', encoding='utf-8') as f:
    registry = json.load(f)

packs = registry.get('packs') or {}
# v0.4.x-v0.9.x used array format: normalize to dict
if isinstance(packs, list):
    packs = {p: {} for p in packs if isinstance(p, str)}
    registry['packs'] = packs
pack_entry = packs.get(pack_name) or {}

# Legacy name lookup: if current name not in registry, check legacy names from manifest
legacy_key = None
if not pack_entry:
    legacy_names = manifest.get('legacy_names') or []
    for legacy in legacy_names:
        if packs.get(legacy):
            pack_entry = packs[legacy]
            legacy_key = legacy
            break

installed_version = pack_entry.get('version')
if not pack_entry:
    print('not-installed')
    sys.exit(0)
if not installed_version:
    print('unknown')
    sys.exit(0)

def parse_semver(version: str):
    parts = version.split('.')
    if len(parts) < 3:
        return None
    values = []
    for part in parts[:3]:
        if not part.isdigit():
            return None
        values.append(int(part))
    return values

installed_parts = parse_semver(installed_version)
source_parts = parse_semver(source_version)
if installed_parts is None or source_parts is None:
    print('unknown')
elif installed_parts == source_parts:
    print('same')
elif installed_parts < source_parts:
    print('newer')
else:
    print('unknown')

if legacy_key:
    print('legacy:' + legacy_key)
PY
}

# --- Pack alias registry ---
declare -A ALIASES=(
    [course]="opencode-course-skills-pack"
    [testdocs]="opencode-skill-pack-testcases-usage-docs"
    [deploy]="repo-deploy-ops-skill-pack"
    [petfish]="petfish-style-skill"
    [companion]="petfish-companion-skill"
    [ppt]="opencode-ppt-skills"
    [init]="project-initializer-skill"
    [trust]="trustskills-governance-pack"
    [fish-guard]="trustskills-governance-pack"
    [calibrate]="anti-sycophancy-calibration-pack"
    [context]="fish-trail"
    [research]="research-skill-pack"
    [reflect]="fish-reflection-pack"
    [fish-init]="project-initializer-skill"
    [fish-core]="petfish-companion-skill"
    [fish-course]="opencode-course-skills-pack"
    [fish-testdocs]="opencode-skill-pack-testcases-usage-docs"
    [fish-deploy]="repo-deploy-ops-skill-pack"
    [fish-style]="petfish-style-skill"
    [fish-slides]="opencode-ppt-skills"
    [fish-calibrate]="anti-sycophancy-calibration-pack"
    [fish-trail]="fish-trail"
    [fish-research]="research-skill-pack"
    [fish-reflect]="fish-reflection-pack"
    [fish-brain]="petfish-companion-skill"
    [toolchain]="petfish-toolchain-skill"
    [series-style]="series-style-governor-pack"
)

# --- Core pack classification ---
# Core packs are always sourced from local packs/core/.
# Optional packs are market-first (petfish-market index), with local fallback.
CORE_ALIASES=("init" "companion" "toolchain" "fish-trail")

is_core_alias() {
    local alias="$1"
    for core in "${CORE_ALIASES[@]}"; do
        [[ "$alias" == "$core" ]] && return 0
    done
    return 1
}

# Core pack names (used to guard pack-name-level checks).
CORE_PACK_NAMES=("project-initializer-skill" "petfish-companion-skill" "petfish-toolchain-skill" "fish-trail")

is_core_pack_name() {
    local pack_name="$1"
    for core in "${CORE_PACK_NAMES[@]}"; do
        [[ "$pack_name" == "$core" ]] && return 0
    done
    return 1
}

# Associative array: pack_name → raw JSON from petfish-market index.
# Populated by resolve_pack() for optional (non-core) packs.
declare -A MARKET_META

# Associative array: pack_name → extracted dir root (non-local market packs).
# Populated during download phase when a market pack has an external repo.
declare -A MARKET_PACK_DIRS

# --- Defaults ---
PACK=""
TARGET="."
TARGET_EXPLICIT=false
PLATFORM="opencode"
PLATFORM_EXPLICIT=false
DETECT=false
FORCE=false
LIST=false
GLOBAL=false
UNINSTALL=false
COMMUNITY_STAGING_DIR=""
MARKET_STAGING_DIR=""
PLATFORMS_TEMP=""
OFFLINE=false

cleanup_community_staging() {
    if [[ -n "$COMMUNITY_STAGING_DIR" && -d "$COMMUNITY_STAGING_DIR" ]]; then
        rm -rf "$COMMUNITY_STAGING_DIR"
    fi
    if [[ -n "$MARKET_STAGING_DIR" && -d "$MARKET_STAGING_DIR" ]]; then
        rm -rf "$MARKET_STAGING_DIR"
    fi
    if [[ -n "$PLATFORMS_TEMP" && -f "$PLATFORMS_TEMP" ]]; then
        rm -f "$PLATFORMS_TEMP"
    fi
}
trap cleanup_community_staging EXIT

# --- Community pack support ---
is_community_pack() {
    [[ "$1" == community/* ]]
}

# Parse community/owner/repo into components
parse_community_spec() {
    local spec="$1"
    # Strip leading "community/"
    local remainder="${spec#community/}"
    local owner="${remainder%%/*}"
    local repo="${remainder#*/}"
    # repo may contain /ref (branch/tag)
    local ref=""
    if [[ "$repo" == */* ]]; then
        ref="${repo#*/}"
        repo="${repo%%/*}"
    fi
    echo "$owner" "$repo" "$ref"
}

# Download a community skill from GitHub and stage it as a pack
# Usage: download_community_pack "community/owner/repo[/ref]"
# Sets COMMUNITY_STAGING_DIR and creates $COMMUNITY_STAGING_DIR/community--owner--repo/.opencode/
download_community_pack() {
    local spec="$1"
    local owner repo ref
    read -r owner repo ref <<< "$(parse_community_spec "$spec")"

    if [[ -z "$owner" || -z "$repo" ]]; then
        echo "Error: Invalid community pack spec '$spec'. Expected: community/<owner>/<repo>[/<ref>]" >&2
        exit 1
    fi

    local pack_dir_name="community--${owner}--${repo}"

    # Create staging dir (once per install run)
    if [[ -z "$COMMUNITY_STAGING_DIR" ]]; then
        COMMUNITY_STAGING_DIR="$(mktemp -d)"
    fi

    local staged_pack="$COMMUNITY_STAGING_DIR/$pack_dir_name"
    if [[ -d "$staged_pack" ]]; then
        # Already downloaded in this run
        echo "$pack_dir_name"
        return 0
    fi

    local github_ref="${ref:-main}"
    local tarball_url="https://github.com/${owner}/${repo}/archive/refs/heads/${github_ref}.tar.gz"

    echo "  [community] Downloading ${owner}/${repo} (ref: ${github_ref})..." >&2

    local dl_tmp
    dl_tmp="$(mktemp -d)"

    # Try tarball download first (retry up to 3 times for rate limits), fall back to git clone
    local dl_ok=false
    if command -v curl &>/dev/null; then
        local http_code
        for attempt in 1 2 3; do
            http_code="$(curl -fsSL -w '%{http_code}' -o "$dl_tmp/archive.tar.gz" \
                ${GITHUB_TOKEN:+-H "Authorization: token $GITHUB_TOKEN"} \
                "$tarball_url" 2>/dev/null)" || true
            if [[ "$http_code" == "200" && -f "$dl_tmp/archive.tar.gz" ]]; then
                dl_ok=true
                break
            fi
            if [[ "$http_code" == "429" || "$http_code" == "403" ]] && [[ $attempt -lt 3 ]]; then
                local wait=$((2 ** attempt))
                echo "  [community] Rate limited (HTTP $http_code), retrying in ${wait}s... (attempt $attempt/3)" >&2
                sleep "$wait"
                rm -f "$dl_tmp/archive.tar.gz"
            else
                break
            fi
        done
    fi

    if ! $dl_ok && command -v wget &>/dev/null; then
        for attempt in 1 2 3; do
            wget -q ${GITHUB_TOKEN:+--header="Authorization: token $GITHUB_TOKEN"} \
                -O "$dl_tmp/archive.tar.gz" "$tarball_url" 2>/dev/null && dl_ok=true && break || true
            if [[ $attempt -lt 3 ]]; then
                local wait=$((2 ** attempt))
                echo "  [community] wget download failed, retrying in ${wait}s... (attempt $attempt/3)" >&2
                sleep "$wait"
                rm -f "$dl_tmp/archive.tar.gz"
            fi
        done
    fi

    if $dl_ok; then
        # Extract tarball
        tar -xzf "$dl_tmp/archive.tar.gz" -C "$dl_tmp" 2>/dev/null
        # Find extracted directory (GitHub names it repo-branch/)
        local extracted
        extracted="$(find "$dl_tmp" -mindepth 1 -maxdepth 1 -type d ! -name "*.tar.gz" | head -1)"
        if [[ -z "$extracted" ]]; then
            echo "Error: Failed to extract community pack tarball for ${owner}/${repo}" >&2
            rm -rf "$dl_tmp"
            exit 1
        fi
        mv "$extracted" "$staged_pack"
    else
        # Fall back to git clone
        if ! command -v git &>/dev/null; then
            echo "Error: Cannot download community pack ${owner}/${repo}. Neither curl/wget tarball download nor git clone available." >&2
            rm -rf "$dl_tmp"
            exit 1
        fi
        echo "  [community] Tarball download failed, falling back to git clone..." >&2
        local clone_url="https://github.com/${owner}/${repo}.git"
        if [[ -n "$GITHUB_TOKEN" ]]; then
            clone_url="https://${GITHUB_TOKEN}@github.com/${owner}/${repo}.git"
        fi
        local clone_ok=false
        for attempt in 1 2 3; do
            git clone --depth 1 ${ref:+--branch "$ref"} "$clone_url" "$staged_pack" 2>/dev/null && clone_ok=true && break
            if [[ $attempt -lt 3 ]]; then
                local wait=$((2 ** attempt))
                echo "  [community] git clone failed, retrying in ${wait}s... (attempt $attempt/3)" >&2
                sleep "$wait"
                rm -rf "$staged_pack"
            fi
        done
        if ! $clone_ok; then
            echo "Error: Failed to clone community pack ${owner}/${repo}" >&2
            rm -rf "$dl_tmp"
            exit 1
        fi
    fi
    rm -rf "$dl_tmp"

    # Validate: must have .opencode/ with at least skills/ or commands/ or agents/
    if [[ ! -d "$staged_pack/.opencode" ]]; then
        echo "Error: Community pack ${owner}/${repo} has no .opencode/ directory. Not a valid skill pack." >&2
        rm -rf "$staged_pack"
        exit 1
    fi

    local has_content=false
    [[ -d "$staged_pack/.opencode/skills" ]] && has_content=true
    [[ -d "$staged_pack/.opencode/commands" ]] && has_content=true
    [[ -d "$staged_pack/.opencode/agents" ]] && has_content=true
    if ! $has_content; then
        echo "Error: Community pack ${owner}/${repo} .opencode/ has no skills/, commands/, or agents/. Not a valid skill pack." >&2
        rm -rf "$staged_pack"
        exit 1
    fi

    # Generate a minimal pack-manifest.json if missing
    if [[ ! -f "$staged_pack/pack-manifest.json" ]]; then
        python3 -c "
import json, os, sys

pack_dir = sys.argv[1]
owner = sys.argv[2]
repo = sys.argv[3]
opencode_dir = os.path.join(pack_dir, '.opencode')
skills = []
commands = []
agents = []
skills_dir = os.path.join(opencode_dir, 'skills')
if os.path.isdir(skills_dir):
    skills = [d for d in os.listdir(skills_dir) if os.path.isdir(os.path.join(skills_dir, d))]
commands_dir = os.path.join(opencode_dir, 'commands')
if os.path.isdir(commands_dir):
    commands = [d for d in os.listdir(commands_dir)]
agents_dir = os.path.join(opencode_dir, 'agents')
if os.path.isdir(agents_dir):
    agents = [d for d in os.listdir(agents_dir) if os.path.isdir(os.path.join(agents_dir, d))]

manifest = {
    'name': f'community/{owner}/{repo}',
    'version': '0.0.0',
    'description': f'Community skill pack from {owner}/{repo}',
    'skills': sorted(skills),
    'commands': sorted(commands),
    'agents': sorted(agents)
}
with open(os.path.join(pack_dir, 'pack-manifest.json'), 'w', encoding='utf-8') as f:
    json.dump(manifest, f, indent=2, ensure_ascii=False)
    f.write(chr(10))
" "$staged_pack" "$owner" "$repo"
        echo "  [community] Generated pack-manifest.json" >&2
    else
        # Validate existing manifest has required fields
        python3 -c "
import json, sys

manifest_path = sys.argv[1]
try:
    with open(manifest_path, 'r', encoding='utf-8') as f:
        m = json.load(f)
except (json.JSONDecodeError, OSError) as e:
    print(f'Error: pack-manifest.json is invalid: {e}', file=sys.stderr)
    sys.exit(1)

required = ['name', 'version', 'description', 'skills']
missing = [k for k in required if k not in m]
if missing:
    print(f'Error: pack-manifest.json missing required fields: {missing}', file=sys.stderr)
    sys.exit(1)

if not isinstance(m.get('skills'), list):
    print('Error: pack-manifest.json \"skills\" must be an array', file=sys.stderr)
    sys.exit(1)
" "$staged_pack/pack-manifest.json"
        if [[ $? -ne 0 ]]; then
            echo "Error: Community pack ${owner}/${repo} has invalid pack-manifest.json" >&2
            rm -rf "$staged_pack"
            exit 1
        fi
    fi

    echo "$pack_dir_name"
}

# --- Market index query ---
# Queries petfish-market index.json for a pack by alias or pack name.
# Echoes the matching pack JSON on success; returns 1 if not found or unavailable.
query_market_index() {
    local pack_alias="$1"
    local market_url="https://raw.githubusercontent.com/kylecui/petfish-market/main/index.json"
    local data
    data="$(curl -fsSL --max-time 10 "$market_url" 2>/dev/null)" || return 1
    python3 -c "
import json, sys
alias = sys.argv[1]
data = json.loads(sys.argv[2])
for pack in data.get('packs', []):
    if alias in pack.get('alias', []) or pack.get('name') == alias:
        print(json.dumps(pack))
        sys.exit(0)
sys.exit(1)
" "$pack_alias" "$data" 2>/dev/null
}

# --- Download market-sourced optional pack from external repo ---
# Usage: download_market_pack <pack_name>
# Reads MARKET_META[pack_name] for repo/ref.
# Stores extracted dir root in MARKET_PACK_DIRS[pack_name].
# Returns 0 on success, 1 on failure.
download_market_pack() {
    local pack_name="$1"
    [[ -z "${MARKET_META[$pack_name]+x}" ]] && return 1

    local _m_repo _m_ref
    _m_repo="$(python3 -c "
import json, sys
try:
    d = json.loads(sys.argv[1])
    print(d.get('repo', ''))
except Exception:
    pass
" "${MARKET_META[$pack_name]}" 2>/dev/null)" || _m_repo=""

    _m_ref="$(python3 -c "
import json, sys
try:
    d = json.loads(sys.argv[1])
    print(d.get('ref', 'main'))
except Exception:
    print('main')
" "${MARKET_META[$pack_name]}" 2>/dev/null)" || _m_ref="main"

    [[ -z "$_m_repo" ]] && return 1

    # Check if another pack from the same external repo was already downloaded.
    local _m_stage=""
    local _k
    for _k in "${!MARKET_PACK_DIRS[@]}"; do
        local _kj="${MARKET_META[$_k]:-}"
        if [[ -n "$_kj" ]]; then
            local _kr _kref
            _kr="$(python3 -c "import json,sys; d=json.loads(sys.argv[1]); print(d.get('repo',''))" "$_kj" 2>/dev/null)" || _kr=""
            _kref="$(python3 -c "import json,sys; d=json.loads(sys.argv[1]); print(d.get('ref','main'))" "$_kj" 2>/dev/null)" || _kref="main"
            if [[ "$_kr" == "$_m_repo" && "$_kref" == "$_m_ref" ]]; then
                _m_stage="${MARKET_PACK_DIRS[$_k]}"
                break
            fi
        fi
    done

    if [[ -z "$_m_stage" ]]; then
        echo "  [market] Downloading ${pack_name} from ${_m_repo}@${_m_ref}..."
        local _m_tmpdir
        _m_tmpdir="$(mktemp -d)"
        MARKET_STAGING_DIR="$_m_tmpdir"
        local _m_url="https://github.com/${_m_repo}/tarball/${_m_ref}"
        local _m_ok=false
        local _m_code
        for _attempt in 1 2 3; do
            _m_code="$(curl -fsSL -w '%{http_code}' -o "$_m_tmpdir/archive.tar.gz" "$_m_url" 2>/dev/null)" || true
            if [[ "$_m_code" == "200" && -f "$_m_tmpdir/archive.tar.gz" ]]; then
                tar xz -C "$_m_tmpdir" < "$_m_tmpdir/archive.tar.gz" && _m_ok=true && break
            fi
            if [[ "$_m_code" == "429" || "$_m_code" == "403" ]] && [[ $_attempt -lt 3 ]]; then
                sleep $((2 ** _attempt))
                rm -f "$_m_tmpdir/archive.tar.gz"
            else
                break
            fi
        done
        rm -f "$_m_tmpdir/archive.tar.gz"
        if $_m_ok; then
            _m_stage="$(find "$_m_tmpdir" -mindepth 1 -maxdepth 1 -type d | head -1)"
        else
            echo "  [market] WARN: failed to download ${pack_name} from ${_m_repo}@${_m_ref}" >&2
            return 1
        fi
    fi

    [[ -n "$_m_stage" ]] && MARKET_PACK_DIRS["$pack_name"]="$_m_stage"
    return 0
}
while [[ $# -gt 0 ]]; do
    case "$1" in
        --pack)
            [[ $# -ge 2 ]] || { echo "Error: --pack requires a value." >&2; exit 1; }
            PACK="$2"; shift 2 ;;
        --target)
            [[ $# -ge 2 ]] || { echo "Error: --target requires a value." >&2; exit 1; }
            TARGET="$2"; TARGET_EXPLICIT=true; shift 2 ;;
        --platform)
            [[ $# -ge 2 ]] || { echo "Error: --platform requires a value." >&2; exit 1; }
            PLATFORM="$2"; PLATFORM_EXPLICIT=true; shift 2 ;;
        --detect)   DETECT=true; shift ;;
        --global)   GLOBAL=true; shift ;;
        --uninstall) UNINSTALL=true; shift ;;
        --force)    FORCE=true; shift ;;
        --list)     LIST=true; shift ;;
        --offline)  OFFLINE=true; shift ;;
        -h|--help)
            echo "Usage: $0 --pack <name|all> [--target <path>] [--platform <opencode|claude|codex|cursor|copilot|windsurf|antigravity|universal|all|primary|ide|cli>] [--detect] [--global] [--uninstall] [--force] [--list] [--offline]"
            echo "胖鱼 PEtFiSh AI Worker's Companion — Self-adaptive Skill Installer"
            echo "Aliases: course, testdocs, deploy, petfish, companion, ppt, init, trust, research"
            echo "  --offline   Skip petfish-market queries; only install packs found locally."
            exit 0 ;;
        *) echo "Unknown option: $1" >&2; exit 1 ;;
    esac
done

if ! $LIST; then
    echo ""
    echo "  ><(((^>  胖鱼 PEtFiSh"
    echo "  [胖鱼 PEtFiSh] AI Worker's Companion — Self-adaptive Skill Installer"
    echo "  Initialize -> Auto-install -> Work immediately"
    echo ""
fi

get_platform_field() {
    local platform_name="$1"
    local field_path="$2"

    python3 - "$PLATFORMS_JSON" "$platform_name" "$field_path" <<'PY'
import json
import sys

registry_file, platform_name, field_path = sys.argv[1:4]

with open(registry_file, 'r', encoding='utf-8') as f:
    registry = json.load(f)

platform = registry.get('platforms', {}).get(platform_name)
if platform is None:
    sys.exit(1)

value = platform
for part in field_path.split('.'):
    if not isinstance(value, dict):
        value = None
        break
    value = value.get(part)

if value is None:
    print("")
elif isinstance(value, list):
    print(",".join(str(item) for item in value))
else:
    print(value)
PY
}

platform_exists() {
    python3 - "$PLATFORMS_JSON" "$1" <<'PY' >/dev/null
import json
import sys

with open(sys.argv[1], 'r', encoding='utf-8') as f:
    registry = json.load(f)

sys.exit(0 if sys.argv[2] in registry.get('platforms', {}) else 1)
PY
}

get_platform_group() {
    local group_name="$1"

    python3 - "$PLATFORMS_JSON" "$group_name" <<'PY'
import json
import sys

with open(sys.argv[1], 'r', encoding='utf-8') as f:
    registry = json.load(f)

group = registry.get('platform_groups', {}).get(sys.argv[2])
if group is None:
    sys.exit(1)

for item in group:
    print(item)
PY
}

get_platforms_for_selection() {
    local selection="$1"

    if get_platform_group "$selection" >/dev/null 2>&1; then
        get_platform_group "$selection"
        return
    fi

    if platform_exists "$selection"; then
        printf '%s\n' "$selection"
        return
    fi

    echo "Error: unsupported platform or group '$selection'" >&2
    exit 1
}

get_detection_order() {
    python3 - "$PLATFORMS_JSON" <<'PY'
import json
import sys

with open(sys.argv[1], 'r', encoding='utf-8') as f:
    registry = json.load(f)

ordered = []
seen = set()

for name in registry.get('platform_groups', {}).get('primary', []):
    if name not in seen:
        ordered.append(name)
        seen.add(name)

for name in registry.get('platforms', {}).keys():
    if name not in seen:
        ordered.append(name)
        seen.add(name)

for name in ordered:
    print(name)
PY
}

expand_home_path() {
    local path_value="$1"

    if [[ -z "$path_value" ]]; then
        echo ""
    elif [[ "$path_value" == "~" ]]; then
        echo "$HOME"
    elif [[ "$path_value" == "~/"* ]]; then
        echo "$HOME/${path_value:2}"
    else
        echo "$path_value"
    fi
}

validate_project_relative_path() {
    local path_value="$1"
    local field_name="$2"

    [[ -z "$path_value" ]] && return 0

    case "$path_value" in
        /*|~*|?:/*|?:\\*)
            echo "Error: invalid $field_name path '$path_value' in platforms.json; project paths must stay relative to target." >&2
            exit 1
            ;;
    esac

    case "/$path_value/" in
        */../*|*/./../*|*/.././*|*/..//*)
            echo "Error: invalid $field_name path '$path_value' in platforms.json; parent traversal is not allowed." >&2
            exit 1
            ;;
    esac
}

get_platform_registry_dir() {
    local skills_dir="$1"

    if [[ -z "$skills_dir" ]]; then
        echo ""
    elif [[ "$skills_dir" == */* ]]; then
        echo "${skills_dir%/*}"
    else
        echo "."
    fi
}

detect_platform() {
    local target_path="$1"

    detect_all_platforms "$target_path" | head -n 1
}

detect_all_platforms() {
    local target_path="$1"
    local found=()
    local platform_name
    while IFS= read -r platform_name; do
        [[ -n "$platform_name" ]] || continue
        local markers
        markers="$(get_platform_field "$platform_name" "detect_markers")"
        [[ -n "$markers" ]] || continue
        local marker
        local -a marker_list=()
        IFS=',' read -r -a marker_list <<< "$markers"
        for marker in "${marker_list[@]}"; do
            [[ -n "$marker" ]] || continue
            if [[ -e "$target_path/$marker" ]]; then
                found+=("$platform_name")
                break
            fi
        done
    done < <(get_detection_order)
    if (( ${#found[@]} == 0 )); then
        echo "opencode"
    else
        printf '%s\n' "${found[@]}"
    fi
}

generate_secondary_instructions() {
    local target_path="$1"
    local force="$2"
    shift 2
    local detected=("$@")

    local primary_instructions="$target_path/AGENTS.md"
    [[ -f "$primary_instructions" ]] || return 0

    echo ""
    echo "  [translate] Generating instruction files for detected platforms..."

    local platform_name
    for platform_name in "${detected[@]}"; do
        [[ "$platform_name" == "$PLATFORM" ]] && continue

        local trans_target
        trans_target="$(get_platform_field "$platform_name" "instructions_translation.target")"
        [[ -n "$trans_target" ]] || continue
        [[ "$trans_target" == "AGENTS.md" ]] && continue

        local max_tokens
        max_tokens="$(get_platform_field "$platform_name" "condense.max_tokens")"

        local source_to_translate="$primary_instructions"
        if [[ -n "$max_tokens" ]] && (( max_tokens > 0 )); then
            local full_content
            full_content="$(cat "$primary_instructions")"
            local condensed
            condensed="$(condense_content "$full_content" "$max_tokens")"
            local condensed_tmp
            condensed_tmp="$(mktemp)"
            printf '%s' "$condensed" > "$condensed_tmp"
            source_to_translate="$condensed_tmp"
        fi

        update_translated_instructions "$source_to_translate" "$target_path/$trans_target" "$platform_name" "$force"

        [[ "$source_to_translate" != "$primary_instructions" ]] && rm -f "$source_to_translate"
    done
}

condense_content() {
    local content="$1"
    local max_tokens="$2"

    local char_count=${#content}
    local est_tokens=$(( char_count / 4 ))

    if (( est_tokens <= max_tokens )); then
        printf '%s' "$content"
        return
    fi

    local tmpfile
    tmpfile="$(mktemp)"
    printf '%s' "$content" > "$tmpfile"

    python3 - "$max_tokens" "$tmpfile" <<'PYEOF'
import os
import sys

max_tokens = int(sys.argv[1])
input_file = sys.argv[2]

with open(input_file, 'r', encoding='utf-8') as f:
    content = f.read()

sections = []
current = []
current_priority = 1
current_name = ""

for line in content.split('\n'):
    if line.startswith('<!-- BEGIN pack:'):
        if current:
            sections.append((current_name, current_priority, '\n'.join(current)))
        current = [line]
        current_name = line.split('pack:')[1].split('-->')[0].strip() if 'pack:' in line else ""
        p0_packs = ['petfish-companion-skill', 'fish-trail']
        if current_name in p0_packs:
            current_priority = 0
        else:
            current_priority = 1
    elif line.startswith('<!-- END pack:'):
        current.append(line)
        sections.append((current_name, current_priority, '\n'.join(current)))
        current = []
        current_name = ""
        current_priority = 1
    else:
        current.append(line)

if current:
    sections.append((current_name, current_priority, '\n'.join(current)))

p0 = [(n, p, c) for n, p, c in sections if p == 0]
p1 = [(n, p, c) for n, p, c in sections if p == 1]

result_parts = []
used_tokens = 0
footer = "\n<!-- Condensed by PEtFiSh. Full rules: AGENTS.md -->"
footer_tokens = len(footer) // 4

for name, pri, text in p0:
    tokens = len(text) // 4
    result_parts.append(text)
    used_tokens += tokens

budget = max_tokens - footer_tokens
for name, pri, text in p1:
    tokens = len(text) // 4
    if used_tokens + tokens <= budget:
        result_parts.append(text)
        used_tokens += tokens
    else:
        lines = text.split('\n')
        snippet_lines = []
        found_content = False
        for l in lines:
            snippet_lines.append(l)
            if found_content and l.strip() == '':
                break
            if l.strip():
                found_content = True
        snippet = '\n'.join(snippet_lines)
        snippet_tokens = len(snippet) // 4
        if used_tokens + snippet_tokens <= budget:
            result_parts.append(snippet)
            used_tokens += snippet_tokens

output = '\n'.join(result_parts) + footer
sys.stdout.write(output)
os.unlink(input_file)
PYEOF
}

update_translated_instructions() {
    local source_file="$1"
    local destination_file="$2"
    local platform_name="$3"
    local force_overwrite="$4"

    [[ -f "$source_file" ]] || return 0

    local method
    method="$(get_platform_field "$platform_name" "instructions_translation.method")"
    [[ -n "$method" ]] || return 0

    local source_content
    source_content="$(cat "$source_file")"
    local prefix=""

    case "$method" in
        rename_with_header)
            prefix="<!-- Generated by PEtFiSh from AGENTS.md -->"
            ;;
        wrap_as_mdc)
            prefix="---
description: \"PEtFiSh project instructions\"
alwaysApply: true
---"
            ;;
        *)
            return 0
            ;;
    esac

    local begin_marker="<!-- BEGIN pack: translation-$platform_name -->"
    local end_marker="<!-- END pack: translation-$platform_name -->"
    local managed_block="${begin_marker}
${source_content}
${end_marker}"
    local translated_content="$managed_block"

    if [[ -n "$prefix" ]]; then
        translated_content="${prefix}
${managed_block}"
    fi

    local parent_dir
    parent_dir="$(dirname "$destination_file")"
    if [[ -n "$parent_dir" && "$parent_dir" != "." ]]; then
        mkdir -p "$parent_dir"
    fi

    local temp_file
    temp_file="$(mktemp)"
    printf '%s\n' "$translated_content" > "$temp_file"

    if [[ ! -f "$destination_file" ]]; then
        cp "$temp_file" "$destination_file"
        rm -f "$temp_file"
        echo "created"
        return
    fi

    local existing
    existing="$(cat "$destination_file")"
    if echo "$existing" | grep -qF "$begin_marker"; then
        if ! $force_overwrite; then
            rm -f "$temp_file"
            echo "exists"
            return
        fi
        python3 - "$begin_marker" "$end_marker" "$managed_block" "$destination_file" <<'PY'
import re
import sys

begin = sys.argv[1]
end = sys.argv[2]
replacement = sys.argv[3]
path = sys.argv[4]

with open(path, 'r', encoding='utf-8') as f:
    text = f.read()

pattern = re.escape(begin) + r'.*?' + re.escape(end)
result = re.sub(pattern, replacement, text, flags=re.DOTALL)

with open(path, 'w', encoding='utf-8') as f:
    f.write(result)
PY
        rm -f "$temp_file"
        echo "updated"
        return
    fi

    printf '\n\n%s\n' "$managed_block" >> "$destination_file"
    rm -f "$temp_file"
    echo "merged"
}

convert_opencode_example_to_claude_settings() {
    local src_file="$1"
    local dst_file="$2"

    if [[ -f "$dst_file" ]]; then
        echo "exists"
        return
    fi

    local parent_dir
    parent_dir="$(dirname "$dst_file")"
    if [[ -n "$parent_dir" && "$parent_dir" != "." ]]; then
        mkdir -p "$parent_dir"
    fi

    python3 - "$src_file" "$dst_file" <<'PY'
import json
import sys

with open(sys.argv[1], 'r', encoding='utf-8') as f:
    src = json.load(f)

permissions = {}
for skill_name, mode in (src.get('permission', {}).get('skill', {}) or {}).items():
    mode = str(mode)
    if mode in {'allow', 'ask', 'deny'}:
        permissions.setdefault(mode, []).append(f'Skill({skill_name})')

dst = {
    '$schema': 'https://json.schemastore.org/claude-code-settings.json'
}
if permissions:
    dst['permissions'] = permissions

with open(sys.argv[2], 'w', encoding='utf-8') as f:
    json.dump(dst, f, indent=2, ensure_ascii=False)
    f.write('\n')
PY

    echo "created"
}

resolve_pack() {
    local name="$1"
    if is_community_pack "$name"; then
        # Community pack: download from GitHub and return staged dir name
        local pack_dir_name
        pack_dir_name="$(download_community_pack "$name")"
        echo "$pack_dir_name"
    elif [[ -n "${ALIASES[$name]+x}" ]]; then
        local pack_name="${ALIASES[$name]}"
        # For optional (non-core) packs not found locally: query market if online
        if ! is_core_alias "$name" && ! is_core_pack_name "$pack_name" && ! $OFFLINE; then
            if [[ ! -d "$PACKS_DIR/core/$pack_name" && ! -d "$PACKS_DIR/optional/$pack_name" ]]; then
                local _mj
                _mj="$(query_market_index "$name" 2>/dev/null)" || true
                if [[ -n "$_mj" ]]; then
                    MARKET_META["$pack_name"]="$_mj"
                fi
            fi
        fi
        echo "$pack_name"
    elif [[ -d "$PACKS_DIR/core/$name" ]] || [[ -d "$PACKS_DIR/optional/$name" ]]; then
        echo "$name"
    elif ! $OFFLINE && ! is_core_pack_name "$name"; then
        # Not found locally and not core: try market by pack name directly
        local _mj
        _mj="$(query_market_index "$name" 2>/dev/null)" || true
        if [[ -n "$_mj" ]]; then
            local _resolved_name
            _resolved_name="$(python3 -c "import json,sys; d=json.loads(sys.argv[1]); print(d.get('name',''))" "$_mj" 2>/dev/null)" || _resolved_name=""
            if [[ -n "$_resolved_name" ]]; then
                MARKET_META["$_resolved_name"]="$_mj"
                echo "$_resolved_name"
                return
            fi
        fi
        echo "Unknown pack: '$name'. Use --list to see available packs." >&2
        exit 1
    else
        echo "Unknown pack: '$name'. Use --list to see available packs." >&2
        exit 1
    fi
}

# Find the actual on-disk path for a pack directory name (v1.4: core/ + optional/)
# For packs downloaded from an external market-sourced repo (MARKET_PACK_DIRS),
# uses the path declared in the market index metadata.
find_pack_dir() {
    local name="$1"
    # External-repo market packs: use the path from market metadata.
    if [[ -n "${MARKET_PACK_DIRS[$name]+x}" && -n "${MARKET_PACK_DIRS[$name]}" ]]; then
        local meta_path
        meta_path="$(python3 -c "
import json, sys
try:
    d = json.loads(sys.argv[1])
    print(d.get('path', ''))
except Exception:
    pass
" "${MARKET_META[$name]}" 2>/dev/null)" || meta_path=""
        if [[ -n "$meta_path" && -d "${MARKET_PACK_DIRS[$name]}/$meta_path" ]]; then
            echo "${MARKET_PACK_DIRS[$name]}/$meta_path"
            return
        fi
        # Fallback: walk extracted tree for the pack dir name.
        local found_dir
        found_dir="$(find "${MARKET_PACK_DIRS[$name]}" -maxdepth 4 -type d -name "$name" | head -1)"
        if [[ -n "$found_dir" ]]; then
            echo "$found_dir"
            return
        fi
    fi
    if [[ -d "$PACKS_DIR/core/$name" ]]; then
        echo "$PACKS_DIR/core/$name"
    elif [[ -d "$PACKS_DIR/optional/$name" ]]; then
        echo "$PACKS_DIR/optional/$name"
    else
        echo "$PACKS_DIR/$name"
    fi
}

get_all_packs() {
    local dir _result=""
    for dir in "$PACKS_DIR"/core/* "$PACKS_DIR"/optional/*; do
        [[ -d "$dir" ]] || continue
        _result+="$(basename "$dir")"$'\n'
    done
    # When online, also include optional packs from market not present locally.
    if ! $OFFLINE; then
        local _market_data
        _market_data="$(curl -fsSL --max-time 10 "https://raw.githubusercontent.com/kylecui/petfish-market/main/index.json" 2>/dev/null)" || true
        if [[ -n "$_market_data" ]]; then
            local _market_packs
            _market_packs="$(python3 -c "
import json, sys
try:
    data = json.loads(sys.argv[1])
    for pack in data.get('packs', []):
        name = pack.get('name', '')
        if name:
            print(name)
except Exception:
    pass
" "$_market_data" 2>/dev/null)" || true
            [[ -n "$_market_packs" ]] && _result+="$_market_packs"$'\n'
        fi
    fi
    echo -n "$_result" | sort -u
}

show_list() {
    echo ""
    echo "Available packs:"
    echo "$(printf '%.0s-' {1..60})"
    for dir in $(get_all_packs); do
        alias=""
        for key in "${!ALIASES[@]}"; do
            if [[ "${ALIASES[$key]}" == "$dir" ]]; then
                alias=" (alias: $key)"
                break
            fi
        done
        echo "  $dir$alias"
    done
    echo ""

    # Show installed community packs from target registry
    local reg_file="$TARGET/.opencode/installed-packs.json"
    if [[ -f "$reg_file" ]]; then
        local community_output
        community_output="$(python3 -c "
import json, sys

reg_file = sys.argv[1]
with open(reg_file, 'r', encoding='utf-8') as f:
    reg = json.load(f)

packs = reg.get('packs') or {}
community = {k: v for k, v in packs.items() if k.startswith('community/')}
if not community:
    sys.exit(0)

for name, info in sorted(community.items()):
    version = info.get('version', 'unknown')
    desc = info.get('description', '')
    skills = info.get('skill_count', len(info.get('skills', [])))
    line = f'  {name}  v{version}  skills={skills}'
    if desc:
        line += f'  ({desc})'
    print(line)
" "$reg_file" 2>/dev/null)"
        if [[ -n "$community_output" ]]; then
            echo "Community packs (installed):"
            echo "$(printf '%.0s-' {1..60})"
            echo "$community_output"
            echo ""
        fi
    fi
}

should_create_gemini() {
    [[ "$1" == "antigravity" ]]
}

# --- Install function for a given platform ---
install_for_platform() {
    local platform_name="$1"
    shift
    local -a packs=("$@")

    local skills_dir
    skills_dir="$(get_platform_field "$platform_name" "project.skills_dir")"
    validate_project_relative_path "$skills_dir" "$platform_name project.skills_dir"
    local agents_dir
    agents_dir="$(get_platform_field "$platform_name" "project.agents_dir")"
    validate_project_relative_path "$agents_dir" "$platform_name project.agents_dir"
    local commands_dir
    commands_dir="$(get_platform_field "$platform_name" "project.commands_dir")"
    validate_project_relative_path "$commands_dir" "$platform_name project.commands_dir"
    local config_file
    config_file="$(get_platform_field "$platform_name" "project.config_file")"
    validate_project_relative_path "$config_file" "$platform_name project.config_file"
    local translation_target
    translation_target="$(get_platform_field "$platform_name" "instructions_translation.target")"
    validate_project_relative_path "$translation_target" "$platform_name instructions_translation.target"
    local rules_dir
    rules_dir="$(get_platform_field "$platform_name" "project.rules_dir")"
    local registry_dir
    registry_dir="$(get_platform_registry_dir "$skills_dir")"
    validate_project_relative_path "$registry_dir" "$platform_name registry_dir"

    # Migrate legacy v0.9.x artifacts (renamed packs, skills, MCP paths)
    migrate_legacy_v0_9 "$TARGET" "$skills_dir" "$config_file" "$rules_dir"

    echo ""
    echo "[$platform_name] Installing..."

    local installed=0
    local skipped=0

    for pack_name in "${packs[@]}"; do
        # Resolve pack root: community packs live in staging dir, official packs in PACKS_DIR
        local pack_root
        if [[ "$pack_name" == community--* && -n "$COMMUNITY_STAGING_DIR" && -d "$COMMUNITY_STAGING_DIR/$pack_name" ]]; then
            pack_root="$COMMUNITY_STAGING_DIR/$pack_name"
        else
            pack_root="$(find_pack_dir "$pack_name")"
        fi

        local pack_opencode="$pack_root/.opencode"
        if [[ ! -d "$pack_opencode" ]]; then
            echo "WARN: Pack '$pack_name' has no .opencode/ directory. Skipping."
            continue
        fi

        echo ""
        echo "  Installing pack: $pack_name"
        local manifest_file="$pack_root/pack-manifest.json"
        local target_registry=""
        if [[ -n "$registry_dir" ]]; then
            target_registry="$TARGET/$registry_dir"
        fi
        local force_this_pack=$FORCE

        if ! $force_this_pack; then
            local version_status_raw version_status legacy_key version_lookup_name
            version_status_raw="$(check_pack_version "$target_registry" "$pack_name" "$manifest_file")"
            version_status="${version_status_raw%%$'\n'*}"
            legacy_key=""
            if [[ "$version_status_raw" == *$'\n'legacy:* ]]; then
                legacy_key="${version_status_raw#*$'\n'legacy:}"
            fi
            version_lookup_name="$pack_name"
            if [[ -n "$legacy_key" ]]; then
                version_lookup_name="$legacy_key"
            fi
            case "$version_status" in
                same)
                    local installed_version
                    installed_version="$(read_installed_pack_version "$target_registry" "$version_lookup_name")"
                    echo "  ✓ $pack_name v$installed_version is current. Use -Force/-force to reinstall." >&2
                    ((skipped++)) || true
                    continue
                    ;;
                newer)
                    local installed_version source_version
                    installed_version="$(read_installed_pack_version "$target_registry" "$version_lookup_name")"
                    source_version="$(read_manifest_pack_version "$manifest_file")"
                    echo "  ⬆ Upgrading $pack_name v$installed_version → v$source_version" >&2
                    force_this_pack=true
                    ;;
            esac
        fi

        # --- Merge AGENTS.md ---
        if [[ -f "$pack_root/AGENTS.md" ]]; then
            # Tiered AGENTS.md: on opencode, packs with L1 rules files skip inline merge
            local has_l1=false
            if [[ "$platform_name" == "opencode" ]]; then
                case "$pack_name" in
                    opencode-course-skills-pack|repo-deploy-ops-skill-pack|petfish-style-skill|petfish-companion-skill|petfish-toolchain-skill|anti-sycophancy-calibration-pack|fish-trail|research-skill-pack|fish-reflection-pack|series-style-governor-pack)
                        has_l1=true ;;
                esac
            fi

            if $has_l1; then
                # L1-only: write standalone rules file, skip inline merge
                write_pack_rules_file "$pack_root/AGENTS.md" "$TARGET" "$pack_name"
                # Also deploy any extra agents-rules files from the pack
                if [[ -d "$pack_opencode/agents-rules" ]]; then
                    local extra_rules_dir="$TARGET/.opencode/agents-rules"
                    mkdir -p "$extra_rules_dir"
                    for rules_file in "$pack_opencode/agents-rules"/*.md; do
                        [[ -f "$rules_file" ]] || continue
                        local rules_basename="$(basename "$rules_file")"
                        cp "$rules_file" "$extra_rules_dir/$rules_basename"
                        echo "    + .opencode/agents-rules/$rules_basename" >&2
                    done
                fi
                # Deliver system-prompt-rules plugin (idempotent, runs for each L1 pack)
                install_plugin_file "$SCRIPT_DIR" "$TARGET"
                register_plugin_in_config "$TARGET/opencode.json"
                # v0.10.x → v0.11.x migration: remove old inline section from AGENTS.md
                remove_inline_pack_section "$TARGET/AGENTS.md" "$pack_name" "$manifest_file"
            else
                # Non-opencode or packs without L1: merge inline as before
                local dst_agents="$TARGET/AGENTS.md"
                local result
                result="$(merge_agents_md "$pack_root/AGENTS.md" "$dst_agents" "$pack_name" "$force_this_pack" "$manifest_file")"
                case "$result" in
                    created) echo "    + AGENTS.md (created)"; ((installed++)) || true ;;
                    merged)  echo "    + AGENTS.md (merged)";  ((installed++)) || true ;;
                    updated) echo "    + AGENTS.md (updated)"; ((installed++)) || true ;;
                    exists)  echo "    SKIP AGENTS.md (pack section exists, use --force to update)"; ((skipped++)) || true ;;
                esac
            fi

            # Antigravity: also create/merge GEMINI.md
            if should_create_gemini "$platform_name"; then
                local dst_gemini="$TARGET/GEMINI.md"
                result="$(merge_agents_md "$pack_root/AGENTS.md" "$dst_gemini" "$pack_name" "$force_this_pack" "$manifest_file")"
                case "$result" in
                    created) echo "    + GEMINI.md (created)"; ((installed++)) || true ;;
                    merged)  echo "    + GEMINI.md (merged)";  ((installed++)) || true ;;
                    updated) echo "    + GEMINI.md (updated)"; ((installed++)) || true ;;
                    exists)  echo "    SKIP GEMINI.md (pack section exists, use --force to update)"; ((skipped++)) || true ;;
                esac
            fi
        fi

        # --- Platform-specific config handling ---
        # Deploy MCP server files from pack's .opencode/mcp/ to target
if [[ -d "$pack_opencode/mcp" ]]; then
    local target_mcp_dir="$TARGET/.opencode/mcp"
    mkdir -p "$target_mcp_dir"
    for mcp_dir in "$pack_opencode/mcp"/*/; do
        [[ -d "$mcp_dir" ]] || continue
        local mcp_name="$(basename "$mcp_dir")"
        local target_mcp="$target_mcp_dir/$mcp_name"
        mkdir -p "$target_mcp"
        cp -r "$mcp_dir"* "$target_mcp/" 2>/dev/null || true
        echo "    + .opencode/mcp/$mcp_name/" >&2
    done
fi

if [[ -n "$config_file" && -f "$pack_root/opencode.example.json" ]]; then
            case "$platform_name" in
                opencode)
                    local dst_oc="$TARGET/$config_file"
                    result="$(merge_opencode_json "$pack_root/opencode.example.json" "$dst_oc" "$force_this_pack" "$skills_dir")"
                    case "$result" in
                        created) echo "    + $config_file (created from example)"; ((installed++)) || true ;;
                        merged)  echo "    + $config_file (merged)";              ((installed++)) || true ;;
                    esac
                    ;;
                claude)
                    local dst_claude="$TARGET/$config_file"
                    result="$(convert_opencode_example_to_claude_settings "$pack_root/opencode.example.json" "$dst_claude")"
                    case "$result" in
                        created) echo "    + $config_file (created from opencode.example.json)"; ((installed++)) || true ;;
                        exists)  echo "    SKIP $config_file (exists, not auto-merging)"; ((skipped++)) || true ;;
                    esac
                    ;;
                codex)
                    echo "    - $config_file (skipped: TOML config not auto-translated)"
                    ;;
            esac
        fi

        # --- Copy skills ---
        local src_skills="$pack_opencode/skills"
        if [[ -n "$skills_dir" && -d "$src_skills" ]]; then
            local target_skills="$TARGET/$skills_dir"
            mkdir -p "$target_skills"
            for item in "$src_skills"/*/; do
                [[ -d "$item" ]] || continue
                local item_name
                item_name="$(basename "$item")"
                local dst_item="$target_skills/$item_name"

                if [[ -d "$dst_item" ]] && ! $force_this_pack; then
                    echo "    SKIP skills/$item_name (exists, use --force to overwrite)"
                    ((skipped++)) || true
                    continue
                fi
                [[ -d "$dst_item" ]] && rm -rf "$dst_item"
                cp -r "$item" "$dst_item"
                echo "    + skills/$item_name"
                ((installed++)) || true
            done
        fi

        # --- Copy agents ---
        local src_agents="$pack_opencode/agents"
        if [[ -n "$agents_dir" && -d "$src_agents" ]]; then
            local target_agents="$TARGET/$agents_dir"
            mkdir -p "$target_agents"
            for item in "$src_agents"/*/; do
                [[ -d "$item" ]] || continue
                local item_name
                item_name="$(basename "$item")"
                local dst_item="$target_agents/$item_name"

                if [[ -d "$dst_item" ]] && ! $force_this_pack; then
                    echo "    SKIP agents/$item_name (exists, use --force to overwrite)"
                    ((skipped++)) || true
                    continue
                fi
                [[ -d "$dst_item" ]] && rm -rf "$dst_item"
                cp -r "$item" "$dst_item"
                echo "    + agents/$item_name"
                ((installed++)) || true
            done
        fi

        # --- Copy commands ---
        local src_commands="$pack_opencode/commands"
        if [[ -n "$commands_dir" && -d "$src_commands" ]]; then
            local target_commands="$TARGET/$commands_dir"
            mkdir -p "$target_commands"
            for item in "$src_commands"/*; do
                [[ -e "$item" ]] || continue
                local item_name
                item_name="$(basename "$item")"
                local dst_item="$target_commands/$item_name"

                if [[ -e "$dst_item" ]] && ! $force_this_pack; then
                    echo "    SKIP commands/$item_name (exists, use --force to overwrite)"
                    ((skipped++)) || true
                    continue
                fi
                if [[ -d "$item" ]]; then
                    [[ -e "$dst_item" ]] && rm -rf "$dst_item"
                    cp -r "$item" "$dst_item"
                else
                    cp -f "$item" "$dst_item"
                fi
                echo "    + commands/$item_name"
                ((installed++)) || true
            done
        fi

        # --- Copy Claude hooks (if platform is claude and pack has hooks) ---
        if [[ "$platform_name" == "claude" ]]; then
            local src_hooks="$pack_root/.claude/hooks"
            if [[ -d "$src_hooks" ]]; then
                local target_hooks="$TARGET/.claude/hooks"
                mkdir -p "$target_hooks"
                for hook_file in "$src_hooks"/*; do
                    [[ -f "$hook_file" ]] || continue
                    local hook_name
                    hook_name="$(basename "$hook_file")"
                    local dst_hook="$target_hooks/$hook_name"
                    if [[ -f "$dst_hook" ]] && ! $force_this_pack; then
                        echo "    SKIP hooks/$hook_name (exists, use --force to overwrite)"
                        ((skipped++)) || true
                        continue
                    fi
                    cp -f "$hook_file" "$dst_hook"
                    chmod +x "$dst_hook"
                    echo "    + hooks/$hook_name"
                    ((installed++)) || true
                done
                # --- Merge hooks into .claude/settings.json ---
                local claude_settings="$TARGET/.claude/settings.json"
                local hooks_config='{"hooks":{"UserPromptSubmit":[{"hooks":[{"type":"command","command":"bash .claude/hooks/fish-trail-gateway.sh","timeout":5}]}],"PreCompact":[{"hooks":[{"type":"command","command":"bash .claude/hooks/fish-trail-precompact.sh","timeout":5}]}],"PostCompact":[{"hooks":[{"type":"command","command":"bash .claude/hooks/fish-trail-postcompact.sh","timeout":5}]}]}}'

                python3 - "$claude_settings" "$hooks_config" <<'PYEOF'
import json, sys, os

settings_path = sys.argv[1]
hooks_to_add = json.loads(sys.argv[2])

if os.path.isfile(settings_path):
    try:
        with open(settings_path, 'r', encoding='utf-8') as f:
            settings = json.load(f)
    except (json.JSONDecodeError, ValueError):
        settings = {}
else:
    os.makedirs(os.path.dirname(settings_path), exist_ok=True)
    settings = {}

if 'hooks' not in settings:
    settings['hooks'] = {}

for event_name, event_groups in hooks_to_add['hooks'].items():
    if event_name not in settings['hooks']:
        settings['hooks'][event_name] = event_groups
    else:
        # Check if our hook command already exists to avoid duplicates
        existing_commands = set()
        for group in settings['hooks'][event_name]:
            for hook in group.get('hooks', []):
                if hook.get('command'):
                    existing_commands.add(hook['command'])
        
        for group in event_groups:
            for hook in group.get('hooks', []):
                if hook.get('command') and hook['command'] not in existing_commands:
                    settings['hooks'][event_name].append(group)
                    break

with open(settings_path, 'w', encoding='utf-8') as f:
    json.dump(settings, f, indent=2, ensure_ascii=False)
    f.write('\n')
PYEOF
                if [[ $? -eq 0 ]]; then
                    echo "    + .claude/settings.json (hooks merged)"
                    ((installed++)) || true
                fi
            fi
        fi

        # --- Update installed-packs registry ---
        if [[ -n "$target_registry" ]]; then
            update_installed_packs "$target_registry" "$pack_name" "$manifest_file"
            echo "    + $registry_dir/installed-packs.json (registry updated)"
        fi
    done

    if [[ -n "$translation_target" && "$translation_target" != "AGENTS.md" && -f "$TARGET/AGENTS.md" ]]; then
        local dst_translated="$TARGET/$translation_target"
        local translated_result
        translated_result="$(update_translated_instructions "$TARGET/AGENTS.md" "$dst_translated" "$platform_name" true)"
        case "$translated_result" in
            created) echo "    + $translation_target (created)"; ((installed++)) || true ;;
            merged)  echo "    + $translation_target (merged)";  ((installed++)) || true ;;
            updated) echo "    + $translation_target (updated)"; ((installed++)) || true ;;
            exists)  echo "    SKIP $translation_target (managed section exists, use --force to update)"; ((skipped++)) || true ;;
        esac
    fi

    echo ""
    echo "  [$platform_name] Done: $installed installed, $skipped skipped."
    if (( installed > 0 )); then
        local restart_hint
        restart_hint="$(get_restart_hint "$platform_name")"
        if [[ -n "$restart_hint" ]]; then
            echo "$restart_hint"
        fi
    fi
}

install_global_for_platform() {
    local platform_name="$1"
    shift
    local -a packs=("$@")

    local global_skills_dir
    global_skills_dir="$(expand_home_path "$(get_platform_field "$platform_name" "global.skills_dir")")"
    local global_commands_dir
    global_commands_dir="$(expand_home_path "$(get_platform_field "$platform_name" "global.commands_dir")")"
    local global_registry_dir=""

    if [[ -z "$global_skills_dir" ]]; then
        echo "WARN: $platform_name does not support global skill installation. Skipping."
        return
    fi

    global_registry_dir="$(get_platform_registry_dir "$global_skills_dir")"

    # Migrate legacy v0.9.x artifacts in global skills dir
    migrate_legacy_v0_9 "$global_skills_dir" "skills" "" ""

    echo ""
    echo "[$platform_name] Global install -> $global_skills_dir"
    if [[ -n "$global_commands_dir" ]]; then
        echo "  Global commands dir: $global_commands_dir"
    else
        echo "  Global commands dir: <not supported>"
    fi
    echo "  Skills only; skipping AGENTS.md and opencode.json."

    local installed=0
    local skipped=0

    mkdir -p "$global_skills_dir"

    for pack_name in "${packs[@]}"; do
        local pack_root
        if [[ "$pack_name" == community--* && -n "$COMMUNITY_STAGING_DIR" && -d "$COMMUNITY_STAGING_DIR/$pack_name" ]]; then
            pack_root="$COMMUNITY_STAGING_DIR/$pack_name"
        else
            pack_root="$(find_pack_dir "$pack_name")"
        fi
        local pack_opencode="$pack_root/.opencode"
        local manifest_file="$pack_root/pack-manifest.json"
        local src_skills="$pack_opencode/skills"

        if [[ ! -d "$src_skills" ]]; then
            echo "WARN: Pack '$pack_name' has no .opencode/skills directory. Skipping."
            continue
        fi

        echo ""
        echo "  Installing pack globally: $pack_name"
        local force_this_pack=$FORCE

        if ! $force_this_pack; then
            local version_status_raw version_status legacy_key version_lookup_name
            version_status_raw="$(check_pack_version "$global_registry_dir" "$pack_name" "$manifest_file")"
            version_status="${version_status_raw%%$'\n'*}"
            legacy_key=""
            if [[ "$version_status_raw" == *$'\n'legacy:* ]]; then
                legacy_key="${version_status_raw#*$'\n'legacy:}"
            fi
            version_lookup_name="$pack_name"
            if [[ -n "$legacy_key" ]]; then
                version_lookup_name="$legacy_key"
            fi
            case "$version_status" in
                same)
                    local installed_version
                    installed_version="$(read_installed_pack_version "$global_registry_dir" "$version_lookup_name")"
                    echo "  ✓ $pack_name v$installed_version is current. Use -Force/-force to reinstall." >&2
                    ((skipped++)) || true
                    continue
                    ;;
                newer)
                    local installed_version source_version
                    installed_version="$(read_installed_pack_version "$global_registry_dir" "$version_lookup_name")"
                    source_version="$(read_manifest_pack_version "$manifest_file")"
                    echo "  ⬆ Upgrading $pack_name v$installed_version → v$source_version" >&2
                    force_this_pack=true
                    ;;
            esac
        fi

        for item in "$src_skills"/*/; do
            [[ -d "$item" ]] || continue
            local item_name
            item_name="$(basename "$item")"
            local dst_item="$global_skills_dir/$item_name"

            if [[ -d "$dst_item" ]] && ! $force_this_pack; then
                echo "    SKIP skills/$item_name (exists in global dir, use --force to overwrite)"
                ((skipped++)) || true
                continue
            fi
            [[ -d "$dst_item" ]] && rm -rf "$dst_item"
            cp -r "$item" "$dst_item"
            echo "    + skills/$item_name"
            ((installed++)) || true
        done

        # --- Copy commands to global commands dir ---
        local src_commands="$pack_opencode/commands"
        if [[ -n "$global_commands_dir" && -d "$src_commands" ]]; then
            mkdir -p "$global_commands_dir"
            for item in "$src_commands"/*; do
                [[ -e "$item" ]] || continue
                local item_name
                item_name="$(basename "$item")"
                local dst_item="$global_commands_dir/$item_name"

                if [[ -e "$dst_item" ]] && ! $force_this_pack; then
                    echo "    SKIP commands/$item_name (exists in global dir, use --force to overwrite)"
                    ((skipped++)) || true
                    continue
                fi
                if [[ -d "$item" ]]; then
                    [[ -d "$dst_item" ]] && rm -rf "$dst_item"
                    cp -r "$item" "$dst_item"
                else
                    cp -f "$item" "$dst_item"
                fi
                echo "    + commands/$item_name"
                ((installed++)) || true
            done
        fi

        if [[ -n "$global_registry_dir" ]]; then
            update_installed_packs "$global_registry_dir" "$pack_name" "$manifest_file"
            echo "    + $global_registry_dir/installed-packs.json (registry updated)"
        fi
    done

    echo ""
    echo "  [$platform_name] Global done: $installed installed, $skipped skipped."
    if (( installed > 0 )); then
        local restart_hint
        restart_hint="$(get_restart_hint "$platform_name")"
        if [[ -n "$restart_hint" ]]; then
            echo "$restart_hint"
        fi
    fi
}

uninstall_pack() {
    local pack_alias="$1"
    local target_path="$2"
    local pack_name
    local is_community=false
    local manifest_file=""

    if is_community_pack "$pack_alias"; then
        is_community=true
        local _owner _repo _ref
        IFS='|' read -r _owner _repo _ref <<< "$(parse_community_spec "$pack_alias")"
        pack_name="community--${_owner}--${_repo}"
    else
        pack_name="$(resolve_pack "$pack_alias")"
    fi

    if [[ "$is_community" == "false" ]]; then
        local pack_root="$(find_pack_dir "$pack_name")"
        manifest_file="$pack_root/pack-manifest.json"
        if [[ ! -f "$manifest_file" ]]; then
            echo "Error: Pack manifest not found: $manifest_file" >&2
            exit 1
        fi
    fi

    local target_skills_rel target_commands_rel target_agents_rel target_registry_rel
    target_skills_rel="$(get_platform_field "$PLATFORM" "project.skills_dir")"
    target_commands_rel="$(get_platform_field "$PLATFORM" "project.commands_dir")"
    target_agents_rel="$(get_platform_field "$PLATFORM" "project.agents_dir")"
    target_registry_rel="$(get_platform_field "$PLATFORM" "project.registry_dir")"

    local target_skills="" target_commands="" target_agents="" target_registry=""
    [[ -n "$target_skills_rel" ]] && target_skills="$target_path/$target_skills_rel"
    [[ -n "$target_commands_rel" ]] && target_commands="$target_path/$target_commands_rel"
    [[ -n "$target_agents_rel" ]] && target_agents="$target_path/$target_agents_rel"
    [[ -n "$target_registry_rel" ]] && target_registry="$target_path/$target_registry_rel"

    local reg_file=""
    if [[ -n "$target_registry" ]]; then
        reg_file="$target_registry/installed-packs.json"
        if [[ ! -f "$reg_file" ]]; then
            echo "Error: No installed-packs.json found at $reg_file. Nothing to uninstall." >&2
            exit 1
        fi

        local is_installed
        if [[ "$is_community" == "true" ]]; then
            # Community packs: just check registry by pack_name (no legacy names)
            is_installed="$(python3 -c "
import json, sys
with open(sys.argv[1], 'r', encoding='utf-8') as f:
    reg = json.load(f)
print('yes' if sys.argv[2] in (reg.get('packs') or {}) else 'no')
" "$reg_file" "$pack_name")"
        else
            is_installed="$(python3 - "$reg_file" "$manifest_file" "$pack_name" <<'PY'
import json
import sys

reg_file, manifest_file, pack_name = sys.argv[1:4]
with open(reg_file, 'r', encoding='utf-8') as f:
    reg = json.load(f)
packs = reg.get('packs') or {}

if pack_name in packs:
    print('yes')
    sys.exit(0)

with open(manifest_file, 'r', encoding='utf-8') as f:
    manifest = json.load(f)

for legacy in manifest.get('legacy_names', []) or []:
    if legacy in packs:
        print('yes')
        sys.exit(0)

print('no')
PY
)"
        fi
        if [[ "$is_installed" != "yes" ]]; then
            echo "Error: Pack '$pack_alias' ($pack_name) is not installed. Nothing to uninstall." >&2
            exit 1
        fi
    fi

    echo ""
    echo "  Uninstalling pack: $pack_name (alias: $pack_alias)"

    local removed=0

    # Read skills/commands/agents list: community packs use registry, official packs use manifest
    local skills="" commands="" agents_list=""
    if [[ "$is_community" == "true" ]]; then
        # Community packs: read from installed-packs.json registry
        read -r skills commands agents_list <<< "$(python3 -c "
import json, sys
with open(sys.argv[1], 'r', encoding='utf-8') as f:
    reg = json.load(f)
entry = (reg.get('packs') or {}).get(sys.argv[2]) or {}
print(' '.join(entry.get('skills', [])))
print(' '.join(entry.get('commands', [])))
print(' '.join(entry.get('agents', [])))
" "$reg_file" "$pack_name")"
        # Convert space-separated to newline-separated
        skills="${skills// /$'\n'}"
        commands="${commands// /$'\n'}"
        agents_list="${agents_list// /$'\n'}"
    else
        # Official packs: read from pack-manifest.json
        skills="$(python3 -c "
import json, sys
with open(sys.argv[1], 'r', encoding='utf-8') as f:
    m = json.load(f)
for s in m.get('skills', []):
    print(s)
" "$manifest_file")"
        commands="$(python3 -c "
import json, sys
with open(sys.argv[1], 'r', encoding='utf-8') as f:
    m = json.load(f)
for c in m.get('commands', []):
    print(c)
" "$manifest_file")"
        agents_list="$(python3 -c "
import json, sys
with open(sys.argv[1], 'r', encoding='utf-8') as f:
    m = json.load(f)
for a in m.get('agents', []):
    print(a)
" "$manifest_file")"
    fi

    if [[ -n "$target_skills" ]]; then
        while IFS= read -r skill; do
            [[ -n "$skill" ]] || continue
            local skill_dir="$target_skills/$skill"
            if [[ -d "$skill_dir" ]]; then
                rm -rf "$skill_dir"
                echo "    - skills/$skill"
                ((removed++)) || true
            fi
        done <<< "$skills"
    fi

    if [[ -n "$target_commands" ]]; then
        while IFS= read -r cmd; do
            [[ -n "$cmd" ]] || continue
            local cmd_dir="$target_commands/$cmd"
            local cmd_file="$target_commands/$cmd.md"
            if [[ -d "$cmd_dir" ]]; then
                rm -rf "$cmd_dir"
                echo "    - commands/$cmd"
                ((removed++)) || true
            elif [[ -f "$cmd_file" ]]; then
                rm -f "$cmd_file"
                echo "    - commands/$cmd.md"
                ((removed++)) || true
            fi
        done <<< "$commands"
    fi

    if [[ -n "$target_agents" ]]; then
        while IFS= read -r agent; do
            [[ -n "$agent" ]] || continue
            local agent_dir="$target_agents/$agent"
            if [[ -d "$agent_dir" ]]; then
                rm -rf "$agent_dir"
                echo "    - agents/$agent"
                ((removed++)) || true
            fi
        done <<< "$agents_list"
    fi

    local agents_file="$target_path/AGENTS.md"
    if [[ "$is_community" == "true" ]]; then
        # Community packs: no manifest file, pass empty string
        remove_inline_pack_section "$agents_file" "$pack_name" ""
    else
        remove_inline_pack_section "$agents_file" "$pack_name" "$manifest_file"
    fi

    local l1_name=""
    case "$pack_name" in
        opencode-course-skills-pack)       l1_name="course-skills.md" ;;
        repo-deploy-ops-skill-pack)        l1_name="deploy-ops.md" ;;
        petfish-style-skill)               l1_name="petfish-style.md" ;;
        petfish-companion-skill)           l1_name="petfish-companion.md" ;;
        petfish-toolchain-skill)           l1_name="petfish-companion.md" ;;
        anti-sycophancy-calibration-pack)  l1_name="anti-sycophancy.md" ;;
        fish-trail)                        l1_name="fish-trail.md" ;;
        research-skill-pack)               l1_name="research.md" ;;
        fish-reflection-pack)              l1_name="fish-reflection.md" ;;
    esac

    if [[ -n "$l1_name" ]]; then
        local rules_file="$target_path/.opencode/agents-rules/$l1_name"
        if [[ -f "$rules_file" ]]; then
            rm -f "$rules_file"
            echo "    - .opencode/agents-rules/$l1_name"
            ((removed++)) || true
        fi

        if [[ -f "$agents_file" ]]; then
            python3 - "$agents_file" "$l1_name" <<'PY'
import re
import sys

agents_file, l1_name = sys.argv[1:3]
with open(agents_file, 'r', encoding='utf-8') as f:
    content = f.read()

pattern = re.compile(rf"^\|[^\n]*{re.escape(l1_name)}[^\n]*\|\s*\n?", re.MULTILINE)
new_content = pattern.sub('', content)
if new_content != content:
    new_content = re.sub(r'\n{3,}', '\n\n', new_content).rstrip() + '\n'
    with open(agents_file, 'w', encoding='utf-8') as f:
        f.write(new_content)
PY
            echo "    - AGENTS.md (removed rules-file reference for $l1_name)"
        fi
    fi

    if [[ -n "$target_registry" ]]; then
        local config_file_rel dst_oc
        config_file_rel="$(get_platform_field "$PLATFORM" "project.config_file")"
        dst_oc=""
        [[ -n "$config_file_rel" ]] && dst_oc="$target_path/$config_file_rel"

        if [[ "$is_community" != "true" && -f "$pack_root/opencode.example.json" && -n "$dst_oc" && -f "$dst_oc" && -f "$reg_file" ]]; then
            python3 - "$PACKS_DIR" "$reg_file" "$pack_name" "$pack_root/opencode.example.json" "$dst_oc" <<'PY'
import json
import os
import sys

packs_dir, reg_file, pack_name, pack_example, target_config = sys.argv[1:6]

with open(pack_example, 'r', encoding='utf-8') as f:
    pack_cfg = json.load(f)

with open(reg_file, 'r', encoding='utf-8') as f:
    reg = json.load(f)

installed = list((reg.get('packs') or {}).keys())

other_claims = {}
for other in installed:
    if other == pack_name:
        continue
    other_example = os.path.join(packs_dir, other, 'opencode.example.json')
    if not os.path.isfile(other_example):
        continue
    try:
        with open(other_example, 'r', encoding='utf-8') as f:
            other_cfg = json.load(f)
    except Exception:
        continue
    for p1, v1 in (other_cfg or {}).items():
        if isinstance(v1, dict):
            s = other_claims.setdefault(p1, set())
            for p2 in v1.keys():
                s.add(p2)

with open(target_config, 'r', encoding='utf-8') as f:
    dst = json.load(f)

changed = False
for p1, v1 in (pack_cfg or {}).items():
    if not isinstance(v1, dict):
        continue
    if not isinstance(dst.get(p1), dict):
        continue
    claimed = other_claims.get(p1, set())
    for p2 in v1.keys():
        if p2 in claimed:
            continue
        if p2 in dst[p1]:
            del dst[p1][p2]
            changed = True

if changed:
    with open(target_config, 'w', encoding='utf-8') as f:
        json.dump(dst, f, indent=2, ensure_ascii=False)
        f.write('\n')
PY
            echo "    - $config_file_rel (removed unique entries from this pack)"
        fi

    if [[ "$is_community" == "true" ]]; then
        # Community packs: just remove by pack_name, no legacy names
        python3 -c "
import json, sys
reg_file, pack_name = sys.argv[1:3]
with open(reg_file, 'r', encoding='utf-8') as f:
    reg = json.load(f)
packs = reg.get('packs') or {}
if pack_name in packs:
    del packs[pack_name]
    reg['packs'] = packs
    with open(reg_file, 'w', encoding='utf-8') as f:
        json.dump(reg, f, indent=2, ensure_ascii=False)
        f.write(chr(10))
" "$reg_file" "$pack_name"
    else
        python3 - "$reg_file" "$pack_name" "$manifest_file" <<'PY'
import json
import sys

reg_file, pack_name, manifest_file = sys.argv[1:4]

with open(reg_file, 'r', encoding='utf-8') as f:
    reg = json.load(f)

packs = reg.get('packs') or {}
changed = False

if pack_name in packs:
    del packs[pack_name]
    changed = True

with open(manifest_file, 'r', encoding='utf-8') as f:
    manifest = json.load(f)

for legacy in manifest.get('legacy_names', []) or []:
    if legacy in packs:
        del packs[legacy]
        changed = True

if changed:
    reg['packs'] = packs
    with open(reg_file, 'w', encoding='utf-8') as f:
        json.dump(reg, f, indent=2, ensure_ascii=False)
        f.write('\n')
PY
    fi
    echo "    - installed-packs.json (registry updated)"
    ((removed++)) || true
    fi

    echo ""
    echo "  Uninstall complete: $removed items removed."
    local restart_hint
    restart_hint="$(get_restart_hint "$PLATFORM")"
    if [[ -n "$restart_hint" ]]; then
        echo "$restart_hint"
    fi
}

uninstall_global_pack() {
    local pack_alias="$1"
    local pack_name
    local is_community=false
    local manifest_file=""

    if is_community_pack "$pack_alias"; then
        is_community=true
        local _owner _repo _ref
        IFS='|' read -r _owner _repo _ref <<< "$(parse_community_spec "$pack_alias")"
        pack_name="community--${_owner}--${_repo}"
    else
        pack_name="$(resolve_pack "$pack_alias")"
    fi

    if [[ "$is_community" == "false" ]]; then
        local pack_root="$(find_pack_dir "$pack_name")"
        manifest_file="$pack_root/pack-manifest.json"
        if [[ ! -f "$manifest_file" ]]; then
            echo "Error: Pack manifest not found: $manifest_file" >&2
            exit 1
        fi
    fi

    local skills_dir
    skills_dir="$(get_platform_field "$PLATFORM" "global.skills_dir")"
    skills_dir="${skills_dir/#\~/$HOME}"
    local commands_dir
    commands_dir="$(get_platform_field "$PLATFORM" "global.commands_dir")"
    commands_dir="${commands_dir/#\~/$HOME}"

    if [[ -z "$skills_dir" ]]; then
        echo "WARN: $PLATFORM does not support global skill installation. Nothing to uninstall."
        return
    fi

    local target_registry
    target_registry="$(get_platform_registry_dir "$skills_dir")"
    local reg_file="$target_registry/installed-packs.json"
    if [[ ! -f "$reg_file" ]]; then
        echo "Error: No installed-packs.json found. Nothing to uninstall." >&2
        exit 1
    fi

    local is_installed
    if [[ "$is_community" == "true" ]]; then
        # Community packs: just check registry by pack_name (no legacy names)
        is_installed="$(python3 -c "
import json, sys
with open(sys.argv[1], 'r', encoding='utf-8') as f:
    reg = json.load(f)
print('yes' if sys.argv[2] in (reg.get('packs') or {}) else 'no')
" "$reg_file" "$pack_name")"
    else
        is_installed="$(python3 - "$reg_file" "$manifest_file" "$pack_name" <<'PY'
import json
import sys

reg_file, manifest_file, pack_name = sys.argv[1:4]
with open(reg_file, 'r', encoding='utf-8') as f:
    reg = json.load(f)
packs = reg.get('packs') or {}

if pack_name in packs:
    print('yes')
    sys.exit(0)

with open(manifest_file, 'r', encoding='utf-8') as f:
    manifest = json.load(f)

for legacy in manifest.get('legacy_names', []) or []:
    if legacy in packs:
        print('yes')
        sys.exit(0)

print('no')
PY
)"
    fi
    if [[ "$is_installed" != "yes" ]]; then
        echo "Error: Pack '$pack_alias' ($pack_name) is not installed globally. Nothing to uninstall." >&2
        exit 1
    fi

    echo ""
    echo "  Uninstalling pack (global): $pack_name (alias: $pack_alias)"

    local removed=0

    # Read skills/commands list: community packs use registry, official packs use manifest
    local skills="" commands=""
    if [[ "$is_community" == "true" ]]; then
        # Community packs: read from installed-packs.json registry
        read -r skills commands <<< "$(python3 -c "
import json, sys
with open(sys.argv[1], 'r', encoding='utf-8') as f:
    reg = json.load(f)
entry = (reg.get('packs') or {}).get(sys.argv[2]) or {}
print(' '.join(entry.get('skills', [])))
print(' '.join(entry.get('commands', [])))
" "$reg_file" "$pack_name")"
        # Convert space-separated to newline-separated
        skills="${skills// /$'\n'}"
        commands="${commands// /$'\n'}"
    else
        # Official packs: read from pack-manifest.json
        skills="$(python3 -c "
import json, sys
with open(sys.argv[1], 'r', encoding='utf-8') as f:
    m = json.load(f)
for s in m.get('skills', []):
    print(s)
" "$manifest_file")"
        commands="$(python3 -c "
import json, sys
with open(sys.argv[1], 'r', encoding='utf-8') as f:
    m = json.load(f)
for c in m.get('commands', []):
    print(c)
" "$manifest_file")"
    fi

    while IFS= read -r skill; do
        [[ -n "$skill" ]] || continue
        local skill_dir="$skills_dir/$skill"
        if [[ -d "$skill_dir" ]]; then
            rm -rf "$skill_dir"
            echo "    - skills/$skill"
            ((removed++)) || true
        fi
    done <<< "$skills"

    if [[ -n "$commands_dir" ]]; then
        while IFS= read -r cmd; do
            [[ -n "$cmd" ]] || continue
            local cmd_dir="$commands_dir/$cmd"
            local cmd_file="$commands_dir/$cmd.md"
            if [[ -d "$cmd_dir" ]]; then
                rm -rf "$cmd_dir"
                echo "    - commands/$cmd"
                ((removed++)) || true
            elif [[ -f "$cmd_file" ]]; then
                rm -f "$cmd_file"
                echo "    - commands/$cmd.md"
                ((removed++)) || true
            fi
        done <<< "$commands"
    fi

    if [[ "$is_community" == "true" ]]; then
        # Community packs: just remove by pack_name, no legacy names
        python3 -c "
import json, sys
reg_file, pack_name = sys.argv[1:3]
with open(reg_file, 'r', encoding='utf-8') as f:
    reg = json.load(f)
packs = reg.get('packs') or {}
if pack_name in packs:
    del packs[pack_name]
    reg['packs'] = packs
    with open(reg_file, 'w', encoding='utf-8') as f:
        json.dump(reg, f, indent=2, ensure_ascii=False)
        f.write(chr(10))
" "$reg_file" "$pack_name"
    else
        python3 - "$reg_file" "$pack_name" "$manifest_file" <<'PY'
import json
import sys

reg_file, pack_name, manifest_file = sys.argv[1:4]

with open(reg_file, 'r', encoding='utf-8') as f:
    reg = json.load(f)

packs = reg.get('packs') or {}
changed = False

if pack_name in packs:
    del packs[pack_name]
    changed = True

with open(manifest_file, 'r', encoding='utf-8') as f:
    manifest = json.load(f)

for legacy in manifest.get('legacy_names', []) or []:
    if legacy in packs:
        del packs[legacy]
        changed = True

if changed:
    reg['packs'] = packs
    with open(reg_file, 'w', encoding='utf-8') as f:
        json.dump(reg, f, indent=2, ensure_ascii=False)
        f.write('\n')
PY
    fi
    echo "    - installed-packs.json (registry updated)"
    ((removed++)) || true

    echo ""
    echo "  Global uninstall complete: $removed items removed."
}

# --- List mode ---
if $LIST; then
    show_list
    exit 0
fi

if [[ -z "$PACK" ]]; then
    echo "Error: --pack required. Use --list to see available packs." >&2
    exit 1
fi

# --- Uninstall mode ---
if $UNINSTALL; then
    if [[ "$PACK" == "all" ]]; then
        echo "Error: Uninstall does not support --pack all. Specify packs individually: --pack course,deploy" >&2
        exit 1
    fi

    if ! $GLOBAL; then
        TARGET="$(cd "$TARGET" && pwd)"
    fi

    IFS=',' read -ra _UNINSTALL_ITEMS <<< "$PACK"
    for _item in "${_UNINSTALL_ITEMS[@]}"; do
        _item="$(echo "$_item" | xargs)"
        if $GLOBAL; then
            uninstall_global_pack "$_item"
        else
            uninstall_pack "$_item" "$TARGET"
        fi
    done
    exit 0
fi

# --- Resolve packs ---
INSTALLS_INIT=false
if [[ "$PACK" == "all" ]]; then
    mapfile -t PACKS < <(get_all_packs)
else
    IFS=',' read -ra _PACK_ITEMS <<< "$PACK"
    PACKS=()
    for _item in "${_PACK_ITEMS[@]}"; do
        _item="$(echo "$_item" | xargs)"
        if [[ "$_item" == "init" || "$_item" == "project-initializer-skill" ]]; then
            INSTALLS_INIT=true
        fi
        PACKS+=("$(resolve_pack "$_item")")
    done
fi

# For --pack all, resolve_pack() was not called per item, so market metadata must be
# populated here for all non-core packs. Falls back silently if market is unreachable.
if [[ "$PACK" == "all" ]] && ! $OFFLINE; then
    for _all_pack in "${PACKS[@]}"; do
        is_community_pack "$_all_pack" && continue
        is_core_pack_name "$_all_pack" && continue
        [[ -n "${MARKET_META[$_all_pack]+x}" ]] && continue
        _all_mj="$(query_market_index "$_all_pack" 2>/dev/null)" || true
        [[ -n "$_all_mj" ]] && MARKET_META["$_all_pack"]="$_all_mj"
    done
fi

# --- Download market-sourced optional packs from external repos ---
# For each optional pack with market metadata, check if it lives in a repo other
# than the local packs/ directory. If so, download that tarball separately.
if ! $OFFLINE; then
    for _mpack in "${PACKS[@]}"; do
        is_community_pack "$_mpack" && continue
        [[ -z "${MARKET_META[$_mpack]+x}" ]] && continue
        is_core_pack_name "$_mpack" && continue
        # Skip if already present locally
        [[ -d "$PACKS_DIR/core/$_mpack" || -d "$PACKS_DIR/optional/$_mpack" ]] && continue
        download_market_pack "$_mpack" || true
    done
fi

if $INSTALLS_INIT && ! $GLOBAL && ! $TARGET_EXPLICIT && [[ "$TARGET" == "." ]]; then
    GLOBAL=true
    echo "  [info] init pack defaults to global install. Use --target to install locally."
fi

# --- Resolve target ---
if $DETECT; then
    DETECT_TARGET="$(cd "$TARGET" && pwd)"
    if $PLATFORM_EXPLICIT; then
        mapfile -t DETECTED_PLATFORMS < <(detect_all_platforms "$DETECT_TARGET")
        echo "  [detect] Primary platform: $PLATFORM (explicit)"
        echo "  [detect] All detected platforms: ${DETECTED_PLATFORMS[*]}"
    else
        mapfile -t DETECTED_PLATFORMS < <(detect_all_platforms "$DETECT_TARGET")
        PLATFORM="${DETECTED_PLATFORMS[0]}"
        echo "  [detect] Detected primary platform: $PLATFORM"
        if (( ${#DETECTED_PLATFORMS[@]} > 1 )); then
            echo "  [detect] Also detected: ${DETECTED_PLATFORMS[*]:1}"
        fi
    fi
else
    DETECTED_PLATFORMS=()
fi

if ! $GLOBAL; then
    TARGET="$(cd "$TARGET" && pwd)"
fi

declare -a PLATFORMS
mapfile -t PLATFORMS < <(get_platforms_for_selection "$PLATFORM")

# --- Install for selected platform(s) ---
if $GLOBAL; then
    for platform_name in "${PLATFORMS[@]}"; do
        install_global_for_platform "$platform_name" "${PACKS[@]}"
    done
    exit 0
fi

for platform_name in "${PLATFORMS[@]}"; do
    install_for_platform "$platform_name" "${PACKS[@]}"
done

# --- Generate instruction files for secondary detected platforms ---
if (( ${#DETECTED_PLATFORMS[@]} > 0 )) && ! $GLOBAL; then
    generate_secondary_instructions "$TARGET" "$FORCE" "${DETECTED_PLATFORMS[@]}"
fi
