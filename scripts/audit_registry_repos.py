# /// script
# requires-python = ">=3.10"
# ///
"""Scan petfish-market registry entries for repo consolidation audit."""
import json
from pathlib import Path

reg_dir = Path("petfish-market/registry/official")
monorepo = "kylecui/petfish.ai"

print(f"{'Name':40s} {'Repo':40s} {'Ref':15s} {'Path':35s} Consolidate?")
print("-" * 165)

for f in sorted(reg_dir.glob("*.json")):
    data = json.loads(f.read_text(encoding="utf-8"))
    name = data.get("name", "?")
    repo = data.get("repo", "?")
    ref = data.get("ref", "?")
    path = data.get("path", "?")
    needs = "YES" if repo != monorepo else "ok"
    print(f"{name:40s} {repo:40s} {ref:15s} {path:35s} {needs}")
