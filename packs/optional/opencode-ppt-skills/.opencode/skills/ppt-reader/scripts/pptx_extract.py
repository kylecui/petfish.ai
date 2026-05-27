# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""Extract structured content from a PPTX file.

Usage:
  uv run scripts/pptx_extract.py input.pptx --out output.json --markdown summary.md
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import zipfile
from pathlib import Path
import posixpath
from typing import Any
from xml.etree import ElementTree as ET

NS = {
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
    "p": "http://schemas.openxmlformats.org/presentationml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
    "rel": "http://schemas.openxmlformats.org/package/2006/relationships",
    "cp": "http://schemas.openxmlformats.org/package/2006/metadata/core-properties",
    "dc": "http://purl.org/dc/elements/1.1/",
    "dcterms": "http://purl.org/dc/terms/",
}

PLACEHOLDER_RE = re.compile(r"\b(lorem|ipsum|todo|tbd|xxxx|xxx|placeholder|your title|sample text|待补充|占位|示例文本)\b", re.I)


def safe_read_xml(zf: zipfile.ZipFile, name: str) -> ET.Element | None:
    try:
        data = zf.read(name)
    except KeyError:
        return None
    try:
        return ET.fromstring(data)
    except ET.ParseError:
        return None


def rels_path_for(part_name: str) -> str:
    p = Path(part_name)
    return str(p.parent / "_rels" / f"{p.name}.rels").replace("\\", "/")


def read_relationships(zf: zipfile.ZipFile, rels_path: str) -> dict[str, dict[str, str]]:
    root = safe_read_xml(zf, rels_path)
    if root is None:
        return {}
    rels: dict[str, dict[str, str]] = {}
    for rel in root.findall("rel:Relationship", NS):
        rid = rel.attrib.get("Id", "")
        if not rid:
            continue
        rels[rid] = {
            "type": rel.attrib.get("Type", ""),
            "target": rel.attrib.get("Target", ""),
            "target_mode": rel.attrib.get("TargetMode", ""),
        }
    return rels


def resolve_target(base_part: str, target: str) -> str:
    if target.startswith("/"):
        return target.lstrip("/")
    base = Path(base_part).parent
    return posixpath.normpath(str((base / target).as_posix()))


def extract_paragraphs(root: ET.Element | None) -> list[str]:
    if root is None:
        return []
    paragraphs: list[str] = []
    for p in root.findall(".//a:p", NS):
        runs = [t.text or "" for t in p.findall(".//a:t", NS)]
        text = "".join(runs).strip()
        if text:
            paragraphs.append(re.sub(r"\s+", " ", text))
    return paragraphs


def extract_alt_text(root: ET.Element | None) -> list[str]:
    if root is None:
        return []
    found: list[str] = []
    for c in root.findall(".//p:cNvPr", NS):
        name = (c.attrib.get("name") or "").strip()
        descr = (c.attrib.get("descr") or "").strip()
        for value in [name, descr]:
            if value and value not in found:
                found.append(value)
    return found


def read_metadata(zf: zipfile.ZipFile) -> dict[str, str]:
    out: dict[str, str] = {}
    core = safe_read_xml(zf, "docProps/core.xml")
    if core is not None:
        fields = {
            "title": "dc:title",
            "subject": "dc:subject",
            "creator": "dc:creator",
            "description": "dc:description",
            "last_modified_by": "cp:lastModifiedBy",
            "created": "dcterms:created",
            "modified": "dcterms:modified",
        }
        for key, xp in fields.items():
            node = core.find(xp, NS)
            if node is not None and node.text:
                out[key] = node.text.strip()
    app = safe_read_xml(zf, "docProps/app.xml")
    if app is not None:
        # app.xml uses a default namespace, so use local-name style by iterating.
        for node in app.iter():
            tag = node.tag.split("}", 1)[-1]
            if tag in {"Application", "Slides", "Company"} and node.text:
                out[tag.lower()] = node.text.strip()
    return out


def slide_order(zf: zipfile.ZipFile) -> list[str]:
    pres = safe_read_xml(zf, "ppt/presentation.xml")
    if pres is None:
        return []
    rels = read_relationships(zf, "ppt/_rels/presentation.xml.rels")
    result: list[str] = []
    for sld_id in pres.findall(".//p:sldId", NS):
        rid = sld_id.attrib.get(f"{{{NS['r']}}}id")
        if not rid or rid not in rels:
            continue
        target = rels[rid]["target"]
        result.append(resolve_target("ppt/presentation.xml", target))
    return result


def collect_external_relationships(zf: zipfile.ZipFile) -> list[dict[str, str]]:
    external: list[dict[str, str]] = []
    for name in zf.namelist():
        if not name.endswith(".rels"):
            continue
        for rid, rel in read_relationships(zf, name).items():
            if rel.get("target_mode") == "External":
                external.append({"rels_file": name, "relationship_id": rid, **rel})
    return external


def extract_comments(zf: zipfile.ZipFile, slide_part: str, rels: dict[str, dict[str, str]]) -> list[str]:
    comments: list[str] = []
    for rel in rels.values():
        if "comments" not in rel.get("type", ""):
            continue
        target = rel.get("target", "")
        if not target or rel.get("target_mode") == "External":
            continue
        comment_part = resolve_target(slide_part, target)
        root = safe_read_xml(zf, comment_part)
        if root is None:
            continue
        texts = extract_paragraphs(root)
        for text in texts:
            if text not in comments:
                comments.append(text)
    return comments


def extract_slide(zf: zipfile.ZipFile, slide_part: str, index: int) -> dict[str, Any]:
    root = safe_read_xml(zf, slide_part)
    paragraphs = extract_paragraphs(root)
    title = paragraphs[0] if paragraphs else ""
    rels = read_relationships(zf, rels_path_for(slide_part))

    media: list[dict[str, str]] = []
    notes: list[str] = []
    for rid, rel in rels.items():
        rtype = rel.get("type", "")
        target = rel.get("target", "")
        if not target:
            continue
        if rel.get("target_mode") == "External":
            continue
        resolved = resolve_target(slide_part, target)
        if "/media/" in resolved or "image" in rtype or "video" in rtype or "audio" in rtype:
            media.append({"relationship_id": rid, "type": rtype, "target": resolved})
        if "notesSlide" in rtype:
            notes_root = safe_read_xml(zf, resolved)
            notes.extend(extract_paragraphs(notes_root))

    issues: list[str] = []
    if not paragraphs and not media:
        issues.append("empty-slide")
    if not title:
        issues.append("missing-title-candidate")
    if any(PLACEHOLDER_RE.search(x) for x in paragraphs):
        issues.append("possible-placeholder-text")

    return {
        "index": index,
        "slide_file": slide_part,
        "title": title,
        "paragraphs": paragraphs,
        "notes": notes,
        "media": media,
        "alt_text": extract_alt_text(root),
        "comments": extract_comments(zf, slide_part, rels),
        "issues": issues,
    }


def make_markdown(data: dict[str, Any]) -> str:
    lines: list[str] = []
    lines.append(f"# PPT读取摘要：{Path(data['file']).name}")
    lines.append("")
    lines.append(f"- 页数：{data['slide_count']}")
    if data.get("metadata"):
        meta = data["metadata"]
        if meta.get("title"):
            lines.append(f"- 文档标题：{meta['title']}")
        if meta.get("creator"):
            lines.append(f"- 创建者：{meta['creator']}")
    if data.get("external_relationships"):
        lines.append(f"- 外部链接/资源：{len(data['external_relationships'])}处")
    if data.get("issues"):
        lines.append(f"- 全局问题：{', '.join(data['issues'])}")
    lines.append("")
    lines.append("## 逐页结构")
    lines.append("")
    lines.append("| 页码 | 标题候选 | 正文段落数 | 备注数 | 媒体数 | 问题 |")
    lines.append("|---|---|---:|---:|---:|---|")
    for slide in data["slides"]:
        title = (slide.get("title") or "").replace("|", "\\|")[:80]
        issues = ", ".join(slide.get("issues") or [])
        lines.append(f"| {slide['index']} | {title} | {len(slide['paragraphs'])} | {len(slide['notes'])} | {len(slide['media'])} | {issues} |")
    lines.append("")
    for slide in data["slides"]:
        lines.append(f"## Slide {slide['index']}：{slide.get('title') or '无标题候选'}")
        lines.append("")
        if slide["paragraphs"]:
            lines.append("### 正文")
            for p in slide["paragraphs"]:
                lines.append(f"- {p}")
        if slide["notes"]:
            lines.append("### Speaker Notes")
            for n in slide["notes"]:
                lines.append(f"- {n}")
        if slide["media"]:
            lines.append("### 媒体")
            for m in slide["media"]:
                lines.append(f"- {m['target']}")
        if slide["alt_text"]:
            lines.append("### Alt Text / Shape Names")
            for a in slide["alt_text"]:
                lines.append(f"- {a}")
        if slide["comments"]:
            lines.append("### Comments")
            for c in slide["comments"]:
                lines.append(f"- {c}")
        if slide["issues"]:
            lines.append("### 机械检查问题")
            for issue in slide["issues"]:
                lines.append(f"- {issue}")
        lines.append("")
    if data.get("external_relationships"):
        lines.append("## 外部链接/资源")
        for rel in data["external_relationships"]:
            lines.append(f"- {rel['rels_file']} {rel['relationship_id']}: {rel['target']}")
    return "\n".join(lines) + "\n"


def extract(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Input file not found: {path}")
    if path.suffix.lower() not in {".pptx", ".pptm"}:
        raise ValueError("Only .pptx and .pptm files are supported by this extractor.")

    with zipfile.ZipFile(path) as zf:
        order = slide_order(zf)
        issues: list[str] = []
        if not order:
            issues.append("no-slides-found-or-invalid-presentation")
        slides = [extract_slide(zf, slide_part, i + 1) for i, slide_part in enumerate(order)]
        if len({s["title"] for s in slides if s["title"]}) < len([s for s in slides if s["title"]]):
            issues.append("duplicate-title-candidates")
        return {
            "file": str(path),
            "slide_count": len(slides),
            "metadata": read_metadata(zf),
            "external_relationships": collect_external_relationships(zf),
            "slides": slides,
            "issues": issues,
        }


def main() -> int:
    parser = argparse.ArgumentParser(description="Extract structured content from a PPTX file.")
    parser.add_argument("input", type=Path, help="Input .pptx or .pptm file")
    parser.add_argument("--out", type=Path, help="Write JSON inventory to this path")
    parser.add_argument("--markdown", type=Path, help="Write Markdown summary to this path")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON to stdout")
    args = parser.parse_args()

    try:
        data = extract(args.input)
    except Exception as exc:  # noqa: BLE001
        print(f"Error: {exc}", file=sys.stderr)
        return 2

    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    if args.markdown:
        args.markdown.parent.mkdir(parents=True, exist_ok=True)
        args.markdown.write_text(make_markdown(data), encoding="utf-8")

    if not args.out and not args.markdown or args.pretty:
        print(json.dumps(data, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
