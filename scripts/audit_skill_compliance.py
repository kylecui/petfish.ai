# /// script
# requires-python = ">=3.10"
# ///
"""Audit all SKILL.md files for agentskills.io compliance."""
import re
from pathlib import Path

root = Path("packs")
results = []
for skill_md in sorted(root.rglob("SKILL.md")):
    content = skill_md.read_text(encoding="utf-8")
    fm_match = re.match(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
    rel = str(skill_md.relative_to(root))

    if not fm_match:
        results.append({"file": rel, "issues": ["NO_FRONTMATTER"]})
        continue

    fm = fm_match.group(1)
    issues = []

    # Check name
    name_match = re.search(r"^name:\s*(.+)$", fm, re.MULTILINE)
    if not name_match:
        issues.append("MISSING_NAME")
    else:
        name = name_match.group(1).strip().strip("\"'")
        if not re.match(r"^[a-z0-9]+(-[a-z0-9]+)*$", name):
            issues.append(f"NAME_NOT_KEBAB: {name}")

    # Check description (handle YAML folded/block scalars)
    desc_match = re.search(r"^description:\s*(.+?)(?=\n[a-zA-Z_-]+:|\Z)", fm, re.MULTILINE | re.DOTALL)
    if not desc_match:
        issues.append("MISSING_DESCRIPTION")
    else:
        desc_raw = desc_match.group(1).strip()
        # Clean YAML folded scalar
        desc_clean = re.sub(r"\s+", " ", desc_raw).strip().strip("\"'")
        if len(desc_clean) < 20:
            issues.append(f"DESC_TOO_SHORT: {len(desc_clean)}")
        if len(desc_clean) > 500:
            issues.append(f"DESC_TOO_LONG: {len(desc_clean)}")
        if not desc_clean:
            issues.append("DESC_EMPTY")

    results.append({"file": rel, "issues": issues, "ok": len(issues) == 0})

ok = [r for r in results if r.get("ok")]
bad = [r for r in results if not r.get("ok")]

print(f"Total SKILL.md files: {len(results)}")
print(f"Compliant: {len(ok)}")
print(f"Non-compliant: {len(bad)}")
print()
if bad:
    print("NON-COMPLIANT FILES:")
    for r in bad:
        print(f"  {r['file']}")
        for issue in r["issues"]:
            print(f"    -> {issue}")
        print()
else:
    print("All skills are agentskills.io compliant!")
