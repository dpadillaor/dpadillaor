"""Builds assets/neofetch-{light,dark}.svg: my portrait in ASCII on the left, a terminal-style card on the right.

Run from the repo root:  python scripts/neofetch.py  (needs Pillow, NumPy, SciPy and fontTools with brotli)
Options:  --left, --right  override ALIGN for one run (to compare both)
          --out <folder>   write somewhere else (to compare versions)

The typeface travels inside the SVG (only the characters it uses), so everyone sees the same one.
"""

import base64
import io
import random
import sys
from html import escape
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter
from fontTools import subset
from fontTools.ttLib import TTFont
from scipy import ndimage

CROP = (330, 60, 1170, 1080)  # head and top of the shoulders, in pixels of the portrait
COLS, ROWS = 100, 61          # size of the ASCII portrait, in characters
CHARS = " .,:;i1tfLCG08@"     # from empty to dense
DETAIL = 1.0                  # how much local contrast is boosted (brows, eyelids, beard)
KEEP_DARK = 25                # percentile kept when shrinking, so thin dark lines (lashes, iris) survive
FONT_NAME = "jetbrains-mono"  # assets/fonts/<name>-400.woff2 and -700.woff2
ART_CW, ART_LH = 3.8, 7.6     # portrait: character width and line height (px); the font size follows from the width
FONT, LH = 14, 21             # card: font size and line height, in px

CARD = [
    ("title", "david@padilla"),
    ("Role", "Engineer · computer vision, AI and robotics"),
    ("Location", "Valencia, Spain · Remote"),
    ("Focus", "Computer vision · 3D · AI · LLMs · Automation"),
    ("", ""),
    ("Education.BSc", "Industrial engineering · Jaume I University"),
    ("Education.BSc", "Mechanical engineering, mechatronics · INSA Lyon"),
    ("Education.MSc", "Industrial engineering · Jaume I University"),
    ("Education.MSc", "Robotics, graphics and computer vision · UNIZAR"),
    ("", ""),
    ("Languages.Code", "Python, C++, Rust, TypeScript, MATLAB"),
    ("Languages.Real", "Spanish, Catalan, English, French"),
    ("", ""),
    ("Stack.DL", "PyTorch, LibTorch, CUDA, ONNX, TensorRT"),
    ("Stack.Models", "YOLO, SAM 2/3, DINOv2, CLIP, SigLIP"),
    ("Stack.Vision3D", "OpenCV, Open3D, COLMAP, Rerun"),
    ("Stack.Infra", "Docker, Linux, Git, CMake"),
    ("", ""),
    ("section", "Contact"),
    ("Website", "davidpadilla.eu"),
    ("Email", "me@davidpadilla.eu"),
    ("LinkedIn", "in/david-padilla-orenga"),
]
GLITCHES = 70               # characters of the portrait that flicker now and then
GLITCH_ROWS = 4             # rows that jump sideways now and then
GLITCH_SYMBOLS = "#%&*/<>?[]{}01"
# How values sit in the card. Change this one word to switch:
#   "right": each value ends at the right edge, under the end of the rules, and the dots fill whatever gap is left
#             (the neofetch look, and the card reads as a clean rectangle next to the portrait)
#   "left":  all values start in the same column, after a fixed run of dots (quicker to scan, ragged right edge)
ALIGN = "right"
FAMILY = "Card,ui-monospace,SFMono-Regular,Menlo,Consolas,monospace"
KEY_W, DOTS_TO = 16, 18      # key column and where the dot leader ends

THEMES = {
    "light": dict(bg="#ffffff", fg="#24292f", key="#ff5a1f", dim="#8c959f", border="#d0d7de", art="#57606a"),
    "dark": dict(bg="#0d1117", fg="#c9d1d9", key="#ff7a45", dim="#6e7681", border="#30363d", art="#c9d1d9"),
}


def person_mask(photo: Image.Image) -> Image.Image:
    """Me without the wall. The wall is light, almost colourless and smooth; whatever looks like that and touches
    the edge of the photo is wall. A few pixels are shaved off the outline so no pale fringe of wall is left."""
    rgb = np.asarray(photo.convert("RGB"), dtype=float)
    grey = ndimage.gaussian_filter(rgb @ [0.299, 0.587, 0.114], 2)
    colour = rgb.max(-1) - rgb.min(-1)
    edges = np.hypot(ndimage.sobel(grey, 0), ndimage.sobel(grey, 1))
    regions, _ = ndimage.label((grey > 150) & (colour < 45) & (edges < 40))
    touching = np.unique(np.concatenate([regions[0], regions[:, 0], regions[:, -1]]))
    wall = ndimage.binary_opening(np.isin(regions, touching[touching > 0]), iterations=3)
    person = ndimage.binary_fill_holes(ndimage.binary_closing(~wall, iterations=6))
    parts, _ = ndimage.label(person)
    person = parts == np.bincount(parts.ravel())[1:].argmax() + 1
    person = ndimage.binary_erosion(person, iterations=4)
    return Image.fromarray((person * 255).astype(np.uint8))


def ascii_portrait(path: Path, theme: str) -> list[str]:
    """Blank outside my outline. Inside, local contrast is boosted so features stand out, and each character
    keeps part of the darkest detail under it (a plain average turns an eye into flat grey). Grey levels are then
    spread evenly over the characters: dark areas dense on the light theme, bright ones on the dark theme."""
    photo = Image.open(path)
    mask = person_mask(photo)
    photo = photo.convert("L")
    k = 6  # pixels per character side while processing
    face = photo.crop(CROP).resize((COLS * k, ROWS * k), Image.LANCZOS)
    fine = np.asarray(face, dtype=float)
    coarse = np.asarray(face.filter(ImageFilter.GaussianBlur(8)), dtype=float)
    sharp = np.clip(fine + DETAIL * (fine - coarse), 0, 255)
    cells = sharp.reshape(ROWS, k, COLS, k).transpose(0, 2, 1, 3).reshape(ROWS, COLS, k * k)
    grey = 0.5 * cells.mean(-1) + 0.5 * np.percentile(cells, KEEP_DARK, axis=-1)
    inside = np.asarray(mask.crop(CROP).resize((COLS, ROWS), Image.BOX)) > 127
    values = np.sort(grey[inside])
    rows = []
    for y in range(ROWS):
        row = ""
        for x in range(COLS):
            if not inside[y, x]:
                row += " "
                continue
            level = np.searchsorted(values, grey[y, x]) / len(values)
            level = 1 - level if theme == "light" else level
            row += CHARS[1 + int(level * (len(CHARS) - 2))]
        rows.append(row.rstrip())
    return rows


GLITCH_CSS = """
  .g { opacity: 0; animation: flick 6s steps(1, end) infinite; }
  .g2 { animation-name: flick2; }
  @keyframes flick { 0%, 90% { opacity: 0; } 91%, 93% { opacity: 1; } 94%, 100% { opacity: 0; } }
  @keyframes flick2 { 0%, 93% { opacity: 0; } 94%, 95% { opacity: 1; } 96%, 100% { opacity: 0; } }
  .r { animation: jump 7s steps(1, end) infinite; }
  @keyframes jump { 0%, 96% { transform: none; } 97% { transform: translateX(6px); } 98% { transform: translateX(-3px); } 99%, 100% { transform: none; } }
  @media (prefers-reduced-motion: reduce) { .g, .r { animation: none; } }
"""


def portrait(art: list[str], t: dict, pad: int, size: float) -> list[str]:
    """The ASCII rows, each stretched to an exact grid so the flickering characters land on top of the right cell
    whatever monospace font the viewer has. A flicker is a background-coloured cell with another character on it,
    shown for an instant: two in a row, with their own period and delay, so they never flicker together."""
    rng = random.Random(7)
    base_y = lambda y: pad + (y + 1) * ART_LH - 2
    jumping = set(rng.sample(range(ROWS // 4, ROWS), GLITCH_ROWS))
    out = []
    for y, row in enumerate(art):
        if not row:
            continue
        extra = f' class="r" style="animation-delay:-{rng.uniform(0, 7):.1f}s"' if y in jumping else ""
        out.append(
            f'<text x="{pad}" y="{base_y(y)}" font-size="{size:.2f}" fill="{t["art"]}" xml:space="preserve" '
            f'textLength="{len(row) * ART_CW:.1f}" lengthAdjust="spacing"{extra}>{escape(row)}</text>'
        )
    cells = [(x, y) for y, row in enumerate(art) for x, ch in enumerate(row) if ch != " "]
    for x, y in rng.sample(cells, GLITCHES):
        period, delay = rng.uniform(4, 11), rng.uniform(0, 11)
        for cls in ("g", "g g2"):
            ch = rng.choice(GLITCH_SYMBOLS if rng.random() < 0.5 else CHARS[1:])
            colour = t["key"] if rng.random() < 0.25 else t["art"]
            out.append(
                f'<g class="{cls}" style="animation-duration:{period:.1f}s;animation-delay:-{delay:.1f}s">'
                f'<rect x="{pad + x * ART_CW:.1f}" y="{base_y(y) - ART_LH + 2:.1f}" width="{ART_CW:.1f}" '
                f'height="{ART_LH:.1f}" fill="{t["bg"]}"/>'
                f'<text x="{pad + x * ART_CW:.1f}" y="{base_y(y)}" font-size="{size:.2f}" fill="{colour}">{escape(ch)}</text></g>'
            )
    return out


def embedded_font(root: Path, name: str, text: str) -> tuple[str, float]:
    """@font-face rules with the typeface cut down to `text`, and its character width as a fraction of the size."""
    rules, advance = [], 0.6
    for weight in (400, 700):
        path = root / f"assets/fonts/{name}-{weight}.woff2"
        if not path.exists():
            continue
        font = TTFont(path)
        advance = font["hmtx"][font.getBestCmap()[ord("M")]][0] / font["head"].unitsPerEm if weight == 400 else advance
        cut = subset.Subsetter()
        cut.populate(text=text)
        cut.subset(font)
        font.flavor = "woff2"
        data = io.BytesIO()
        font.save(data)
        rules.append(
            f"@font-face {{ font-family: Card; font-weight: {weight}; "
            f"src: url(data:font/woff2;base64,{base64.b64encode(data.getvalue()).decode()}) format('woff2'); }}"
        )
    return "\n".join(rules), advance


def body(theme: str, art: list[str], advance: float, right: bool = False) -> tuple[list[str], int, int]:
    """Portrait and card, without any frame: the elements, and the width and height they take."""
    t = THEMES[theme]
    cw = FONT * advance
    pad, gap = 24, 36
    card_x = pad + COLS * ART_CW + gap
    card_chars = max(KEY_W + 4 + len(v) for k, v in CARD) + 3
    width = int(card_x + card_chars * cw + pad)
    height = int(pad * 2 + max(ROWS * ART_LH, len(CARD) * LH))
    out = portrait(art, t, pad, ART_CW / advance)
    card_top = pad + (height - 2 * pad - len(CARD) * LH) / 2
    rule_end = card_x + (card_chars - 2) * cw
    for i, (k, v) in enumerate(CARD):
        y = card_top + (i + 1) * LH - 5
        if k in ("title", "section"):
            # the name and each section heading carry a rule to the end of the line: "- Contact ────"
            lead = "" if k == "title" else f'<tspan fill="{t["dim"]}">- </tspan>'
            line = f'{lead}<tspan fill="{t["key"]}" font-weight="700">{escape(v)}</tspan>'
            start = card_x + (len(v) + (1 if k == "title" else 3)) * cw
            out.append(f'<line x1="{start:.0f}" x2="{rule_end:.0f}" y1="{y - 5:.0f}" y2="{y - 5:.0f}" stroke="{t["dim"]}"/>')
        elif k:
            # each entry starts with ". ", as in neofetch-style cards
            dots = "." * ((card_chars - 2) - 2 - len(k) - 2 - len(v) if right else DOTS_TO - len(k))
            line = (f'<tspan fill="{t["dim"]}">. </tspan><tspan fill="{t["key"]}">{escape(k)}</tspan>'
                    f'<tspan fill="{t["dim"]}">:{dots} </tspan><tspan fill="{t["fg"]}">{escape(v)}</tspan>')
        else:
            continue
        # each line is stretched to its exact width, so columns and the rules line up whatever the font measures
        chars = len(v) + (0 if k == "title" else 2 if k == "section" else 2 + len(k) + 1 + len(dots) + 1)
        out.append(f'<text x="{card_x:.0f}" y="{y:.0f}" xml:space="preserve" font-size="{FONT}" '
                   f'textLength="{chars * cw:.1f}" lengthAdjust="spacing">{line}</text>')
    return out, width, height


def svg(theme: str, art: list[str], font_css: str, advance: float, right: bool = False) -> str:
    t = THEMES[theme]
    elements, width, height = body(theme, art, advance, right)
    return "\n".join([
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" '
        f'font-family="{FAMILY}">',
        f"<style>{font_css}\n{GLITCH_CSS}</style>",
        f'<rect x="0.5" y="0.5" width="{width - 1}" height="{height - 1}" rx="8" fill="{t["bg"]}" stroke="{t["border"]}"/>',
        *elements,
        "</svg>",
    ])


if __name__ == "__main__":
    root = Path(__file__).resolve().parent.parent
    args = sys.argv[1:]
    right = "--right" in args or (ALIGN == "right" and "--left" not in args)
    folder = Path(args[args.index("--out") + 1]) if "--out" in args else root / "assets"
    arts = {theme: ascii_portrait(root / "assets/retrato.jpg", theme) for theme in THEMES}
    used = "".join(k + v for k, v in CARD) + ":." + CHARS + GLITCH_SYMBOLS
    font_css, advance = embedded_font(root, FONT_NAME, used)
    for theme, art in arts.items():
        (folder / f"neofetch-{theme}.svg").write_text(svg(theme, art, font_css, advance, right), encoding="utf-8")
