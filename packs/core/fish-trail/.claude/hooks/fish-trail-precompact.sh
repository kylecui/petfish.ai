#!/usr/bin/env bash
# PEtFiSh fish-trail — PreCompact hook for Claude Code
# Preserves active topic context through session compaction.

FISH_TRAIL_DIR=".petfish/fish-trail"
REGISTRY="$FISH_TRAIL_DIR/topic-registry.json"

if [ ! -f "$REGISTRY" ]; then
    exit 0
fi

# Extract active topic ID and summary for compaction context
python3 - "$REGISTRY" "$FISH_TRAIL_DIR" 2>/dev/null <<'PYEOF'
import json, sys, os

registry_path = sys.argv[1]
base_dir = sys.argv[2]

try:
    with open(registry_path, 'r', encoding='utf-8') as f:
        registry = json.load(f)
except (json.JSONDecodeError, FileNotFoundError):
    sys.exit(0)

active_id = registry.get('active_topic')
if not active_id:
    sys.exit(0)

topic_file = os.path.join(base_dir, 'topics', f'{active_id}.json')
if not os.path.isfile(topic_file):
    print(f"🐟 [pre-compact] Active topic: {active_id} (details unavailable)")
    sys.exit(0)

try:
    with open(topic_file, 'r', encoding='utf-8') as f:
        topic = json.load(f)
except (json.JSONDecodeError, FileNotFoundError):
    print(f"🐟 [pre-compact] Active topic: {active_id} (details unavailable)")
    sys.exit(0)

summary = topic.get('summary', 'No summary')
title = topic.get('title', active_id)
status = topic.get('status', 'unknown')

print(f"🐟 [pre-compact] Active topic: {title} (id: {active_id}, status: {status})")
print(f"   Summary: {summary}")
PYEOF

exit 0
