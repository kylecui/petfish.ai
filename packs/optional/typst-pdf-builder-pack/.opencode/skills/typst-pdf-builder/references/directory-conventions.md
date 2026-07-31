# Directory Conventions

The `typst-pdf-builder` pipeline expects a clear separation between source
assets, exported assets, and build outputs. This document explains each
directory and why the layout matters.

---

## Directory Layout

```
project-root/
├── content/                  # Markdown chapter source files
│   └── Ch00_*.md ... Ch09_*.md
├── diagrams-source/          # Editable draw.io diagrams
│   ├── M0/
│   ├── M1/
│   └── ...
├── diagrams-export/          # Exported PNG diagrams used by the PDF
│   ├── M0/
│   ├── M1/
│   └── ...
├── handbook-layout/          # Build scripts and Typst template
│   ├── book-template.typ
│   └── build_pdf.py
└── print-ready/              # Final PDF output
    ├── Book_Title.pdf
    └── per-chapter/
        ├── Ch00.pdf
        └── ...
```

The actual names can vary; `build_pdf.py` auto-detects the content, output,
and template directories by searching the project root.

---

## `diagrams-source/M#/` — Canonical Diagram Source

This is the only place where draw.io diagrams should be edited. Every `.drawio`
file here is the source of truth for a single diagram.

Convention:

- Use module folders `M0/`, `M1/`, ..., `M9/` that match the book's module
  numbering.
- Name files like `M#_NN_short_description.drawio`.
- Do not copy `.drawio` files into the content directory.

---

## `diagrams-export/M#/` — Exported PNGs for the Build

`export_drawio.py` writes PNG exports here, mirroring the `diagrams-source/`
structure. The module folder names are preserved exactly (`M0/`, `M1/`, ...).

`build_pdf.py` reads PNGs from this directory, not from the content directory.

---

## `content/Ch*_*.md` — Markdown Source Chapters

Chapters follow the naming convention `Ch{NN}_{description}.md`. The leading
`ChNN_` prefix is required because `build_pdf.py` and `add_table_captions.py`
auto-discover chapters by globbing this pattern.

Examples:

- `Ch00_导论.md`
- `Ch01_任务层.md`
- `Ch09_综合实战.md`

Inside the Markdown, images are referenced as if they lived next to the
chapter files:

```markdown
![Overview](diagrams/m0/fig0_1_overview.png)
```

---

## `handbook-layout/` — Build Scripts and Template

This directory holds the project-specific copy of `book-template.typ` and the
build scripts. It is usually the working directory from which the user runs
`build_pdf.py`.

When the skill is installed under `.opencode/skills/typst-pdf-builder/`, the
user should copy `templates/book-template.typ` from the skill into this project
directory and customize the title variables at the top.

---

## `print-ready/` — PDF Output

Final PDFs are written here. The full book PDF uses a sanitized version of the
book title. Per-chapter PDFs are placed in the `per-chapter/` subdirectory.

This directory is a build artifact and should not be committed to version
control.

---

## Path Rewrite Rule

Markdown image references use lowercase module folders relative to the content
directory:

```markdown
![Alt text](diagrams/m0/fig0_1_overview.png)
```

During `fix_typst_paths()`, `build_pdf.py` rewrites these paths so that the
compiled PDF loads the exported PNGs from the canonical export directory:

```typst
image("../../05-visual-assets/diagrams-export/M0/fig0_1_overview.png")
```

The rewrite rule is:

```regex
image\("(?:\.\./)*diagrams/m(\d+)/
  ->
image("../../05-visual-assets/diagrams-export/M\1/
```

This design keeps Markdown source paths simple while ensuring the build uses
the exported, versioned PNGs.

---

## Why Not Sync Three Copies?

In earlier versions of the project, diagrams existed in three places:

1. `diagrams-source/M#/` — editable source.
2. `diagrams-export/M#/` — exported PNGs.
3. `content/diagrams/m#/` — a manual copy next to the Markdown.

The third copy was abandoned because:

- It inevitably drifts out of sync with the source.
- It doubles the number of files under version control.
- It makes it unclear whether an image is the latest export.

The current design uses exactly one editable source and one build-time export.
The Markdown references a logical `diagrams/m#/` path that is rewritten at
build time, so authors can keep writing simple relative paths without
maintaining a physical copy.
