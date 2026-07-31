// A4 textbook排版模板 v2.0
// Based on the AI应用系统架构师教材 pipeline.
// CUSTOMIZATION: edit the two variables below for a new project.

// ===== CUSTOMIZATION =====
// Change these strings to match your book. They are used in the running header.
#let BOOK_TITLE = "Book Title"
#let BOOK_SUBTITLE = "Subtitle"

// The header text combines title and subtitle. Keep the string short enough to fit.
#let HEADER_TEXT = if BOOK_SUBTITLE == "" {
  BOOK_TITLE
} else {
  BOOK_TITLE + " · " + BOOK_SUBTITLE
}

#let book-template(body) = {
  // ===== Page setup =====
  // A4 paper with 3.0cm margins on all sides.
  set page(
    paper: "a4",
    margin: (
      top: 3.0cm,
      bottom: 3.0cm,
      inside: 3.0cm,
      outside: 3.0cm,
    ),
    header: context {
      let page-num = here().page()
      if page-num > 1 [
        #set text(size: 10.5pt, font: ("Times New Roman", "SimSun"))
        #align(center)[#HEADER_TEXT]
      ]
    },
    footer: context {
      let page-num = here().page()
      align(center)[
        #set text(size: 10.5pt, font: ("Times New Roman", "SimSun"))
        #page-num
      ]
    },
  )

  // ===== Base font =====
  // Chinese Songti + Western Times New Roman, 12pt (small 4), Chinese locale.
  set text(
    font: ("Times New Roman", "SimSun"),
    size: 12pt,
    lang: "zh",
    region: "cn",
  )

  // ===== Paragraph format =====
  // Leading 20pt, spacing 24pt (spacing > leading). First-line indent is
  // inserted by build_pdf.py post-processing because Typst's first-line-indent
  // does not apply reliably after custom headings/figures/tables.
  set par(
    leading: 20pt,
    justify: true,
    spacing: 24pt,
  )

  // ===== Headings =====
  // H1 resets the custom chapter counter and the per-chapter image counter.
  // This implements 图X.Y. numbering.
  show heading.where(level: 1): it => {
    counter("chapter").update(c => c + 1)
    counter(figure.where(kind: image)).update(0)
    pagebreak(weak: true)
    v(24pt)
    set text(size: 16pt, font: ("Arial", "SimHei"), weight: "bold")
    set par(leading: 20pt, first-line-indent: 0em, justify: false)
    align(center)[#it]
    v(18pt)
  }

  // H2: 14pt Heiti, left aligned, 24pt before, 6pt after.
  show heading.where(level: 2): it => {
    v(24pt)
    set text(size: 14pt, font: ("Arial", "SimHei"), weight: "bold")
    set par(leading: 20pt, first-line-indent: 0em)
    it
    v(6pt)
  }

  // H3: 13pt Heiti, left aligned, 12pt before, 6pt after.
  show heading.where(level: 3): it => {
    v(12pt)
    set text(size: 13pt, font: ("Arial", "SimHei"), weight: "bold")
    set par(leading: 20pt, first-line-indent: 0em)
    it
    v(6pt)
  }

  // H4: 12pt Heiti, left aligned, 12pt before, 6pt after.
  show heading.where(level: 4): it => {
    v(12pt)
    set text(size: 12pt, font: ("Arial", "SimHei"), weight: "bold")
    set par(leading: 20pt, first-line-indent: 0em)
    it
    v(6pt)
  }

  // ===== Figures / images =====
  // Step 1: strip Typst's default "图 N — body" caption prefix.
  show figure.caption: it => it.body

  // Step 2: custom image rendering with per-chapter numbering.
  show figure.where(kind: image): it => {
    set par(first-line-indent: 0em, leading: 20pt)
    v(6pt)
    align(center)[#it.body]
    if it.caption != none {
      v(2pt)
      set text(size: 9pt, font: ("Times New Roman", "FangSong"))
      context {
        let ch = counter("chapter").get().first() - 1
        let fig = counter(figure.where(kind: image)).get().at(0)
        align(center)[图#ch.#fig. #it.caption]
      }
    }
    v(2pt)
  }

  // ===== Tables: allow page breaks =====
  // Table figures are normally non-breaking; unwrap them so long tables can split.
  show figure.where(kind: table): it => {
    set par(first-line-indent: 0em)
    it.body
  }

  // ===== Code blocks =====
  show raw.where(block: true): it => {
    set par(first-line-indent: 0em, leading: 14pt)
    block(
      fill: luma(245),
      inset: (x: 12pt, y: 8pt),
      width: 100%,
      stroke: 0.5pt + luma(180),
    )[
      #set text(font: ("Consolas",), size: 10pt)
      #it
    ]
    v(6pt)
  }

  show raw.where(block: false): it => {
    box[
      #set text(font: ("Consolas",), size: 11pt)
      #it
    ]
  }

  // ===== Block quotes =====
  show quote: it => {
    block(
      width: 100%,
      inset: (left: 1.5em, right: 0em),
    )[
      #set par(first-line-indent: 0em, leading: 20pt)
      #it
    ]
  }

  // ===== Lists: no first-line indent =====
  show list: it => {
    set par(first-line-indent: 0em)
    it
  }

  show enum: it => {
    set par(first-line-indent: 0em)
    it
  }

  // ===== Math =====
  show math.equation.where(block: true): it => {
    v(6pt)
    align(center)[#it]
    v(6pt)
  }

  // ===== Tables: FangSong + Times New Roman, auto-shrink for wide tables =====
  show table: it => {
    let n = if it.columns == auto { 2 } else { it.columns.len() }
    let sz = if n > 5 { 8pt } else { 10.5pt }
    let ld = if n > 5 { 12pt } else { 16pt }
    set text(font: ("Times New Roman", "FangSong"), size: sz)
    set par(leading: ld, first-line-indent: 0em, spacing: 0pt)
    it
  }

  body
}
