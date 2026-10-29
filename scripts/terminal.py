"""Builds assets/terminal-{light,dark}.svg: one terminal window with a session that types itself out.

    david@padilla:~$ cat mission.txt     -> the headline of the cover, with the knot
    david@padilla:~$ neofetch            -> the ASCII portrait and the card
    david@padilla:~$ _

Made of the pieces of scripts/banner.py and scripts/neofetch.py, so the images always match. `window` is the
frame, also used by scripts/services.py.
Run from the repo root:  python scripts/terminal.py
"""

from pathlib import Path

import banner
import neofetch

BAR = 38          # height of the title bar
PAD = 28          # left and right margin inside the window
TITLE = "david@padilla: ~"
LIGHTS = ["#ff5f57", "#febc2e", "#28c840"]

REVEAL_CSS = """
  @keyframes grow { from { height: 0; } to { height: var(--h); } }
  .reveal { animation: grow 0.9s steps(30) both; }
  @media (prefers-reduced-motion: reduce) { .reveal { animation: none; height: var(--h); } }
"""


def window(theme: str, width: float, height: float, title: str = TITLE) -> tuple[list[str], list[str]]:
    """The window around a session: what goes before its content and what goes after."""
    t = banner.colours(theme)
    frame = "#f6f8fa" if theme == "light" else "#161b22"
    before = [
        f'<clipPath id="window"><rect width="{width}" height="{height}" rx="10"/></clipPath>',
        '<g clip-path="url(#window)">',
        f'<rect width="{width}" height="{height}" fill="{t["bg"]}"/>',
        # title bar: the three lights and the title
        f'<rect width="{width}" height="{BAR}" fill="{frame}"/>',
        f'<line x1="0" x2="{width}" y1="{BAR - 0.5}" y2="{BAR - 0.5}" stroke="{t["border"]}"/>',
        *(f'<circle cx="{20 + i * 20}" cy="{BAR / 2}" r="6" fill="{c}"/>' for i, c in enumerate(LIGHTS)),
        f'<text x="{width / 2}" y="{BAR / 2 + 5}" font-size="13" fill="{t["dim"]}" text-anchor="middle">{title}</text>',
    ]
    after = [
        *banner.rainbow(0, height - 4, width, 4),
        "</g>",
        f'<rect x="0.5" y="0.5" width="{width - 1}" height="{height - 1}" rx="10" fill="none" stroke="{t["border"]}"/>',
    ]
    return before, after


def svg(theme: str, art: list[str], font_css: str, advance: float) -> str:
    t = banner.colours(theme)
    card, card_w, card_h = neofetch.body(theme, art, advance, right=neofetch.ALIGN == "right")
    width = card_w + 2 * (PAD - 24)

    mission, t1, h1 = banner.body(theme, advance, PAD, BAR + 26, width - 2 * PAD, start=0.5, knot_w=400)
    y2 = BAR + 26 + h1 + 44
    command, t2 = banner.prompt(PAD, y2, "neofetch", t1 + 0.4, t, advance, "p1")
    y_card = y2 + 6
    y3 = y_card + card_h + 10
    final, _ = banner.prompt(PAD, y3, "", t2 + 1.1, t, advance, "p2", last=True)
    height = int(y3 + 30)
    before, after = window(theme, width, height)

    return "\n".join([
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" '
        f'font-family="{neofetch.FAMILY}">',
        f"<style>{font_css}\n{banner.CSS}\n{neofetch.GLITCH_CSS}\n{REVEAL_CSS}</style>",
        *before,
        *mission,
        *command,
        # the output of neofetch prints top to bottom
        f'<clipPath id="out"><rect class="reveal" x="0" y="{y_card}" width="{width}" height="{card_h}" '
        f'style="--h:{card_h}px;animation-delay:{t2 + 0.2:.2f}s"/></clipPath>',
        f'<g clip-path="url(#out)"><g transform="translate({PAD - 24},{y_card})">',
        *card,
        "</g></g>",
        *final,
        *after,
        "</svg>",
    ])


if __name__ == "__main__":
    root = Path(__file__).resolve().parent.parent
    used = banner.TEXT + "neofetch" + TITLE + "".join(k + v for k, v in neofetch.CARD) + ":.-" + neofetch.CHARS \
        + neofetch.GLITCH_SYMBOLS
    font_css, advance = neofetch.embedded_font(root, neofetch.FONT_NAME, used)
    for theme in neofetch.THEMES:
        art = neofetch.ascii_portrait(root / "assets/retrato.jpg", theme)
        (root / f"assets/terminal-{theme}.svg").write_text(svg(theme, art, font_css, advance), encoding="utf-8")
