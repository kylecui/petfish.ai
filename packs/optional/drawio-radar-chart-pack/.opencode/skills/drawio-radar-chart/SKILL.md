---
name: drawio-radar-chart
description: >-
  Generate radar/spider charts as draw.io XML (.drawio) files with precise
  hexagonal geometry, multi-series data polygons, concentric circle grid, and
  PNG export. Use when user asks to "draw a radar chart", "create a spider
  diagram", "generate FDE capability radar", "画雷达图", "能力雷达", or needs
  a multi-axis comparison chart in draw.io format. Do NOT use for bar charts,
  line charts, pie charts, or matplotlib-based visualizations.
license: MIT
compatibility: Requires draw.io desktop CLI for PNG export; Python 3.10+ for coordinate generation script.
metadata:
  author: sisyphus
  version: 1.0.0
---

# drawio-radar-chart

## Role

Generate publication-ready radar/spider charts in draw.io XML format with
precise vertex coordinates, multi-series data overlays, and automated PNG export.

## When to Use

- User requests a radar chart, spider chart, or capability comparison hexagon
- User has multi-dimensional data (3-12 axes) to compare across 2-5 series
- User specifically wants draw.io source files (editable, not matplotlib)
- User wants hexagonal/polygonal radar (not circular polar plot)

## When NOT to Use

- Bar charts, line charts, pie charts → use matplotlib or chart libraries
- Single-series data (no comparison needed) → simple table suffices
- User explicitly wants Python/matplotlib polar plot → use gen_radar.py directly

## Critical Domain Rules

### Rule 1: Edges with sourcePoint/targetPoint DO NOT render in draw.io PNG export

This is the #1 failure mode. draw.io's `--export --format png` silently drops
edges that only have `<mxPoint as="sourcePoint">` and `<mxPoint as="targetPoint">`
geometry. The edges appear in the draw.io editor but vanish in PNG export.

**Fix**: Always create invisible vertex cells (2×2px, fillColor=none, strokeColor=none)
at each polygon vertex, then connect them with edges using `source="vertex_id_1"
target="vertex_id_2"` attributes.

### Rule 2: `polyCoords` semicolons conflict with draw.io style parser

The `shape=polygon;polyCoords=[[x1,y1];[x2,y2];...]` syntax breaks because
`;` is the draw.io style property separator. The parser truncates `polyCoords`
at the first internal `;`, corrupting the polygon shape.

**Fix**: Do NOT use `polyCoords`. Use the invisible-vertex + connected-edge
approach from Rule 1 instead.

### Rule 3: `dashPattern` with spaces breaks style parsing

`dashPattern=8 4` contains a space that the draw.io style parser interprets as
a property boundary, breaking all subsequent style properties (including
`strokeColor`).

**Fix**: Use `dashed=1` without `dashPattern`. The default dash pattern is
sufficient for visual distinction.

### Rule 4: Non-square geometry boxes distort hexagonal shapes

A polygon shape inside a 400×360 (non-square) geometry box will have its
vertices scaled differently in x and y, producing an ellipse-like shape
instead of a hexagon.

**Fix**: Always use square geometry boxes (width = height) for polygon data
overlays. Calculate polyCoords relative to the square box.

### Rule 5: Rendering order matters — largest polygon first

Draw the largest data polygon first (bottom z-order), smallest last (top
z-order). This ensures smaller polygons are not hidden behind larger ones.

## Workflow

1. **Collect data**: axis labels, number of axes (typically 6), data series
   (2-5 series, each with one value per axis, range 0-max_scale)
2. **Calculate coordinates**: use the vertex formula (see @references/coordinate-formula.md)
3. **Generate draw.io XML**: use `scripts/generate_radar.py` with the data
4. **Export PNG**: use draw.io desktop CLI (`--export --format png --scale 2 --border 20`)
5. **Verify visually**: check that all polygons are visible and distinguishable

## Output Contract

The skill must produce:

1. **`.drawio` file** — editable draw.io source with:
   - Concentric circle grid (3 rings: inner/middle/outer)
   - N radial axis lines (dashed, light gray)
   - Axis labels (outside outer ring)
   - Scale numbers (2, 4, 6 or custom)
   - M data polygon outlines (connected edges, colored)
   - Legend box with color swatches
2. **`.png` file** — exported at 2× resolution with 20px border

## Anti-Patterns

- ❌ Using `sourcePoint`/`targetPoint` on edges without source/target vertices
- ❌ Using `polyCoords` with semicolons in style string
- ❌ Using `dashPattern=8 4` (space breaks parsing)
- ❌ Non-square geometry box for polygons
- ❌ Drawing smallest polygon first (gets hidden)
- ❌ Using `startFill=0;endFill=0` (unnecessary, may cause issues)

## Handoff & Boundaries

**This skill owns**: draw.io XML generation for radar charts, coordinate
calculation, PNG export

**This skill does NOT own**: chart type selection, data analysis, matplotlib
charts, general draw.io diagram creation

**Adjacent skills**: `drawio-course-diagrams` (general draw.io diagrams),
`ppt-writer` (slide embedding), `markdown-course-writing` (figure embedding)

## References

- `references/coordinate-formula.md` — vertex calculation formula and examples
- `references/drawio-xml-anatomy.md` — XML structure with annotations
- `references/export-troubleshooting.md` — common export failures and fixes
