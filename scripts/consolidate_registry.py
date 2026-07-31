# /// script
# requires-python = ">=3.10"
# ///
"""Consolidate petfish-market registry entries to point to monorepo."""
import json
from pathlib import Path

MONOREPO = "kylecui/petfish.ai"
REF = "master"  # Will be updated to release tag on publish

# Mapping: registry name → packs/optional/ directory name (None = skip/exception)
CONSOLIDATION_MAP = {
    "fish-reflection-pack": "fish-reflection-pack",
    "judgment-calibration-pack": "judgment-calibration-pack",
    "opencode-course-skills-pack": "opencode-course-skills-pack",
    "opencode-ppt-skills": "opencode-ppt-skills",
    "opencode-skill-pack-testcases-usage-docs": "opencode-skill-pack-testcases-usage-docs",
    "petfish-style-skill": "petfish-style-skill",
    "repo-deploy-ops-skill-pack": "repo-deploy-ops-skill-pack",
    "research-skill-pack": "research-skill-pack",
    "series-style-governor-pack": "series-style-governor-pack",
    "trustskills-governance-pack": "trustskills-governance-pack",
}

reg_dir = Path("petfish-market/registry/official")
updated = 0
skipped = 0

for f in sorted(reg_dir.glob("*.json")):
    data = json.loads(f.read_text(encoding="utf-8"))
    name = data.get("name", "")

    if name not in CONSOLIDATION_MAP:
        print(f"  SKIP  {name:45s} (not in packs/optional/ or already monorepo)")
        skipped += 1
        continue

    pack_path = f"packs/optional/{CONSOLIDATION_MAP[name]}"
    old_repo = data.get("repo", "?")
    old_ref = data.get("ref", "?")

    data["repo"] = MONOREPO
    data["ref"] = REF
    data["path"] = pack_path

    f.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"  DONE  {name:45s} {old_repo}:{old_ref} → {MONOREPO}:{REF} path={pack_path}")
    updated += 1

print(f"\nConsolidated: {updated}, Skipped: {skipped}")
