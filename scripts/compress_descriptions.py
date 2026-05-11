# /// script
# requires-python = ">=3.10"
# ///
"""
Batch compress SKILL.md frontmatter descriptions.

Compression strategy (proven in course pack pilot - 0% regression):
- Tier 1: Remove filler prefixes ("Use this skill when the user wants/needs/asks to")
- Tier 1b: Remove "Use this skill when" variants
- Tier 2: Tighten trailing filler
- Preserve ALL keywords — no semantic changes

Usage:
    uv run python scripts/compress_descriptions.py --root packs/ --dry-run
    uv run python scripts/compress_descriptions.py --root packs/ --apply
"""

import argparse
import re
import sys
from pathlib import Path


# Filler prefixes to strip (order matters — longest first)
FILLER_PREFIXES = [
    r"Use this skill when the user wants to\s+",
    r"Use this skill when the user needs to\s+",
    r"Use this skill when the user asks to\s+",
    r"Use this skill when the user wants\s+",
    r"Use this skill when the user needs\s+",
    r"Use this skill when the user asks\s+",
    r"Use this skill when the user\s+",
    r"Use this skill to\s+",
    r"Use this skill when\s+",
    r"Use this skill for\s+",
]

# Mid-sentence filler to compress
MID_FILLERS = [
    (r"\bthe user wants to\b", ""),
    (r"\bthe user needs to\b", ""),
    (r"\bthe user asks to\b", ""),
    (r"\bthe user wants\b", ""),
    (r"\bthe user provides or mentions\b", "given"),
]


def extract_description(content: str) -> tuple[str, int, int] | None:
    """Extract description from YAML frontmatter. Returns (desc, start, end) or None."""
    # Match frontmatter
    fm_match = re.match(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
    if not fm_match:
        return None

    fm = fm_match.group(1)

    # Find description field - handle both inline and multiline
    # Pattern 1: description: "quoted string" or description: 'quoted string'
    m = re.search(r'^description:\s*(["\'])(.*?)\1\s*$', fm, re.MULTILINE | re.DOTALL)
    if m:
        return m.group(2), fm_match.start(1) + m.start(2), fm_match.start(1) + m.end(2)

    # Pattern 2: description: >- or description: | (block scalar)
    m = re.search(r"^description:\s*[>|]-?\s*\n((?:[ \t]+.*\n?)*)", fm, re.MULTILINE)
    if m:
        raw = m.group(1)
        # Dedent
        lines = raw.rstrip("\n").split("\n")
        indent = len(lines[0]) - len(lines[0].lstrip()) if lines else 0
        desc = " ".join(line[indent:].strip() for line in lines if line.strip())
        return desc, fm_match.start(1) + m.start(1), fm_match.start(1) + m.end(1)

    # Pattern 3: description: plain text (single line)
    m = re.search(r"^description:\s+(.+)$", fm, re.MULTILINE)
    if m:
        return (
            m.group(1).strip(),
            fm_match.start(1) + m.start(1),
            fm_match.start(1) + m.end(1),
        )

    return None


def compress_description(desc: str) -> str:
    """Apply compression transforms to a description string."""
    original = desc

    # Tier 1: Strip filler prefixes
    for pattern in FILLER_PREFIXES:
        new = re.sub(r"^" + pattern, "", desc, count=1, flags=re.IGNORECASE)
        if new != desc:
            # Capitalize first letter — but not code identifiers (contains _ or starts with known tech terms)
            if new and new[0].islower() and "_" not in new.split()[0]:
                new = new[0].upper() + new[1:]
            desc = new
            break

    # Tier 2: Compress mid-sentence fillers (only if prefix was already removed)
    if desc != original:
        for pattern, replacement in MID_FILLERS:
            desc = re.sub(pattern, replacement, desc, flags=re.IGNORECASE)
        # Clean up double spaces
        desc = re.sub(r"  +", " ", desc)

    return desc.strip()


def process_file(path: Path, apply: bool = False) -> dict | None:
    """Process a single SKILL.md file. Returns change info or None if no change."""
    content = path.read_text(encoding="utf-8")

    result = extract_description(content)
    if not result:
        return None

    desc, _, _ = result
    compressed = compress_description(desc)

    if compressed == desc:
        return None

    old_len = len(desc)
    new_len = len(compressed)
    reduction = (old_len - new_len) / old_len * 100 if old_len > 0 else 0

    change = {
        "file": str(path),
        "skill": path.parent.name,
        "original": desc[:120] + ("..." if len(desc) > 120 else ""),
        "compressed": compressed[:120] + ("..." if len(compressed) > 120 else ""),
        "old_len": old_len,
        "new_len": new_len,
        "reduction_pct": reduction,
    }

    if apply:
        # Replace in file — need to reconstruct the description in the original format
        # Find and replace the description value in the frontmatter
        new_content = replace_description(content, desc, compressed)
        if new_content != content:
            path.write_text(new_content, encoding="utf-8")
            change["applied"] = True
        else:
            change["applied"] = False
            change["error"] = "Could not replace in file"

    return change


def replace_description(content: str, old_desc: str, new_desc: str) -> str:
    """Replace description in SKILL.md content, handling various YAML formats."""

    # Try quoted string replacement
    for q in ['"', "'"]:
        old_pattern = f"description: {q}{old_desc}{q}"
        if old_pattern in content:
            return content.replace(old_pattern, f"description: {q}{new_desc}{q}", 1)

    # Try single-line unquoted
    old_pattern = f"description: {old_desc}"
    if old_pattern in content:
        return content.replace(old_pattern, f"description: {new_desc}", 1)

    # Try block scalar (>- or |) — replace the indented block
    fm_match = re.match(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
    if not fm_match:
        return content

    fm = fm_match.group(1)

    # Find the block scalar description
    m = re.search(r"^(description:\s*[>|]-?\s*\n)((?:[ \t]+.*\n?)*)", fm, re.MULTILINE)
    if m:
        prefix = m.group(1)
        old_block = m.group(2)
        # Detect indent
        first_line = old_block.split("\n")[0]
        indent = len(first_line) - len(first_line.lstrip())
        indent_str = " " * indent

        # Wrap new description to ~80 char lines with proper indent
        words = new_desc.split()
        lines = []
        current = indent_str
        for w in words:
            if len(current) + len(w) + 1 > 80 and current.strip():
                lines.append(current.rstrip())
                current = indent_str + w
            else:
                if current == indent_str:
                    current += w
                else:
                    current += " " + w
        if current.strip():
            lines.append(current.rstrip())

        new_block = "\n".join(lines) + "\n"
        new_fm = fm[: m.start(2)] + new_block + fm[m.end(2) :]
        return content[: fm_match.start(1)] + new_fm + content[fm_match.end(1) :]

    return content


def main():
    parser = argparse.ArgumentParser(description="Compress SKILL.md descriptions")
    parser.add_argument(
        "--root", type=str, default="packs/", help="Root directory to scan"
    )
    parser.add_argument(
        "--apply", action="store_true", help="Apply changes (default: dry-run)"
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Show changes without applying"
    )
    parser.add_argument("--skip-packs", nargs="*", default=[], help="Pack dirs to skip")
    args = parser.parse_args()

    root = Path(args.root)
    if not root.exists():
        print(f"Error: {root} does not exist", file=sys.stderr)
        sys.exit(1)

    apply = args.apply and not args.dry_run

    files = sorted(root.rglob("SKILL.md"))
    print(f"Found {len(files)} SKILL.md files")

    changes = []
    skipped = 0
    errors = 0

    for f in files:
        # Skip specified packs
        if any(skip in str(f) for skip in args.skip_packs):
            skipped += 1
            continue

        try:
            change = process_file(f, apply=apply)
            if change:
                changes.append(change)
        except Exception as e:
            print(f"  ERROR {f}: {e}", file=sys.stderr)
            errors += 1

    # Report
    print(f"\n{'=' * 60}")
    print(
        f"Results: {len(changes)} files would change, {len(files) - len(changes) - skipped} already compact, {skipped} skipped, {errors} errors"
    )
    print(f"{'=' * 60}\n")

    total_old = 0
    total_new = 0

    for c in changes:
        total_old += c["old_len"]
        total_new += c["new_len"]
        status = (
            "✅ APPLIED"
            if c.get("applied")
            else ("❌ FAILED" if c.get("error") else "📋 DRY-RUN")
        )
        print(f"{status} {c['skill']}")
        print(f"  -{c['reduction_pct']:.0f}% ({c['old_len']}→{c['new_len']} chars)")
        print(f"  OLD: {c['original']}")
        print(f"  NEW: {c['compressed']}")
        print()

    if total_old > 0:
        print(
            f"Total: {total_old}→{total_new} chars ({(total_old - total_new) / total_old * 100:.1f}% reduction)"
        )

    if not apply and changes:
        print(f"\nRun with --apply to write changes.")


if __name__ == "__main__":
    main()
