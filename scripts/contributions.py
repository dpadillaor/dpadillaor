"""Builds assets/contributions-{light,dark}.svg: my last year on GitHub, as a terminal window.

Left, the contribution calendar in 3D: a column per day, as tall as that day's contributions, in the website's
oranges. Right, a radar of what kind of contributions they are. Private work counts as GitHub counts it on my
profile: a number per day, nothing else (and on the radar it goes with the commits, which it nearly all is).
Run from the repo root:  python scripts/contributions.py   (needs `gh` signed in)
"""

import json
import math
import subprocess
from datetime import date
from html import escape
from pathlib import Path

import banner
import neofetch
from services import WIDTH
from terminal import BAR, PAD, window

ROOT = Path(__file__).resolve().parent.parent
OWNER = "dpadillaor"
COMMAND = "contributions --last-year"
QUERY = """{user(login:"%s"){contributionsCollection{totalCommitContributions totalIssueContributions
  totalPullRequestContributions totalPullRequestReviewContributions totalRepositoryContributions
  restrictedContributionsCount contributionCalendar{totalContributions weeks{contributionDays{date contributionCount
  contributionLevel}}}}}}"""
# from no contributions to the most, like GitHub's five levels, in the website's oranges
LEVELS = ["NONE", "FIRST_QUARTILE", "SECOND_QUARTILE", "THIRD_QUARTILE", "FOURTH_QUARTILE"]
ORANGES = {"light": ["#ebedf0", "#ffd2c0", "#ff9a72", "#ff5a1f", "#c23d0c"],
           "dark": ["#21262d", "#5a2410", "#a63c14", "#ff5a1f", "#ffb08f"]}
CELL = 10.5          # side of a day's square, in px
TALLEST = 70         # height of the busiest day's column


def fetch() -> dict:
    out = subprocess.run(["gh", "api", "graphql", "-f", f"query={QUERY % OWNER}"],
                         capture_output=True, text=True, check=True).stdout
    return json.loads(out)["data"]["user"]["contributionsCollection"]


def shade(colour: str, factor: float) -> str:
    r, g, b = (int(colour[i:i + 2], 16) for i in (1, 3, 5))
    return "#%02x%02x%02x" % tuple(int(c * factor) for c in (r, g, b))


def calendar(theme: str, data: dict, ox: float, oy: float, start: float) -> list[str]:
    """Isometric columns, a row per weekday and a column per week, drawn from the back to the front; each one grows
    from the floor, week after week."""
    weeks = data["contributionCalendar"]["weeks"]
    busiest = max(d["contributionCount"] for w in weeks for d in w["contributionDays"]) or 1
    cos, sin = math.cos(math.pi / 6), math.sin(math.pi / 6)
    days = [(w, (date.fromisoformat(day["date"]).weekday() + 1) % 7, day)  # GitHub's weeks start on Sunday
            for w, week in enumerate(weeks) for day in week["contributionDays"]]
    pts = lambda p: " ".join(f"{a:.1f},{b:.1f}" for a, b in p)
    out = []
    for w, d, day in sorted(days, key=lambda c: (c[0] + c[1], c[0])):
        count = day["contributionCount"]
        colour = ORANGES[theme][LEVELS.index(day["contributionLevel"])]
        h = 0 if not count else 3 + TALLEST * math.sqrt(count / busiest)
        x = ox + (w - d) * CELL * cos
        y = oy + (w + d) * CELL * sin
        top = [(x, y - h), (x + CELL * cos, y - h + CELL * sin), (x, y - h + 2 * CELL * sin),
               (x - CELL * cos, y - h + CELL * sin)]
        if not h:
            out.append(f'<polygon points="{pts(top)}" fill="{colour}"/>')
            continue
        left = [top[3], top[2], (top[2][0], top[2][1] + h), (top[3][0], top[3][1] + h)]
        right = [top[2], top[1], (top[1][0], top[1][1] + h), (top[2][0], top[2][1] + h)]
        floor = y + 2 * CELL * sin
        out.append(f'<g class="grow" style="transform-origin:{x:.1f}px {floor:.1f}px;animation-delay:{start + w * 0.025:.2f}s">'
                   f'<polygon points="{pts(left)}" fill="{shade(colour, 0.82)}"/>'
                   f'<polygon points="{pts(right)}" fill="{shade(colour, 0.66)}"/>'
                   f'<polygon points="{pts(top)}" fill="{colour}"/></g>')
    return out


def axes(data: dict) -> list[tuple[str, int]]:
    """What kind of contributions. Private ones go with the commits: GitHub only gives their number."""
    return [("Commits", data["totalCommitContributions"] + data["restrictedContributionsCount"]),
            ("Issues", data["totalIssueContributions"]),
            ("Pull requests", data["totalPullRequestContributions"]),
            ("Reviews", data["totalPullRequestReviewContributions"]),
            ("Repos", data["totalRepositoryContributions"])]


def compact(n: int) -> str:
    return f"{n / 1000:.1f}K" if n >= 1000 else str(n)


def radar(theme: str, data: dict, cx: float, cy: float, r: float, start: float) -> list[str]:
    """Five axes on a logarithmic scale with five rings, 1 to 10K, as on the old profile: nothing sits on the first
    ring, so the shape always closes."""
    t = banner.colours(theme)
    reach = lambda v: (math.log10(max(v, 1)) + 1) / 5
    point = lambda i, f: (cx + r * f * math.sin(2 * math.pi * i / 5), cy - r * f * math.cos(2 * math.pi * i / 5))
    out = []
    for ring in range(1, 6):
        out.append(f'<polygon points="{" ".join("%.1f,%.1f" % point(i, ring / 5) for i in range(5))}" fill="none" '
                   f'stroke="{t["border"]}"/>')
    for i, (name, value) in enumerate(axes(data)):
        x, y = point(i, 1)
        out.append(f'<line x1="{cx}" y1="{cy}" x2="{x:.1f}" y2="{y:.1f}" stroke="{t["border"]}"/>')
        lx, ly = point(i, 1.2)
        anchor = "middle" if abs(lx - cx) < 5 else ("start" if lx > cx else "end")
        out.append(f'<text x="{lx:.1f}" y="{ly:.1f}" font-size="13" text-anchor="{anchor}">'
                   f'<tspan fill="{t["dim2"]}">{name} </tspan><tspan fill="{t["key"]}" font-weight="700">'
                   f'{compact(value)}</tspan></text>')
    for ring, label in zip(range(1, 6), ["1", "10", "100", "1K", "10K"]):
        x, y = point(0, ring / 5)
        out.append(f'<text x="{x + 4:.1f}" y="{y + 4:.1f}" font-size="9" fill="{t["dim"]}">{label}</text>')
    shape = " ".join("%.1f,%.1f" % point(i, reach(v)) for i, (_, v) in enumerate(axes(data)))
    out.append(f'<polygon class="grow" style="transform-origin:{cx}px {cy}px;animation-delay:{start:.2f}s;animation-duration:0.8s" '
               f'points="{shape}" fill="{t["key"]}" fill-opacity="0.22" stroke="{t["key"]}" stroke-width="2" '
               f'stroke-linejoin="round"/>')
    return out


GROW_CSS = ("\n  .grow { transform: scaleY(0); animation: rise 0.45s ease-out forwards; }"
            "\n  polygon.grow { transform: scale(0); }"
            "\n  @keyframes rise { to { transform: none; } }"
            "\n  @media (prefers-reduced-motion: reduce) { .grow { animation: none; transform: none; } }")


def note(data: dict) -> str:
    total = data["contributionCalendar"]["totalContributions"]
    return f"{total:,} contributions in the last year, {data['restrictedContributionsCount']:,} of them in private repositories"


def body(theme: str, data: dict, x0: float, top: float, right: float, start: float) -> tuple[list[str], float]:
    """The calendar on the left and the radar on the right. Returns the elements and the bottom they reach."""
    out = calendar(theme, data, x0 + 7 * CELL * math.cos(math.pi / 6) + 10, top + 36, start)
    out += radar(theme, data, right - 200, top + 160, 110, start + 1.4)
    return out, top + 360


def svg(theme: str, data: dict, font_css: str, advance: float) -> str:
    t = banner.colours(theme)
    cmd, start = banner.prompt(PAD, BAR + 34, COMMAND, 0.4, t, advance, "c0")
    out, bottom = body(theme, data, PAD, BAR + 34, WIDTH - PAD, start + 0.3)
    out.append(f'<text class="later" style="animation-delay:{start + 1.9:.2f}s" x="{PAD}" y="{bottom + 22}" '
               f'font-size="13" fill="{t["dim"]}">{escape(note(data))}</text>')
    final, _ = banner.prompt(PAD, bottom + 62, "", start + 2.2, t, advance, "c1", last=True)
    height = int(bottom + 92)
    before, after = window(theme, WIDTH, height)
    return "\n".join([
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{height}" viewBox="0 0 {WIDTH} {height}" '
        f'font-family="{neofetch.FAMILY}">',
        f"<style>{font_css}\n{banner.CSS}{GROW_CSS}</style>",
        *before, *cmd, *out, *final, *after, "</svg>",
    ])


if __name__ == "__main__":
    data = fetch()
    used = banner.PROMPT + COMMAND + "CommitsIssuesPull requestsReviewsRepos10K0123456789,." + \
        "contributions in the last year of them in private repositories"
    font_css, advance = neofetch.embedded_font(ROOT, neofetch.FONT_NAME, used)
    for theme in neofetch.THEMES:
        (ROOT / f"assets/contributions-{theme}.svg").write_text(svg(theme, data, font_css, advance), encoding="utf-8")
