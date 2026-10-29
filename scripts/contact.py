"""The goodbye: the last commands of the activity terminal (scripts/activity.py), after the stats.

    david@padilla:~$ ./contact.sh       -> a headline typed out, then where to find me
    david@padilla:~$ exit               -> logout: the session that opens the profile closes here

The links go under the image, in the README (the same keys as at the top), since nothing inside an image can be
clicked.
"""

from html import escape

import banner
from terminal import PAD

COMMAND = "./contact.sh"
HEADLINE = [("Have a project in mind? ", "fg", 700), ("Let's talk.", "key", 700)]
CONTACT = [
    ("website", "davidpadilla.eu"),
    ("email", "me@davidpadilla.eu"),
    ("linkedin", "in/david-padilla-orenga"),
]
SIZE, LH = 15, 26
TEXT = COMMAND + "exit logout" + "".join(s for s, _, _ in HEADLINE) + "".join(k + v for k, v in CONTACT)


def body(theme: str, y: float, start: float, advance: float) -> tuple[list[str], float]:
    """From the prompt at `y` to the logout. Returns the elements and the height used."""
    t = banner.colours(theme)
    cw = advance * SIZE
    top = y
    out, start = banner.prompt(PAD, y, COMMAND, start, t, advance, "c0")
    y += 46
    head, start = banner.typed(PAD + 2 * cw, y, HEADLINE, 26, start + 0.3, 0.04, t, advance, "c1")
    out += head
    y += 18
    label_w = max(len(k) for k, _ in CONTACT) + 3
    for i, (key, value) in enumerate(CONTACT):
        y += LH
        out.append(f'<text class="later" style="animation-delay:{start + 0.2 + i * 0.2:.2f}s" x="{PAD + 2 * cw:.1f}" '
                   f'y="{y}" font-size="{SIZE}" xml:space="preserve"><tspan fill="{t["dim2"]}">{escape(key)}</tspan>'
                   f'<tspan x="{PAD + (2 + label_w) * cw:.1f}" fill="{t["fg"]}" font-weight="700">{escape(value)}</tspan>'
                   "</text>")
    start += 0.2 + len(CONTACT) * 0.2 + 0.6
    y += 44
    bye, start = banner.prompt(PAD, y, "exit", start, t, advance, "c2")
    out += bye
    y += LH
    out.append(f'<text class="later" style="animation-delay:{start + 0.2:.2f}s" x="{PAD}" y="{y}" font-size="{SIZE}" '
               f'fill="{t["dim"]}">logout</text>')
    return out, y - top
