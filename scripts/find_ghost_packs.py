# /// script
# requires-python = ">=3.10"
# ///
"""Find ghost entries in market index vs monorepo pack directories."""
import json
from pathlib import Path

# Get market index pack names
idx = json.loads(Path("petfish-market/index.json").read_text(encoding="utf-8"))
market_names = [p.get("name", "") for p in idx.get("packs", [])]

# Get monorepo pack directory names
repo_packs = []
for subdir in ("core", "optional"):
    base = Path("packs") / subdir
    if base.exists():
        for d in base.iterdir():
            if (d / "pack-manifest.json").is_file():
                repo_packs.append(d.name)

print("Market index pack names vs repo directories:")
for n in sorted(market_names):
    status = "OK" if n in repo_packs else "*** GHOST (not in repo) ***"
    print(f"  {n:45s} {status}")

print()
print("Repo pack dirs NOT in market index:")
for n in sorted(repo_packs):
    if n not in market_names:
        print(f"  {n}")
