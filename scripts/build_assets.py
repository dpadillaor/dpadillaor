"""Generate the profile hero card (assets/hero-light.svg, assets/hero-dark.svg).

Visual language mirrors the portfolio site (portfolio/src/styles/tokens.css):
monospace, orange accent, a point cloud with orange 3D boxes. The card loops:
a room gets mapped while a pipeline lights up capture, perceive, map, automate, ship.

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

def project(p, cam=(0.0, 3.4, -5.6), f=430.0):
    """Pinhole projection, camera above the room looking down into it, yawed."""
    yaw = math.radians(-14)
    x, y, z = p[0] - cam[0], p[1] - cam[1], p[2] - cam[2]
    x, z = x * math.cos(yaw) - z * math.sin(yaw), x * math.sin(yaw) + z * math.cos(yaw)
    pitch = math.radians(-26)
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


CARD = {
    "light": {"top": "#ffffff", "bottom": "#f7f7f5", "stroke": "#e6e6e6", "spine": "#e2e2df"},
    "dark": {"top": "#161b22", "bottom": "#0d1117", "stroke": "#262c36", "spine": "#2a303b"},
}

PIPELINE = [
    ("CAPTURE", "video · RGB-D", "sensors"),
    ("PERCEIVE", "YOLO · SAM", "CLIP · tracking"),
    ("MAP", "SLAM · SfM", "3D instances"),
    ("AUTOMATE", "LLM agents", "workflows"),
    ("SHIP", "measured on", "your hardware"),
]

CYCLE = 10  # seconds per loop


def _fade(name, start, hold_end=88.0, out=95.0):
    """Keyframes: hidden until `start`%, visible until `hold_end`%, faded out by `out`%."""
    return (f"@keyframes {name}{{0%,{start:.1f}%{{opacity:0}}{start + 3:.1f}%,{hold_end:.1f}%{{opacity:1}}"
            f"{out:.1f}%,100%{{opacity:0}}}}")


def hero(theme):
    c, card = THEMES[theme], CARD[theme]
    rng = random.Random(11)
    W, H = 900, 320

    pts = [(project(p), inst) for p, inst in scene_points(rng)]
    traj3 = [project(p) for p in trajectory()]
    corners3 = {
        name: [project((cx + sx * dx, cy + sy * dy, cz + sz * dz))
               for dx in (-1, 1) for dy in (-1, 1) for dz in (-1, 1)]
        for name, (cx, cy, cz), (sx, sy, sz), *_ in INSTANCES
    }

    # Scene lives in the lower-left of the card.
    X0, Y0, X1, Y1 = 40, 172, 440, 300
    xs = [q[0] for q, _ in pts] + [q[0] for q in traj3]
    ys = [q[1] for q, _ in pts] + [q[1] for q in traj3]
    k = min((X1 - X0) / (max(xs) - min(xs)), (Y1 - Y0) / (max(ys) - min(ys)))
    ox = X0 + ((X1 - X0) - k * (max(xs) - min(xs))) / 2 - k * min(xs)
    oy = Y0 + ((Y1 - Y0) - k * (max(ys) - min(ys))) / 2 - k * min(ys)

    def fit(q):
        return ox + k * q[0], oy + k * q[1]

    # Points appear in four sweeps, left to right, while the camera explores.
    batches = [[] for _ in range(4)]
    for q, inst in sorted(pts, key=lambda e: -e[0][2]):
        x, y = fit(q)
        b = min(3, int((x - X0) / (X1 - X0) * 4))
        fill = c["soft"] if inst else c["point"]
        batches[b].append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{max(0.8, 5.0 / q[2]):.2f}" fill="{fill}"/>')
    dots = "".join(f'<g class="b{i}">{"".join(g)}</g>' for i, g in enumerate(batches))

    edges = [(a, b) for a in range(8) for b in range(a + 1, 8) if bin(a ^ b).count("1") == 1]
    counts = {name: n for name, _, _, n, _ in INSTANCES}
    boxes = []
    for i, (name, *_rest, (odx, ody)) in enumerate(INSTANCES):
        cs = [fit(q) for q in corners3[name]]
        d = " ".join(f"M{cs[a][0]:.1f},{cs[a][1]:.1f} L{cs[b][0]:.1f},{cs[b][1]:.1f}" for a, b in edges)
        top = min(cs, key=lambda p: p[1])
        text = f"{name} {counts[name]}"
        w = len(text) * 6.1 + 12
        ax = top[0] + odx * 0.45
        lx, ly = ax - w / 2, top[1] + ody * 0.45 - 16
        boxes.append(
            f'<g class="x{i}"><path d="{d}" fill="none" stroke="{ACCENT}" stroke-width="1.2"/>'
            f'<line x1="{ax:.1f}" y1="{ly + 16:.1f}" x2="{top[0]:.1f}" y2="{top[1]:.1f}" stroke="{ACCENT}" stroke-width=".8"/>'
            f'<rect x="{lx:.1f}" y="{ly:.1f}" width="{w:.1f}" height="16" fill="{card["top"]}" stroke="{ACCENT}" stroke-width=".8"/>'
            f'<text x="{lx + 6:.1f}" y="{ly + 11.5:.1f}" class="mono" font-size="10" font-weight="600" fill="{c["ink"]}">{name} '
            f'<tspan fill="{ACCENT}">{counts[name]}</tspan></text></g>'
        )

    traj = [fit(q) for q in traj3]
    path = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in traj)
    plen = sum(math.dist(traj[i], traj[i + 1]) for i in range(len(traj) - 1))

    # Pipeline on the right: a spine with five stages lighting up in turn.
    SX0, SX1, SY = 494, 846, 222
    step = (SX1 - SX0) / (len(PIPELINE) - 1)
    stages = []
    for i, (label, l1, l2) in enumerate(PIPELINE):
        x = SX0 + i * step
        stages.append(
            f'<text x="{x:.1f}" y="{SY - 22}" class="mono" font-size="10.5" font-weight="700" letter-spacing="1.2" '
            f'text-anchor="middle" fill="{c["ink"]}">{label}</text>'
            f'<circle cx="{x:.1f}" cy="{SY}" r="6" fill="{card["top"]}" stroke="{c["faint"]}" stroke-width="1.5"/>'
            f'<g class="s{i}"><circle cx="{x:.1f}" cy="{SY}" r="16" fill="url(#glow)"/>'
            f'<circle cx="{x:.1f}" cy="{SY}" r="6" fill="{ACCENT}"/></g>'
            f'<text x="{x:.1f}" y="{SY + 28}" class="mono" font-size="10" text-anchor="middle" fill="{c["faint"]}">{l1}</text>'
            f'<text x="{x:.1f}" y="{SY + 42}" class="mono" font-size="10" text-anchor="middle" fill="{c["faint"]}">{l2}</text>'
        )
    stage_at = [8 + i * 16 for i in range(len(PIPELINE))]  # % of the cycle

    css = "\n".join(
        [_fade(f"b{i}", 4 + i * 9) for i in range(4)]
        + [_fade(f"x{i}", 42 + i * 7) for i in range(len(INSTANCES))]
        + [_fade(f"s{i}", t) for i, t in enumerate(stage_at)]
        + [f".b{i}{{animation:b{i} {CYCLE}s linear infinite}}" for i in range(4)]
        + [f".x{i}{{animation:x{i} {CYCLE}s linear infinite}}" for i in range(len(INSTANCES))]
        + [f".s{i}{{animation:s{i} {CYCLE}s linear infinite}}" for i in range(len(PIPELINE))]
    )
    still = ",".join([f".b{i}" for i in range(4)] + [f".x{i}" for i in range(len(INSTANCES))]
                     + [f".s{i}" for i in range(len(PIPELINE))] + [".dot"])
    span = SX1 - SX0

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-labelledby="t d">
<title id="t">David Padilla Orenga — Computer Vision · AI · Robotics · Automation</title>
<desc id="d">Animated card: a 3D map of a room builds up from points while a camera explores it and objects get boxed; beside it, a pipeline lights up stage by stage: capture, perceive, map, automate, ship.</desc>
<style>
.mono{{font-family:{MONO}}}
{css}
.traj{{stroke-dasharray:{plen:.0f};animation:traj {CYCLE}s cubic-bezier(.5,0,.4,1) infinite}}
@keyframes traj{{0%{{stroke-dashoffset:{plen:.0f};opacity:1}}60%,88%{{stroke-dashoffset:0;opacity:1}}95%,100%{{stroke-dashoffset:0;opacity:0}}}}
.spine{{stroke-dasharray:{span};animation:spine {CYCLE}s linear infinite}}
@keyframes spine{{0%,8%{{stroke-dashoffset:{span};opacity:1}}72%,88%{{stroke-dashoffset:0;opacity:1}}95%,100%{{stroke-dashoffset:0;opacity:0}}}}
.dot{{animation:dot 1.6s ease-in-out infinite}}
@keyframes dot{{50%{{opacity:.25}}}}
@media (prefers-reduced-motion:reduce){{
{still}{{animation:none;opacity:1}}
.traj,.spine{{animation:none;stroke-dashoffset:0}}
}}
</style>
<defs>
<linearGradient id="panel" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{card["top"]}"/><stop offset="1" stop-color="{card["bottom"]}"/></linearGradient>
<linearGradient id="rule" x1="0" x2="1"><stop offset="0" stop-color="{ACCENT}" stop-opacity=".7"/><stop offset=".18" stop-color="{card["stroke"]}"/><stop offset="1" stop-color="{card["stroke"]}" stop-opacity="0"/></linearGradient>
<radialGradient id="aura" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="{ACCENT}" stop-opacity=".10"/><stop offset="1" stop-color="{ACCENT}" stop-opacity="0"/></radialGradient>
<radialGradient id="glow" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="{ACCENT}" stop-opacity=".45"/><stop offset="1" stop-color="{ACCENT}" stop-opacity="0"/></radialGradient>
<clipPath id="card"><rect x="8" y="6" width="{W - 16}" height="{H - 12}" rx="18"/></clipPath>
</defs>

<rect x="8" y="6" width="{W - 16}" height="{H - 12}" rx="18" fill="url(#panel)" stroke="{card["stroke"]}"/>
<ellipse cx="232" cy="236" rx="250" ry="95" fill="url(#aura)" clip-path="url(#card)"/>

<!-- headline -->
<rect x="32" y="34" width="3" height="36" rx="1.5" fill="{ACCENT}"/>
<text class="mono" x="48" y="62" font-size="30" font-weight="800" letter-spacing="-.5" fill="{c["ink"]}">David Padilla Orenga</text>
<text class="mono" x="49" y="88" font-size="12" fill="{c["soft"]}">Freelance engineer · Computer Vision · AI · Robotics · Automation</text>
<circle cx="{W - 166}" cy="50" r="4" fill="{ACCENT}" class="dot"/>
<text class="mono" x="{W - 48}" y="54" font-size="12" font-weight="700" letter-spacing="2.4" text-anchor="end" fill="{ACCENT}">OPEN TO WORK</text>
<text class="mono" x="{W - 48}" y="76" font-size="11" text-anchor="end" fill="{c["faint"]}">Valencia · remote</text>
<rect x="32" y="108" width="{W - 64}" height="1" fill="url(#rule)"/>

<text class="mono" x="48" y="138" font-size="10.5" letter-spacing="2.2" fill="{c["faint"]}">3D MAP · LIVE</text>
<text class="mono" x="{W - 48}" y="138" font-size="10.5" letter-spacing="2.2" text-anchor="end" fill="{c["faint"]}">FROM PIXELS TO PRODUCTION</text>

<!-- scene -->
{dots}
<path d="{path}" fill="none" stroke="{c["soft"]}" stroke-width="1.2" stroke-linecap="round" class="traj"/>
{"".join(boxes)}

<!-- pipeline -->
<path d="M{SX0} {SY}H{SX1}" stroke="{card["spine"]}" stroke-width="2"/>
<path d="M{SX0} {SY}H{SX1}" stroke="{ACCENT}" stroke-width="2" class="spine"/>
{"".join(stages)}
</svg>
"""

if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    for theme in THEMES:
        (OUT / f"hero-{theme}.svg").write_text(hero(theme), encoding="utf-8")
    print("assets written to", OUT)
