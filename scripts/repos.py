"""Builds assets/repos-{light,dark}.svg: my projects, as `ls -l` in a terminal window.

A line per project, as `ls -l` prints a folder, then what it is. The permissions say which ones are open:
drwxr-xr-x anyone can read it (a public repository), drwx------ only the owner (client or research work with no
public code, told as a case study on the website). The links go under the image, in the README, since nothing
inside an image can be clicked.
Run from the repo root:  python scripts/repos.py
"""

from html import escape
from pathlib import Path

import banner
import neofetch
from services import WIDTH
from terminal import BAR, PAD, window

ROOT = Path(__file__).resolve().parent.parent
COMMAND = "ls -l ~/projects/"
SIZE, LH = 14, 22
# (name, public, tags, lines): from each repository's description and its case study on davidpadilla.eu
REPOS = [
    ("sfmkit/", True, "Python · MIT licence",
     ["Where was this century-old photograph taken from, and what has changed since?",
      "Structure from Motion written from the geometry up, scored against COLMAP."]),
    ("OVO/", True, "Python · fork of tberriel/OVO",
     ["Open-vocabulary 3D semantic mapping with SLAM: my master's thesis, on top of OVO.",
      "Three improvements: more consistent objects, merged five times faster."]),
    ("endoscopy-place-recognition/", False, "private · case study",
     ["Deep-learning place recognition in a real-time endoscopic SLAM, ported to C++."]),
    ("water-meter-iot-platform/", False, "private · case study",
     ["Remote reading of water meters over LoRaWAN or M-Bus, with alerts as soon as something goes wrong."]),
    ("enerforge-automation/", False, "private · case study",
     ["An engineering firm's paperwork, sorted by AI with human review at every step."]),
]


def svg(theme: str, font_css: str, advance: float) -> str:
    t = banner.colours(theme)
    cw = advance * SIZE
    cmd, start = banner.prompt(PAD, BAR + 34, COMMAND, 0.4, t, advance, "r0")
    start += 0.3
    out, y = [], BAR + 34
    for i, (name, public, tags, lines) in enumerate(REPOS):
        y += LH * 1.6
        mode = "drwxr-xr-x" if public else "drwx------"
        row = [f'<text x="{PAD}" y="{y:.1f}" font-size="{SIZE}" xml:space="preserve">'
               f'<tspan fill="{t["dim"]}">{mode}  </tspan><tspan fill="{t["key"]}" font-weight="700">{escape(name)}</tspan></text>',
               f'<text x="{WIDTH - PAD}" y="{y:.1f}" font-size="{SIZE - 1}" fill="{t["dim2"]}" '
               f'text-anchor="end">{escape(tags)}</text>']
        for k, line in enumerate(lines):
            row.append(f'<text x="{PAD + 12 * cw:.1f}" y="{y + (k + 1) * LH:.1f}" font-size="{SIZE}" '
                       f'fill="{t["fg"] if k == 0 else t["dim2"]}"{" font-style=\"italic\"" if k == 0 and public else ""} '
                       f'xml:space="preserve">{escape(line)}</text>')
        out.append(f'<g class="later" style="animation-delay:{start + i * 0.25:.2f}s">' + "".join(row) + "</g>")
        y += len(lines) * LH
    final, _ = banner.prompt(PAD, y + 46, "", start + len(REPOS) * 0.3 + 0.2, t, advance, "r1", last=True)
    height = int(y + 76)
    before, after = window(theme, WIDTH, height)
    return "\n".join([
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{height}" viewBox="0 0 {WIDTH} {height}" '
        f'font-family="{neofetch.FAMILY}">',
        f"<style>{font_css}\n{banner.CSS}</style>",
        *before, *cmd, *out, *final, *after, "</svg>",
    ])


if __name__ == "__main__":
    used = banner.PROMPT + COMMAND + "drwxr-x" + "".join(n + tg + "".join(ls) for n, _, tg, ls in REPOS)
    font_css, advance = neofetch.embedded_font(ROOT, neofetch.FONT_NAME, used)
    for theme in neofetch.THEMES:
        (ROOT / f"assets/repos-{theme}.svg").write_text(svg(theme, font_css, advance), encoding="utf-8")
