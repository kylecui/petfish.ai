# draw.io XML Anatomy for Radar Charts

## Overall Structure

```xml
<mxGraphModel dx="1400" dy="1100" grid="0" page="0"
  pageWidth="1200" pageHeight="1050">
  <root>
    <mxCell id="0" />
    <mxCell id="1" parent="0" />
    <!-- All cells go here, parent="1" -->
  </root>
</mxGraphModel>
```

**Important**: `page="0"` means no page boundary restriction.
Set `pageWidth`/`pageHeight` larger than your content area.

## Cell Types

### Vertex (shapes, text, images)

```xml
<mxCell id="unique_id" value="text" style="..." vertex="1" parent="1">
  <mxGeometry x="100" y="200" width="50" height="50" as="geometry" />
</mxCell>
```

### Edge (lines connecting vertices) — BULLETPROOF METHOD

```xml
<mxCell id="edge_id" value="" style="endArrow=none;strokeColor=#3b82f6;strokeWidth=3;"
  edge="1" parent="1"
  source="source_vertex_id" target="target_vertex_id">
  <mxGeometry relative="1" as="geometry" />
</mxCell>
```

**CRITICAL**: `source` and `target` must reference existing vertex cell IDs.
Edges without `source`/`target` (only sourcePoint/targetPoint) may not render
in PNG export.

### Edge with sourcePoint only (UNRELIABLE — DO NOT USE for data polygons)

```xml
<!-- ❌ This may NOT render in PNG export -->
<mxCell id="edge_id" style="..." edge="1" parent="1">
  <mxGeometry relative="1" as="geometry">
    <mxPoint x="100" y="200" as="sourcePoint" />
    <mxPoint x="300" y="400" as="targetPoint" />
  </mxGeometry>
</mxCell>
```

## Grid Circle (Ellipse)

```xml
<mxCell id="ring6" value=""
  style="ellipse;fillColor=none;strokeColor=#d8e4f2;strokeWidth=1;dashed=1;"
  vertex="1" parent="1">
  <mxGeometry x="190" y="160" width="820" height="820" as="geometry" />
</mxCell>
```

- x, y = top-left corner = (cx - r, cy - r)
- width = height = 2 × r (must be square for circle)

## Invisible Vertex (anchor point for polygon edges)

```xml
<mxCell id="L1_v0" value=""
  style="ellipse;fillColor=none;strokeColor=none;"
  vertex="1" parent="1">
  <mxGeometry x="599" y="364" width="2" height="2" as="geometry" />
</mxCell>
```

- 2×2px, no fill, no stroke — invisible in output
- x = vertex_x - 1, y = vertex_y - 1 (center the 2px dot on the exact point)
- Serves as connection anchor for polygon edges

## Polygon Edge (connecting two invisible vertices)

```xml
<mxCell id="L1_e0" value=""
  style="endArrow=none;strokeColor=#3b82f6;strokeWidth=3;"
  edge="1" parent="1"
  source="L1_v0" target="L1_v1">
  <mxGeometry relative="1" as="geometry" />
</mxCell>
```

For dashed lines, add `dashed=1;` (NOT `dashPattern=8 4` — space breaks parsing).

## Text Label

```xml
<mxCell id="lbl_模型认知" value="模型认知"
  style="text;align=center;fontFamily=FangSong;fontSize=12;fontStyle=1;fontColor=#1A3C5E;"
  vertex="1" parent="1">
  <mxGeometry x="540" y="117" width="120" height="28" as="geometry" />
</mxCell>
```

## Style String Pitfalls

| Style fragment | Works? | Issue |
|---------------|--------|-------|
| `strokeColor=#3b82f6` | ✅ | — |
| `strokeWidth=3` | ✅ | — |
| `dashed=1` | ✅ | Default dash pattern |
| `dashPattern=8 4` | ❌ | Space breaks parser, drops subsequent props |
| `polyCoords=[[0.5,0.1];...]` | ❌ | Semicolons conflict with style `;` separator |
| `startFill=0;endFill=0` | ⚠️ | Unnecessary, may cause rendering issues |
| `html=1` | ✅ | Required for HTML entities in values |

## Rendering Order

Cells render in XML order. Later cells appear ON TOP of earlier cells.

For radar charts:
1. Grid circles (background)
2. Axis lines
3. Scale numbers, labels
4. Data polygons — LARGEST FIRST (so smaller ones aren't hidden)
5. Legend (foreground)
