"""Find a boat route through the Gull chain from the Narrows (Cottage 9) to the
Nisswa Lake Park public docks, using OSM water polygons. Needs Pillow.
Usage: python tools/build_route.py  ->  tools/data/route-raw.json
"""
import json, math, sys
from collections import deque
from PIL import Image, ImageDraw, ImageFilter

S_, N_, W_, E_ = 46.385, 46.545, -94.425, -94.285
WIDTH = 1000; KX = math.cos(math.radians((S_+N_)/2)); HEIGHT = round(WIDTH*(N_-S_)/((E_-W_)*KX))
SC = 3
def xy(lat, lon): return ((lon-W_)/(E_-W_)*WIDTH*SC, (N_-lat)/(N_-S_)*HEIGHT*SC)
d = json.load(open('/Users/lhouge/Code/lost-lake-cabin-9/tools/data/osm-water.json'))
img = Image.new('L', (WIDTH*SC, HEIGHT*SC), 0); dr = ImageDraw.Draw(img)
for e in d['elements']:
    if e.get('tags',{}).get('name') == 'Lost Lake': continue   # separate lake, not navigable to Gull
    rings = []
    if e['type']=='way': rings=[e.get('geometry') or []]; holes=[]
    else:
        rings=[m.get('geometry',[]) for m in e['members'] if m.get('role')=='outer']
        holes=[m.get('geometry',[]) for m in e['members'] if m.get('role')=='inner']
    for r in rings:
        if len(r)>2: dr.polygon([xy(p['lat'],p['lon']) for p in r], fill=255)
    for r in (holes if e['type']!='way' else []):
        if len(r)>2: dr.polygon([xy(p['lat'],p['lon']) for p in r], fill=0)
img = img.filter(ImageFilter.MaxFilter(7))  # bridge narrow channels mapped as lines
W, H = img.size; px = img.load()
def nearest_water(x, y):
    best=None
    for r in range(0, 200):
        for dx in range(-r, r+1):
            for dy in (-r, r):
                for (a,b) in ((x+dx,y+dy),(x+dy,y+dx)):
                    if 0<=a<W and 0<=b<H and px[a,b]>0: return (a,b)
    return None
sx, sy = map(int, xy(46.5185, -94.3462)); ex, ey = map(int, xy(46.5193, -94.2907))
s = nearest_water(sx, sy); t = nearest_water(ex, ey)
print('start', s, 'end', t)
prev = {s: None}; q = deque([s])
while q:
    c = q.popleft()
    if c == t: break
    x, y = c
    for dx, dy in ((1,0),(-1,0),(0,1),(0,-1),(1,1),(1,-1),(-1,1),(-1,-1)):
        n = (x+dx, y+dy)
        if 0<=n[0]<W and 0<=n[1]<H and px[n]>0 and n not in prev:
            prev[n] = c; q.append(n)
if t not in prev: print('NO PATH'); sys.exit(1)
path=[]; c=t
while c: path.append(c); c=prev[c]
path=path[::-1]
print('len', len(path))
json.dump([(x/SC, y/SC) for x,y in path], open('/Users/lhouge/Code/lost-lake-cabin-9/tools/data/route-raw.json','w'))
