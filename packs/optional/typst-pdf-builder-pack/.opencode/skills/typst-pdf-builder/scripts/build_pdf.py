#!/usr/bin/env python3
"""
Generalized Markdown → Typst → PDF build script.

This script is the reusable core of the typst-pdf-builder skill. It discovers
Markdown chapter files, converts them with pandoc, applies Typst-specific
post-processing, and compiles a PDF with typst.

Setup for a new project:
1. Copy templates/book-template.typ into your project (e.g. handbook-layout/).2. Place Markdown chapters in a content directory using the Ch*_*.md naming convention.
3. Run:
       python scripts/build_pdf.py --root . --title "Book Title" --subtitle "Subtitle"

Usage:
    python build_pdf.py                       # full build, auto-discover project
    python build_pdf.py --ch 0                # single chapter pilot
    python build_pdf.py --ch 0,1,2            # selected chapters
    python build_pdf.py --per-chapter         # build each chapter individually
"""

import argparse
import datetime
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path


# ===== Defaults =====
DEFAULT_TITLE = "Untitled Book"
DEFAULT_SUBTITLE = ""
DEFAULT_EDITION = "教材版"


def _skill_dir() -> Path:
    """Return the directory that contains this skill (scripts/..)."""
    return Path(__file__).resolve().parent.parent


def _is_under_skill_dir(path: Path) -> bool:
    """Return True if path is inside the typst-pdf-builder skill directory."""
    skill = _skill_dir()
    try:
        path.relative_to(skill)
        return True
    except ValueError:
        return False


def discover_project_root() -> Path:
    """Derive project root from the script location (..../.opencode/skills/<name>/scripts)."""
    script_dir = Path(__file__).resolve().parent
    # scripts/ → typst-pdf-builder/ → skills/ → .opencode/ → project root
    candidate = script_dir.parent.parent.parent.parent
    if candidate.exists():
        return candidate
    return Path.cwd()


def discover_content_dir(root: Path) -> Path:
    """Auto-detect the content directory by looking for Ch*_*.md files.

    Segment files (paths containing 'segment' or 'segments') are ignored so that
    the main chapter directory is selected rather than a per-chapter split folder.
    """
    candidates: list[Path] = []
    for md in sorted(root.rglob("Ch*_*.md")):
        if _is_under_skill_dir(md):
            continue
        if "segment" in md.as_posix().lower():
            continue
        if re.match(r"Ch\d+_.*\.md$", md.name):
            candidates.append(md.parent)
    if not candidates:
        raise FileNotFoundError(f"No Ch*_*.md chapter files found under {root}")
    # Prefer the directory that contains the most matching files.
    best = max(set(candidates), key=lambda d: candidates.count(d))
    return best


def discover_output_dir(root: Path) -> Path:
    """Auto-detect or default the PDF output directory."""
    existing = sorted(root.rglob("print-ready"))
    for cand in existing:
        if cand.is_dir() and not _is_under_skill_dir(cand):
            return cand
    return root / "print-ready"


def discover_template_file(root: Path) -> Path:
    """Auto-detect or default the Typst template file (excluding the skill's own template)."""
    for typ in sorted(root.rglob("book-template.typ")):
        if not _is_under_skill_dir(typ):
            return typ
    return root / "handbook-layout" / "book-template.typ"


def discover_chapters(content_dir: Path) -> list[tuple[int, str]]:
    """Return sorted (chapter_number, filename) tuples discovered from content_dir.

    Segment files are ignored and chapter numbers are deduplicated so that only
    one file per chapter is selected.
    """
    files = sorted(content_dir.glob("Ch*_*.md"))
    seen: set[int] = set()
    chapters: list[tuple[int, str]] = []
    for f in files:
        if "segment" in f.name.lower():
            continue
        m = re.match(r"Ch(\d+)_.*\.md$", f.name)
        if m:
            num = int(m.group(1))
            if num not in seen:
                seen.add(num)
                chapters.append((num, f.name))
    return sorted(chapters, key=lambda item: item[0])


def run(cmd: list[str], cwd: str | Path | None = None) -> tuple[int, str]:
    """Run a subprocess command and return (returncode, combined_output)."""
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        cwd=cwd,
        encoding="utf-8",
        timeout=300,
        creationflags=0x08000000,  # CREATE_NO_WINDOW — prevent console handle inheritance on Windows
    )
    output = result.stdout + result.stderr
    return result.returncode, output


def compact_cn_en(text: str) -> str:
    """
    Remove extra spaces between CJK characters and Latin/digits for compact typography.

    Rules:
    - CJK/Latin mixed terms are compact (e.g. AI模型, Token预算).
    - Numbered labels keep their trailing space (e.g. 图0.0 绪论, 表4.1 工具, §0.1 概述).
    - Heading lines (starting with #) are skipped by the caller.
    """
    cjk = r"\u4e00-\u9fff\u3000-\u303f\uff00-\uffef"
    latin = r"a-zA-Z0-9"

    # Protect the space after figure/table/section labels.
    PLACEHOLDER = "\x00"
    text = re.sub(r"([图表§]\d+\.?\d*)\s+", lambda m: m.group(1) + PLACEHOLDER, text)

    # Remove spaces between CJK and Latin/digits in both directions.
    text = re.sub(rf"([{cjk}])\s+([{latin}])", r"\1\2", text)
    text = re.sub(rf"([{latin}])\s+([{cjk}])", r"\1\2", text)

    # Restore protected spaces.
    text = text.replace("\x00", " ")

    return text


def preprocess_md(content: str) -> str:
    """
    Pre-process Markdown before pandoc sees it.

    1. Compact CJK-English spacing (skipping headings and code blocks).
    2. Replace <= / >= with ≤ / ≥ inside code blocks.
    3. Replace < / > with full-width ＜ / ＞ in code blocks and table rows.
    """
    lines = content.split("\n")
    in_code_block = False
    result: list[str] = []

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("```"):
            in_code_block = not in_code_block
            result.append(line)
            continue

        if in_code_block:
            line = line.replace("<=", "≤").replace(">=", "≥")
            line = line.replace("<", "＜").replace(">", "＞")
        elif stripped.startswith("|"):
            line = line.replace("<", "＜").replace(">", "＞")
            line = compact_cn_en(line)
        elif stripped.startswith("#"):
            # Headings are left untouched to preserve "0.1 标题" spacing.
            pass
        elif stripped.startswith(">"):
            line = compact_cn_en(line)
        else:
            line = compact_cn_en(line)

        result.append(line)

    return "\n".join(result)


def convert_chapter(md_path: Path) -> Path:
    """Convert a single Markdown chapter to Typst using pandoc."""
    typ_path = md_path.with_suffix(".typ")

    raw_content = md_path.read_text(encoding="utf-8")
    processed = preprocess_md(raw_content)

    result = subprocess.run(
        [
            "pandoc",
            "-f", "markdown-yaml_metadata_block-raw_html-native_divs-native_spans",
            "-t", "typst",
            "--wrap=none",
        ],
        input=processed,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=120,
        creationflags=0x08000000,  # CREATE_NO_WINDOW
    )

    if result.returncode != 0:
        print(f"  FAIL pandoc conversion: {md_path.name}")
        print(f"     {result.stderr[:500]}")
        sys.exit(1)

    typ_path.write_text(result.stdout, encoding="utf-8")
    print(f"  OK {md_path.name} -> {typ_path.name}")
    return typ_path


def fix_typst_paths(typ_path: Path, ch_num: int = 0) -> None:
    """
    Post-process a pandoc-generated Typst file.

    Fixes applied in order:
    0. Rewrite image paths: diagrams/mN/ → ../../05-visual-assets/diagrams-export/MN/.
    0.5. Adapt table column widths: columns: N → columns: (auto, 1fr, ...).
    1. Convert #horizontalrule to Typst line syntax.
    2. Remove leftover pandoc span tags.
    3. Balance code block fences.
    4. Insert #h(2em) first-line indents after headings/figures/tables.
    5. Replace missing images with gray placeholders.
    6. Merge figure description paragraphs into the caption block.
    7. Restyle table caption lines as centered 9pt FangSong with per-chapter numbering.
    """
    content = typ_path.read_text(encoding="utf-8")
    base_dir = typ_path.parent

    # 0. Rewrite image paths.
    content = re.sub(
        r'image\("(?:\.\./)*diagrams/m(\d+)/',
        r'image("../../05-visual-assets/diagrams-export/M\1/',
        content,
    )

    # 0.5. Table column width adaptation.
    def replace_columns(match: re.Match[str]) -> str:
        n = int(match.group(1))
        if n < 2:
            return match.group(0)
        frs = ", ".join(["1fr"] * (n - 1))
        return f"columns: (auto, {frs})"

    content = re.sub(
        r"columns:\s*(\d+)\s*([,\)])",
        lambda m: replace_columns(m) + m.group(2),
        content,
    )
    content = re.sub(
        r"columns:\s*\((?:[\d.]+%,?\s*)+\)",
        lambda m: f"columns: (auto, {', '.join(['1fr'] * (m.group(0).count('%') - 1))})",
        content,
    )

    # 1. Horizontal rule.
    content = content.replace(
        "#horizontalrule",
        "#v(0.5em)\n#align(center)[#line(length: 30%, stroke: 0.5pt + gray)]\n#v(0.5em)",
    )

    # 2. Remove pandoc span tag residuals.
    content = re.sub(r"<[^>]+>", "", content)

    # 3. Balance code block fences.
    lines = content.split("\n")
    result: list[str] = []
    in_raw = False

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("```"):
            if in_raw:
                lang = stripped[3:].strip()
                if lang:
                    result.append("```")
                    result.append(line)
                    in_raw = True
                else:
                    result.append(line)
                    in_raw = False
            else:
                result.append(line)
                in_raw = True
        else:
            result.append(line)

    if in_raw:
        result.append("```")

    content = "\n".join(result)

    # 4. Insert first-line indents.
    lines = content.split("\n")
    result = []
    in_raw_block = False
    at_para_start = True
    block_depth = 0

    for line in lines:
        stripped = line.strip()

        if stripped.startswith("```"):
            in_raw_block = not in_raw_block
            at_para_start = True
            result.append(line)
            continue

        if in_raw_block:
            result.append(line)
            continue

        if re.match(r'^={1,4}\s', stripped):
            at_para_start = True
            result.append(line)
            continue

        if stripped == "":
            at_para_start = True
            result.append(line)
            continue

        if block_depth > 0:
            block_depth += stripped.count("(") - stripped.count(")")
            block_depth += stripped.count("[") - stripped.count("]")
            if block_depth < 0:
                block_depth = 0
            result.append(line)
            continue

        block_starts = ("#figure", "#table", "#quote", "#align(", "#block(")
        is_block_start = any(stripped.startswith(bs) for bs in block_starts)

        if is_block_start:
            opens = stripped.count("(") + stripped.count("[")
            closes = stripped.count(")") + stripped.count("]")
            block_depth = opens - closes
            at_para_start = True
            result.append(line)
            continue

        if at_para_start:
            at_para_start = False

            if line != line.lstrip():
                result.append(line)
                continue

            typst_prefixes = (
                "#v(", "#line(", "#pagebreak", "#horizontalrule",
                "#metadata", "#outline", "#set ", "#show ",
                "#import", "#let ", "#include", "#context",
                "#colbreak", "#h(2em)",
                "#strong[图", "#strong[表",
                "#figure", "#align(", "#block(", "#table", "#colbreak"
            )
            if any(stripped.startswith(tp) for tp in typst_prefixes):
                result.append(line)
                continue

            if re.match(r'^[-*+]\s', stripped) or re.match(r'^\d+[.)]\s', stripped):
                result.append(line)
                continue

            result.append("#h(2em) " + line)
        else:
            result.append(line)

    content = "\n".join(result)

    # 5. Replace missing images with placeholders.
    def replace_missing_image(match: re.Match[str]) -> str:
        img_path_str = match.group(1)
        img_path = base_dir / img_path_str
        if not img_path.exists():
            alt_text = match.group(2) if match.group(2) else img_path_str
            return (
                f'#align(center)[#block(fill: luma(235), inset: 12pt, radius: 4pt)'
                f'[#text(fill: gray)[图片缺失: {alt_text}]]]'
            )
        return match.group(0)

    content = re.sub(
        r'#figure\(image\("([^"]+)",\s*alt:\s*"([^"]*)"\)',
        replace_missing_image,
        content,
    )

    # 6. Merge figure description paragraphs into the caption block.
    lines = content.split("\n")
    result = []
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        if stripped.startswith("#figure("):
            figure_lines = [line]
            paren_depth = stripped.count("(") - stripped.count(")")
            bracket_depth = stripped.count("[") - stripped.count("]")
            i += 1
            while i < len(lines) and (paren_depth > 0 or bracket_depth > 0):
                figure_lines.append(lines[i])
                s = lines[i].strip()
                paren_depth += s.count("(") - s.count(")")
                bracket_depth += s.count("[") - s.count("]")
                i += 1

            j = i
            while j < len(lines) and lines[j].strip() == "":
                j += 1

            if j < len(lines) and lines[j].strip().startswith("#h(2em)"):
                desc_text = lines[j].strip()[len("#h(2em)"):].strip()
                new_fig_lines = []
                for fl in figure_lines:
                    if fl.strip() == "]":
                        new_fig_lines.append(f"    #linebreak() {desc_text}")
                    new_fig_lines.append(fl)
                result.extend(new_fig_lines)
                i = j + 1
            else:
                result.extend(figure_lines)
        else:
            result.append(line)
            i += 1

    content = "\n".join(result)

    # 7. Table caption restyling with per-chapter numbering.
    content = re.sub(
        r'#strong\[(表)(\d+)\.?\s+([^\]]+)\]',
        lambda m: (
            f'#align(center)[#text(size: 9pt, font: ("Times New Roman", "FangSong"))'
            f'[{m.group(1)}{ch_num}.{m.group(2)}. {m.group(3)}]]'
        ),
        content,
    )

    typ_path.write_text(content, encoding="utf-8")


def generate_title_page(book_title: str, book_subtitle: str, edition: str = DEFAULT_EDITION) -> str:
    """Generate Typst code for the title, copyright, and outline pages."""
    return f'''
// ===== Title page =====
#page(
  margin: (top: 3cm, bottom: 3cm, inside: 3cm, outside: 3cm),
  header: [],
  footer: [],
)[
  #align(center)[
    #v(4cm)
    #text(size: 24pt, font: ("Times New Roman", "SimHei"), weight: "bold")[{book_title}]
    #v(1.5cm)
    #text(size: 14pt, font: ("Times New Roman", "KaiTi"))[{book_subtitle}]
    #v(1fr)
    #text(size: 12pt, font: ("Times New Roman", "SimSun"))[{edition}]
    #v(2cm)
  ]
]

// ===== Copyright page =====
#page(
  margin: (top: 3cm, bottom: 3cm, inside: 3cm, outside: 3cm),
  header: [],
  footer: [],
)[
  #v(6cm)
  #align(center)[
    #text(size: 12pt, font: ("Times New Roman", "SimSun"))[
      Generated by typst-pdf-builder.\\
      Markdown sources and editable diagram files are the project truth.\\
      See references/ for typography and pipeline documentation.
    ]
  ]
]

// ===== Outline page =====
#page(
  margin: (top: 3cm, bottom: 3cm, inside: 3cm, outside: 3cm),
  header: [],
  footer: align(center)[
    #set text(size: 10.5pt, font: ("Times New Roman", "SimSun"))
    #context[#counter(page).display("1")]
  ],
)[
  #text(size: 16pt, font: ("Times New Roman", "SimHei"), weight: "bold")[
    #align(center)[目录]
  ]
  #v(1cm)
  #outline(
    title: none,
    indent: 2em,
    depth: 2,
  )
]

'''


def build_book(
    chapter_nums: list[int] | None = None,
    project_root: Path | None = None,
    content_dir: Path | None = None,
    output_dir: Path | None = None,
    template_file: Path | None = None,
    book_title: str = DEFAULT_TITLE,
    book_subtitle: str = DEFAULT_SUBTITLE,
) -> Path | None:
    """Build the PDF from discovered or selected Markdown chapters."""
    root = project_root or discover_project_root()
    content_dir = content_dir or discover_content_dir(root)
    output_dir = output_dir or discover_output_dir(root)
    template_file = template_file or discover_template_file(root)

    if not content_dir.exists():
        print(f"ERROR content directory not found: {content_dir}")
        sys.exit(1)

    chapters = discover_chapters(content_dir)
    if not chapters:
        print(f"ERROR no Ch*_*.md files found in {content_dir}")
        sys.exit(1)

    print("=" * 60)
    print(f"PDF build: {book_title}")
    print("=" * 60)

    if chapter_nums is not None:
        selected = [(n, f) for n, f in chapters if n in chapter_nums]
    else:
        selected = chapters

    if not selected:
        print(f"ERROR no matching chapters found in {content_dir}")
        sys.exit(1)

    print(f"\nSelected chapters: Ch{','.join(str(n) for n, _ in selected)}")

    # Step 1: Markdown → Typst
    print("\nStep 1/3: Markdown -> Typst (pandoc)")
    typ_files: list[tuple[int, Path]] = []
    for ch_num, md_name in selected:
        md_path = content_dir / md_name
        if not md_path.exists():
            print(f"  SKIP (missing): {md_name}")
            continue
        typ_path = convert_chapter(md_path)
        fix_typst_paths(typ_path, ch_num)
        typ_files.append((ch_num, typ_path))

    # Step 2: Generate book.typ
    print("\nStep 2/3: Generate book.typ")
    book_typ = content_dir / "book.typ"
    lines: list[str] = []
    lines.append("// Auto-generated. Do not edit manually.")
    lines.append(f"// Generated at: {datetime.datetime.now().isoformat()}")
    lines.append("")
    template_rel = os.path.relpath(template_file, content_dir).replace("\\", "/")
    lines.append(f'#import "{template_rel}": book-template')
    lines.append("")
    lines.append("#show: book-template")
    lines.append("")

    if chapter_nums is None:
        lines.append(generate_title_page(book_title, book_subtitle))
        lines.append("// ===== Body =====")
        lines.append("")

    for ch_num, typ_path in typ_files:
        rel_path = typ_path.relative_to(content_dir).as_posix()
        lines.append(f"// ----- Ch{ch_num:02d} -----")
        lines.append(f'#include "{rel_path}"')
        lines.append("")

    book_typ.write_text("\n".join(lines), encoding="utf-8")
    print(f"  OK {book_typ.name} ({len(typ_files)} chapters)")

    # Step 3: Compile PDF
    print("\nStep 3/3: Typst -> PDF")
    output_dir.mkdir(parents=True, exist_ok=True)

    if chapter_nums is not None and len(chapter_nums) == 1:
        pdf_name = f"Ch{chapter_nums[0]:02d}_pilot.pdf"
    else:
        safe_title = re.sub(r'[^\w\-]+', "_", book_title).strip("_")
        pdf_name = f"{safe_title}.pdf"
    pdf_path = output_dir / pdf_name

    rc, out = run(
        [
            "typst", "compile",
            "--root", str(root),
            str(book_typ),
            str(pdf_path),
        ],
        cwd=str(content_dir),
    )

    if rc != 0:
        print("  FAIL Typst compilation:")
        for line in out.split("\n"):
            if line.strip():
                print(f"     {line}")
        return None

    size_mb = pdf_path.stat().st_size / (1024 * 1024)
    print(f"  OK {pdf_name} ({size_mb:.1f} MB)")

    print(f"\n{'=' * 60}")
    print(f"Build complete: {pdf_path}")
    print(f"{'=' * 60}")
    return pdf_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Markdown to PDF build tool via pandoc+Typst")
    parser.add_argument(
        "--root",
        type=Path,
        default=None,
        help="Project root directory (default: derived from script location)",
    )
    parser.add_argument(
        "--content-dir",
        type=Path,
        default=None,
        help="Directory containing Ch*_*.md files (default: auto-detect)",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="Directory for PDF output (default: auto-detect or ROOT/print-ready)",
    )
    parser.add_argument(
        "--template",
        type=Path,
        default=None,
        help="Path to book-template.typ (default: auto-detect)",
    )
    parser.add_argument(
        "--title",
        type=str,
        default=DEFAULT_TITLE,
        help="Book title for the title page",
    )
    parser.add_argument(
        "--subtitle",
        type=str,
        default=DEFAULT_SUBTITLE,
        help="Book subtitle for the title page",
    )
    parser.add_argument(
        "--ch",
        type=str,
        default=None,
        help="Comma-separated chapter numbers to build, e.g. --ch 0 or --ch 0,1,2",
    )
    parser.add_argument(
        "--per-chapter",
        action="store_true",
        help="Build each chapter as a separate PDF and place them in OUTPUT_DIR/per-chapter/",
    )
    args = parser.parse_args()

    root = args.root or discover_project_root()
    content_dir = args.content_dir or discover_content_dir(root)
    output_dir = args.output_dir or discover_output_dir(root)
    template_file = args.template or discover_template_file(root)

    if args.per_chapter:
        chapters = discover_chapters(content_dir)
        chapter_nums = sorted({n for n, _ in chapters})
        per_chapter_dir = output_dir / "per-chapter"
        per_chapter_dir.mkdir(parents=True, exist_ok=True)
        for ch_num in chapter_nums:
            pdf_path = build_book(
                chapter_nums=[ch_num],
                project_root=root,
                content_dir=content_dir,
                output_dir=output_dir,
                template_file=template_file,
                book_title=args.title,
                book_subtitle=args.subtitle,
            )
            if pdf_path and pdf_path.exists():
                target = per_chapter_dir / f"Ch{ch_num:02d}.pdf"
                shutil.move(str(pdf_path), str(target))
                print(f"  Moved to {target}")
    else:
        chapter_nums = None
        if args.ch:
            chapter_nums = [int(x.strip()) for x in args.ch.split(",")]
        build_book(
            chapter_nums=chapter_nums,
            project_root=root,
            content_dir=content_dir,
            output_dir=output_dir,
            template_file=template_file,
            book_title=args.title,
            book_subtitle=args.subtitle,
        )


if __name__ == "__main__":
    main()
    sys.stdout.flush()
    sys.stderr.flush()
    os._exit(0)  # Force exit to skip Python pipe cleanup that can hang on Windows.
