# drawio-radar-chart

> 所属包: **drawio**

>-

**兼容性:** Requires draw.io desktop CLI for PNG export; Python 3.10+ for coordinate generation script.

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

*... (完整 SKILL.md 中还有 31 行)*
