"""Build an illustrated SVG map of the Gull Lake area from OpenStreetMap data.

Usage: python3 tools/build_map.py water.json > assets/img/gull-lake-map.svg
water.json = Overpass `out geom` result for natural=water in the bbox below.
Map data © OpenStreetMap contributors (ODbL).
"""
import json, math, sys

S, N, W, E = 46.385, 46.545, -94.425, -94.285
WIDTH = 1000
KX = math.cos(math.radians((S + N) / 2))
HEIGHT = round(WIDTH * (N - S) / ((E - W) * KX))

def xy(lat, lon):
    return ((lon - W) / (E - W) * WIDTH, (N - lat) / (N - S) * HEIGHT)

def rdp(pts, eps):
    if len(pts) < 3:
        return pts
    (x1, y1), (x2, y2) = pts[0], pts[-1]
    dx, dy = x2 - x1, y2 - y1
    norm = math.hypot(dx, dy) or 1e-9
    i_max, d_max = 0, 0
    for i in range(1, len(pts) - 1):
        d = abs(dy * pts[i][0] - dx * pts[i][1] + x2 * y1 - y2 * x1) / norm
        if d > d_max:
            i_max, d_max = i, d
    if d_max > eps:
        return rdp(pts[: i_max + 1], eps)[:-1] + rdp(pts[i_max:], eps)
    return [pts[0], pts[-1]]

def join_rings(ways):
    """Stitch way geometries into closed rings."""
    ways = [list(w) for w in ways if w]
    rings = []
    while ways:
        ring = ways.pop(0)
        changed = True
        while ring[0] != ring[-1] and changed:
            changed = False
            for i, w in enumerate(ways):
                if w[0] == ring[-1]:
                    ring += w[1:]
                elif w[-1] == ring[-1]:
                    ring += w[::-1][1:]
                elif w[-1] == ring[0]:
                    ring = w[:-1] + ring
                elif w[0] == ring[0]:
                    ring = w[::-1][:-1] + ring
                else:
                    continue
                ways.pop(i)
                changed = True
                break
        rings.append(ring)
    return rings

def path(rings, eps=0.6):
    out = []
    for r in rings:
        raw = [xy(lat, lon) for lat, lon in r]
        mid = len(raw) // 2  # split closed rings so RDP has a real baseline
        pts = rdp(raw[: mid + 1], eps)[:-1] + rdp(raw[mid:], eps)
        if len(pts) < 3:
            continue
        out.append("M" + "L".join(f"{x:.1f} {y:.1f}" for x, y in pts) + "Z")
    return "".join(out)

CHAIN = {"Gull Lake", "Upper Gull Lake", "Lake Margaret", "Roy Lake", "Spider Lake", "Bass Lake", "Round Lake"}

data = json.load(open(sys.argv[1]))
chain, other, lost = [], [], []
for e in data["elements"]:
    name = e.get("tags", {}).get("name", "")
    if e["type"] == "way":
        g = e.get("geometry") or []
        rings = [[(p["lat"], p["lon"]) for p in g]]
        holes = []
    else:
        outer = [[(p["lat"], p["lon"]) for p in m.get("geometry", [])] for m in e["members"] if m.get("role") == "outer"]
        inner = [[(p["lat"], p["lon"]) for p in m.get("geometry", [])] for m in e["members"] if m.get("role") == "inner"]
        rings, holes = join_rings(outer), join_rings(inner)
    d = path(rings + holes)
    if not d:
        continue
    if name == "Lost Lake":
        lost.append(d)
    elif name in CHAIN and (name != "Bass Lake" or e["id"] == 59064941):
        chain.append(d)
    else:
        other.append(d)

def pt(lat, lon):
    x, y = xy(lat, lon)
    return f'{x:.0f}', f'{y:.0f}'

# Points of interest (lat, lon). Cottage 9 position is approximate:
# between private Lost Lake (east) and the Gull Lake Narrows (west).
HOME = (46.5185, -94.3462)
POIS = [
    ("1", "Zorbaz on Gull", 46.5110, -94.3442),
    ("2", "Bar Harbor Supper Club", 46.5080, -94.3499),
    ("3", "Dock 77 at Quarterdeck", 46.4483, -94.3635),
    ("4", "Ernie's on Gull", 46.4230, -94.3608),
    ("5", "Gull Point sandbar", 46.4195, -94.3530),
    ("6", "Gull Lake Dam &amp; Rec Area", 46.4111, -94.3534),
    ("7", "Grand View Lodge golf", 46.4980, -94.3135),
    ("8", "Madden's · The Classic", 46.3960, -94.3740),
]

hx, hy = pt(*HOME)
svg = [f'<svg class="lake-map" viewBox="0 0 {WIDTH} {HEIGHT}" style="overflow:hidden" role="img" aria-labelledby="map-title map-desc" xmlns="http://www.w3.org/2000/svg">',
       '<title id="map-title">Map of Gull Lake showing Cottage 9</title>',
       '<desc id="map-desc">Illustrated map of the Gull Lake chain near Nisswa, Minnesota. Cottage 9 sits at the north end between private Lost Lake and the Gull Lake Narrows. Numbered markers show boat-up restaurants, the sandbar, the dam and golf.</desc>',
       f'<defs><clipPath id="map-clip"><rect width="{WIDTH}" height="{HEIGHT}"/></clipPath></defs>',
       f'<rect class="map-land" width="{WIDTH}" height="{HEIGHT}"/>',
       '<g clip-path="url(#map-clip)">',
       f'<g class="map-other">' + "".join(f'<path d="{d}"/>' for d in other) + '</g>',
       f'<g class="map-chain">' + "".join(f'<path d="{d}"/>' for d in chain) + '</g>',
       f'<g class="map-lost">' + "".join(f'<path d="{d}"/>' for d in lost) + '</g>', '</g>']

# Lake labels
for label, lat, lon, size, cls in [
    ("GULL LAKE", 46.462, -94.343, 34, "map-label-big"),
    ("Upper Gull", 46.528, -94.3575, 15, "map-label"),
    ("Lake Margaret", 46.4935, -94.381, 15, "map-label"),
    ("Roy Lake", 46.5345, -94.316, 15, "map-label"),
]:
    x, y = pt(lat, lon)
    svg.append(f'<text class="{cls}" x="{x}" y="{y}" text-anchor="middle" font-size="{size}">{label}</text>')
nx, ny = pt(46.5205, -94.2886)
svg.append(f'<g class="map-town"><circle cx="{nx}" cy="{ny}" r="6"/><text x="{int(nx) - 12}" y="{int(ny) + 5}" text-anchor="end" font-size="17">Nisswa</text></g>')

for num, name, lat, lon in POIS:
    x, y = pt(lat, lon)
    svg.append(f'<g class="map-poi"><title>{name}</title><circle cx="{x}" cy="{y}" r="13"/><text x="{x}" y="{int(y) + 5}" text-anchor="middle" font-size="15">{num}</text></g>')

lx, ly = pt(46.5205, -94.3405)
svg.append(f'<text class="map-label map-label-lost" x="{int(lx) + 14}" y="{ly}" font-size="14">Lost Lake</text>')
svg.append(f'<g class="map-home"><circle class="map-home-pulse" cx="{hx}" cy="{hy}" r="20"/>'
           f'<circle cx="{hx}" cy="{hy}" r="11"/>'
           f'<g transform="translate({int(hx) - 205} {int(hy) - 62})"><rect width="170" height="42" rx="21"/>'
           f'<text x="85" y="27" text-anchor="middle" font-size="18">Cottage 9 is here</text></g>'
           f'<path d="M{int(hx) - 40} {int(hy) - 30} L{int(hx) - 14} {int(hy) - 8}" class="map-home-leader"/></g>')
# Compass
cx, cy = WIDTH - 60, HEIGHT - 70
svg.append(f'<g class="map-compass" transform="translate({cx} {cy})"><path d="M0 -30 L9 0 L0 -6 L-9 0Z"/><text y="-38" text-anchor="middle" font-size="15">N</text></g>')
svg.append(f'<text class="map-credit" x="{WIDTH - 12}" y="{HEIGHT - 12}" text-anchor="end" font-size="11">Map data © OpenStreetMap contributors</text>')
svg.append('</svg>')
print("\n".join(svg))
