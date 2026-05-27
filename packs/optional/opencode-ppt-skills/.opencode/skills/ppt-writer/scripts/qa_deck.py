# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""Run mechanical QA checks on a PPTX deck.

Usage:
  uv run scripts/qa_deck.py output/deck.pptx --expected-slides 10 --out qa.json
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import zipfile
from pathlib import Path
import posixpath
from xml.etree import ElementTree as ET

NS = {
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
    "p": "http://schemas.openxmlformats.org/presentationml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
    "rel": "http://schemas.openxmlformats.org/package/2006/relationships",
}
PLACEHOLDER_RE = re.compile(r"\b(lorem|ipsum|todo|tbd|xxxx|xxx|placeholder|your title|sample text|待补充|占位|示例文本)\b", re.I)


def safe_xml(zf: zipfile.ZipFile, name: str):
    try:
        return ET.fromstring(zf.read(name))
    except Exception:  # noqa: BLE001
        return None


def rels(zf: zipfile.ZipFile, name: str) -> dict[str, dict[str, str]]:
    root = safe_xml(zf, name)
    if root is None:
        return {}
    out = {}
    for rel in root.findall("rel:Relationship", NS):
        rid = rel.attrib.get("Id")
        if rid:
            out[rid] = {"type": rel.attrib.get("Type", ""), "target": rel.attrib.get("Target", ""), "target_mode": rel.attrib.get("TargetMode", "")}
    return out


def resolve(base: str, target: str) -> str:
    if target.startswith("/"):
        return target.lstrip("/")
    return posixpath.normpath(str((Path(base).parent / target).as_posix()))


def slide_order(zf: zipfile.ZipFile) -> list[str]:
    root = safe_xml(zf, "ppt/presentation.xml")
    if root is None:
        return []
    pr = rels(zf, "ppt/_rels/presentation.xml.rels")
    slides = []
    for s in root.findall(".//p:sldId", NS):
        rid = s.attrib.get(f"{{{NS['r']}}}id")
        if rid in pr:
            slides.append(resolve("ppt/presentation.xml", pr[rid]["target"]))
    return slides


def text_of(zf: zipfile.ZipFile, part: str) -> list[str]:
    root = safe_xml(zf, part)
    if root is None:
        return []
    vals = []
    for p in root.findall(".//a:p", NS):
        text = "".join(t.text or "" for t in p.findall(".//a:t", NS)).strip()
        if text:
            vals.append(re.sub(r"\s+", " ", text))
    return vals


def qa(path: Path, expected_slides: int | None = None) -> dict:
    result = {"file": str(path), "passed": True, "checks": [], "slides": []}
    if not path.exists():
        return {"file": str(path), "passed": False, "checks": [{"name": "file-exists", "passed": False, "evidence": "file not found"}]}
    try:
        zf = zipfile.ZipFile(path)
    except zipfile.BadZipFile:
        return {"file": str(path), "passed": False, "checks": [{"name": "valid-zip", "passed": False, "evidence": "not a valid pptx zip"}]}
    with zf:
        slides = slide_order(zf)
        def add_check(name: str, passed: bool, evidence: str):
            result["checks"].append({"name": name, "passed": passed, "evidence": evidence})
            if not passed:
                result["passed"] = False

        add_check("has-slides", bool(slides), f"slide_count={len(slides)}")
        if expected_slides is not None:
            add_check("expected-slide-count", len(slides) == expected_slides, f"expected={expected_slides}, actual={len(slides)}")
        all_names = set(zf.namelist())
        external = []
        missing_targets = []
        for name in all_names:
            if not name.endswith(".rels"):
                continue
            base = name.replace("/_rels/", "/").removesuffix(".rels")
            for rid, rel in rels(zf, name).items():
                if rel["target_mode"] == "External":
                    external.append({"rels_file": name, "relationship_id": rid, "target": rel["target"]})
                elif rel["target"] and not rel["target"].startswith("#"):
                    target = resolve(base, rel["target"])
                    if not target.startswith("../") and target not in all_names and not target.startswith("ppt/slideLayouts"):
                        # Some layout/theme targets are intentionally relative outside this simple check.
                        if target.startswith("ppt/") or target.startswith("docProps/"):
                            missing_targets.append({"rels_file": name, "relationship_id": rid, "target": target})
        add_check("no-external-relationships", len(external) == 0, f"external_count={len(external)}")
        if missing_targets:
            add_check("no-missing-relationship-targets", False, f"missing_count={len(missing_targets)}")
        else:
            add_check("no-missing-relationship-targets", True, "missing_count=0")

        placeholder_hits = []
        empty_slides = []
        for i, part in enumerate(slides, 1):
            texts = text_of(zf, part)
            joined = "\n".join(texts)
            hits = PLACEHOLDER_RE.findall(joined)
            if hits:
                placeholder_hits.append({"slide": i, "hits": sorted(set(h.lower() for h in hits))})
            if not joined.strip():
                empty_slides.append(i)
            result["slides"].append({"index": i, "part": part, "text_count": len(texts), "title": texts[0] if texts else ""})
        add_check("no-placeholder-text", len(placeholder_hits) == 0, json.dumps(placeholder_hits, ensure_ascii=False))
        add_check("no-empty-slides", len(empty_slides) == 0, f"empty_slides={empty_slides}")
        result["external_relationships"] = external
        result["missing_targets"] = missing_targets
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Mechanical QA checks for PPTX decks.")
    parser.add_argument("input", type=Path, help="Input .pptx")
    parser.add_argument("--expected-slides", type=int, help="Expected number of slides")
    parser.add_argument("--out", type=Path, help="Output JSON QA report")
    args = parser.parse_args()
    result = qa(args.input, args.expected_slides)
    text = json.dumps(result, ensure_ascii=False, indent=2)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text, encoding="utf-8")
    print(text)
    return 0 if result.get("passed") else 1


if __name__ == "__main__":
    raise SystemExit(main())
