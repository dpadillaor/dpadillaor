"""Builds assets/banner-{light,dark}.svg: the LinkedIn cover redone as a terminal.

The knot is drawn with characters, each in the colour it has in the cover (assets/portada.png); the headline is
typed out after a prompt, with a blinking cursor. Same typeface as the card, embedded the same way.
Its pieces (`body`, `typed`, `cursor`, `CSS`) are also used by scripts/terminal.py.

Run from the repo root:  python scripts/banner.py
"""

import random
from html import escape
from pathlib import Path

import numpy as np
from PIL import Image

from neofetch import FAMILY, FONT_NAME, THEMES, embedded_font

W, H = 1280, 320                  # size of the banner, in px
KNOT_SRC = (980, 0, 1584, 384)    # the knot in the cover, in its pixels (without its rainbow strip)
CELL_W, CELL_H = 6, 10            # size of each character of the knot
KNOT_CHARS = " .:-=+*#%@"         # from empty to dense
KNOT_FLICKERS = 40

PROMPT = "david@padilla:~$ "
COMMAND = "cat mission.txt"
LINE1 = [("Engineering", "fg", 700), (" built around", "dim2", 400)]
LINE2 = [("your challenges", "key", 700)]
TAGS = "Computer vision · 3D · AI · LLMs · Automation"
SITE = "davidpadilla.eu"
RAINBOW = ["#4f8ff7", "#5ac8d8", "#8ee07a", "#f5e663", "#f7a541", "#f2645a"]
TEXT = PROMPT + COMMAND + "".join(s for s, _, _ in LINE1 + LINE2) + TAGS + SITE + KNOT_CHARS + "·"

CSS = """
  .type { animation-fill-mode: both; }
  @keyframes type { from { width: 0; } to { width: var(--w); } }
  @keyframes walk { from { transform: translateX(0); } to { transform: translateX(var(--w)); } }
  @keyframes during { from, to { opacity: 1; } }
  @keyframes blink { 0%, 49% { opacity: 1; } 50%, 100% { opacity: 0; } }
  .later { opacity: 0; animation: show 0.4s ease-out forwards; }
  @keyframes show { to { opacity: 1; } }
  .k { animation: flick 6s steps(1, end) infinite; }
  @keyframes flick { 0%, 92% { opacity: 1; } 93%, 95% { opacity: 0.15; } 96%, 100% { opacity: 1; } }
  @media (prefers-reduced-motion: reduce) {
    .type, .later, .k { animation: none; opacity: 1; }
    .type { width: var(--w); }
    .walker { animation: none; opacity: 0; }
    .walker.last { opacity: 1; }
  }
"""


def colours(theme: str) -> dict:
    return dict(THEMES[theme], dim2="#57606a" if theme == "light" else "#8b949e")


def knot(theme: str, x0: float, y0: float, width: float, height: float) -> list[str]:
    """One <text> per character of the knot: denser where the cover has more colour, in that colour."""
    cover = Image.open(Path(__file__).resolve().parent.parent / "assets/portada.png").convert("RGB").crop(KNOT_SRC)
    cols, rows = int(width // CELL_W), int(height // CELL_H)
    small = np.asarray(cover.resize((cols, rows), Image.BOX), dtype=float)
    ink = 1 - small.min(-1) / 255
    out, rng = [], random.Random(3)
    for y in range(rows):
        for x in range(cols):
            level = ink[y, x]
            if level < 0.08:
                continue
            ch = KNOT_CHARS[min(len(KNOT_CHARS) - 1, 1 + int(level * 1.4 * (len(KNOT_CHARS) - 1)))]
            r, g, b = small[y, x].astype(int)
            if theme == "dark":  # the pale, faded dots of the cover would glow on a dark background: dim them
                fade = min(1.0, level * 1.6)
                r, g, b = (int(c * fade + 13 * (1 - fade)) for c in (r, g, b))
            flick = ""
            if rng.random() < KNOT_FLICKERS / (rows * cols * 0.35):
                flick = f' class="k" style="animation-duration:{rng.uniform(3, 9):.1f}s;animation-delay:-{rng.uniform(0, 9):.1f}s"'
            out.append(f'<text x="{x0 + x * CELL_W:.0f}" y="{y0 + (y + 1) * CELL_H - 2:.0f}" font-size="{CELL_W / 0.6:.1f}" '
                       f'fill="#{r:02x}{g:02x}{b:02x}"{flick}>{escape(ch)}</text>')
    return out


def cursor(x: float, y: float, size: float, n: int, width: float, start: float, speed: float, colour: str,
           last: bool = False) -> str:
    """A block that walks along the line while it types, one character at a time. Only visible while typing;
    the last one stays at the end, blinking. Steps with jump-none: the last step is exactly the end (with a plain
    steps(n), Chrome stops one character short on short lines)."""
    blink = f", blink 1.1s steps(1) {start + n * speed:.2f}s infinite" if last else ""
    return (f'<rect class="walker{" last" if last else ""}" x="{x}" y="{y - size * 0.8:.1f}" width="{size * 0.55:.1f}" '
            f'height="{size:.1f}" fill="{colour}" opacity="0" style="--w:{width:.1f}px;animation:walk '
            f'{n * speed:.2f}s steps({n + 1}, jump-none) {start:.2f}s both, during {n * speed:.2f}s {start:.2f}s{blink}"/>')


def typed(x: float, y: float, parts: list, size: float, start: float, speed: float, t: dict, advance: float,
          ident: str, last: bool = False) -> tuple[list[str], float]:
    """A line that types itself out: a clip that grows one character at a time, with the cursor in front.
    Returns the elements and when it finishes."""
    n = sum(len(s) for s, _, _ in parts)
    spans = "".join(f'<tspan fill="{t[c]}" font-weight="{w}">{escape(s)}</tspan>' for s, c, w in parts)
    width = n * advance * size
    return [
        cursor(x, y, size, n, width, start, speed, t["key"], last),
        f'<clipPath id="{ident}"><rect class="type" x="{x}" y="{y - size}" width="{width:.1f}" height="{size * 1.4:.1f}" '
        f'style="--w:{width:.1f}px;animation:type {n * speed:.2f}s steps({n + 1}, jump-none) {start:.2f}s both"/></clipPath>',
        f'<text x="{x}" y="{y}" font-size="{size}" clip-path="url(#{ident})" xml:space="preserve" '
        f'textLength="{width:.1f}" lengthAdjust="spacing">{spans}</text>',
    ], start + n * speed


def prompt(x: float, y: float, command: str, start: float, t: dict, advance: float, ident: str,
           size: float = 15, last: bool = False) -> tuple[list[str], float]:
    """The prompt appears at once; the command after it is typed."""
    width = len(PROMPT) * advance * size
    out = [f'<text class="later" style="animation-delay:{start:.2f}s;animation-duration:0.01s" x="{x}" y="{y}" '
           f'font-size="{size}" fill="{t["key"]}" xml:space="preserve" textLength="{width:.1f}" '
           f'lengthAdjust="spacing">{escape(PROMPT)}</text>']
    if not command:
        out.append(cursor(x + width, y, size, 1, 0, start, 0.01, t["key"], last=True))
        return out, start
    more, end = typed(x + width, y, [(command, "dim2", 400)], size, start + 0.3, 0.045, t, advance, ident, last)
    return out + more, end


def body(theme: str, advance: float, x: float, y: float, width: float, start: float = 0.0,
         with_prompt: bool = True, knot_w: float = 480) -> tuple[list[str], float, float]:
    """The mission: prompt and command, headline typed out, tags and site, the knot on the right.
    Returns the elements, when the typing ends and the height used."""
    t = colours(theme)
    out, top = [], y
    if with_prompt:
        out, start = prompt(x, y + 12, COMMAND, start, t, advance, "p0")
        top = y + 30
    # the knot is part of the output: it shows up as the headline starts
    out += [f'<g class="later" style="animation-delay:{start + 0.2:.2f}s">',
            *knot(theme, x + width - knot_w, y - 20, knot_w, 300), "</g>"]
    line1, end1 = typed(x, top + 52, LINE1, 44, start + 0.3, 0.05, t, advance, "l1")
    line2, end2 = typed(x, top + 106, LINE2, 44, end1, 0.05, t, advance, "l2", last=not with_prompt)
    out += line1 + line2
    out.append(f'<text class="later" style="animation-delay:{end2 + 0.1:.2f}s" x="{x}" y="{top + 148}" font-size="17" '
               f'fill="{t["fg"]}" xml:space="preserve" textLength="{len(TAGS) * advance * 17:.1f}" '
               f'lengthAdjust="spacing">{escape(TAGS)}</text>')
    out.append(f'<text class="later" style="animation-delay:{end2 + 0.3:.2f}s" x="{x}" y="{top + 182}" font-size="15" '
               f'font-weight="700" fill="{t["key"]}">{escape(SITE)}</text>')
    return out, end2 + 0.4, top + 200 - y


def dots(x: float, y: float, t: dict) -> list[str]:
    """The grid of dots in the corner of the cover, fading out, with one orange."""
    out = []
    for gy in range(6):
        for gx in range(9):
            fade = max(0.0, 1 - (gx + gy * 1.3) / 9)
            if fade <= 0.05:
                continue
            orange = (gx, gy) == (2, 2)
            out.append(f'<text x="{x + gx * 22}" y="{y + gy * 22}" font-size="18" fill="{t["key"] if orange else t["dim"]}" '
                       f'opacity="{1 if orange else fade:.2f}">·</text>')
    return out


def rainbow(x: float, y: float, width: float, height: float) -> list[str]:
    stops = "".join(f'<stop offset="{i / (len(RAINBOW) - 1):.2f}" stop-color="{c}"/>' for i, c in enumerate(RAINBOW))
    return [f'<linearGradient id="rainbow">{stops}</linearGradient>',
            f'<rect x="{x}" y="{y}" width="{width}" height="{height}" fill="url(#rainbow)"/>']


def svg(theme: str, font_css: str, advance: float) -> str:
    t = colours(theme)
    elements, _, _ = body(theme, advance, 300, 60, W - 300, start=0.3)
    return "\n".join([
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="{FAMILY}">',
        f"<style>{font_css}\n{CSS}</style>",
        f'<rect width="{W}" height="{H}" fill="{t["bg"]}"/>',
        *dots(14, 22, t),
        *elements,
        *rainbow(0, H - 6, W, 6),
        "</svg>",
    ])


if __name__ == "__main__":
    root = Path(__file__).resolve().parent.parent
    font_css, advance = embedded_font(root, FONT_NAME, TEXT)
    for theme in THEMES:
        (root / f"assets/banner-{theme}.svg").write_text(svg(theme, font_css, advance), encoding="utf-8")
