#!/usr/bin/env python3
"""
draw.io Radar Chart Generator

Generates a .drawio file with a hexagonal radar chart: concentric circle grid,
N radial axes, and M data polygon series. Polygons use the bulletproof
invisible-vertex + connected-edge method for reliable PNG export.

Usage:
    python generate_radar.py --output radar.drawio \\
        --axes "模型认知,提示与上下文工程,系统架构设计,安全与治理,多智能体编排,业务建模" \\
        --max-scale 6 \\
        --series "L1:3,4,1,1,1,2:#3b82f6" "L2:4,4,5,4,3,4:#2563eb" "L3:5,5,5.5,6,5.5,5:#7c3aed:dashed" \\
        --title "FDE 能力雷达图" \\
        --font-cn FangSong --font-en "Times New Roman"

    python generate_radar.py --help
"""
import argparse
import math
import sys


def vertex(cx, cy, R, score, max_scale, angle_deg):
    """Calculate pixel coordinates for a radar data point."""
    rad = math.radians(angle_deg)
    x = cx + R * (score / max_scale) * math.cos(rad)
    y = cy + R * (score / max_scale) * math.sin(rad)
    return round(x), round(y)


def generate_radar(
    axes_labels,
    series_data,
    max_scale=6,
    cx=600,
    cy=570,
    R=410,
    title="Radar Chart",
    font_cn="FangSong",
    font_en="Times New Roman",
    grid_color="#d8e4f2",
):
    """
    Generate draw.io XML for a radar chart.

    Args:
        axes_labels: list of axis label strings
        series_data: list of (name, scores_list, color_hex, is_dashed) tuples
        max_scale: maximum scale value
        cx, cy, R: chart center and outer radius in pixels
        title: chart title
        font_cn: Chinese font family
        font_en: Western font family
        grid_color: hex color for grid lines

    Returns:
        draw.io XML string
    """
    n_axes = len(axes_labels)
    angles_deg = [-90 + i * (360 / n_axes) for i in range(n_axes)]

    L = []
    page_w = cx + R + 120
    page_h = cy + R + 100
    L.append(f'<mxGraphModel dx="{int(page_w*1.2)}" dy="{int(page_h*1.1)}" '
             f'grid="0" page="0" pageWidth="{int(page_w)}" pageHeight="{int(page_h)}">')
    L.append('  <root>')
    L.append('    <mxCell id="0" />')
    L.append('    <mxCell id="1" parent="0" />')

    # Title
    L.append(f'    <mxCell id="title" value="{title}" '
             f'style="text;align=center;fontSize=18;fontFamily={font_cn};'
             f'fontStyle=1;fontColor=#1A3C5E;" vertex="1" parent="1">'
             f'<mxGeometry x="{cx-200}" y="15" width="400" height="35" as="geometry" /></mxCell>')

    # Grid circles
    ring_values = [max_scale * f // 3 for f in [1, 2, 3]]
    for val in ring_values:
        r = round(R * val / max_scale)
        L.append(f'    <mxCell id="ring{val}" value="" '
                 f'style="ellipse;fillColor=none;strokeColor={grid_color};'
                 f'strokeWidth=1;dashed=1;" vertex="1" parent="1">'
                 f'<mxGeometry x="{cx-r}" y="{cy-r}" width="{r*2}" height="{r*2}" as="geometry" /></mxCell>')
        # Scale number
        L.append(f'    <mxCell id="sc{val}" value="{val}" '
                 f'style="text;align=center;fontFamily={font_en};fontSize=9;fontColor=#a0aec0;" '
                 f'vertex="1" parent="1">'
                 f'<mxGeometry x="{cx+6}" y="{cy-r-7}" width="18" height="14" as="geometry" /></mxCell>')

    # Center dot
    L.append(f'    <mxCell id="center" value="" '
             f'style="ellipse;fillColor=#718096;strokeColor=none;" vertex="1" parent="1">'
             f'<mxGeometry x="{cx-4}" y="{cy-4}" width="8" height="8" as="geometry" /></mxCell>')

    # Axis lines
    for i, deg in enumerate(angles_deg):
        rad = math.radians(deg)
        tx = round(cx + R * math.cos(rad))
        ty = round(cy + R * math.sin(rad))
        L.append(f'    <mxCell id="ax{i}" value="" '
                 f'style="endArrow=none;strokeColor={grid_color};strokeWidth=1;dashed=1;" '
                 f'edge="1" parent="1">'
                 f'<mxGeometry relative="1" as="geometry">'
                 f'<mxPoint x="{cx}" y="{cy}" as="sourcePoint" />'
                 f'<mxPoint x="{tx}" y="{ty}" as="targetPoint" />'
                 f'</mxGeometry></mxCell>')

    # Axis labels
    for i, (label, deg) in enumerate(zip(axes_labels, angles_deg)):
        rad = math.radians(deg)
        lr = R + 35
        lx = round(cx + lr * math.cos(rad))
        ly = round(cy + lr * math.sin(rad))
        L.append(f'    <mxCell id="lbl{i}" value="{label}" '
                 f'style="text;align=center;fontFamily={font_cn};fontSize=12;'
                 f'fontStyle=1;fontColor=#1A3C5E;" vertex="1" parent="1">'
                 f'<mxGeometry x="{lx-60}" y="{ly-15}" width="120" height="30" as="geometry" /></mxCell>')

    # Data polygons — largest first (back z-order)
    # Sort by total score (descending) so largest renders first
    sorted_series = sorted(series_data, key=lambda s: sum(s[1]), reverse=True)

    for name, scores, color, is_dashed in sorted_series:
        pts = [vertex(cx, cy, R, s, max_scale, a)
               for s, a in zip(scores, angles_deg)]
        dash = 'dashed=1;' if is_dashed else ''

        # Create invisible vertex cells at each polygon vertex
        vids = []
        for j, (px, py) in enumerate(pts):
            vn = f'{name}_v{j}'
            vids.append(vn)
            L.append(f'    <mxCell id="{vn}" value="" '
                     f'style="ellipse;fillColor=none;strokeColor=none;" vertex="1" parent="1">'
                     f'<mxGeometry x="{px-1}" y="{py-1}" width="2" height="2" as="geometry" /></mxCell>')

        # Create edges connecting consecutive vertices (closed polygon)
        for j in range(n_axes):
            src = vids[j]
            tgt = vids[(j + 1) % n_axes]
            L.append(f'    <mxCell id="{name}_e{j}" value="" '
                     f'style="endArrow=none;strokeColor={color};strokeWidth=3;{dash}" '
                     f'edge="1" parent="1" source="{src}" target="{tgt}">'
                     f'<mxGeometry relative="1" as="geometry" /></mxCell>')

    # Legend
    leg_y = cy + R + 30
    leg_w = len(sorted_series) * 110
    leg_x = cx - leg_w // 2
    L.append(f'    <mxCell id="leg_bg" value="" '
             f'style="rounded=1;fillColor=#f7fafc;strokeColor={grid_color};" vertex="1" parent="1">'
             f'<mxGeometry x="{leg_x}" y="{leg_y}" width="{leg_w}" height="28" as="geometry" /></mxCell>')

    for i, (name, scores, color, is_dashed) in enumerate(sorted_series):
        sx = leg_x + 10 + i * 110
        dash = 'dashed=1;' if is_dashed else ''
        font = font_en if name.startswith('L') and name[1:].isdigit() else font_cn
        v1 = f'leg_{name}_v1'
        v2 = f'leg_{name}_v2'
        L.append(f'    <mxCell id="{v1}" value="" style="ellipse;fillColor=none;strokeColor=none;" '
                 f'vertex="1" parent="1"><mxGeometry x="{sx}" y="{leg_y+13}" width="2" height="2" as="geometry" /></mxCell>')
        L.append(f'    <mxCell id="{v2}" value="" style="ellipse;fillColor=none;strokeColor=none;" '
                 f'vertex="1" parent="1"><mxGeometry x="{sx+22}" y="{leg_y+13}" width="2" height="2" as="geometry" /></mxCell>')
        L.append(f'    <mxCell id="leg_{name}_l" value="" '
                 f'style="endArrow=none;strokeColor={color};strokeWidth=3;{dash}" '
                 f'edge="1" parent="1" source="{v1}" target="{v2}">'
                 f'<mxGeometry relative="1" as="geometry" /></mxCell>')
        L.append(f'    <mxCell id="leg_{name}_t" value="{name}" '
                 f'style="text;align=left;fontFamily={font};fontSize=10;fontColor={color};fontStyle=1;" '
                 f'vertex="1" parent="1"><mxGeometry x="{sx+28}" y="{leg_y+4}" width="80" height="20" as="geometry" /></mxCell>')

    L.append('  </root>')
    L.append('</mxGraphModel>')

    return '\n'.join(L)


def parse_series_arg(s):
    """Parse a series argument: 'name:scores:color[:dashed]'"""
    parts = s.split(':')
    if len(parts) < 3:
        raise ValueError(f"Series must be 'name:scores:color[:dashed]', got: {s}")
    name = parts[0]
    scores = [float(x) for x in parts[1].split(',')]
    color = parts[2]
    is_dashed = len(parts) > 3 and parts[3] == 'dashed'
    return (name, scores, color, is_dashed)


def main():
    parser = argparse.ArgumentParser(description='Generate draw.io radar chart')
    parser.add_argument('--output', '-o', required=True, help='Output .drawio file path')
    parser.add_argument('--axes', required=True,
                        help='Comma-separated axis labels (e.g., "A,B,C,D,E,F")')
    parser.add_argument('--max-scale', type=int, default=6, help='Maximum scale value')
    parser.add_argument('--series', nargs='+', required=True,
                        help='Series data: "name:s1,s2,...:color[:dashed]"')
    parser.add_argument('--title', default='Radar Chart', help='Chart title')
    parser.add_argument('--font-cn', default='FangSong', help='Chinese font')
    parser.add_argument('--font-en', default='Times New Roman', help='Western font')
    parser.add_argument('--cx', type=int, default=600, help='Center X')
    parser.add_argument('--cy', type=int, default=570, help='Center Y')
    parser.add_argument('--radius', type=int, default=410, help='Outer ring radius')

    args = parser.parse_args()

    axes = args.axes.split(',')
    series = [parse_series_arg(s) for s in args.series]

    xml = generate_radar(
        axes_labels=axes,
        series_data=series,
        max_scale=args.max_scale,
        cx=args.cx, cy=args.cy, R=args.radius,
        title=args.title,
        font_cn=args.font_cn, font_en=args.font_en,
    )

    with open(args.output, 'w', encoding='utf-8') as f:
        f.write(xml)
    print(f'Written: {args.output}')
    print(f'  Axes: {len(axes)}')
    print(f'  Series: {len(series)}')
    print(f'  Export: draw.io --export --format png --scale 2 --border 20 '
          f'--output output.png "{args.output}"')


if __name__ == '__main__':
    main()
