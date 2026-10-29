"""Builds assets/toolbox-{light,dark}.svg: what I work with.

Same groups and technologies as "What I work with" on davidpadilla.eu, each one with its logo in its brand colour on
a small light tile (so dark logos still show on the dark theme). Logos and their sources: assets/toolbox/.
Layouts, to compare:  python scripts/toolbox.py [ls|grid|marquee|periodic] [--out <folder>]
"""

import sys

import base64
import json
from html import escape
from pathlib import Path

import banner
import neofetch
from services import ICONS, WIDTH
from terminal import BAR, PAD, window

ROOT = Path(__file__).resolve().parent.parent
LOGOS = json.loads((ROOT / "assets/toolbox/logos.json").read_text())
IMAGES = {"matlab": "matlab.png", "rerun": "rerun.png", "colmap": "colmap.svg"}

# (folder, [(name, logo)]): as in content/en/sobre-mi.yml of the website. `bot` is the website's agents icon.
GROUPS = [
    ("languages", [("Python", "python"), ("C++", "cplusplus"), ("Rust", "rust"), ("TypeScript", "typescript"),
                   ("MATLAB", "matlab")]),
    ("ai-and-deep-learning", [("PyTorch · LibTorch", "pytorch"), ("TensorFlow", "tensorflow"), ("CUDA", "nvidia"),
                              ("ONNX", "onnx"), ("TensorRT", "nvidia"), ("Roboflow", "roboflow")]),
    ("models", [("YOLO", "yolo"), ("SAM 2/3 · DETR · DINOv2 · Perception Encoder", "meta"), ("CLIP", "openai"),
                ("SigLIP", "google"), ("Depth Anything", "bytedance"), ("LLMs and agents", "bot")]),
    ("vision-and-3d", [("OpenCV", "opencv"), ("Open3D", "open3d"), ("COLMAP", "colmap"), ("three.js", "threedotjs"),
                       ("Rerun", "rerun")]),
    ("apps-and-infra", [("Docker", "docker"), ("SQLite", "sqlite"), ("Linux", "linux"), ("Git", "git"),
                        ("CMake", "cmake"), ("n8n", "n8n")]),
]
COMMAND = "ls ~/toolbox/"
LAYOUT = "marquee"
# one tile per tool: entries that joined several tools are split. Short names only, so the strip keeps its rhythm
# (Perception Encoder and Depth Anything are left out here; they are still on the website).
TILES = [
    ("languages", [("Python", "python", "Py"), ("C++", "cplusplus", "C++"), ("Rust", "rust", "Rs"),
                   ("TypeScript", "typescript", "Ts"), ("MATLAB", "matlab", "Ml")]),
    ("ai-and-deep-learning", [("PyTorch", "pytorch", "Pt"), ("LibTorch", "pytorch", "Lt"), ("TensorFlow", "tensorflow", "Tf"),
                              ("CUDA", "nvidia", "Cu"), ("ONNX", "onnx", "Ox"), ("TensorRT", "nvidia", "Trt"),
                              ("Roboflow", "roboflow", "Rf")]),
    ("models", [("YOLO", "yolo", "Yo"), ("SAM 2/3", "meta", "Sam"), ("DETR", "meta", "Dt"), ("DINOv2", "meta", "Dn"),
("CLIP", "openai", "Cl"), ("SigLIP", "google", "Sl"),
                ("LLMs", "bot", "Llm"), ("Agents", "bot", "Ag"), ("LangChain", "langchain", "Lc")]),
    ("vision-and-3d", [("OpenCV", "opencv", "Cv"), ("Open3D", "open3d", "O3d"), ("COLMAP", "colmap", "Cm"),
                       ("three.js", "threedotjs", "3js"), ("Rerun", "rerun", "Rr")]),
    ("apps-and-infra", [("Docker", "docker", "Dk"), ("SQLite", "sqlite", "Sq"), ("Linux", "linux", "Lx"),
                        ("Git", "git", "Gt"), ("CMake", "cmake", "Cmk"), ("n8n", "n8n", "N8n")]),
]
SIZE, TILE, CHIP_H, GAP = 14, 26, 32, 22


def mark(name: str, x: float, y: float, inner: float, t: dict) -> str:
    """Just the logo, `inner` px wide, its top-left corner at (x, y)."""
    if name in IMAGES:
        path = ROOT / "assets/toolbox" / IMAGES[name]
        mime = "image/svg+xml" if path.suffix == ".svg" else "image/png"
        data = base64.b64encode(path.read_bytes()).decode()
        return f'<image href="data:{mime};base64,{data}" x="{x:.1f}" y="{y:.1f}" width="{inner}" height="{inner}"/>'
    if name == "bot":
        return (f'<g transform="translate({x:.1f},{y:.1f}) scale({inner / 24})" fill="none" stroke="{t["key"]}" '
                f'stroke-width="2" stroke-linecap="round" stroke-linejoin="round">{ICONS["bot"]}</g>')
    data = LOGOS[name]
    colour = "#24292f" if data.get("mono") else data["color"]
    return f'<g transform="translate({x:.1f},{y:.1f}) scale({inner / 24})" fill="{colour}"><path d="{data["d"]}"/></g>'


TILE_BG = {"light": "#f6f8fa", "dark": "#e6edf3"}  # light tiles on both themes, so dark logos still show


def logo(name: str, x: float, y: float, t: dict) -> str:
    """The logo on its tile."""
    tile = f'<rect x="{x}" y="{y}" width="{TILE}" height="{TILE}" rx="5" fill="#f6f8fa" stroke="{t["border"]}"/>'
    inner, off = 16, (TILE - 16) / 2
    if name in IMAGES:
        path = ROOT / "assets/toolbox" / IMAGES[name]
        mime = "image/svg+xml" if path.suffix == ".svg" else "image/png"
        data = base64.b64encode(path.read_bytes()).decode()
        mark = f'<image href="data:{mime};base64,{data}" x="{x + off}" y="{y + off}" width="{inner}" height="{inner}"/>'
    elif name == "bot":
        mark = (f'<g transform="translate({x + off},{y + off}) scale({inner / 24})" fill="none" stroke="{t["key"]}" '
                f'stroke-width="2" stroke-linecap="round" stroke-linejoin="round">{ICONS["bot"]}</g>')
    else:
        logo = LOGOS[name]
        colour = "#24292f" if logo.get("mono") else logo["color"]
        mark = (f'<g transform="translate({x + off},{y + off}) scale({inner / 24})" fill="{colour}">'
                f'<path d="{logo["d"]}"/></g>')
    return tile + mark


def big_tile(theme: str, t: dict, x: float, y: float, size: float, name: str, logo_name: str, advance: float) -> list[str]:
    """A square tile with the logo, and the name under it."""
    label = escape(name)
    return [f'<rect x="{x:.1f}" y="{y:.1f}" width="{size}" height="{size}" rx="{size * 0.2:.1f}" fill="{TILE_BG[theme]}" '
            f'stroke="{t["border"]}"/>',
            mark(logo_name, x + size * 0.22, y + size * 0.22, size * 0.56, t),
            f'<text x="{x + size / 2:.1f}" y="{y + size + 18:.1f}" font-size="12" fill="{t["fg"]}" '
            f'text-anchor="middle">{label}</text>']


def slot(name: str, size: float, advance: float) -> float:
    """Width a tile takes: its own, or its name's if that is wider."""
    return max(size, len(name) * advance * 12)


def grid(theme: str, t: dict, advance: float) -> tuple[list[str], int]:
    """A centred row of big tiles per group, the group's name above it."""
    size, gap, y = 54, 18, 20
    out = []
    for g, (folder, items) in enumerate(TILES):
        out.append(f'<text x="{WIDTH / 2}" y="{y + 14}" font-size="14" font-weight="700" fill="{t["key"]}" '
                   f'text-anchor="middle">{escape(folder)}/</text>')
        slots = [slot(name, size, advance) for name, _, _ in items]
        x = (WIDTH - sum(slots) - gap * (len(items) - 1)) / 2
        elems = []
        for (name, logo_name, _), w in zip(items, slots):
            elems += big_tile(theme, t, x + (w - size) / 2, y + 30, size, name, logo_name, advance)
            x += w + gap
        out.append(f'<g class="later" style="animation-delay:{0.2 + g * 0.15:.2f}s">' + "".join(elems) + "</g>")
        y += 30 + size + 46
    return out, y


def spread(items: list, rows: int) -> list:
    """Order the tiles so two with the same logo are never side by side in a strip (counting the wrap-around,
    since each strip loops). Deterministic: the first order, from a fixed sequence of shuffles, that works."""
    import random
    rng = random.Random(1)
    order = list(items)
    for _ in range(10000):
        size = (len(order) + rows - 1) // rows
        strips = [order[i:i + size] for i in range(0, len(order), size)]
        if all(a[1] != b[1] for strip in strips for a, b in zip(strip, strip[1:] + strip[:1])):
            return order
        rng.shuffle(order)
    raise ValueError("no order keeps equal logos apart")


def marquee(theme: str, t: dict, advance: float) -> tuple[list[str], int]:
    """Two strips of tiles that scroll for ever, in opposite directions."""
    items = spread([it for _, group in TILES for it in group], 2)
    half = (len(items) + 1) // 2
    size, gap = 54, 30
    out = ["<style>@keyframes left { to { transform: translateX(var(--d)); } } "
           "@keyframes right { from { transform: translateX(var(--d)); } to { transform: none; } } "
           "@media (prefers-reduced-motion: reduce) { .strip { animation: none !important; } }</style>"]
    for r, row in enumerate([items[:half], items[half:]]):
        y = 24 + r * (size + 44)
        slots = [slot(name, size, advance) + gap for name, _, _ in row]
        span = sum(slots)
        tiles = []
        for copy in range(3):  # three copies, so the strip never shows its end
            x = copy * span + 20
            for (name, logo_name, _), w in zip(row, slots):
                tiles += big_tile(theme, t, x + (w - gap - size) / 2, y, size, name, logo_name, advance)
                x += w
        direction = "left" if r == 0 else "right"
        out.append(f'<g class="strip" style="--d:-{span}px;animation:{direction} {len(row) * 2.2:.1f}s linear infinite">'
                   + "".join(tiles) + "</g>")
    fade = t["bg"]
    out.append(f'<linearGradient id="fadeL"><stop offset="0" stop-color="{fade}"/><stop offset="1" stop-color="{fade}" '
               f'stop-opacity="0"/></linearGradient><linearGradient id="fadeR"><stop offset="0" stop-color="{fade}" '
               f'stop-opacity="0"/><stop offset="1" stop-color="{fade}"/></linearGradient>')
    out.append(f'<rect width="90" height="{2 * (size + 44) + 20}" fill="url(#fadeL)"/>'
               f'<rect x="{WIDTH - 90}" width="90" height="{2 * (size + 44) + 20}" fill="url(#fadeR)"/>')
    return out, 2 * (size + 44) + 24


def periodic(theme: str, t: dict, advance: float) -> tuple[list[str], int]:
    """A periodic table: one column per group, each tool an element with its symbol, logo and name."""
    from banner import RAINBOW
    colours = [RAINBOW[0], RAINBOW[1], "#3fb950" if theme == "dark" else "#2da44e", "#d4a72c", RAINBOW[5]]
    w, h, gap = 140, 70, 8
    cols = len(TILES)
    x0 = (WIDTH - cols * w - (cols - 1) * 24) / 2
    out, deepest, n = [], 0, 0
    for c, (folder, items) in enumerate(TILES):
        x = x0 + c * (w + 24)
        col = colours[c]
        out.append(f'<text x="{x + w / 2:.1f}" y="30" font-size="12" font-weight="700" fill="{col}" '
                   f'text-anchor="middle">{escape(folder)}/</text>')
        for r, (name, logo_name, symbol) in enumerate(items):
            n += 1
            y = 44 + r * (h + gap)
            short = name
            out.append(f'<g class="later" style="animation-delay:{0.2 + n * 0.04:.2f}s">'
                       f'<rect x="{x:.1f}" y="{y}" width="{w}" height="{h}" rx="4" fill="{col}" fill-opacity="0.12" '
                       f'stroke="{col}"/>'
                       f'<text x="{x + 6:.1f}" y="{y + 13}" font-size="10" fill="{t["dim"]}">{n}</text>'
                       + mark(logo_name, x + w - 20, y + 5, 14, t) +
                       f'<text x="{x + w / 2:.1f}" y="{y + 42}" font-size="22" font-weight="700" fill="{t["fg"]}" '
                       f'text-anchor="middle">{escape(symbol)}</text>'
                       f'<text x="{x + w / 2:.1f}" y="{y + 60}" font-size="11" fill="{t["fg"]}" '
                       f'text-anchor="middle">{escape(short)}</text></g>')
            deepest = max(deepest, y + h)
    return out, deepest + 20


def plain_svg(theme: str, font_css: str, advance: float, layout: str) -> str:
    """The layouts without a window: the README's own background around them."""
    t = banner.colours(theme)
    body, height = {"grid": grid, "marquee": marquee, "periodic": periodic}[layout](theme, t, advance)
    return "\n".join([
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{height}" viewBox="0 0 {WIDTH} {height}" '
        f'font-family="{neofetch.FAMILY}">',
        f"<style>{font_css}\n{banner.CSS}</style>",
        *body, "</svg>",
    ])


def svg(theme: str, font_css: str, advance: float) -> str:
    t = banner.colours(theme)
    cw = advance * SIZE
    cmd, start = banner.prompt(PAD, BAR + 34, COMMAND, 0.4, t, advance, "t0")
    start += 0.3
    out, y = [], BAR + 34 + 20
    for g, (folder, items) in enumerate(GROUPS):
        y += 30
        group = [f'<text x="{PAD}" y="{y}" font-size="{SIZE}" font-weight="700" fill="{t["key"]}">{escape(folder)}/</text>']
        x, y_row = PAD, y + 12
        for name, mark in items:
            w = TILE + 8 + len(name) * cw
            if x + w > WIDTH - PAD:
                x, y_row = PAD, y_row + CHIP_H + 8
            group.append(logo(mark, x, y_row + (CHIP_H - TILE) / 2, t))
            group.append(f'<text x="{x + TILE + 8:.1f}" y="{y_row + CHIP_H / 2 + 5:.1f}" font-size="{SIZE}" '
                         f'fill="{t["fg"]}" xml:space="preserve" textLength="{len(name) * cw:.1f}" '
                         f'lengthAdjust="spacing">{escape(name)}</text>')
            x += w + GAP
        y = y_row + CHIP_H
        out.append(f'<g class="later" style="animation-delay:{start + g * 0.18:.2f}s;animation-duration:0.05s">'
                   + "".join(group) + "</g>")
    final, _ = banner.prompt(PAD, y + 44, "", start + len(GROUPS) * 0.18 + 0.2, t, advance, "t1", last=True)
    height = int(y + 74)
    before, after = window(theme, WIDTH, height)
    return "\n".join([
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{height}" viewBox="0 0 {WIDTH} {height}" '
        f'font-family="{neofetch.FAMILY}">',
        f"<style>{font_css}\n{banner.CSS}</style>",
        *before, *cmd, *out, *final, *after, "</svg>",
    ])


if __name__ == "__main__":
    args = sys.argv[1:]
    layout = next((a for a in args if a in ("ls", "grid", "marquee", "periodic")), LAYOUT)
    folder = Path(args[args.index("--out") + 1]) if "--out" in args else ROOT / "assets"
    used = banner.PROMPT + COMMAND + "".join(f + "/" + "".join(n for n, _ in items) for f, items in GROUPS) \
        + "".join(n + s for _, items in TILES for n, _, s in items) + "0123456789…"
    font_css, advance = neofetch.embedded_font(ROOT, neofetch.FONT_NAME, used)
    for theme in neofetch.THEMES:
        content = svg(theme, font_css, advance) if layout == "ls" else plain_svg(theme, font_css, advance, layout)
        (folder / f"toolbox-{theme}.svg").write_text(content, encoding="utf-8")
