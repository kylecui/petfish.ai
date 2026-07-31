# Export Troubleshooting

## Symptom: Polygons not visible in PNG

### Cause 1: Edges without source/target vertices (MOST COMMON)

**Diagnosis**: Open the .drawio in draw.io desktop editor. If polygons are
visible in the editor but NOT in the exported PNG, the edges likely only have
`sourcePoint`/`targetPoint` geometry.

**Fix**: Replace each edge with:
1. Two invisible vertex cells at the endpoints
2. An edge with `source="v1_id" target="v2_id"`

### Cause 2: `dashPattern` with space

**Diagnosis**: Only dashed polygons are missing; solid ones render fine.

**Fix**: Remove `dashPattern=X Y` from style. Use bare `dashed=1`.

### Cause 3: `polyCoords` semicolons

**Diagnosis**: Polygon shape is wrong (ellipse-like, not hexagonal) or polygon
is invisible.

**Fix**: Do not use `shape=polygon;polyCoords=...`. Use the invisible-vertex +
connected-edge method instead.

### Cause 4: Non-square geometry box

**Diagnosis**: Polygons appear squished or stretched.

**Fix**: Ensure the polygon's `<mxGeometry>` has `width == height`.

## Symptom: Colors not visible

### Cause: `strokeColor` after broken style property

**Diagnosis**: Edges render but with default color (black or invisible),
not the specified hex color.

**Fix**: Check the style string for any property with spaces or semicolons
that could break parsing. Simplify the style to minimum properties.

## Export Command

```powershell
$drawio = "C:\Users\<user>\AppData\Local\Programs\draw.io\draw.io.exe"
& $drawio --export --format png --scale 2 --border 20 --output "output.png" "input.drawio"
```

| Flag | Value | Purpose |
|------|-------|---------|
| `--export` | — | Export mode |
| `--format` | png | Output format |
| `--scale` | 2 | 2× resolution for crisp print |
| `--border` | 20 | Padding around content (px) |
| `--output` | path | Output file path |

## Verification

After export, always verify visually:
1. All N axes visible with labels
2. All M data polygons visible with distinct colors
3. Grid rings visible (dashed, light)
4. Legend present with color swatches
5. No clipping at edges

If any element is missing, check the XML for the style pitfalls listed above.
