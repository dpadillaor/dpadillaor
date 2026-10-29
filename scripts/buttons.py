"""Builds the link buttons under the terminal: assets/buttons/<style>-<name>-<theme>.svg.

Each button is its own image, so each one can be a separate link in the README. Same typeface and colours as
the terminal. Run from the repo root:  python scripts/buttons.py [style ...]   (no style: the one in STYLE)
"""

import base64
import sys
from html import escape
from pathlib import Path

from neofetch import FAMILY, FONT_NAME, THEMES, embedded_font

ROOT = Path(__file__).resolve().parent.parent
SIZE, H = 14, 34   # font size and button height

# the icons of the website (src/lib/contenido/iconos.ts in the portfolio), 24×24
LINKEDIN = ('<path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 '
            '2.939v5.667H9.351V9h3.414v1.561h.046c.477-.948 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 '
            '5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 '
            '2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 '
            '0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 '
            '0 22.222 0h.003z"/>')
MAIL = ('<path d="M2 6.5A2.5 2.5 0 0 1 4.5 4h15A2.5 2.5 0 0 1 22 6.5v.3l-10 6.1L2 6.8v-.3Z"/>'
        '<path d="M2 9.1v8.4A2.5 2.5 0 0 0 4.5 20h15a2.5 2.5 0 0 0 2.5-2.5V9.1l-9.48 5.78a1 1 0 0 1-1.04 0L2 9.1Z"/>')
LOGO = base64.b64encode((ROOT / "assets/logo-64.png").read_bytes()).decode()

# name: (icon, plain label, label as a command)
BUTTONS = {
    "website": ("logo", "davidpadilla.eu", ("open", "davidpadilla.eu")),
    "linkedin": (LINKEDIN, "LinkedIn", ("open", "linkedin")),
    "email": (MAIL, "me@davidpadilla.eu", ("mail", "me@davidpadilla.eu")),
}


def icon(kind: str, x: float, y: float, size: float, colour: str) -> str:
    if kind == "logo":
        return f'<image href="data:image/png;base64,{LOGO}" x="{x}" y="{y}" width="{size}" height="{size}"/>'
    return f'<g transform="translate({x},{y}) scale({size / 24})" fill="{colour}">{kind}</g>'


def text(x: float, parts: list, advance: float) -> str:
    n = sum(len(s) for s, _ in parts)
    spans = "".join(f'<tspan fill="{c}">{escape(s)}</tspan>' for s, c in parts)
    return (f'<text x="{x}" y="{H / 2 + SIZE * 0.36:.1f}" font-size="{SIZE}" xml:space="preserve" '
            f'textLength="{n * advance * SIZE:.1f}" lengthAdjust="spacing">{spans}</text>')


def button(style: str, name: str, theme: str, font_css: str, advance: float) -> str:
    t = THEMES[theme]
    kind, label, (verb, target) = BUTTONS[name]
    cw = advance * SIZE
    frame = "#f6f8fa" if theme == "light" else "#161b22"
    shadow = "#d0d7de" if theme == "light" else "#30363d"
    main = name == "website"
    ic = 16
    if style == "command":      # $ open davidpadilla.eu
        parts = [("$ ", t["key"]), (verb + " ", t["dim"]), (target, t["fg"])]
        n = sum(len(s) for s, _ in parts)
        w = 14 + n * cw + 14
        body = [f'<rect x="0.5" y="0.5" width="{w - 1:.1f}" height="{H - 1}" rx="6" fill="{t["bg"]}" stroke="{t["border"]}"/>',
                text(14, parts, advance)]
    elif style == "pill":       # icon + label, the website one filled in orange
        fg = "#ffffff" if main else t["fg"]
        w = 14 + ic + 8 + len(label) * cw + 16
        fill, stroke = (t["key"], t["key"]) if main else (t["bg"], t["border"])
        body = [f'<rect x="0.5" y="0.5" width="{w - 1:.1f}" height="{H - 1}" rx="{H / 2}" fill="{fill}" stroke="{stroke}"/>',
                icon(kind, 14, (H - ic) / 2, ic, fg), text(14 + ic + 8, [(label, fg)], advance)]
    elif style == "brackets":   # [ icon label ↗ ]  (the arrow is drawn: the typeface has none)
        x = 2 + 2 * cw + ic + 8
        end = x + len(label) * cw + 6
        body = [text(2, [("[ ", t["key"])], advance), icon(kind, 2 + 2 * cw, (H - ic) / 2, ic, t["fg"]),
                text(x, [(label, t["fg"])], advance),
                f'<path d="M{end} {H / 2 + 4} l8 -8 M{end + 2} {H / 2 - 4} h6 v6" fill="none" stroke="{t["key"]}" '
                f'stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/>',
                text(end + 8, [(" ]", t["key"])], advance)]
        w = end + 8 + 2 * cw + 2
    else:                       # key: a keyboard key, with its edge underneath
        w = 12 + ic + 8 + len(label) * cw + 14
        body = [f'<rect x="0.5" y="3.5" width="{w - 1:.1f}" height="{H - 4}" rx="6" fill="{shadow}"/>',
                f'<rect x="0.5" y="0.5" width="{w - 1:.1f}" height="{H - 4}" rx="6" fill="{frame}" stroke="{t["border"]}"/>',
                f'<g transform="translate(0,-2)">', icon(kind, 12, (H - ic) / 2, ic, t["key"] if not main else t["fg"]),
                text(12 + ic + 8, [(label, t["fg"])], advance), "</g>"]
    w = int(w + 1)
    return "\n".join([
        f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{w}" height="{H}" '
        f'viewBox="0 0 {w} {H}" font-family="{FAMILY}">',
        f"<style>{font_css}</style>", *body, "</svg>"])


STYLES = ["command", "pill", "brackets", "key"]
STYLE = "key"   # the one the README uses; the others are kept to try them again

if __name__ == "__main__":
    styles = sys.argv[1:] or [STYLE]
    used = "".join(label + verb + target for _, label, (verb, target) in BUTTONS.values()) + "$ []"
    font_css, advance = embedded_font(ROOT, FONT_NAME, used)
    (ROOT / "assets/buttons").mkdir(exist_ok=True)
    for style in styles:
        for name in BUTTONS:
            for theme in THEMES:
                (ROOT / f"assets/buttons/{style}-{name}-{theme}.svg").write_text(
                    button(style, name, theme, font_css, advance), encoding="utf-8")
