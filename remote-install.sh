#!/usr/bin/env bash
#
# 胖鱼 PEtFiSh - Remote installer for AI coding platform skill packs from GitHub.
#
# Usage (curl one-liner):
#   curl -fsSL https://raw.githubusercontent.com/kylecui/petfish.ai/master/remote-install.sh | bash -s -- --pack course
#   curl -fsSL https://raw.githubusercontent.com/kylecui/petfish.ai/master/remote-install.sh | bash -s -- --pack all --platform claude
#   curl -fsSL https://raw.githubusercontent.com/kylecui/petfish.ai/master/remote-install.sh | bash -s -- --pack petfish --platform all
#   curl -fsSL https://raw.githubusercontent.com/kylecui/petfish.ai/master/remote-install.sh | bash -s -- --pack deploy --detect
#
# For private repos, set GITHUB_TOKEN:
#   curl -fsSL -H "Authorization: token $GITHUB_TOKEN" https://raw.githubusercontent.com/kylecui/petfish.ai/master/remote-install.sh | GITHUB_TOKEN=$GITHUB_TOKEN bash -s -- --pack course
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

REPO="kylecui/petfish.ai"
BRANCH="master"
BRANCH_OVERRIDE=false

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
    # Insert replacement at the position of the earliest removed section
    # Adjust first_pos since removals may have shifted text
    # Simpler: just insert at the cleaned position
    text = text.strip()
    # Find insertion point: look for the position in cleaned text
    # Strategy: remove all, then insert at first_pos (clamped)
    first_pos = min(first_pos, len(text))
    text = text[:first_pos].rstrip() + '\n\n' + replacement + '\n\n' + text[first_pos:].lstrip()

# Clean up multiple blank lines
text = re.sub(r'\n{3,}', '\n\n', text).strip() + '\n'
open(dst_file, 'w', encoding='utf-8').write(text)
" "$pack_name" "$wrapped" "$dst_file" "$legacy_names_json"
        echo "updated"
        return
    fi

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
        anti-sycophancy-calibration-pack)  l1_name="anti-sycophancy.md" ;;
        fish-trail)                        l1_name="fish-trail.md" ;;
        research-skill-pack)               l1_name="research.md" ;;
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

    printf '%s\n' "$content" > "$rules_dir/$l1_name"
    echo "    + .opencode/agents-rules/$l1_name" >&2
}

# Install system-prompt-rules plugin file to .opencode/plugin/ (v0.11.0+)
# Only for OpenCode platform when L1 packs are present.
install_plugin_file() {
    local source_root="$1" target_dir="$2"
    local src_plugin="$source_root/lib/plugin/system-prompt-rules.ts"
    [[ -f "$src_plugin" ]] || return 0

    local plugin_dir="$target_dir/.opencode/plugin"
    mkdir -p "$plugin_dir"
    cp "$src_plugin" "$plugin_dir/system-prompt-rules.ts"
    echo "    + .opencode/plugin/system-prompt-rules.ts" >&2
}

# Register plugin tuple in opencode.json (idempotent)
register_plugin_in_config() {
    local config_file="$1"
    [[ -f "$config_file" ]] || return 0

    python3 -c "
import json, sys

config_file = sys.argv[1]
plugin_path = '.opencode/plugin/system-prompt-rules.ts'
plugin_tuple = [plugin_path, {'mode': 'all'}]

with open(config_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

if 'plugin' in data:
    # Check if already registered
    for entry in data['plugin']:
        if isinstance(entry, list) and len(entry) >= 1 and entry[0] == plugin_path:
            sys.exit(0)
    data['plugin'].append(plugin_tuple)
else:
    data['plugin'] = [plugin_tuple]

with open(config_file, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)
    f.write('\n')
print('    + opencode.json (plugin registered)')
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

merge_opencode_json() {
    local src_file="$1" dst_file="$2" force="$3" skills_dir="${4:-.opencode/skills}"

    python3 -c "
import json, os, sys

force = sys.argv[3] == 'true'
skills_dir = sys.argv[4] if len(sys.argv) > 4 else '.opencode/skills'
with open(sys.argv[1], 'r', encoding='utf-8') as f:
    src = json.load(f)

normalized_skills_dir = skills_dir.rstrip('/\\\\') or '.opencode/skills'
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
            printf '%s\n' 'ℹ️  Restart may be needed. Skills might reload dynamically; if not, exit with Ctrl+C and re-launch.'
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
    for key in ('version', 'skills', 'description', 'skill_count', 'command_count', 'agent_count'):
        if key in m:
            entry[key] = m[key]
    if 'skill_count' not in entry and 'skills' in m:
        entry['skill_count'] = len(m['skills'])

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
    [research]="research-skill-pack"
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
)
ALL_PACKS=("opencode-course-skills-pack" "opencode-skill-pack-testcases-usage-docs" "repo-deploy-ops-skill-pack" "petfish-style-skill" "petfish-companion-skill" "opencode-ppt-skills" "project-initializer-skill" "trustskills-governance-pack" "anti-sycophancy-calibration-pack" "fish-trail" "research-skill-pack")

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
    echo "  opencode-course-skills-pack              (aliases: course, fish-course)"
    echo "  opencode-skill-pack-testcases-usage-docs (aliases: testdocs, fish-testdocs)"
    echo "  repo-deploy-ops-skill-pack               (aliases: deploy, fish-deploy)"
    echo "  petfish-style-skill                      (aliases: petfish, fish-style)"
    echo "  petfish-companion-skill                  (aliases: companion, fish-core)"
    echo "  opencode-ppt-skills                      (aliases: ppt, fish-slides)"
    echo "  project-initializer-skill                (aliases: init, fish-init)"
    echo "  trustskills-governance-pack               (alias: trust)"
    echo "  anti-sycophancy-calibration-pack         (aliases: calibrate, fish-calibrate)"
    echo "  fish-trail                               (aliases: context, fish-trail)"
    echo "  research-skill-pack                      (aliases: research, fish-research)"
    echo ""
    exit 0
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
        echo "  [detect] No platform marker found. Falling back to 'universal'. Use --platform to specify explicitly." >&2
        echo "universal"
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

        # --- Merge instructions file (AGENTS.md / CLAUDE.md / etc) ---
        if [[ -n "$instructions_file" && -f "$pack_root/AGENTS.md" ]]; then
            # Tiered AGENTS.md: on opencode, packs with L1 rules files skip inline merge
            local has_l1=false
            if [[ "$platform_name" == "opencode" ]]; then
                case "$pack_name" in
                    opencode-course-skills-pack|repo-deploy-ops-skill-pack|petfish-style-skill|petfish-companion-skill|anti-sycophancy-calibration-pack|fish-trail|research-skill-pack)
                        has_l1=true ;;
                esac
            fi

            if $has_l1; then
                # L1-only: write standalone rules file, skip inline merge
                write_pack_rules_file "$pack_root/AGENTS.md" "$TARGET" "$pack_name"
                # Deliver system-prompt-rules plugin (idempotent, runs for each L1 pack)
                install_plugin_file "$EXTRACT_DIR" "$TARGET"
                register_plugin_in_config "$TARGET/opencode.json"
                # v0.10.x → v0.11.x migration: remove old inline section from AGENTS.md
                remove_inline_pack_section "$TARGET/AGENTS.md" "$pack_name" "$manifest_file"
            else
                # Non-opencode or packs without L1: merge inline as before
                local dst_instructions="$TARGET/$instructions_file"
                local result
                result="$(merge_agents_md "$pack_root/AGENTS.md" "$dst_instructions" "$pack_name" "$force_this_pack" "$manifest_file")"
                case "$result" in
                    created) echo "    + $instructions_file (created)"; ((installed++)) || true ;;
                    merged)  echo "    + $instructions_file (merged)";  ((installed++)) || true ;;
                    updated) echo "    + $instructions_file (updated)"; ((installed++)) || true ;;
                    exists)  echo "    SKIP $instructions_file (pack section exists, use --force to update)"; ((skipped++)) || true ;;
                esac
            fi

            # Antigravity: also create/merge GEMINI.md
            if [[ "$platform_name" == "antigravity" ]]; then
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

        # --- Merge opencode.json (OpenCode only) ---
        if [[ "$platform_name" == "opencode" && -n "$config_file" && -f "$pack_root/opencode.example.json" ]]; then
            local dst_config="$TARGET/$config_file"
            result="$(merge_opencode_json "$pack_root/opencode.example.json" "$dst_config" "$force_this_pack" "$skills_dir")"
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

                    if [[ -e "$dst_item" ]] && ! $force_this_pack; then
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
    done

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

        # --- Copy skills ---
        local src_skills="$pack_opencode/skills"
        if [[ -d "$src_skills" ]]; then
            for item in "$src_skills"/*/; do
                [[ -d "$item" ]] || continue
                local item_name
                item_name="$(basename "$item")"
                local dst_item="$global_skills_dir/$item_name"

                if [[ -d "$dst_item" ]] && ! $force_this_pack; then
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

                if [[ -e "$dst_item" ]] && ! $force_this_pack; then
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
    if (( installed > 0 )); then
        local restart_hint
        restart_hint="$(get_restart_hint "$platform_name")"
        if [[ -n "$restart_hint" ]]; then
            echo "$restart_hint"
        fi
    fi
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

# --- Generate instruction files for secondary detected platforms ---
if (( ${#DETECTED_PLATFORMS[@]} > 0 )) && ! $GLOBAL; then
    generate_secondary_instructions "$TARGET" "$FORCE" "${DETECTED_PLATFORMS[@]}"
fi
