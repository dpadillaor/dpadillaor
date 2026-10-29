"""Builds assets/activity-{light,dark}.svg: my activity in one terminal window, two commands one after the other.

    $ contributions --last-year    -> the calendar and what kind of contributions they are
    $ languages --all-repos        -> the languages I write
    $ ./contact.sh, exit           -> the goodbye (scripts/contact.py): where to find me, and the session closes

The data and the drawings come from scripts/contributions.py and scripts/languages.py. Three styles, to compare:
  graphics  the drawings as they are
  text      everything on the character grid, like htop or btop: a heatmap of characters and bars of blocks
  panels    the drawings inside boxes with their title on the border
Run from the repo root:  python scripts/activity.py [graphics|text|panels] [--out <folder>]
"""

import json
import math
import sys
from datetime import date
from html import escape
from pathlib import Path

import banner
import contact
import contributions as contrib
import languages as langs
import neofetch
from services import WIDTH
from terminal import BAR, PAD, window

ROOT = Path(__file__).resolve().parent.parent
STYLE = "text"
TEXT_SIZE, TEXT_LH = 13, 17
HEAT_CHARS = [".", ":", "+", "*", "#"]   # GitHub's five levels, as characters
# brighter than the 3D calendar's: a thin character in a dark orange vanishes on a dark background
HEAT_COLOURS = {"light": [None, "#ff9a72", "#ff7a45", "#ff5a1f", "#c23d0c"],
                "dark": [None, "#b8532a", "#e0662f", "#ff7a45", "#ffb08f"]}


def appear(delay: float) -> str:
    return f' class="later" style="animation-delay:{delay:.2f}s"'


def blocks(x: float, y: float, n: int, filled: float, colour: str, empty: str, cw: float) -> str:
    """A bar of n character cells, the first `filled` of them lit: like a meter in btop."""
    cells = []
    for i in range(n):
        lit = i < round(filled)
        cells.append(f'<rect x="{x + i * cw:.1f}" y="{y - TEXT_LH * 0.62:.1f}" width="{cw - 1.5:.1f}" '
                     f'height="{TEXT_LH * 0.7:.1f}" rx="1" fill="{colour if lit else empty}"/>')
    return "".join(cells)


CONTRIB_VIEW = "heatmap"   # "heatmap": a block per day, as GitHub's grid; "weekly": a column of blocks per week


def month_labels(weeks: list, x0: float, step: float, y: float, t: dict) -> list[str]:
    out, last_month, last_w = [], None, -9
    for w, week in enumerate(weeks):
        month = week["contributionDays"][0]["date"][5:7]
        if month != last_month and w < len(weeks) - 2 and (last_month is None or (w - last_w) * step >= 4 * 7.8):
            name = date.fromisoformat(week["contributionDays"][0]["date"]).strftime("%b")
            out.append(f'<text x="{x0 + w * step:.1f}" y="{y}" font-size="{TEXT_SIZE}" fill="{t["dim"]}">{name}</text>')
            last_month, last_w = month, w
    return out


def heatmap(theme: str, data: dict, top: float, start: float, advance: float,
            chars_per_week: float = 2) -> tuple[list[str], float]:
    """A block per day, the size of a character cell: weeks across, weekdays down."""
    t = banner.colours(theme)
    cw = advance * TEXT_SIZE
    weeks = data["contributionCalendar"]["weeks"]
    step = chars_per_week * cw         # a block and a gap
    x0, y0 = PAD + 5 * cw, top + 2 * TEXT_LH
    side = TEXT_LH * 0.78
    out = month_labels(weeks, x0, step, top + TEXT_LH, t)
    for d, name in ((1, "Mon"), (3, "Wed"), (5, "Fri")):
        out.append(f'<text x="{PAD}" y="{y0 + d * TEXT_LH}" font-size="{TEXT_SIZE}" fill="{t["dim"]}">{name}</text>')
    empty = "#ebedf0" if theme == "light" else "#21262d"
    for w, week in enumerate(weeks):
        column = []
        for day in week["contributionDays"]:
            d = (date.fromisoformat(day["date"]).weekday() + 1) % 7
            level = contrib.LEVELS.index(day["contributionLevel"])
            colour = empty if not level else HEAT_COLOURS[theme][level]
            column.append(f'<rect x="{x0 + w * step:.1f}" y="{y0 + d * TEXT_LH - side * 0.85:.1f}" width="{step - 3:.1f}" '
                          f'height="{side:.1f}" rx="1.5" fill="{colour}"/>')
        out.append(f"<g{appear(start + w * 0.02)}>" + "".join(column) + "</g>")
    # the legend, as GitHub's: less ... more
    lx = x0 + len(weeks) * step - 7 * step
    legend = [f'<text x="{lx - 5 * cw:.1f}" y="{y0 + 8 * TEXT_LH + 4}" font-size="{TEXT_SIZE}" fill="{t["dim"]}">less</text>']
    for i in range(5):
        legend.append(f'<rect x="{lx + i * step:.1f}" y="{y0 + 8 * TEXT_LH + 4 - side * 0.85:.1f}" width="{step - 3:.1f}" '
                      f'height="{side:.1f}" rx="1.5" fill="{empty if not i else HEAT_COLOURS[theme][i]}"/>')
    legend.append(f'<text x="{lx + 5 * step + 4:.1f}" y="{y0 + 8 * TEXT_LH + 4}" font-size="{TEXT_SIZE}" '
                  f'fill="{t["dim"]}">more</text>')
    out.append(f"<g{appear(start + len(weeks) * 0.02)}>" + "".join(legend) + "</g>")
    return out, y0 + 8 * TEXT_LH + 4


def weekly(theme: str, data: dict, top: float, start: float, advance: float) -> tuple[list[str], float]:
    """A column per week, rising in eighths of a character, like the graphs in btop."""
    t = banner.colours(theme)
    cw = advance * TEXT_SIZE
    weeks = data["contributionCalendar"]["weeks"]
    totals = [sum(d["contributionCount"] for d in w["contributionDays"]) for w in weeks]
    busiest = max(totals) or 1
    rows = 7                           # height of the graph, in characters
    step = 2 * cw
    x0, base = PAD + 5 * cw, top + TEXT_LH + rows * TEXT_LH + 6
    out = []
    for k, label in ((0, "0"), (rows, f"{busiest}")):
        out.append(f'<text x="{x0 - 1.0 * cw:.1f}" y="{base - k * TEXT_LH + 4:.1f}" font-size="{TEXT_SIZE}" '
                   f'fill="{t["dim"]}" text-anchor="end">{label}</text>')
    out.append(f'<line x1="{x0 - 4}" x2="{x0 + len(weeks) * step}" y1="{base + 2}" y2="{base + 2}" stroke="{t["border"]}"/>')
    out += month_labels(weeks, x0, step, base + TEXT_LH + 4, t)
    levels = [c for c in HEAT_COLOURS[theme][1:]]
    for w, total in enumerate(totals):
        eighths = round(total / busiest * rows * 8)
        if not eighths and total:
            eighths = 1
        h = eighths / 8 * TEXT_LH
        colour = levels[min(3, int(total / busiest * 4))] if total else None
        if not total:
            continue
        out.append(f'<rect class="grow" x="{x0 + w * step:.1f}" y="{base - h:.1f}" width="{step - 3:.1f}" height="{h:.1f}" '
                   f'fill="{colour}" style="transform-origin:0 {base:.1f}px;animation-delay:{start + w * 0.02:.2f}s"/>')
    out.append(f'<text{appear(start)} x="{x0 + len(weeks) * step + cw:.1f}" y="{base - rows * TEXT_LH + 4:.1f}" '
               f'font-size="{TEXT_SIZE}" fill="{t["dim"]}">contributions</text>')
    out.append(f'<text{appear(start)} x="{x0 + len(weeks) * step + cw:.1f}" y="{base - rows * TEXT_LH + 4 + TEXT_LH:.1f}" '
               f'font-size="{TEXT_SIZE}" fill="{t["dim"]}">per week</text>')
    return out, base + TEXT_LH + 4


RADAR = "halfblocks"   # next to the bars: "dots" (a matrix of dots, as terminal plots), "lines" (the old radar),
#                 "blocks" (character cells, as the heatmap) or "halfblocks" (half a cell each, like ▀ ▄ in a terminal)


def dot_radar(theme: str, data: dict, cx: float, cy: float, r: float, start: float, advance: float) -> list[str]:
    """The radar as a matrix of dots: rings and axes in grey, the shape filled in orange. Same scale as the old one:
    five rings, 1 to 10K, nothing below the first."""
    t = banner.colours(theme)
    values = [v for _, v in contrib.axes(data)]
    reach = [(math.log10(max(v, 1)) + 1) / 5 for v in values]
    corner = lambda i, f: (cx + r * f * math.sin(2 * math.pi * i / 5), cy - r * f * math.cos(2 * math.pi * i / 5))
    shape = [corner(i, f) for i, f in enumerate(reach)]

    def inside(x, y):   # ray casting against the shape
        hit = False
        for (x1, y1), (x2, y2) in zip(shape, shape[1:] + shape[:1]):
            if (y1 > y) != (y2 > y) and x < x1 + (y - y1) * (x2 - x1) / (y2 - y1):
                hit = not hit
        return hit

    def near_segment(x, y, a, b, tol):
        (x1, y1), (x2, y2) = a, b
        dx, dy = x2 - x1, y2 - y1
        k = max(0, min(1, ((x - x1) * dx + (y - y1) * dy) / (dx * dx + dy * dy)))
        return math.hypot(x - x1 - k * dx, y - y1 - k * dy) < tol

    grid, out = 4.0, []
    dim, lit = [], []
    n = int(r * 1.05 / grid)
    for gy in range(-n, n + 1):
        for gx in range(-n, n + 1):
            x, y = cx + gx * grid, cy + gy * grid
            if inside(x, y):
                edge = any(near_segment(x, y, a, b, 2.2) for a, b in zip(shape, shape[1:] + shape[:1]))
                lit.append((x, y, 1.5 if edge else 1.1))
                continue
            on_ring = any(near_segment(x, y, corner(i, k / 5), corner(i + 1, k / 5), 1.2)
                          for k in range(1, 6) for i in range(5))
            on_axis = any(near_segment(x, y, (cx, cy), corner(i, 1), 1.2) for i in range(5))
            if on_ring or on_axis:
                dim.append((x, y))
    out.append("".join(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="0.9" fill="{t["dim"]}"/>' for x, y in dim))
    out.append(f'<g class="grow" style="transform-origin:{cx}px {cy}px;animation-delay:{start:.2f}s;'
               f'animation-duration:0.8s;transform:scale(0)">'
               + "".join(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{s}" fill="{t["key"]}"/>' for x, y, s in lit) + "</g>")
    for i, (name, _) in enumerate(contrib.axes(data)):
        lx, ly = corner(i, 1.16)
        anchor = "middle" if abs(lx - cx) < 5 else ("start" if lx > cx else "end")
        out.append(f'<text x="{lx:.1f}" y="{ly + 4:.1f}" font-size="11" fill="{t["dim"]}" text-anchor="{anchor}">{name}</text>')
    return out


def block_radar(theme: str, data: dict, cx: float, cy: float, r: float, start: float, advance: float,
                half: bool) -> list[str]:
    """The radar on the character grid: every cell is a pixel. Cells inside the shape are orange blocks, cells on a
    ring or an axis a grey dot. With `half`, each cell is split in two pixels, top and bottom."""
    t = banner.colours(theme)
    cw, lh = advance * TEXT_SIZE, TEXT_LH
    ph = lh / 2 if half else lh
    reach = [(math.log10(max(v, 1)) + 1) / 5 for _, v in contrib.axes(data)]
    corner = lambda i, f: (cx + r * f * math.sin(2 * math.pi * i / 5), cy - r * f * math.cos(2 * math.pi * i / 5))
    shape = [corner(i, f) for i, f in enumerate(reach)]

    def inside(x, y):
        hit = False
        for (x1, y1), (x2, y2) in zip(shape, shape[1:] + shape[:1]):
            if (y1 > y) != (y2 > y) and x < x1 + (y - y1) * (x2 - x1) / (y2 - y1):
                hit = not hit
        return hit

    def near(x, y, a, b, tol):
        (x1, y1), (x2, y2) = a, b
        dx, dy = x2 - x1, y2 - y1
        k = max(0, min(1, ((x - x1) * dx + (y - y1) * dy) / (dx * dx + dy * dy)))
        return math.hypot(x - x1 - k * dx, y - y1 - k * dy) < tol

    lit, dots = [], []
    cols, rows = int(1.1 * r / cw), int(1.1 * r / ph)
    for gy in range(-rows, rows + 1):
        for gx in range(-cols, cols + 1):
            x, y = cx + gx * cw, cy + gy * ph
            if inside(x, y):
                lit.append(f'<rect x="{x - cw / 2 + 0.7:.1f}" y="{y - ph / 2 + 0.7:.1f}" width="{cw - 1.4:.1f}" '
                           f'height="{ph - 1.4:.1f}" rx="1" fill="{t["key"]}"/>')
            elif any(near(x, y, corner(i, k / 5), corner(i + 1, k / 5), ph * 0.62) for k in range(1, 6) for i in range(5)) \
                    or any(near(x, y, (cx, cy), corner(i, 1), cw * 0.5) for i in range(5)):
                outer = any(near(x, y, corner(i, 1), corner(i + 1, 1), ph * 0.62) for i in range(5))
                dots.append(f'<rect x="{x - 1.3:.1f}" y="{y - 1.3:.1f}" width="2.6" height="2.6" '
                            f'fill="{t["dim"] if outer else t["border"]}"/>')
    out = ["".join(dots),
           f'<g class="grow" style="transform-origin:{cx}px {cy}px;animation-delay:{start:.2f}s;animation-duration:0.8s;'
           f'transform:scale(0)">' + "".join(lit) + "</g>"]
    for i, (name, _) in enumerate(contrib.axes(data)):
        lx, ly = corner(i, 1.2)
        anchor = "middle" if abs(lx - cx) < 5 else ("start" if lx > cx else "end")
        out.append(f'<text x="{lx:.1f}" y="{ly + 4:.1f}" font-size="11" fill="{t["dim"]}" text-anchor="{anchor}">{name}</text>')
    return out


RADAR_PLACE = "beside"   # the radar without bars: "below" the heatmap, centred, or "beside" it, on the right
CONTRIB_BARS = False    # bars per kind of contribution next to the radar (they put the zeros in the spotlight)


def draw_radar(theme: str, data: dict, cx: float, cy: float, r: float, start: float, advance: float) -> list[str]:
    if RADAR == "dots":
        return dot_radar(theme, data, cx, cy, r, start, advance)
    if RADAR in ("blocks", "halfblocks"):
        return block_radar(theme, data, cx, cy, r, start, advance, RADAR == "halfblocks")
    t = banner.colours(theme)
    return ([e for e in contrib.radar(theme, data, cx, cy, r, start) if "<tspan" not in e]
            + [f'<text x="{x:.1f}" y="{y:.1f}" font-size="11" fill="{t["dim"]}" text-anchor="{a}">{n}</text>'
               for n, x, y, a in radar_labels(data, cx, cy, r)])


def text_contributions(theme: str, data: dict, top: float, start: float, advance: float) -> tuple[list[str], float]:
    """The year as a heatmap, and the radar of what kind of contributions they are (with bars, if CONTRIB_BARS)."""
    t = banner.colours(theme)
    cw = advance * TEXT_SIZE
    late = start + len(data["contributionCalendar"]["weeks"]) * 0.02
    if CONTRIB_BARS:
        out, y = heatmap(theme, data, top, start, advance)
        radius = 96
        cx, cy = PAD + radius + 70, y + 34 + radius
        out += draw_radar(theme, data, cx, cy, radius, late, advance)
        x0, rows = PAD + 2 * radius + 160, 5
        first = cy - (rows - 1) * TEXT_LH * 1.3 / 2 + 4
        for i, (name, value) in enumerate(contrib.axes(data)):
            reach = (math.log10(max(value, 1)) + 1) / 5 if value else 0
            yy = first + i * TEXT_LH * 1.3
            row = (f'<text x="{x0}" y="{yy:.1f}" font-size="{TEXT_SIZE}" fill="{t["fg"]}">{name}</text>'
                   + blocks(x0 + 15 * cw, yy, 36, reach * 36, t["key"], t["border"], cw)
                   + f'<text x="{x0 + 53 * cw:.1f}" y="{yy:.1f}" font-size="{TEXT_SIZE}" '
                     f'fill="{t["key"]}" font-weight="700">{contrib.compact(value)}</text>')
            out.append(f"<g{appear(late + i * 0.12)}>{row}</g>")
        return out, cy + radius + 22
    if RADAR_PLACE == "beside":
        out, y = heatmap(theme, data, top, start, advance, chars_per_week=1.45)
        radius = 84
        cx, cy = WIDTH - PAD - radius - 70, top + 20 + radius
        out += draw_radar(theme, data, cx, cy, radius, late, advance)
        return out, max(y, cy + radius + 22)
    out, y = heatmap(theme, data, top, start, advance)
    radius = 96
    cx, cy = WIDTH / 2, y + 40 + radius
    out += draw_radar(theme, data, cx, cy, radius, late, advance)
    return out, cy + radius + 26


def radar_labels(data: dict, cx: float, cy: float, r: float) -> list:
    out = []
    for i, (name, _) in enumerate(contrib.axes(data)):
        lx, ly = cx + r * 1.16 * math.sin(2 * math.pi * i / 5), cy - r * 1.16 * math.cos(2 * math.pi * i / 5)
        out.append((name, lx, ly + 4, "middle" if abs(lx - cx) < 5 else ("start" if lx > cx else "end")))
    return out


SUMMARY = "kv"   # the line under each output: "kv" (key=value), "comment" (# ...) or "arrow" (→ ...)


def contrib_status(data: dict) -> list[tuple[str, str]]:
    total = data["contributionCalendar"]["totalContributions"]
    return [("contributions", f"{total:,}", "contributions"),
            ("private", f"{data['restrictedContributionsCount']:,}", "in private repos"),
            ("pull_requests", f"{data['totalPullRequestContributions']}", "pull requests"), ("period", "last_year", "")]


def langs_status(data: dict) -> list[tuple[str, str]]:
    return [("repositories", f"{data['repositories']}", "repositories"), ("private", f"{data['private']}", "private"),
            ("measured", "bytes", "")]


def status(x: float, y: float, width: float, parts: list[tuple[str, str, str]], t: dict, advance: float,
           delay: float) -> str:
    """The summary under an output, as plain terminal text. Each part: key, value and the words for it in prose."""
    cw = advance * TEXT_SIZE
    if SUMMARY == "kv":
        spans, n = [], 0
        for k, v, _ in parts:
            spans.append(f'<tspan fill="{t["key"]}">{k}</tspan><tspan fill="{t["dim"]}">=</tspan>'
                         f'<tspan fill="{t["fg"]}">{escape(v)}</tspan><tspan>   </tspan>')
            n += len(k) + 1 + len(v) + 3
        line = "".join(spans)
        return (f'<text{appear(delay)} x="{x}" y="{y}" font-size="{TEXT_SIZE}" xml:space="preserve" '
                f'textLength="{n * cw:.1f}" lengthAdjust="spacing">{line}</text>')
    facts = [f"{v} {w}" for _, v, w in parts if w]
    if SUMMARY == "comment":
        text = "# " + " · ".join(facts)
        return (f'<text{appear(delay)} x="{x}" y="{y}" font-size="{TEXT_SIZE}" fill="{t["dim"]}" xml:space="preserve" '
                f'textLength="{len(text) * cw:.1f}" lengthAdjust="spacing">{escape(text)}</text>')
    text = " · ".join(facts)
    arrow = (f'<path d="M{x} {y - 4.5} h11 m-4 -4 l4 4 l-4 4" fill="none" stroke="{t["key"]}" stroke-width="1.6" '
             f'stroke-linecap="round" stroke-linejoin="round"/>')
    return (f'<g{appear(delay)}>{arrow}<text x="{x + 2.6 * cw:.1f}" y="{y}" font-size="{TEXT_SIZE}" fill="{t["fg"]}" '
            f'xml:space="preserve" textLength="{len(text) * cw:.1f}" lengthAdjust="spacing">{escape(text)}</text></g>')


RING_CHARS = "#"   # what the ring of characters is drawn with
RING_SIZE = 9      # its font size: smaller than the text, so the ring has enough characters to look round
LANG_RING = "ascii"   # next to the bars: "ascii" (a ring of characters) or "graphic" (the smooth ring)


def ascii_ring(theme: str, data: dict, cx: float, cy: float, radius: float, start: float, advance: float) -> list[str]:
    """A ring of characters on the terminal grid, each one in the colour of the language whose slice it falls in.
    It appears as a sweep, clockwise from the top."""
    t = banner.colours(theme)
    cw, lh = advance * RING_SIZE, RING_SIZE * 1.08
    inner = radius * 0.58
    shares = list(data["shares"].items())
    bounds, acc = [], 0.0
    for name, share in shares:
        acc += share
        bounds.append((acc, name))
    out = []
    rows, cols = int(2 * radius / lh) + 1, int(2 * radius / cw) + 1
    for row in range(rows):
        for col in range(cols):
            x = cx - radius + col * cw + cw / 2
            y = cy - radius + row * lh + lh / 2
            dist = math.hypot(x - cx, y - cy)
            if not inner <= dist <= radius:
                continue
            angle = (math.degrees(math.atan2(x - cx, cy - y)) + 360) % 360   # 0 at the top, clockwise
            share_at = angle / 3.6
            name = next(n for b, n in bounds if share_at <= b + 1e-9)
            colour = langs.COLOURS.get(name, t["dim"])
            out.append(f'<text x="{x - cw / 2:.1f}" y="{y + lh * 0.35:.1f}" font-size="{RING_SIZE}" fill="{colour}" '
                       f'font-weight="700" class="later" style="animation-delay:{start + angle / 360 * 1.0:.2f}s;'
                       f'animation-duration:0.05s">{RING_CHARS}</text>')
    return out


def smooth_ring(theme: str, data: dict, cx: float, cy: float, radius: float, start: float) -> list[str]:
    """The smooth ring, the size of the ring of characters, drawn slice by slice."""
    t = banner.colours(theme)
    stroke = radius * 0.4
    r = radius - stroke / 2
    circumference = 2 * math.pi * r
    out, offset = [], 0.0
    for i, (name, share) in enumerate(data["shares"].items()):
        out.append(f'<circle cx="{cx}" cy="{cy}" r="{r:.1f}" fill="none" stroke="{langs.COLOURS.get(name, t["dim"])}" '
                   f'stroke-width="{stroke:.1f}" stroke-dasharray="0 {circumference:.1f}" '
                   f'transform="rotate({-90 + 3.6 * offset:.2f} {cx} {cy})" style="--l:{circumference * share / 100:.1f}px;'
                   f'--c:{circumference:.1f}px;animation:arc 0.5s ease-out {start + i * 0.15:.2f}s forwards"/>')
        offset += share
    return out


def text_languages(theme: str, data: dict, top: float, start: float, advance: float) -> tuple[list[str], float]:
    """The ring (of characters, or smooth) on the left and a bar of blocks per language on the right."""
    t = banner.colours(theme)
    cw = advance * TEXT_SIZE
    radius = 92
    cx, cy = PAD + radius + 8, top + 14 + radius
    if LANG_RING == "ascii":
        out = ascii_ring(theme, data, cx, cy, radius, start, advance)
    else:
        out = smooth_ring(theme, data, cx, cy, radius, start)
    x0 = PAD + 2 * radius + 50
    rows = len(data["shares"])
    first = cy - (rows - 1) * TEXT_LH * 1.3 / 2 + 4
    for i, (name, share) in enumerate(data["shares"].items()):
        y = first + i * TEXT_LH * 1.3
        colour = langs.COLOURS.get(name, t["dim"])
        out.append(f"<g{appear(start + i * 0.12)}>"
                   f'<text x="{x0}" y="{y:.1f}" font-size="{TEXT_SIZE}" fill="{t["fg"]}">{escape(name)}</text>'
                   + blocks(x0 + 13 * cw, y, 50, share / 2, colour, t["border"], cw) +
                   f'<text x="{x0 + 70 * cw:.1f}" y="{y:.1f}" font-size="{TEXT_SIZE}" fill="{t["dim2"]}" '
                   f'text-anchor="end">{share:.1f}%</text></g>')
    return out, cy + radius + 6


def panel(x: float, y: float, w: float, h: float, title: str, t: dict, advance: float) -> list[str]:
    """A box with its title on the top border, as in btop."""
    label = f" {title} "
    lw = len(label) * advance * 13
    return [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="4" fill="none" stroke="{t["border"]}"/>',
            f'<rect x="{x + 14}" y="{y - 8}" width="{lw:.1f}" height="16" fill="{t["bg"]}"/>',
            f'<text x="{x + 14}" y="{y + 4.5}" font-size="13" font-weight="700" fill="{t["key"]}" '
            f'xml:space="preserve">{escape(label)}</text>']


def svg(theme: str, style: str, contributions: dict, languages: dict, font_css: str, advance: float) -> str:
    t = banner.colours(theme)
    out = []
    y = BAR + 34
    if style == "panels":
        cmd, start = banner.prompt(PAD, y, "activity --dashboard", 0.4, t, advance, "a0")
        out += cmd
        y += 30
        body, bottom = contrib.body(theme, contributions, PAD + 16, y + 10, WIDTH - PAD - 16, start + 0.3)
        out += panel(PAD, y, WIDTH - 2 * PAD, bottom - y + 34, "contributions · last year", t, advance) + body
        out.append(f'<text{appear(start + 1.9)} x="{PAD + 16}" y="{bottom + 20}" font-size="12" fill="{t["dim"]}">'
                   f'{escape(contrib.note(contributions))}</text>')
        y = bottom + 34 + 30
        body, bottom = langs.ring(theme, languages, PAD + 16, y + 22, WIDTH - PAD - 16, start + 2.1)
        out += panel(PAD, y, WIDTH - 2 * PAD, bottom - y + 50, "languages · all repos", t, advance) + body
        out.append(f'<text{appear(start + 3.2)} x="{PAD + 16}" y="{bottom + 34}" font-size="12" fill="{t["dim"]}">'
                   f'{escape(langs.note(languages))}</text>')
        end, y = start + 3.4, bottom + 50 + 40
    else:
        cmd, start = banner.prompt(PAD, y, contrib.COMMAND, 0.4, t, advance, "a0")
        out += cmd
        if style == "text":
            body, bottom = text_contributions(theme, contributions, y + 8, start + 0.3, advance)
            end1 = start + 2.0
            bottom += 8
        else:
            body, bottom = contrib.body(theme, contributions, PAD, y, WIDTH - PAD, start + 0.3)
            end1 = start + 2.4
        out += body
        if style == "text":
            out.append(status(PAD, bottom + 22, WIDTH - 2 * PAD, contrib_status(contributions), t, advance, end1 - 0.3))
        else:
            out.append(f'<text{appear(end1 - 0.3)} x="{PAD}" y="{bottom + 20}" font-size="13" fill="{t["dim"]}">'
                       f'{escape(contrib.note(contributions))}</text>')
        y = bottom + 66
        cmd, start = banner.prompt(PAD, y, langs.COMMAND, end1, t, advance, "a1")
        out += cmd
        if style == "text":
            body, bottom = text_languages(theme, languages, y + 8, start + 0.3, advance)
        else:
            body, bottom = langs.ring(theme, languages, PAD, y + 22, WIDTH - PAD, start + 0.3)
        out += body
        if style == "text":
            out.append(status(PAD, bottom + 26, WIDTH - 2 * PAD, langs_status(languages), t, advance, start + 1.4))
        else:
            out.append(f'<text{appear(start + 1.4)} x="{PAD}" y="{bottom + 22}" font-size="13" fill="{t["dim"]}">'
                       f'{escape(langs.note(languages))}</text>')
        end, y = start + 1.6, bottom + 66
    final, used = contact.body(theme, y, end, advance)
    height = int(y + used + 34)
    before, after = window(theme, WIDTH, height)
    return "\n".join([
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{height}" viewBox="0 0 {WIDTH} {height}" '
        f'font-family="{neofetch.FAMILY}">',
        f"<style>{font_css}\n{banner.CSS}{contrib.GROW_CSS}{langs.RING_CSS}</style>",
        *before, *out, *final, *after, "</svg>",
    ])


if __name__ == "__main__":
    args = sys.argv[1:]
    style = next((a for a in args if a in ("graphics", "text", "panels")), STYLE)
    if "--ring" in args:
        LANG_RING = args[args.index("--ring") + 1]
    if "--summary" in args:
        SUMMARY = args[args.index("--summary") + 1]
    if "--place" in args:
        RADAR_PLACE = args[args.index("--place") + 1]
    if "--bars" in args:
        CONTRIB_BARS = True
    if "--radar" in args:
        RADAR = args[args.index("--radar") + 1]
    if "--view" in args:
        CONTRIB_VIEW = args[args.index("--view") + 1]
    folder = Path(args[args.index("--out") + 1]) if "--out" in args else ROOT / "assets"
    contributions = contrib.fetch()
    languages = langs.measure()
    (ROOT / "assets/languages.json").write_text(json.dumps(languages, indent=1) + "\n", encoding="utf-8")
    used = (banner.PROMPT + contrib.COMMAND + langs.COMMAND + "activity --dashboard contributions · last year languages "
            "all repos" + "".join(languages["shares"]) + contrib.note(contributions) + langs.note(languages)
            + "CommitsIssuesPull requestsReviewsRepos0123456789.,%K" + "".join(HEAT_CHARS) + "MonWedFri" + RING_CHARS
            + "JanFebMarAprMayJunJulAugSepOctNovDec" + "log scale, 1 to 10K" + contact.TEXT)
    font_css, advance = neofetch.embedded_font(ROOT, neofetch.FONT_NAME, used)
    for theme in neofetch.THEMES:
        (folder / f"activity-{theme}.svg").write_text(
            svg(theme, style, contributions, languages, font_css, advance), encoding="utf-8")
