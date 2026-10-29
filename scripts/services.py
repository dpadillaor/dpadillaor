"""Builds assets/services-{light,dark}.svg: what I do, as a terminal window.

The eight services of the website's home page (content/en/portada.yml in the portfolio), with their icons.
Two layouts, so they can be compared:  python scripts/services.py [tree|panes] [--out <folder>]
"""

import sys
from html import escape
from pathlib import Path

import banner
import neofetch
from terminal import BAR, PAD, window

WIDTH = 1068   # same as the terminal on top
LAYOUT = "tree"

# Lucide icons (lucide.dev, ISC licence), as on the website: src/lib/contenido/iconos.ts
ICONS = {
    "ojo": '<path d="M3 7V5a2 2 0 0 1 2-2h2" /><path d="M17 3h2a2 2 0 0 1 2 2v2" /><path d="M21 17v2a2 2 0 0 1-2 2h-2" /><path d="M7 21H5a2 2 0 0 1-2-2v-2" /><circle cx="12" cy="12" r="1" /><path d="M18.944 12.33a1 1 0 0 0 0-.66 7.5 7.5 0 0 0-13.888 0 1 1 0 0 0 0 .66 7.5 7.5 0 0 0 13.888 0" />',
    "cubo": '<path d="M21 8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16Z" /><path d="m3.3 7 8.7 5 8.7-5" /><path d="M12 22V12" />',
    "cerebro": '<path d="M12 5a3 3 0 1 0-5.997.125 4 4 0 0 0-2.526 5.77 4 4 0 0 0 .556 6.588A4 4 0 1 0 12 18Z" /><path d="M9 13a4.5 4.5 0 0 0 3-4" /><path d="M6.003 5.125A3 3 0 0 0 6.401 6.5" /><path d="M3.477 10.896a4 4 0 0 1 .585-.396" /><path d="M6 18a4 4 0 0 1-1.967-.516" /><path d="M12 13h4" /><path d="M12 18h6a2 2 0 0 1 2 2v1" /><path d="M12 8h8" /><path d="M16 8V5a2 2 0 0 1 2-2" /><circle cx="16" cy="13" r=".5" /><circle cx="18" cy="3" r=".5" /><circle cx="20" cy="21" r=".5" /><circle cx="20" cy="8" r=".5" />',
    "rayo": '<path d="M4 14a1 1 0 0 1-.78-1.63l9.9-10.2a.5.5 0 0 1 .86.46l-1.92 6.02A1 1 0 0 0 13 10h7a1 1 0 0 1 .78 1.63l-9.9 10.2a.5.5 0 0 1-.86-.46l1.92-6.02A1 1 0 0 0 11 14z" />',
    "bot": '<path d="M12 8V4H8" /><rect width="16" height="12" x="4" y="8" rx="2" /><path d="M2 14h2" /><path d="M20 14h2" /><path d="M15 13v2" /><path d="M9 13v2" />',
    "documentos": '<path d="M21 7h-3a2 2 0 0 1-2-2V2" /><path d="M21 6v6.5c0 .8-.7 1.5-1.5 1.5h-7c-.8 0-1.5-.7-1.5-1.5v-9c0-.8.7-1.5 1.5-1.5H17Z" /><path d="M7 8v8.8c0 .3.2.6.4.8.2.2.5.4.8.4H15" /><path d="M3 12v8.8c0 .3.2.6.4.8.2.2.5.4.8.4H11" />',
    "antena": '<path d="M4.9 16.1C1 12.2 1 5.8 4.9 1.9" /><path d="M7.8 4.7a6.14 6.14 0 0 0-.8 7.5" /><circle cx="12" cy="9" r="2" /><path d="M16.2 4.8c2 2 2.26 5.11.8 7.47" /><path d="M19.1 1.9a9.96 9.96 0 0 1 0 14.1" /><path d="M9.5 18h5" /><path d="m8 22 4-11 4 11" />',
    "indicador": '<path d="m12 14 4-4" /><path d="M3.34 19a10 10 0 1 1 17.32 0" />',
}

# (group, [(folder name, category, title, icon)]): the groups follow the introduction (see / read and act)
SERVICES = [
    ("see", [
        ("computer-vision", "Computer vision", "Cameras that tell you what they see", "ojo"),
        ("spatial-intelligence", "Spatial intelligence", "Understanding 3D, not just navigating it", "cubo"),
        ("model-deployment", "Model deployment", "Faster, lighter, cheaper", "rayo"),
    ]),
    ("think-and-act", [
        ("machine-learning", "Machine learning", "Models trained on your data", "cerebro"),
        ("ai-agents", "AI agents", "AI that works, not just chats", "bot"),
        ("digitalisation", "Digitalisation", "Goodbye to spreadsheets and paper", "documentos"),
    ]),
    ("connect", [
        ("iot", "IoT", "Your equipment data, all in one place", "antena"),
        ("digital-twins", "Digital twins", "Your facility, in digital form", "indicador"),
    ]),
]
COMMAND = {"tree": "tree what-i-do/", "panes": "services --all"}
LH, SIZE = 27, 15


def icon(name: str, x: float, y: float, size: float, colour: str) -> str:
    return (f'<g transform="translate({x},{y}) scale({size / 24})" fill="none" stroke="{colour}" stroke-width="2" '
            f'stroke-linecap="round" stroke-linejoin="round">{ICONS[name]}</g>')


def line(x: float, y: float, parts: list, advance: float, size: float = SIZE, extra: str = "") -> str:
    n = sum(len(s) for s, _ in parts)
    spans = "".join(f'<tspan fill="{c}">{escape(s)}</tspan>' for s, c in parts)
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" xml:space="preserve" textLength="{n * advance * size:.1f}" '
            f'lengthAdjust="spacing"{extra}>{spans}</text>')


def appear(delay: float) -> str:
    return f' class="later" style="animation-delay:{delay:.2f}s;animation-duration:0.05s"'


def tree(t: dict, advance: float, top: float, start: float) -> tuple[list[str], float]:
    """`tree` output: a folder per group, a line per service with an icon and its title right-aligned."""
    cw = advance * SIZE
    out, y, i = [], top, 0
    out.append(f'<g{appear(start)}>' + line(PAD, y, [("what-i-do/", t["fg"])], advance) + "</g>")
    right = WIDTH - PAD
    for g, (group, items) in enumerate(SERVICES):
        last_group = g == len(SERVICES) - 1
        y += LH
        i += 1
        x0 = PAD + cw * 0.5
        elems = [f'<line x1="{x0:.1f}" x2="{x0:.1f}" y1="{y - LH + 6:.1f}" y2="{y - 5 if last_group else y + 6:.1f}" stroke="{t["dim"]}"/>',
                 f'<line x1="{x0:.1f}" x2="{x0 + 16:.1f}" y1="{y - 5:.1f}" y2="{y - 5:.1f}" stroke="{t["dim"]}"/>',
                 line(x0 + 24, y, [(group + "/", t["key"])], advance, extra=' font-weight="700"')]
        out.append(f'<g{appear(start + i * 0.08)}>' + "".join(elems) + "</g>")
        for k, (name, _, title, ic) in enumerate(items):
            y += LH
            i += 1
            last = k == len(items) - 1
            x1 = x0 + 24 + cw * 0.5
            elems = []
            if not last_group:  # the group's line carries on past its children
                elems.append(f'<line x1="{x0:.1f}" x2="{x0:.1f}" y1="{y - LH + 6:.1f}" y2="{y + 6:.1f}" stroke="{t["dim"]}"/>')
            elems += [f'<line x1="{x1:.1f}" x2="{x1:.1f}" y1="{y - LH + 6:.1f}" y2="{y - 5 if last else y + 6:.1f}" stroke="{t["dim"]}"/>',
                      f'<line x1="{x1:.1f}" x2="{x1 + 16:.1f}" y1="{y - 5:.1f}" y2="{y - 5:.1f}" stroke="{t["dim"]}"/>',
                      icon(ic, x1 + 24, y - 15, 18, t["key"])]
            name_x = x1 + 50
            dots = int((right - name_x) / cw) - len(name) - len(title) - 2
            elems.append(line(name_x, y, [(name, t["fg"]), (" " + "." * dots + " ", t["dim"]), (title, t["fg"])], advance))
            out.append(f'<g{appear(start + i * 0.08)}>' + "".join(elems) + "</g>")
    return out, y


def wrap(text: str, width: int) -> list[str]:
    lines, cur = [], ""
    for word in text.split():
        if cur and len(cur) + 1 + len(word) > width:
            lines.append(cur)
            cur = word
        else:
            cur = f"{cur} {word}".strip()
    return lines + [cur]


def panes(t: dict, advance: float, top: float, start: float) -> tuple[list[str], float]:
    """A grid of panes, as in tmux: the category on the border, the icon and the title inside."""
    items = [it for _, group in SERVICES for it in group]
    cols, gap, h = 4, 12, 132
    w = (WIDTH - 2 * PAD - (cols - 1) * gap) / cols
    out = []
    for n, (_, category, title, ic) in enumerate(items):
        x, y = PAD + (n % cols) * (w + gap), top + (n // cols) * (h + gap)
        label = f" {category} "
        lw = len(label) * advance * 13
        elems = [f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h}" rx="4" fill="none" stroke="{t["border"]}"/>',
                 f'<rect x="{x + 12:.1f}" y="{y - 8:.1f}" width="{lw:.1f}" height="16" fill="{t["bg"]}"/>',
                 line(x + 12, y + 4.5, [(label, t["key"])], advance, 13, ' font-weight="700"'),
                 icon(ic, x + 16, y + 22, 26, t["key"])]
        for k, text in enumerate(wrap(title, int((w - 32) / (advance * SIZE)))):
            elems.append(line(x + 16, y + 76 + k * 21, [(text, t["fg"])], advance))
        out.append(f'<g{appear(start + n * 0.12)}>' + "".join(elems) + "</g>")
    return out, top + 2 * (h + gap) - gap


def svg(theme: str, font_css: str, advance: float, layout: str) -> str:
    t = banner.colours(theme)
    cmd, typed_end = banner.prompt(PAD, BAR + 34, COMMAND[layout], 0.4, t, advance, "s0")
    body, bottom = (tree if layout == "tree" else panes)(t, advance, BAR + 34 + (34 if layout == "tree" else 46),
                                                         typed_end + 0.3)
    end = typed_end + 0.3 + 1.2
    final, _ = banner.prompt(PAD, bottom + 40, "", end, t, advance, "s1", last=True)
    height = int(bottom + 70)
    before, after = window(theme, WIDTH, height, "david@padilla: ~")
    return "\n".join([
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{height}" viewBox="0 0 {WIDTH} {height}" '
        f'font-family="{neofetch.FAMILY}">',
        f"<style>{font_css}\n{banner.CSS}</style>",
        *before, *cmd, *body, *final, *after, "</svg>",
    ])


if __name__ == "__main__":
    root = Path(__file__).resolve().parent.parent
    args = sys.argv[1:]
    layout = next((a for a in args if a in COMMAND), LAYOUT)
    folder = Path(args[args.index("--out") + 1]) if "--out" in args else root / "assets"
    used = banner.PROMPT + "".join(COMMAND.values()) + "what-i-do/. " + "".join(
        g + "/" + "".join(n + c + ti for n, c, ti, _ in items) for g, items in SERVICES)
    font_css, advance = neofetch.embedded_font(root, neofetch.FONT_NAME, used)
    for theme in neofetch.THEMES:
        (folder / f"services-{theme}.svg").write_text(svg(theme, font_css, advance, layout), encoding="utf-8")
