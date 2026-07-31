# Coordinate Formula for Radar Chart Vertices

## Formula

For each data point at axis angle θ with score s:

```
x = cx + R × (score / max_scale) × cos(θ)
y = cy + R × (score / max_scale) × sin(θ)
```

Where:
- `cx, cy` = center of the radar chart (pixel coordinates)
- `R` = radius of the outermost ring (pixels)
- `score` = data value for this axis (0 to max_scale)
- `max_scale` = maximum scale value (typically 6)
- `θ` = axis angle in radians (measured from positive x-axis, y-down)

## Angle Convention

For a radar with N axes starting from top, going clockwise:

```
angle_i = -90° + i × (360° / N)    for i = 0, 1, ..., N-1
```

For a standard 6-axis radar:

| Axis | Angle (deg) | Position |
|------|-------------|----------|
| 0    | -90         | Top      |
| 1    | -30         | Top-right|
| 2    |  30         | Bot-right|
| 3    |  90         | Bottom   |
| 4    | 150         | Bot-left |
| 5    | 210         | Top-left |

## Example

With cx=600, cy=570, R=410, max_scale=6:

For L3 治理者视野 score=6 on axis 3 (bottom, 90°):
```
x = 600 + 410 × (6/6) × cos(90°) = 600 + 0 = 600
y = 570 + 410 × (6/6) × sin(90°) = 570 + 410 = 980
```

For L1 Prompter score=1 on axis 2 (bot-right, 30°):
```
x = 600 + 410 × (1/6) × cos(30°) = 600 + 410 × 0.167 × 0.866 = 600 + 59 = 659
y = 570 + 410 × (1/6) × sin(30°) = 570 + 410 × 0.167 × 0.5 = 570 + 34 = 604
```

## Grid Ring Radii

For rings at values v1, v2, v3 (e.g., 2, 4, 6):

```
r_vi = R × (vi / max_scale)
```

Example (R=410, max=6):
- Ring at 2: r = 410 × 2/6 = 137px
- Ring at 4: r = 410 × 4/6 = 273px
- Ring at 6: r = 410 × 6/6 = 410px

Each ring is an ellipse centered at (cx, cy) with width=height=2×r.

## Axis Endpoint Calculation

For axis i at angle θ_i, the endpoint (outer ring intersection):

```
x_end = cx + R × cos(θ_i)
y_end = cy + R × sin(θ_i)
```

## Label Positioning

Labels are placed outside the outer ring at distance R + offset:

```
x_label = cx + (R + 35) × cos(θ_i)
y_label = cy + (R + 35) × sin(θ_i)
```

Adjust `35` based on label length and font size.
