"""Build the multi-view area map (DRAFT): boating / biking / snowmobiling / eat & drink / golf.

Inputs (OpenStreetMap extracts, © OpenStreetMap contributors, ODbL):
  tools/data/osm-water.json            detailed Gull Lake area water
  tools/data/region/*.json             regional water, roads, golf, snow trails, rivers, bike trails
  tools/data/route-raw.json            boat route (tools/build_route.py)
  tools/data/area-pois.json            curated points of interest per view
Output: assets/img/area-map.svg (inline-able <svg>, uses the page's #i-* icon sprite)

Markers and labels are wrapped in groups scaled by the CSS variable --k, which the
page's JS sets from the current viewBox width, so they stay the same size on screen
at every zoom level.
"""
import json, math, os

HERE = os.path.dirname(__file__)
DATA = os.path.join(HERE, 'data')
S, N, W, E = 46.28, 46.80, -94.52, -93.85
WIDTH = 2400
KX = math.cos(math.radians((S + N) / 2))
HEIGHT = round(WIDTH * (N - S) / ((E - W) * KX))
GULL_BOX = (46.38, 46.55, -94.43, -94.28)

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

def ring_path(ring, eps):
    raw = [xy(la, lo) for la, lo in ring]
    if len(raw) < 4:
        return ''
    mid = len(raw) // 2
    pts = rdp(raw[: mid + 1], eps)[:-1] + rdp(raw[mid:], eps)
    if len(pts) < 3:
        return ''
    return 'M' + 'L'.join(f'{x:.1f} {y:.1f}' for x, y in pts) + 'Z'

def line_path(geom, eps):
    pts = rdp([xy(p['lat'], p['lon']) for p in geom], eps)
    return 'M' + 'L'.join(f'{x:.1f} {y:.1f}' for x, y in pts) if len(pts) > 1 else ''

def join_rings(ways):
    ways = [list(w) for w in ways if w]
    rings = []
    while ways:
        ring = ways.pop(0)
        changed = True
        while ring[0] != ring[-1] and changed:
            changed = False
            for i, w in enumerate(ways):
                if w[0] == ring[-1]: ring += w[1:]
                elif w[-1] == ring[-1]: ring += w[::-1][1:]
                elif w[-1] == ring[0]: ring = w[:-1] + ring
                elif w[0] == ring[0]: ring = w[::-1][:-1] + ring
                else: continue
                ways.pop(i); changed = True; break
        rings.append(ring)
    return rings

def load(path):
    p = os.path.join(DATA, path)
    return json.load(open(p))['elements'] if os.path.exists(p) else []

def area_rings(e):
    if e['type'] == 'way':
        g = e.get('geometry') or []
        return [[(p['lat'], p['lon']) for p in g]], []
    outer = [[(p['lat'], p['lon']) for p in m.get('geometry', [])] for m in e.get('members', []) if m.get('role') == 'outer']
    inner = [[(p['lat'], p['lon']) for p in m.get('geometry', [])] for m in e.get('members', []) if m.get('role') == 'inner']
    return join_rings(outer), join_rings(inner)

def in_gull(e):
    b = e.get('bounds') or {}
    return b and b['minlat'] < GULL_BOX[1] and b['maxlat'] > GULL_BOX[0] and b['minlon'] < GULL_BOX[3] and b['maxlon'] > GULL_BOX[2]

def bbox_area(e):
    b = e.get('bounds') or {}
    return (b.get('maxlat', 0) - b.get('minlat', 0)) * (b.get('maxlon', 0) - b.get('minlon', 0))

# Boat-connected Gull chain (OSM ids) and private Lost Lake
CHAIN_IDS = {('relation', 911711), ('way', 59071053), ('way', 59073622), ('relation', 911693),
             ('way', 59073710), ('way', 59064941), ('way', 59056105)}
LOST_ID = ('way', 59056549)

# ---------- water ----------
seen, chain, lost, other = set(), [], [], []
for e in load('osm-water.json') + [x for f in sorted(os.listdir(os.path.join(DATA, 'region'))) if f.startswith('water') for x in load(os.path.join('region', f))]:
    key = (e['type'], e['id'])
    if key in seen:
        continue
    seen.add(key)
    near = in_gull(e)
    if not near and bbox_area(e) < 2.5e-6:   # drop tiny ponds away from Gull Lake
        continue
    eps = 0.35 if near else 1.4
    outer, inner = area_rings(e)
    d = ''.join(ring_path(r, eps) for r in outer + inner)
    if not d:
        continue
    (lost if key == LOST_ID else chain if key in CHAIN_IDS else other).append(d)

# ---------- lines ----------
def load_prefix(prefix):
    d = os.path.join(DATA, 'region')
    return [x for f in sorted(os.listdir(d)) if f.startswith(prefix) for x in load(os.path.join('region', f))]

def lines(prefix, keep, eps):
    out = []
    for e in load_prefix(prefix):
        t = e.get('tags', {})
        if e['type'] == 'way' and keep(t):
            d = line_path(e.get('geometry') or [], eps)
            if d: out.append((t, d))
        elif e['type'] == 'relation' and keep(t):
            for m in e.get('members', []):
                if m.get('type') == 'way' and m.get('geometry'):
                    d = line_path(m['geometry'], eps)
                    if d: out.append((t, d))
    return out

roads = lines('roads', lambda t: True, 1.2)
rivers = lines('river', lambda t: t.get('name') in ('Mississippi River', 'Crow Wing River', 'Pine River'), 1.2)
snow = lines('snow', lambda t: True, 1.0)
bike = lines('bike', lambda t: True, 0.8)
golf_areas = []
for e in load_prefix('golf'):
    outer, inner = area_rings(e)
    d = ''.join(ring_path(r, 0.8) for r in outer + inner)
    if d: golf_areas.append(d)

# ---------- boat route (precomputed in the old 1000-wide Gull map projection) ----------
OS, ON, OW, OE = 46.385, 46.545, -94.425, -94.285
OKX = math.cos(math.radians((OS + ON) / 2)); OH = round(1000 * (ON - OS) / ((OE - OW) * OKX))
def old_to_new(x, y):
    lon = OW + x / 1000 * (OE - OW); lat = ON - y / OH * (ON - OS)
    return xy(lat, lon)
route_d = ''
rp = os.path.join(DATA, 'route-raw.json')
if os.path.exists(rp):
    pts = [old_to_new(*p) for p in json.load(open(rp))]
    pts = rdp(pts, 2.2 * 0.6)
    for _ in range(2):
        pts = [pts[0]] + [q for a, b in zip(pts, pts[1:]) for q in ((a[0]*.75 + b[0]*.25, a[1]*.75 + b[1]*.25), (a[0]*.25 + b[0]*.75, a[1]*.25 + b[1]*.75))] + [pts[-1]]
    route_d = 'M' + 'L'.join(f'{x:.1f} {y:.1f}' for x, y in pts)

# ---------- points ----------
pois = json.load(open(os.path.join(DATA, 'area-pois.json'))) if os.path.exists(os.path.join(DATA, 'area-pois.json')) else {}

def esc(s):
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('"', '&quot;')

def scaled(x, y, inner, cls, extra=''):
    return f'<g class="{cls}" style="transform:translate({x:.1f}px,{y:.1f}px) scale(var(--k,1))"{extra}>{inner}</g>'

out = [f'<svg class="lake-map area-map" viewBox="0 0 {WIDTH} {HEIGHT}" role="img" aria-labelledby="am-title am-desc" xmlns="http://www.w3.org/2000/svg">',
       '<title id="am-title">Map of Gull Lake and the Brainerd Lakes area around Cottage 9</title>',
       '<desc id="am-desc">Interactive map with views for boating, biking, snowmobiling, restaurants and golf around Cottage 9 at Lost Lake Lodge.</desc>',
       f'<defs><clipPath id="am-clip"><rect width="{WIDTH}" height="{HEIGHT}"/></clipPath></defs>',
       f'<rect class="map-land" width="{WIDTH}" height="{HEIGHT}"/>',
       '<g clip-path="url(#am-clip)">',
       '<g class="layer layer-golfarea">' + ''.join(f'<path d="{d}"/>' for d in golf_areas) + '</g>',
       '<g class="map-river">' + ''.join(f'<path d="{d}"/>' for _, d in rivers) + '</g>',
       '<g class="map-other">' + ''.join(f'<path d="{d}"/>' for d in other) + '</g>',
       '<g class="map-chain">' + ''.join(f'<path d="{d}"/>' for d in chain) + '</g>',
       '<g class="map-lost">' + ''.join(f'<path d="{d}"/>' for d in lost) + '</g>',
       '<g class="map-roads">' + ''.join(f'<path class="r-{esc(t.get("highway", ""))}" d="{d}"/>' for t, d in roads) + '</g>',
       '<g class="layer layer-bike map-trail">' + ''.join(f'<path d="{d}"/>' for _, d in bike) + '</g>',
       '<g class="layer layer-snow map-snow">' + ''.join(f'<path d="{d}"/>' for _, d in snow) + '</g>',
       f'<g class="layer layer-boating"><path class="map-route" pathLength="1" d="{route_d}"/></g>' if route_d else '',
       '</g>']

# lake + town labels (scaled so they stay readable)
LAKES = [("Gull Lake", 46.462, -94.343, 'big', 'boating'), ("Upper Gull", 46.528, -94.3575, '', 'boating'),
         ("Lake Margaret", 46.4935, -94.381, '', 'boating'), ("Roy Lake", 46.5108, -94.3205, 'water', 'boating'),
         ("North Long Lake", 46.44, -94.24, '', 'all'), ("Pelican Lake", 46.60, -94.15, '', 'all'),
         ("Cross Lake", 46.67, -94.11, '', 'all')]
for name, la, lo, kind, layer in LAKES:
    x, y = xy(la, lo)
    cls = 'map-label' + (' map-label-big' if kind == 'big' else '') + (' map-label-water' if kind == 'water' else '')
    out.append(scaled(x, y, f'<text class="{cls}" text-anchor="middle" font-size="{30 if kind == "big" else 14}">{name}</text>',
                      f'lbl layer layer-{layer}' if layer != 'all' else 'lbl layer layer-wide'))
TOWNS = [("Nisswa", 46.5205, -94.2886), ("Pequot Lakes", 46.6030, -94.3094), ("Breezy Point", 46.6166, -94.2169),
         ("Baxter", 46.3433, -94.2867), ("Brainerd", 46.3580, -94.2008), ("Crosslake", 46.6594, -94.1139),
         ("Merrifield", 46.4650, -94.1728), ("Jenkins", 46.6461, -94.3347), ("Crosby", 46.4822, -93.9578)]
for name, la, lo in TOWNS:
    x, y = xy(la, lo)
    out.append(scaled(x, y, f'<circle r="4.5"/><text x="8" y="5" font-size="15">{name}</text>', 'map-town'))

# launch + home
lx, ly = xy(46.50991, -94.34394)
out.append(scaled(lx, ly, '<line x1="0" y1="0" x2="24" y2="10"/><circle cx="30" cy="12" r="11"/><use href="#i-launch" x="22" y="4" width="16" height="16"/>',
                  'map-launch layer layer-boating', ' data-poi="boating-L"'))

for layer, items in pois.items():
    for i, p in enumerate(items, 1):
        if p.get('lat') is None:
            continue
        x, y = xy(p['lat'], p['lon'])
        num = str(p.get('num', i))
        fs = 15 if len(num) == 1 else 12.5
        star = '<circle class="pick" cx="10" cy="-10" r="5"/>' if p.get('pick') else ''
        out.append(scaled(x, y, f'<title>{esc(p["name"])}</title><circle r="13"/><text y="5" text-anchor="middle" font-size="{fs}">{num}</text>{star}',
                          f'map-poi layer layer-{layer}', f' data-poi="{layer}-{num}"'))

hx, hy = xy(46.5185, -94.3462)
out.append(scaled(hx, hy, '<circle class="map-home-pulse" r="20"/><circle r="11"/>'
                          '<g class="home-tag"><rect x="-118" y="-15" width="92" height="30" rx="15"/><text x="-72" y="5" text-anchor="middle" font-size="14">Cottage 9</text>'
                          '<path d="M-26 0H-12" class="map-home-leader"/></g>', 'map-home'))
out.append(f'<text class="map-credit" x="{WIDTH - 12}" y="{HEIGHT - 12}" text-anchor="end" font-size="14">Map data © OpenStreetMap contributors</text>')
out.append('</svg>')
svg = '\n'.join(o for o in out if o)
open(os.path.join(HERE, '..', 'assets', 'img', 'area-map.svg'), 'w').write(svg)

# viewBoxes for each view (aspect 0.8 = width / height), centered on lat/lon boxes
def box(s, n, w, e, aspect=0.8, pad=1.04):
    x0, y0 = xy(n, w); x1, y1 = xy(s, e)
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    bw, bh = (x1 - x0) * pad, (y1 - y0) * pad
    if bw / bh > aspect: bh = bw / aspect
    else: bw = bh * aspect
    return f'{cx - bw / 2:.0f} {cy - bh / 2:.0f} {bw:.0f} {bh:.0f}'
views = {
    'boating': box(46.385, 46.545, -94.425, -94.285),
    'north':   box(46.495, 46.535, -94.365, -94.282, pad=1.12),
    'biking':  box(46.40, 46.63, -94.40, -94.20),
    'snow':    box(46.33, 46.70, -94.45, -94.08),
    'eat':     box(46.33, 46.67, -94.42, -94.12),
    'golf':    box(46.33, 46.78, -94.42, -93.86),
    'todo':    box(46.27, 46.56, -94.42, -93.98),
}
json.dump(views, open(os.path.join(HERE, '..', 'assets', 'img', 'area-map-views.json'), 'w'), indent=1)
print('svg bytes', len(svg), 'views', views)
