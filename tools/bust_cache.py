"""Stamp asset links in index.html with a content hash (?v=xxxxxxxx) so browsers
fetch fresh CSS/JS after each update. Run before committing: python3 tools/bust_cache.py"""
import hashlib, os, re
ROOT = os.path.join(os.path.dirname(__file__), '..')
page = os.path.join(ROOT, 'index.html')
s = open(page).read()
for asset in ['assets/css/site.css', 'assets/js/site.js']:
    h = hashlib.md5(open(os.path.join(ROOT, asset), 'rb').read()).hexdigest()[:8]
    s, n = re.subn(re.escape(asset) + r'(\?v=[0-9a-f]+)?"', f'{asset}?v={h}"', s)
    print(asset, h, n)
open(page, 'w').write(s)
