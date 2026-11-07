"""Build the Cottage 9 badge logo (option E) with seasonal accents.

Writes assets/img/logo-{summer,fall,winter}.svg and prints an inline <svg>
(all three variants, toggled by [data-only]) for the site header.
Usage: python3 tools/build_logo.py > /tmp/inline.svg
"""
import math, os

OUT = os.path.join(os.path.dirname(__file__), '..', 'assets', 'img')
VB = '-7 -9 78 78'  # room around the 64px badge for accents

PALETTES = {
    'summer': dict(bg='#0f3b4f', ring='#ffc857', nine='#ffc857', pine='#f7efe1', wave='#7fc4d6'),
    'fall':   dict(bg='#2b2a1e', ring='#f0a73a', nine='#e07a2e', pine='#f7efe1', wave='#8fb3a8'),
    'winter': dict(bg='#14263a', ring='#a9d6f2', nine='#a9d6f2', pine='#f7efe1', wave='#cfe6f5'),
}

def badge(p):
    return (f'<circle cx="32" cy="32" r="32" fill="{p["bg"]}"/>'
            f'<circle cx="32" cy="32" r="27" fill="none" stroke="{p["ring"]}" stroke-width="1.6" stroke-dasharray="2.5 3"/>'
            f'<path d="M22 13 28 22h-3l5 8h-4l6 9H14l6-9h-4l5-8h-3z" fill="{p["pine"]}"/>'
            f'<text x="42" y="44" text-anchor="middle" font-family="Fraunces, Georgia, \'Times New Roman\', serif" font-style="italic" font-weight="700" font-size="30" fill="{p["nine"]}">9</text>'
            f'<path d="M13 50q4.75-3 9.5 0t9.5 0 9.5 0 9.5 0" fill="none" stroke="{p["wave"]}" stroke-width="2.4" stroke-linecap="round"/>')

def smooth(pts):
    """Closed Catmull-Rom spline through pts, as cubic Bezier path data."""
    n = len(pts)
    out = [f'M{pts[0][0]:.1f} {pts[0][1]:.1f}']
    for i in range(n):
        p0, p1, p2, p3 = pts[i - 1], pts[i], pts[(i + 1) % n], pts[(i + 2) % n]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        out.append(f'C{c1[0]:.1f} {c1[1]:.1f} {c2[0]:.1f} {c2[1]:.1f} {p2[0]:.1f} {p2[1]:.1f}')
    return ''.join(out) + 'Z'

def snow_cap():
    """Snow drift hugging the top of the badge, with a few drips."""
    a0, a1 = math.radians(-158), math.radians(-22)
    outer = []
    for i in range(13):
        a = a0 + (a1 - a0) * i / 12
        r = 33.4 + 2.4 * math.sin(i / 12 * math.pi) + (0.9 if i % 2 else -0.3)  # soft lumpy top
        outer.append((32 + r * math.cos(a), 32 + r * math.sin(a)))
    inner = []
    drips = {4: 4.2, 9: 3.0, 14: 5.0}   # index -> drip length
    for i in range(18, -1, -1):
        a = a0 + (a1 - a0) * i / 18
        r = 28.4 - 0.8 * math.sin(i * 1.3) - drips.get(i, 0)
        inner.append((32 + r * math.cos(a), 32 + r * math.sin(a)))
    d = smooth(outer + inner)
    return (f'<path d="{d}" fill="#ffffff" stroke="#dbe9f3" stroke-width=".8" stroke-linejoin="round"/>'
            '<g fill="#ffffff"><circle cx="9" cy="40" r="1.3"/><circle cx="56" cy="44" r="1.1"/><circle cx="50" cy="56" r="1"/><circle cx="16" cy="55" r=".9"/><circle cx="37" cy="21" r=".9"/></g>')

LEAF = 'M0 -10C1 -7 3 -6 6 -7C5 -4 6 -2 9 -1C6 0 5 2 6 5C3 4 1 5 0 9C-1 5 -3 4 -6 5C-5 2 -6 0 -9 -1C-6 -2 -5 -4 -6 -7C-3 -6 -1 -7 0 -10Z'

def leaves():
    return (f'<g transform="translate(55 6) rotate(28) scale(1.15)"><path d="{LEAF}" fill="#d9622b"/><path d="M0 -5V13" stroke="#7a3214" stroke-width=".9" stroke-linecap="round"/></g>'
            f'<g transform="translate(5 52) rotate(-35) scale(.7)"><path d="{LEAF}" fill="#e9a23b"/><path d="M0 -5V13" stroke="#8a5a14" stroke-width="1.1" stroke-linecap="round"/></g>')

def sun_behind():
    rays = ''.join(
        f'<line x1="{56 + 11 * math.cos(math.radians(a)):.1f}" y1="{6 + 11 * math.sin(math.radians(a)):.1f}" '
        f'x2="{56 + 15 * math.cos(math.radians(a)):.1f}" y2="{6 + 15 * math.sin(math.radians(a)):.1f}"/>'
        for a in range(-150, 60, 30))
    return (f'<g stroke="#ffc857" stroke-width="2.2" stroke-linecap="round">{rays}</g>'
            '<circle cx="56" cy="6" r="8.5" fill="#ffc857"/>')

def svg_for(season, inline=False):
    p = PALETTES[season]
    behind = sun_behind() if season == 'summer' else ''
    front = snow_cap() if season == 'winter' else leaves() if season == 'fall' else ''
    body = behind + badge(p) + front
    return body

for s in PALETTES:
    with open(os.path.join(OUT, f'logo-{s}.svg'), 'w') as f:
        f.write(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{VB}">{svg_for(s)}</svg>\n')

print(f'<svg class="logo" viewBox="{VB}" aria-hidden="true">'
      + ''.join(f'<g data-only="{s}">{svg_for(s)}</g>' for s in PALETTES) + '</svg>')
