"""Builds assets/languages-{light,dark}.svg: the languages I write, as a ring in a terminal window.

Measured like GitHub does it, by bytes of code, but over all my repositories, private ones included:
  - my own repositories count whole;
  - a fork counts only what I added to it (the lines of my commits, compared with the original);
  - TeX, HTML, CSS and notebooks are left out (writing and markup, not programming);
  - a few languages that a tool generated for me are left out of a repository (see GENERATED).
The numbers also go to assets/languages.json, so anyone can see what the ring is made of.

Needs the GitHub CLI (`gh`) signed in with access to private repositories: on my machine, my own session; in the
daily GitHub Action, a read-only token (secret PROFILE_TOKEN).
Run from the repo root:  python scripts/languages.py
"""

import json
import math
import subprocess
from collections import Counter
from html import escape
from pathlib import Path

import banner
import neofetch
from services import WIDTH
from terminal import BAR, PAD, window

ROOT = Path(__file__).resolve().parent.parent
OWNER = "dpadillaor"
EXCLUDED = {"TeX", "HTML", "CSS", "SCSS", "Jupyter Notebook"}
# Code a framework wrote, not me: Flutter's desktop and mobile runners in Janus
GENERATED = {"Janus": {"C++", "CMake", "Swift", "Kotlin", "Objective-C", "C"}}
SMALL = 1.0       # languages under this percentage go together as "Other"
# by file extension, for what I added to forks
EXTENSIONS = {"py": "Python", "cpp": "C++", "cc": "C++", "cxx": "C++", "hpp": "C++", "h": "C++", "cu": "Cuda",
              "ts": "TypeScript", "tsx": "TypeScript", "js": "JavaScript", "mjs": "JavaScript", "rs": "Rust",
              "dart": "Dart", "sh": "Shell", "cmake": "CMake"}
# GitHub's own colours for each language (github-linguist), so they look as they do on GitHub
COLOURS = {"Python": "#3572A5", "TypeScript": "#3178c6", "JavaScript": "#f1e05a", "Dart": "#00B4AB",
           "Astro": "#ff5a03", "C++": "#f34b7d", "Rust": "#dea584", "CMake": "#DA3434", "Shell": "#89e051",
           "Cuda": "#3A4E3A", "Dockerfile": "#384d54", "Makefile": "#427819", "C": "#555555", "Other": "#8b949e"}
COMMAND = "languages --all-repos"


def gh(path: str, many: bool = False):
    """A call to the GitHub API through `gh`. `many`: a list spread over several pages, joined."""
    args = ["gh", "api", path] + (["--paginate", "--slurp"] if many else [])
    data = json.loads(subprocess.run(args, capture_output=True, text=True, check=True).stdout)
    return [item for page in data for item in page] if many else data


def added_by_me(repo: dict) -> Counter:
    """Bytes of the lines my commits added to a fork, by language."""
    fork = gh(f"/repos/{OWNER}/{repo['name']}")
    parent = fork["parent"]
    diff = gh(f"/repos/{parent['full_name']}/compare/{parent['default_branch']}...{OWNER}:{repo['name']}:{fork['default_branch']}")
    sizes = Counter()
    for f in diff.get("files", []):
        language = EXTENSIONS.get(f["filename"].rsplit(".", 1)[-1].lower())
        if language and f.get("patch"):
            sizes[language] += sum(len(line) for line in f["patch"].splitlines()
                                   if line.startswith("+") and not line.startswith("+++"))
    return sizes


def measure() -> dict:
    total, per_repo = Counter(), {}
    for repo in gh("/user/repos?affiliation=owner&per_page=100", many=True):
        if repo["fork"]:
            sizes = added_by_me(repo)
        else:
            sizes = Counter(gh(f"/repos/{OWNER}/{repo['name']}/languages"))
        skip = EXCLUDED | GENERATED.get(repo["name"], set())
        sizes = Counter({k: v for k, v in sizes.items() if k not in skip and v > 0})
        if sizes:
            per_repo[repo["name"]] = {"private": repo["private"], "fork": repo["fork"], "bytes": dict(sizes)}
            total += sizes
    everything = sum(total.values())
    shares = {k: 100 * v / everything for k, v in total.most_common()}
    main = {k: v for k, v in shares.items() if v >= SMALL}
    other = sum(v for k, v in shares.items() if v < SMALL)
    if other:
        main["Other"] = other
    # private repositories are counted, never named
    return {"shares": {k: round(v, 1) for k, v in main.items()}, "bytes": dict(total.most_common()),
            "repositories": len(per_repo), "private": sum(r["private"] for r in per_repo.values())}


RING_CSS = ("\n  @keyframes arc { to { stroke-dasharray: var(--l) var(--c); } }"
            "\n  @media (prefers-reduced-motion: reduce) { circle { animation: none !important; "
            "stroke-dasharray: var(--l) var(--c); } }")


def note(data: dict) -> str:
    return f'{data["repositories"]} repositories, {data["private"]} of them private'


def ring(theme: str, data: dict, x0: float, top: float, right: float, start: float) -> tuple[list[str], float]:
    """The ring on the left and the legend with bars on the right, between x0 and right. Returns the elements and
    the bottom they reach."""
    t = banner.colours(theme)
    r, stroke = 105, 34
    cx, cy = x0 + 122, top + r + stroke / 2
    circumference = 2 * math.pi * r
    out, offset = [], 0.0
    legend_x, legend_y = x0 + 312, top + 30
    bar_w = right - (legend_x + 160) - 70  # room for the percentage on the right
    for i, (name, share) in enumerate(data["shares"].items()):
        length = circumference * share / 100
        colour = COLOURS.get(name, t["dim"])
        delay = start + i * 0.15
        # one arc per language, drawn in turn
        out.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{colour}" stroke-width="{stroke}" '
                   f'stroke-dasharray="0 {circumference:.1f}" transform="rotate({-90 + 360 * offset / 100:.2f} {cx} {cy})" '
                   f'style="--l:{length:.1f}px;--c:{circumference:.1f}px;animation:arc 0.5s ease-out {delay:.2f}s forwards"/>')
        y = legend_y + i * 34
        out.append(f'<g class="later" style="animation-delay:{delay:.2f}s">'
                   f'<rect x="{legend_x}" y="{y - 11}" width="12" height="12" rx="2" fill="{colour}"/>'
                   f'<text x="{legend_x + 22}" y="{y}" font-size="15" fill="{t["fg"]}">{escape(name)}</text>'
                   f'<rect x="{legend_x + 160}" y="{y - 9}" width="{bar_w:.0f}" height="8" rx="4" fill="{t["border"]}"/>'
                   f'<rect x="{legend_x + 160}" y="{y - 9}" width="{bar_w * share / max(data["shares"].values()):.0f}" '
                   f'height="8" rx="4" fill="{colour}"/>'
                   f'<text x="{right}" y="{y}" font-size="15" fill="{t["dim2"]}" text-anchor="end">{share:.1f}%</text></g>')
        offset += share
    return out, max(cy + r + stroke / 2, legend_y + len(data["shares"]) * 34)


def svg(theme: str, data: dict, font_css: str, advance: float) -> str:
    t = banner.colours(theme)
    cmd, start = banner.prompt(PAD, BAR + 34, COMMAND, 0.4, t, advance, "g0")
    out, bottom = ring(theme, data, PAD, BAR + 56, WIDTH - PAD, start + 0.3)
    out.append(f'<text class="later" style="animation-delay:{start + 1.5:.2f}s" x="{PAD}" y="{bottom + 22}" '
               f'font-size="13" fill="{t["dim"]}">{escape(note(data))}</text>')
    final, _ = banner.prompt(PAD, bottom + 62, "", start + 1.7, t, advance, "g1", last=True)
    height = int(bottom + 92)
    before, after = window(theme, WIDTH, height)
    return "\n".join([
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{height}" viewBox="0 0 {WIDTH} {height}" '
        f'font-family="{neofetch.FAMILY}">',
        f"<style>{font_css}\n{banner.CSS}{RING_CSS}</style>",
        *before, *cmd, *out, *final, *after, "</svg>",
    ])


if __name__ == "__main__":
    data = measure()
    (ROOT / "assets/languages.json").write_text(json.dumps(data, indent=1) + "\n", encoding="utf-8")
    used = banner.PROMPT + COMMAND + "".join(data["shares"]) + "0123456789.%, ·:" + \
        "repositories of them private forks only my own commits"
    font_css, advance = neofetch.embedded_font(ROOT, neofetch.FONT_NAME, used)
    for theme in neofetch.THEMES:
        (ROOT / f"assets/languages-{theme}.svg").write_text(svg(theme, data, font_css, advance), encoding="utf-8")
    print(data["shares"])
