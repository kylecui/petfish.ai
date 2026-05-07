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

merge_opencode_json() {
    local src_file="$1" dst_file="$2" force="$3" skills_dir="${4:-.opencode/skills}"

    python3 -c "
import json, os, sys

force = sys.argv[3] == 'true'
skills_dir = sys.argv[4] if len(sys.argv) > 4 else '.opencode/skills'
with open(sys.argv[1], 'r', encoding='utf-8') as f:
    src = json.load(f)

normalized_skills_dir = skills_dir.rstrip('/\\') or '.opencode/skills'
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
    for key in ('version', 'skills', 'description'):
        if key in m:
            entry[key] = m[key]

if os.path.isfile(reg_file):
    with open(reg_file, 'r') as f:
        reg = json.load(f)
else:
    reg = {'packs': {}}

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

version = ((reg.get('packs') or {}).get(pack_name) or {}).get('version')
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
    [calibrate]="anti-sycophancy-calibration-pack"
    [context]="fish-trail"
    [fish-init]="project-initializer-skill"
    [fish-core]="petfish-companion-skill"
    [fish-course]="opencode-course-skills-pack"
    [fish-testdocs]="opencode-skill-pack-testcases-usage-docs"
    [fish-deploy]="repo-deploy-ops-skill-pack"
    [fish-style]="petfish-style-skill"
    [fish-slides]="opencode-ppt-skills"
    [fish-calibrate]="anti-sycophancy-calibration-pack"
    [fish-trail]="fish-trail"
)

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

# --- Parse args ---
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
        --force)    FORCE=true; shift ;;
        --list)     LIST=true; shift ;;
        -h|--help)
            echo "Usage: $0 --pack <name|all> [--target <path>] [--platform <opencode|claude|codex|cursor|copilot|windsurf|antigravity|universal|all|primary|ide|cli>] [--detect] [--global] [--force] [--list]"
            echo "胖鱼 PEtFiSh AI Worker's Companion — Self-adaptive Skill Installer"
            echo "Aliases: course, testdocs, deploy, petfish, companion, ppt, init, trust"
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
                printf '%s\n' "$platform_name"
                return
            fi
        done
    done < <(get_detection_order)

    printf '%s\n' "opencode"
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
    if [[ -n "${ALIASES[$name]+x}" ]]; then
        echo "${ALIASES[$name]}"
    elif [[ -d "$PACKS_DIR/$name" ]]; then
        echo "$name"
    else
        echo "Unknown pack: '$name'. Use --list to see available packs." >&2
        exit 1
    fi
}

get_all_packs() {
    local dir
    for dir in "$PACKS_DIR"/*; do
        [[ -d "$dir" ]] || continue
        basename "$dir"
    done | sort
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
    local registry_dir
    registry_dir="$(get_platform_registry_dir "$skills_dir")"
    validate_project_relative_path "$registry_dir" "$platform_name registry_dir"

    echo ""
    echo "[$platform_name] Installing..."

    local installed=0
    local skipped=0

    for pack_name in "${packs[@]}"; do
        local pack_opencode="$PACKS_DIR/$pack_name/.opencode"
        if [[ ! -d "$pack_opencode" ]]; then
            echo "WARN: Pack '$pack_name' has no .opencode/ directory. Skipping."
            continue
        fi

        echo ""
        echo "  Installing pack: $pack_name"

        local pack_root="$PACKS_DIR/$pack_name"
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
            local dst_agents="$TARGET/AGENTS.md"
            local result
            result="$(merge_agents_md "$pack_root/AGENTS.md" "$dst_agents" "$pack_name" "$force_this_pack" "$manifest_file")"
            case "$result" in
                created) echo "    + AGENTS.md (created)"; ((installed++)) || true ;;
                merged)  echo "    + AGENTS.md (merged)";  ((installed++)) || true ;;
                updated) echo "    + AGENTS.md (updated)"; ((installed++)) || true ;;
                exists)  echo "    SKIP AGENTS.md (pack section exists, use --force to update)"; ((skipped++)) || true ;;
            esac

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
        local pack_opencode="$PACKS_DIR/$pack_name/.opencode"
        local pack_root="$PACKS_DIR/$pack_name"
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

# --- List mode ---
if $LIST; then
    show_list
    exit 0
fi

if $DETECT && $PLATFORM_EXPLICIT; then
    echo "Error: --detect cannot be used together with an explicit --platform value." >&2
    exit 1
fi

if [[ -z "$PACK" ]]; then
    echo "Error: --pack required. Use --list to see available packs." >&2
    exit 1
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

if $INSTALLS_INIT && ! $GLOBAL && ! $TARGET_EXPLICIT && [[ "$TARGET" == "." ]]; then
    GLOBAL=true
    echo "  [info] init pack defaults to global install. Use --target to install locally."
fi

# --- Resolve target ---
if $DETECT; then
    DETECT_TARGET="$(cd "$TARGET" && pwd)"
    PLATFORM="$(detect_platform "$DETECT_TARGET")"
    echo "  [detect] Detected platform: $PLATFORM"
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
