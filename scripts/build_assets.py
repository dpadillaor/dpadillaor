"""Generate the profile SVGs (header banner + tech ribbon), light and dark.

Visual language mirrors the portfolio site (portfolio/src/styles/tokens.css):
monospace everywhere, bold uppercase headline, point cloud with orange 3D boxes
labelled "NAME n pts", and a small live HUD.

Run:  python scripts/build_assets.py
"""

import math
import random
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "assets"

THEMES = {
    "light": {
        "bg": "#ffffff",
        "ink": "#0a0a0a",
        "soft": "#565656",
        "faint": "#8a8a86",
        "line": "#e6e6e6",
        "point": "#b9b9b4",
        "label": "#ffffff",
    },
    "dark": {
        "bg": "#0d1117",
        "ink": "#f0f0ee",
        "soft": "#a8a8a3",
        "faint": "#7a7a76",
        "line": "#262c36",
        "point": "#565b63",
        "label": "#0d1117",
    },
}
ACCENT = "#ff5a1f"

# The site loads JetBrains Mono; an SVG inside <img> cannot, so fall back gracefully.
MONO = "'JetBrains Mono', ui-monospace, SFMono-Regular, Menlo, Consolas, 'Liberation Mono', monospace"


# ---------------------------------------------------------------- header scene

def project(p, cam=(0.0, 4.6, -4.6), f=430.0):
    """Pinhole projection, camera above the room looking down into it, yawed."""
    yaw = math.radians(-32)
    x, y, z = p[0] - cam[0], p[1] - cam[1], p[2] - cam[2]
    x, z = x * math.cos(yaw) - z * math.sin(yaw), x * math.sin(yaw) + z * math.cos(yaw)
    pitch = math.radians(-40)
    y, z = y * math.cos(pitch) - z * math.sin(pitch), y * math.sin(pitch) + z * math.cos(pitch)
    return f * x / z, -f * y / z, z


# name, centre, half-size, number of points, label offset (dx, dy) in px
INSTANCES = [
    ("SOFA", (-1.6, 0.42, 2.4), (0.95, 0.42, 0.55), 210, (-30, -34)),
    ("TABLE", (0.7, 0.36, 1.2), (0.55, 0.36, 0.5), 140, (40, -44)),
    ("SHELF", (2.35, 0.95, 2.95), (0.38, 0.95, 0.38), 120, (30, -26)),
    ("ROBOT", (-0.9, 0.25, 0.0), (0.28, 0.25, 0.28), 70, (-70, -30)),
]


def scene_points(rng):
    """A small room as a point cloud: floor, two walls and a few object instances."""
    pts = []  # (xyz, instance name or None)
    for _ in range(340):
        pts.append(((rng.uniform(-3, 3), 0, rng.uniform(-1.6, 3.5)), None))
    for _ in range(200):
        pts.append(((rng.uniform(-3, 3), rng.uniform(0, 2.4), 3.5), None))
    for _ in range(150):
        pts.append(((-3, rng.uniform(0, 2.4), rng.uniform(-1.6, 3.5)), None))
    for name, c, s, n, _ in INSTANCES:
        for _ in range(n):
            face = rng.randrange(3)
            q = [0.0, 0.0, 0.0]
            q[face] = rng.choice((-1, 1))
            q[(face + 1) % 3], q[(face + 2) % 3] = rng.uniform(-1, 1), rng.uniform(-1, 1)
            jitter = [rng.gauss(0, 0.02) for _ in range(3)]
            pts.append(((c[0] + q[0] * s[0] + jitter[0], c[1] + q[1] * s[1] + jitter[1],
                         c[2] + q[2] * s[2] + jitter[2]), name))
    return pts


def trajectory():
    """Camera path walking through the room."""
    out = []
    for i in range(70):
        t = i / 69
        out.append((-2.3 + 4.0 * t, 1.2 + 0.05 * math.sin(t * 11),
                    -1.2 + 1.0 * math.sin(t * math.pi * 1.1)))
    return out


def frustum(c, look, s=10):
    a = math.atan2(look[1], look[0])
    l = (c[0] + math.cos(a + 0.5) * s * 2, c[1] + math.sin(a + 0.5) * s * 2)
    r = (c[0] + math.cos(a - 0.5) * s * 2, c[1] + math.sin(a - 0.5) * s * 2)
    return f'M{c[0]:.1f},{c[1]:.1f} L{l[0]:.1f},{l[1]:.1f} L{r[0]:.1f},{r[1]:.1f} Z'


def header(theme):
    c = THEMES[theme]
    rng = random.Random(11)
    W, H = 1200, 460

    pts = [(project(p), inst) for p, inst in scene_points(rng)]
    traj3 = [project(p) for p in trajectory()]
    corners3 = {
        name: [project((cx + sx * dx, cy + sy * dy, cz + sz * dz))
               for dx in (-1, 1) for dy in (-1, 1) for dz in (-1, 1)]
        for name, (cx, cy, cz), (sx, sy, sz), *_ in INSTANCES
    }

    # Fit the projected scene into the right half of the banner.
    X0, Y0, X1, Y1 = 610, 92, W - 44, H - 92
    xs = [q[0] for q, _ in pts] + [q[0] for q in traj3]
    ys = [q[1] for q, _ in pts] + [q[1] for q in traj3]
    k = min((X1 - X0) / (max(xs) - min(xs)), (Y1 - Y0) / (max(ys) - min(ys)))
    ox = X0 + ((X1 - X0) - k * (max(xs) - min(xs))) / 2 - k * min(xs)
    oy = Y0 + ((Y1 - Y0) - k * (max(ys) - min(ys))) / 2 - k * min(ys)

    def fit(q):
        return ox + k * q[0], oy + k * q[1]

    dots = []
    for q, inst in sorted(pts, key=lambda e: -e[0][2]):
        x, y = fit(q)
        r = max(0.9, 6.0 / q[2])
        delay = (x - X0) / (X1 - X0) * 2.2 + rng.uniform(0, 0.6)
        fill = c["soft"] if inst else c["point"]
        dots.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.2f}" fill="{fill}" '
                    f'class="pt" style="animation-delay:{delay:.2f}s"/>')

    # Orange 3D boxes + "NAME n pts" labels, like the site's hero.
    counts = {name: n for name, _, _, n, _ in INSTANCES}
    boxes, labels = [], []
    edges = [(a, b) for a in range(8) for b in range(a + 1, 8) if bin(a ^ b).count("1") == 1]
    for i, (name, *_rest, (odx, ody)) in enumerate(INSTANCES):
        cs = [fit(q) for q in corners3[name]]
        d = " ".join(f"M{cs[a][0]:.1f},{cs[a][1]:.1f} L{cs[b][0]:.1f},{cs[b][1]:.1f}" for a, b in edges)
        delay = 2.6 + i * 0.35
        boxes.append(f'<path d="{d}" style="animation-delay:{delay:.2f}s"/>')
        top = min(cs, key=lambda p: p[1])
        text = f"{name} {counts[name]} pts"
        w = len(text) * 7.8 + 18
        lx, ly = top[0] - w / 2 + odx, top[1] + ody - 24
        labels.append(
            f'<g class="lab" style="animation-delay:{delay + .15:.2f}s">'
            f'<line x1="{top[0] + odx:.1f}" y1="{ly + 24:.1f}" x2="{top[0]:.1f}" y2="{top[1]:.1f}" stroke="{ACCENT}"/>'
            f'<rect x="{lx:.1f}" y="{ly:.1f}" width="{w:.1f}" height="24" fill="{c["label"]}" stroke="{ACCENT}"/>'
            f'<text x="{lx + 9:.1f}" y="{ly + 16.5:.1f}" class="lt">{name} '
            f'<tspan fill="{ACCENT}">{counts[name]}</tspan> <tspan fill="{c["faint"]}">pts</tspan></text></g>'
        )

    traj = [fit(q) for q in traj3]
    path = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in traj)
    centre = fit(project((0, 0.5, 2.0)))

    def look_at(p):
        return centre[0] - p[0], centre[1] - p[1]

    frusta = "".join(
        f'<path d="{frustum(traj[i], look_at(traj[i]))}" style="animation-delay:{0.5 + j * 0.45:.2f}s"/>'
        for j, i in enumerate(range(5, len(traj) - 5, 10))
    )
    head = traj[-1]
    n_kf = len(range(5, len(traj) - 5, 10)) + 1

    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-labelledby="t d">
<title id="t">David Padilla Orenga — Computer Vision · AI · Robotics · Automation</title>
<desc id="d">Freelance engineer. A live 3D map: a room as a point cloud, a camera trajectory and object instances in orange boxes.</desc>
<style>
  text {{ font-family: {MONO}; }}
  .k {{ font-size: 14px; font-weight: 500; letter-spacing: .14em; fill: {c["soft"]}; }}
  .h {{ font-size: 50px; font-weight: 800; letter-spacing: -.01em; fill: {c["ink"]}; }}
  .h2 {{ font-size: 50px; font-weight: 400; letter-spacing: -.01em; fill: {c["faint"]}; }}
  .s {{ font-size: 16px; fill: {c["soft"]}; }}
  .m {{ font-size: 13px; letter-spacing: .06em; fill: {c["faint"]}; }}
  .mb {{ font-weight: 700; fill: {c["ink"]}; }}
  .lt {{ font-size: 13px; font-weight: 600; letter-spacing: .04em; fill: {c["ink"]}; }}
  .pt, .fr path, .bx path, .lab, .cam {{ opacity: 0; animation: pop .45s ease-out forwards; }}
  .traj {{ stroke-dasharray: 1600; stroke-dashoffset: 1600; animation: draw 3s cubic-bezier(.6,0,.3,1) .3s forwards; }}
  .cam {{ animation-delay: 3.2s; }}
  .pulse {{ transform-box: fill-box; transform-origin: center; opacity: 0; animation: pulse 2s ease-out 3.4s infinite; }}
  .live {{ animation: blink 1.4s steps(2) infinite; }}
  @keyframes pop {{ to {{ opacity: 1; }} }}
  @keyframes draw {{ to {{ stroke-dashoffset: 0; }} }}
  @keyframes pulse {{ 0% {{ opacity: .6; transform: scale(.4); }} 100% {{ opacity: 0; transform: scale(2.6); }} }}
  @keyframes blink {{ 50% {{ opacity: .15; }} }}
  @media (prefers-reduced-motion: reduce) {{
    .pt, .fr path, .bx path, .lab, .cam {{ animation: none; opacity: 1; }}
    .traj {{ animation: none; stroke-dashoffset: 0; }}
    .pulse, .live {{ animation: none; }}
  }}
</style>
<rect width="{W}" height="{H}" rx="12" fill="{c["bg"]}"/>
<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="12" fill="none" stroke="{c["line"]}"/>

<!-- copy -->
<line x1="56" y1="86" x2="92" y2="86" stroke="{c["soft"]}"/>
<text x="104" y="91" class="k">FREELANCE ENGINEER</text>
<text x="54" y="168" class="h">COMPUTER VISION</text>
<text x="54" y="226" class="h2">AI · ROBOTICS ·</text>
<text x="54" y="284" class="h">AUTOMATION<tspan fill="{ACCENT}">.</tspan></text>
<text x="56" y="336" class="s">Perception, 3D and automation systems</text>
<text x="56" y="360" class="s">that hold up outside the lab<tspan fill="{ACCENT}"> — and in production.</tspan></text>
<text x="56" y="{H - 40}" class="m"><tspan class="mb">DAVID PADILLA ORENGA</tspan> · VALENCIA · REMOTE</text>

<!-- scene -->
<g>{"".join(dots)}</g>
<path d="{path}" fill="none" stroke="{c["soft"]}" stroke-width="1.4" stroke-linecap="round" class="traj"/>
<g class="fr" fill="none" stroke="{c["soft"]}" stroke-width="1.1" stroke-linejoin="round">{frusta}</g>
<g class="bx" fill="none" stroke="{ACCENT}" stroke-width="1.5" stroke-linejoin="round">{"".join(boxes)}</g>
<g>{"".join(labels)}</g>
<g class="cam">
  <circle cx="{head[0]:.1f}" cy="{head[1]:.1f}" r="12" fill="{ACCENT}" class="pulse"/>
  <path d="{frustum(head, look_at(head), 13)}" fill="{ACCENT}" fill-opacity=".15" stroke="{ACCENT}" stroke-width="2" stroke-linejoin="round"/>
  <circle cx="{head[0]:.1f}" cy="{head[1]:.1f}" r="4" fill="{ACCENT}"/>
</g>

<!-- HUD -->
<circle cx="{X0 + 4}" cy="{H - 54}" r="4" fill="{ACCENT}" class="live"/>
<text x="{X0 + 16}" y="{H - 50}" class="m"><tspan class="mb">3D MAP</tspan> · LIVE</text>
<text x="{X0}" y="{H - 28}" class="m">INSTANCES <tspan class="mb">{len(INSTANCES)}</tspan> · POINTS <tspan class="mb">{len(pts)}</tspan></text>
<text x="{W - 44}" y="{H - 50}" class="m" text-anchor="end">KEYFRAMES <tspan class="mb">{n_kf}</tspan></text>
<text x="{W - 44}" y="{H - 28}" class="m" text-anchor="end">LAST <tspan fill="{ACCENT}">{INSTANCES[-1][0]}</tspan></text>
</svg>
"""


# ---------------------------------------------------------------- tech ribbon

RIBBON = [
    "Computer Vision", "YOLO", "SAM 2 / SAM 3", "CLIP", "SigLIP",
    "Multi-object tracking", "SLAM", "Structure from Motion", "Bundle Adjustment",
    "Gaussian Splatting", "COLMAP", "Open-vocabulary 3D", "Robotics",
    "PyTorch", "LibTorch", "CUDA", "C++", "Python", "Rust", "Rerun",
    "LLM agents", "n8n", "Process automation", "Digital twins",
]


def ribbon(theme):
    c = THEMES[theme]
    fs, cw, gap = 14, 14 * 0.6, 46  # monospace advance ≈ 0.6em; textLength pins it exactly
    W, H = 1200, 52
    items, x = [], 0.0
    for word in RIBBON:
        word = word.upper()
        w = len(word) * cw
        items.append((x, word, w))
        x += w + gap
    period = x

    def row(offset):
        out = []
        for x0, word, w in items:
            mx = offset + x0 + w + gap / 2
            out.append(
                f'<text x="{offset + x0:.1f}" y="{H / 2 + 5:.1f}" textLength="{w:.1f}" '
                f'lengthAdjust="spacing">{word}</text>'
                f'<rect x="{mx - 3:.1f}" y="{H / 2 - 3:.1f}" width="6" height="6" fill="{ACCENT}" '
                f'transform="rotate(45 {mx:.1f} {H / 2:.1f})"/>'
            )
        return "".join(out)

    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="{" · ".join(RIBBON)}">
<style>
  text {{ font: 500 {fs}px {MONO}; letter-spacing: .04em; fill: {c["soft"]}; }}
  .belt {{ animation: run {period / 40:.1f}s linear infinite; }}
  @keyframes run {{ to {{ transform: translateX(-{period:.1f}px); }} }}
  @media (prefers-reduced-motion: reduce) {{ .belt {{ animation: none; }} }}
</style>
<defs>
  <linearGradient id="fade" x1="0" x2="1">
    <stop offset="0" stop-color="{c["bg"]}"/><stop offset=".06" stop-color="{c["bg"]}" stop-opacity="0"/>
    <stop offset=".94" stop-color="{c["bg"]}" stop-opacity="0"/><stop offset="1" stop-color="{c["bg"]}"/>
  </linearGradient>
  <clipPath id="clip"><rect width="{W}" height="{H}" rx="10"/></clipPath>
</defs>
<g clip-path="url(#clip)">
  <rect width="{W}" height="{H}" fill="{c["bg"]}"/>
  <g class="belt">{row(24)}{row(24 + period)}</g>
  <rect width="{W}" height="{H}" fill="url(#fade)"/>
</g>
<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="10" fill="none" stroke="{c["line"]}"/>
</svg>
"""


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    for theme in THEMES:
        (OUT / f"header-{theme}.svg").write_text(header(theme), encoding="utf-8")
        (OUT / f"ribbon-{theme}.svg").write_text(ribbon(theme), encoding="utf-8")
    print("assets written to", OUT)
