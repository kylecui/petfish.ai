#!/usr/bin/env bash
#
# 胖鱼 PEtFiSh - Remote installer for AI coding platform skill packs from GitHub.
#
# Usage (curl one-liner):
#   curl -fsSL https://raw.githubusercontent.com/kylecui/SKILL_builder/master/remote-install.sh | bash -s -- --pack course
#   curl -fsSL https://raw.githubusercontent.com/kylecui/SKILL_builder/master/remote-install.sh | bash -s -- --pack all --platform claude
#   curl -fsSL https://raw.githubusercontent.com/kylecui/SKILL_builder/master/remote-install.sh | bash -s -- --pack petfish --platform all
#   curl -fsSL https://raw.githubusercontent.com/kylecui/SKILL_builder/master/remote-install.sh | bash -s -- --pack deploy --detect
#
# For private repos, set GITHUB_TOKEN:
#   curl -fsSL -H "Authorization: token $GITHUB_TOKEN" https://raw.githubusercontent.com/kylecui/SKILL_builder/master/remote-install.sh | GITHUB_TOKEN=$GITHUB_TOKEN bash -s -- --pack course
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

REPO="kylecui/SKILL_builder"
BRANCH="master"
BRANCH_OVERRIDE=false

# --- Merge helpers ---

merge_agents_md() {
    local src_file="$1" dst_file="$2" pack_name="$3" force="$4"
    local begin_marker="<!-- BEGIN pack: $pack_name -->"
    local end_marker="<!-- END pack: $pack_name -->"
    local src_content
    src_content="$(cat "$src_file")"
    local wrapped="${begin_marker}
${src_content}
${end_marker}"

    if [[ ! -f "$dst_file" ]]; then
        printf '%s\n' "$wrapped" > "$dst_file"
        echo "created"
        return
    fi

    local existing
    existing="$(cat "$dst_file")"
    if echo "$existing" | grep -qF "$begin_marker"; then
        if ! $force; then
            echo "exists"
            return
        fi
        python3 -c "
import re, sys
begin = sys.argv[1]
end = sys.argv[2]
replacement = sys.argv[3]
text = open(sys.argv[4], 'r', encoding='utf-8').read()
pattern = re.escape(begin) + r'.*?' + re.escape(end)
result = re.sub(pattern, replacement, text, flags=re.DOTALL)
open(sys.argv[4], 'w', encoding='utf-8').write(result)
" "$begin_marker" "$end_marker" "$wrapped" "$dst_file"
        echo "updated"
        return
    fi

    printf '\n\n%s\n' "$wrapped" >> "$dst_file"
    echo "merged"
}

merge_opencode_json() {
    local src_file="$1" dst_file="$2" force="$3"

    if [[ ! -f "$dst_file" ]]; then
        cp "$src_file" "$dst_file"
        echo "created"
        return
    fi

    python3 -c "
import json, sys

force = sys.argv[3] == 'true'
with open(sys.argv[1], 'r') as f:
    src = json.load(f)
with open(sys.argv[2], 'r') as f:
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
with open(sys.argv[2], 'w') as f:
    json.dump(dst, f, indent=2, ensure_ascii=False)
    f.write('\n')
" "$src_file" "$dst_file" "$force"
    echo "merged"
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

pack_entry = ((registry.get('packs') or {}).get(pack_name) or {})
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
    [context]="context-router-skill"
)
ALL_PACKS=("opencode-course-skills-pack" "opencode-skill-pack-testcases-usage-docs" "repo-deploy-ops-skill-pack" "petfish-style-skill" "petfish-companion-skill" "opencode-ppt-skills" "project-initializer-skill" "trustskills-governance-pack" "anti-sycophancy-calibration-pack" "context-router-skill")

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
        --force)    FORCE=true; shift ;;
        --global)   GLOBAL=true; shift ;;
        --list)     LIST=true; shift ;;
        --repo)     REPO="$2"; shift 2 ;;
        --branch)   BRANCH="$2"; BRANCH_OVERRIDE=true; shift 2 ;;
        -h|--help)
            echo "Usage: curl ... | bash -s -- --pack <name|all> [--target <path>] [--platform <platform>] [--detect] [--force] [--global]"
            echo ""
            echo "胖鱼 PEtFiSh — AI Worker's Companion — Self-adaptive Skill Installer (remote)"
            echo ""
            echo "Options:"
            echo "  --pack <name|all>       Pack to install (course, testdocs, deploy, petfish, companion, ppt, init, trust, or all)"
            echo "  --target <path>         Target project directory (default: ., ignored with --global)"
            echo "  --platform <platform>   Target platform: opencode, claude, codex, cursor, copilot, windsurf, antigravity, universal"
            echo "                          Or group: all, primary, ide, cli"
            echo "  --detect                Auto-detect platform from target project markers"
            echo "  --force                 Overwrite existing skills"
            echo "  --global                Install skills to the global platform skills directory"
            echo "  --list                  List available packs"
            echo "  --repo <owner/repo>     Override GitHub repo (default: $REPO)"
            echo "  --branch <branch>       Override branch (default: $BRANCH)"
            exit 0 ;;
        *) echo "Unknown option: $1" >&2; exit 1 ;;
    esac
done

# --- Auto-detect latest release tag if BRANCH not explicitly set ---
if ! $BRANCH_OVERRIDE; then
    latest_tag=""
    
    # Construct API URL and optional auth header
    api_url="https://api.github.com/repos/$REPO/releases/latest"
    auth_header_api=""
    if [[ -n "${GITHUB_TOKEN:-}" ]]; then
        auth_header_api="Authorization: token $GITHUB_TOKEN"
    fi
    
    # Fetch latest release tag with error suppression
    if [[ -n "$auth_header_api" ]]; then
        latest_tag=$(curl -fsSL -H "$auth_header_api" "$api_url" 2>/dev/null | grep -o '"tag_name"[^,]*' | head -1 | sed 's/"tag_name"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/' 2>/dev/null)
    else
        latest_tag=$(curl -fsSL "$api_url" 2>/dev/null | grep -o '"tag_name"[^,]*' | head -1 | sed 's/"tag_name"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/' 2>/dev/null)
    fi
    
    # Use detected tag if valid, otherwise fall back to master
    if [[ -n "$latest_tag" && "$latest_tag" != "null" ]]; then
        BRANCH="$latest_tag"
    fi
fi

if ! $LIST; then
    echo ""
    echo "  ><(((^>  胖鱼 PEtFiSh"
    echo "  [胖鱼 PEtFiSh] AI Worker's Companion — Self-adaptive Skill Installer (remote)"
    echo "  Initialize -> Auto-install -> Work immediately"
    echo ""
fi

# --- List mode ---
if $LIST; then
    echo ""
    echo "Available packs:"
    echo "------------------------------------------------------------"
    echo "  opencode-course-skills-pack              (alias: course)"
    echo "  opencode-skill-pack-testcases-usage-docs  (alias: testdocs)"
    echo "  repo-deploy-ops-skill-pack               (alias: deploy)"
    echo "  petfish-style-skill                      (alias: petfish)"
    echo "  petfish-companion-skill                  (alias: companion)"
    echo "  opencode-ppt-skills                      (alias: ppt)"
    echo "  project-initializer-skill                (alias: init)"
    echo "  trustskills-governance-pack               (alias: trust)"
    echo "  anti-sycophancy-calibration-pack         (alias: calibrate)"
    echo "  context-router-skill                     (alias: context)"
    echo ""
    exit 0
fi

if $DETECT && $PLATFORM_EXPLICIT; then
    echo "Error: --detect cannot be used together with an explicit --platform value." >&2
    exit 1
fi

if [[ -z "$PACK" ]]; then
    echo "Error: --pack required. Use --list to see available packs." >&2
    echo "Example: curl -fsSL https://raw.githubusercontent.com/$REPO/$BRANCH/remote-install.sh | bash -s -- --pack course" >&2
    exit 1
fi

# --- Resolve pack names ---
resolve_pack() {
    local name="$1"
    if [[ -n "${ALIASES[$name]+x}" ]]; then
        echo "${ALIASES[$name]}"
    else
        for p in "${ALL_PACKS[@]}"; do
            if [[ "$p" == "$name" ]]; then
                echo "$name"
                return
            fi
        done
        echo "Unknown pack: '$name'. Available: course, testdocs, deploy, petfish, companion, ppt, init, trust, all" >&2
        exit 1
    fi
}

INSTALLS_INIT=false
if [[ "$PACK" == "all" ]]; then
    PACKS=("${ALL_PACKS[@]}")
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
if ! $GLOBAL; then
    mkdir -p "$TARGET"
    TARGET="$(cd "$TARGET" && pwd)"
fi

# --- Download tarball ---
TMPDIR="$(mktemp -d)"
trap 'rm -rf "$TMPDIR"' EXIT

TARBALL_URL="https://github.com/$REPO/tarball/$BRANCH"
AUTH_HEADER=""
if [[ -n "${GITHUB_TOKEN:-}" ]]; then
    AUTH_HEADER="Authorization: token $GITHUB_TOKEN"
fi

echo "Downloading $REPO@$BRANCH..."
if [[ -n "$AUTH_HEADER" ]]; then
    curl -fsSL -H "$AUTH_HEADER" "$TARBALL_URL" | tar xz -C "$TMPDIR"
else
    curl -fsSL "$TARBALL_URL" | tar xz -C "$TMPDIR"
fi

# GitHub tarballs extract into <owner>-<repo>-<sha>/
EXTRACT_DIR="$(find "$TMPDIR" -mindepth 1 -maxdepth 1 -type d | head -1)"
if [[ -z "$EXTRACT_DIR" ]]; then
    echo "Error: failed to extract tarball" >&2
    exit 1
fi

PACKS_DIR="$EXTRACT_DIR/packs"
PLATFORMS_JSON="$EXTRACT_DIR/platforms.json"

if [[ ! -f "$PLATFORMS_JSON" ]]; then
    echo "Error: platforms.json not found in downloaded repo" >&2
    exit 1
fi

# --- Platform config helpers (read from platforms.json via python3) ---

get_platform_field() {
    local platform_name="$1"
    local field_path="$2"

    python3 - "$PLATFORMS_JSON" "$platform_name" "$field_path" <<'PY'
import json
import sys

registry_file, platform_name, field_path = sys.argv[1:4]

with open(registry_file, 'r', encoding='utf-8') as f:
    registry = json.load(f)

platforms = registry.get('platforms', {})
if platform_name not in platforms:
    sys.exit(0)

obj = platforms[platform_name]
for key in field_path.split('.'):
    if isinstance(obj, dict) and key in obj:
        obj = obj[key]
    else:
        sys.exit(0)

if obj is None:
    sys.exit(0)

if isinstance(obj, list):
    print(','.join(str(x) for x in obj))
elif isinstance(obj, dict):
    print(json.dumps(obj))
else:
    print(obj)
PY
}

get_all_platform_names() {
    python3 - "$PLATFORMS_JSON" <<'PY'
import json, sys
with open(sys.argv[1], 'r', encoding='utf-8') as f:
    registry = json.load(f)
for name in registry.get('platforms', {}):
    print(name)
PY
}

get_platforms_for_selection() {
    local selection="$1"

    python3 - "$PLATFORMS_JSON" "$selection" <<'PY'
import json, sys

with open(sys.argv[1], 'r', encoding='utf-8') as f:
    registry = json.load(f)

selection = sys.argv[2]
groups = registry.get('platform_groups', {})

if selection in groups:
    for name in groups[selection]:
        print(name)
elif selection in registry.get('platforms', {}):
    print(selection)
else:
    print(f"Error: unknown platform or group '{selection}'", file=sys.stderr)
    sys.exit(1)
PY
}

get_detection_order() {
    python3 - "$PLATFORMS_JSON" <<'PY'
import json, sys
with open(sys.argv[1], 'r', encoding='utf-8') as f:
    registry = json.load(f)
priority = ['opencode', 'claude', 'codex', 'cursor', 'copilot', 'windsurf', 'antigravity']
for name in priority:
    if name in registry.get('platforms', {}):
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
---
"
            ;;
        *)
            return 0
            ;;
    esac

    if [[ -f "$destination_file" ]] && ! $force_overwrite; then
        echo "    SKIP $(basename "$destination_file") (exists, use --force to overwrite)"
        return 0
    fi

    local parent_dir
    parent_dir="$(dirname "$destination_file")"
    [[ -d "$parent_dir" ]] || mkdir -p "$parent_dir"

    printf '%s\n%s\n' "$prefix" "$source_content" > "$destination_file"
    echo "    + $(basename "$destination_file") (translated from AGENTS.md)"
}

# --- Detect platform if requested ---
if $DETECT; then
    DETECT_TARGET="$(cd "$TARGET" && pwd)"
    PLATFORM="$(detect_platform "$DETECT_TARGET")"
    echo "  [detect] Detected platform: $PLATFORM"
fi

# --- Resolve platform list ---
declare -a PLATFORMS
mapfile -t PLATFORMS < <(get_platforms_for_selection "$PLATFORM")

# --- Install function for a given platform (project-level) ---
install_for_platform() {
    local platform_name="$1"
    shift
    local pack_list=("$@")

    local skills_dir commands_dir agents_dir config_file instructions_file rules_dir
    skills_dir="$(get_platform_field "$platform_name" "project.skills_dir")"
    commands_dir="$(get_platform_field "$platform_name" "project.commands_dir")"
    agents_dir="$(get_platform_field "$platform_name" "project.agents_dir")"
    config_file="$(get_platform_field "$platform_name" "project.config_file")"
    instructions_file="$(get_platform_field "$platform_name" "project.instructions_file")"
    rules_dir="$(get_platform_field "$platform_name" "project.rules_dir")"

    if [[ -z "$skills_dir" ]]; then
        echo "  [$platform_name] No project skills_dir configured. Skipping."
        return
    fi

    validate_project_relative_path "$skills_dir" "project.skills_dir"
    [[ -n "$commands_dir" ]] && validate_project_relative_path "$commands_dir" "project.commands_dir"
    [[ -n "$agents_dir" ]] && validate_project_relative_path "$agents_dir" "project.agents_dir"

    local registry_dir
    registry_dir="$(get_platform_registry_dir "$skills_dir")"

    echo ""
    echo "  [$platform_name] Installing to $TARGET..."

    local installed=0
    local skipped=0

    for pack_name in "${pack_list[@]}"; do
        local pack_root="$PACKS_DIR/$pack_name"
        local pack_opencode="$pack_root/.opencode"
        if [[ ! -d "$pack_opencode" ]]; then
            echo "    WARN: Pack '$pack_name' has no .opencode/ directory. Skipping."
            continue
        fi

        echo ""
        echo "    Installing pack: $pack_name"

        local manifest_file="$pack_root/pack-manifest.json"
        local target_registry="$TARGET/$registry_dir"

        if ! $FORCE; then
            local version_status
            version_status="$(check_pack_version "$target_registry" "$pack_name" "$manifest_file")"
            case "$version_status" in
                same)
                    local installed_version
                    installed_version="$(read_installed_pack_version "$target_registry" "$pack_name")"
                    echo "  ✓ $pack_name v$installed_version is current. Use -Force/-force to reinstall." >&2
                    ((skipped++)) || true
                    continue
                    ;;
                newer)
                    local installed_version source_version
                    installed_version="$(read_installed_pack_version "$target_registry" "$pack_name")"
                    source_version="$(read_manifest_pack_version "$manifest_file")"
                    echo "  ⬆ UPDATE: $pack_name v$installed_version → v$source_version (use -Force/--force to upgrade)" >&2
                    ((skipped++)) || true
                    continue
                    ;;
            esac
        fi

        # --- Merge instructions file (AGENTS.md / CLAUDE.md / etc) ---
        if [[ -n "$instructions_file" && -f "$pack_root/AGENTS.md" ]]; then
            local dst_instructions="$TARGET/$instructions_file"
            local result
            result="$(merge_agents_md "$pack_root/AGENTS.md" "$dst_instructions" "$pack_name" "$FORCE")"
            case "$result" in
                created) echo "    + $instructions_file (created)"; ((installed++)) || true ;;
                merged)  echo "    + $instructions_file (merged)";  ((installed++)) || true ;;
                updated) echo "    + $instructions_file (updated)"; ((installed++)) || true ;;
                exists)  echo "    SKIP $instructions_file (pack section exists, use --force to update)"; ((skipped++)) || true ;;
            esac

            # Antigravity: also create/merge GEMINI.md
            if [[ "$platform_name" == "antigravity" ]]; then
                local dst_gemini="$TARGET/GEMINI.md"
                result="$(merge_agents_md "$pack_root/AGENTS.md" "$dst_gemini" "$pack_name" "$FORCE")"
                case "$result" in
                    created) echo "    + GEMINI.md (created)"; ((installed++)) || true ;;
                    merged)  echo "    + GEMINI.md (merged)";  ((installed++)) || true ;;
                    updated) echo "    + GEMINI.md (updated)"; ((installed++)) || true ;;
                    exists)  echo "    SKIP GEMINI.md (pack section exists, use --force to update)"; ((skipped++)) || true ;;
                esac
            fi

            # Instructions translation (AGENTS.md → CLAUDE.md, .mdc, copilot-instructions.md, .windsurfrules)
            local trans_target
            trans_target="$(get_platform_field "$platform_name" "instructions_translation.target")"
            if [[ -n "$trans_target" ]]; then
                update_translated_instructions "$dst_instructions" "$TARGET/$trans_target" "$platform_name" "$FORCE"
            fi
        fi

        # --- Merge opencode.json (OpenCode only) ---
        if [[ "$platform_name" == "opencode" && -n "$config_file" && -f "$pack_root/opencode.example.json" ]]; then
            local dst_config="$TARGET/$config_file"
            result="$(merge_opencode_json "$pack_root/opencode.example.json" "$dst_config" "$FORCE")"
            case "$result" in
                created) echo "    + $config_file (created from example)"; ((installed++)) || true ;;
                merged)  echo "    + $config_file (merged)";              ((installed++)) || true ;;
            esac
        fi

        # --- Update installed-packs registry ---
        update_installed_packs "$target_registry" "$pack_name" "$manifest_file"
        echo "    + $registry_dir/installed-packs.json (registry updated)"

        # --- Copy skills ---
        local src_skills="$pack_opencode/skills"
        if [[ -d "$src_skills" ]]; then
            local target_skills="$TARGET/$skills_dir"
            mkdir -p "$target_skills"
            for item in "$src_skills"/*/; do
                [[ -d "$item" ]] || continue
                local item_name
                item_name="$(basename "$item")"
                local dst_item="$target_skills/$item_name"

                if [[ -d "$dst_item" ]] && ! $FORCE; then
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
        if [[ -n "$agents_dir" ]]; then
            local src_agents="$pack_opencode/agents"
            if [[ -d "$src_agents" ]]; then
                local target_agents="$TARGET/$agents_dir"
                mkdir -p "$target_agents"
                for item in "$src_agents"/*/; do
                    [[ -d "$item" ]] || continue
                    local item_name
                    item_name="$(basename "$item")"
                    local dst_item="$target_agents/$item_name"

                    if [[ -d "$dst_item" ]] && ! $FORCE; then
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
        fi

        # --- Copy commands ---
        if [[ -n "$commands_dir" ]]; then
            local src_commands="$pack_opencode/commands"
            if [[ -d "$src_commands" ]]; then
                local target_commands="$TARGET/$commands_dir"
                mkdir -p "$target_commands"
                for item in "$src_commands"/*; do
                    [[ -e "$item" ]] || continue
                    local item_name
                    item_name="$(basename "$item")"
                    local dst_item="$target_commands/$item_name"

                    if [[ -e "$dst_item" ]] && ! $FORCE; then
                        echo "    SKIP commands/$item_name (exists, use --force to overwrite)"
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
        fi
    done

    echo ""
    echo "  [$platform_name] Done: $installed installed, $skipped skipped."
}

# --- Global install function ---
install_global_for_platform() {
    local platform_name="$1"
    shift
    local pack_list=("$@")

    local global_skills_dir global_commands_dir
    global_skills_dir="$(get_platform_field "$platform_name" "global.skills_dir")"
    global_commands_dir="$(get_platform_field "$platform_name" "global.commands_dir")"

    if [[ -z "$global_skills_dir" ]]; then
        echo "  [$platform_name] No global skills_dir configured. Skipping global install."
        return
    fi

    global_skills_dir="$(expand_home_path "$global_skills_dir")"
    [[ -n "$global_commands_dir" ]] && global_commands_dir="$(expand_home_path "$global_commands_dir")"
    local global_registry_dir
    global_registry_dir="$(get_platform_registry_dir "$global_skills_dir")"

    echo ""
    echo "  [$platform_name] Global install to $global_skills_dir..."
    mkdir -p "$global_skills_dir"

    local installed=0
    local skipped=0

    for pack_name in "${pack_list[@]}"; do
        local pack_opencode="$PACKS_DIR/$pack_name/.opencode"
        local pack_root="$PACKS_DIR/$pack_name"
        local manifest_file="$pack_root/pack-manifest.json"
        if [[ ! -d "$pack_opencode" ]]; then
            echo "    WARN: Pack '$pack_name' has no .opencode/ directory. Skipping."
            continue
        fi

        echo ""
        echo "    Installing pack (global): $pack_name"

        if ! $FORCE; then
            local version_status
            version_status="$(check_pack_version "$global_registry_dir" "$pack_name" "$manifest_file")"
            case "$version_status" in
                same)
                    local installed_version
                    installed_version="$(read_installed_pack_version "$global_registry_dir" "$pack_name")"
                    echo "  ✓ $pack_name v$installed_version is current. Use -Force/-force to reinstall." >&2
                    ((skipped++)) || true
                    continue
                    ;;
                newer)
                    local installed_version source_version
                    installed_version="$(read_installed_pack_version "$global_registry_dir" "$pack_name")"
                    source_version="$(read_manifest_pack_version "$manifest_file")"
                    echo "  ⬆ UPDATE: $pack_name v$installed_version → v$source_version (use -Force/--force to upgrade)" >&2
                    ((skipped++)) || true
                    continue
                    ;;
            esac
        fi

        # --- Copy skills ---
        local src_skills="$pack_opencode/skills"
        if [[ -d "$src_skills" ]]; then
            for item in "$src_skills"/*/; do
                [[ -d "$item" ]] || continue
                local item_name
                item_name="$(basename "$item")"
                local dst_item="$global_skills_dir/$item_name"

                if [[ -d "$dst_item" ]] && ! $FORCE; then
                    echo "    SKIP global skills/$item_name (exists, use --force to overwrite)"
                    ((skipped++)) || true
                    continue
                fi
                [[ -d "$dst_item" ]] && rm -rf "$dst_item"
                cp -r "$item" "$dst_item"
                echo "    + global skills/$item_name -> $global_skills_dir"
                ((installed++)) || true
            done
        fi

        # --- Copy commands ---
        local src_commands="$pack_opencode/commands"
        if [[ -d "$src_commands" && -n "$global_commands_dir" ]]; then
            mkdir -p "$global_commands_dir"
            for item in "$src_commands"/*; do
                [[ -e "$item" ]] || continue
                local item_name
                item_name="$(basename "$item")"
                local dst_item="$global_commands_dir/$item_name"

                if [[ -e "$dst_item" ]] && ! $FORCE; then
                    echo "    SKIP global commands/$item_name (exists, use --force to overwrite)"
                    ((skipped++)) || true
                    continue
                fi
                if [[ -d "$item" ]]; then
                    [[ -d "$dst_item" ]] && rm -rf "$dst_item"
                    cp -r "$item" "$dst_item"
                else
                    cp -f "$item" "$dst_item"
                fi
                echo "    + global commands/$item_name -> $global_commands_dir"
                ((installed++)) || true
            done
        fi

        update_installed_packs "$global_registry_dir" "$pack_name" "$manifest_file"
        echo "    + $global_registry_dir/installed-packs.json (registry updated)"
    done

    echo ""
    echo "  [$platform_name] Global done: $installed installed, $skipped skipped."
}

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
