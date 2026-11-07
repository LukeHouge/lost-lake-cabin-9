"""Resize/compress selected photos into images/ as WebP (EXIF/GPS stripped).
Usage: python tools/process_photos.py "<path to 'cabin pics' folder>"
"""
import sys, os
from PIL import Image, ImageOps
SRC = sys.argv[1]; OUT = os.path.join(os.path.dirname(__file__), '..', 'images')
M, R = 'mine', 'from resort'
PICKS = {  # output name: (folder, file, max width)
  'hero-summer': (M, 'IMG_5969.jpeg', 2400),
  'hero-summer-tall': (M, 'IMG_4039.jpeg', 1200),
  'hero-fall': (R, 'Lost-Lake-Fall-20-PS-120.jpg', 2250),
  'hero-winter': (M, 'IMG_5976.jpeg', 2400),
  'exterior': (M, 'IMG_4007.jpeg', 1600),
  'exterior-pro': (R, 'Cottage_9.13_PS_120.avif', 1600),
  'great-room': (M, 'IMG_6538.jpeg', 1200),
  'great-room-pro': (R, 'Cottage_9.1_PS_120.avif', 1600),
  'kitchen': (R, 'Cottage_9.2_PS_120.avif', 1600),
  'dining': (R, 'Cottage_9.3_PS_120.avif', 1600),
  'porch': (M, 'IMG_1364.jpeg', 1600),
  'deck-sunset': (M, 'IMG_1693.jpeg', 1600),
  'loft': (R, 'Cottage_9.8_PS_120.avif', 1600),
  'lower-lounge': (R, 'Cottage_9.9_PS_120.avif', 1600),
  'lower-tv': (M, 'IMG_6561.jpeg', 1600),
  'pool-table': (M, 'IMG_8291.jpeg', 1600),
  'wet-bar': (R, 'Cottage_9.10_PS_120.avif', 1600),
  'bed-king': (R, 'Cottage_9.4_PS_120.avif', 1600),
  'bed-queens': (R, 'Cottage_9.6_PS_120.avif', 1600),
  'bed-queens-2': (R, 'Cottage_9.7_PS_120.avif', 1600),
  'bed-lower-king': (R, 'Cottage_9.12_PS_120.avif', 1600),
  'bath': (R, 'Cottage_9.5_PS_120.avif', 1600),
  'dock-sunset': (M, 'IMG_4040.jpeg', 1200),
  'dock-dusk': (M, 'IMG_5966.jpeg', 1200),
  'dock-stairs': (M, 'IMG_6414.jpeg', 1200),
  'fall-path': (M, 'IMG_7926.jpeg', 1600),
  'fall-birches': (M, 'IMG_7928.jpeg', 1600),
  'fall-view': (M, 'a6831c67-a907-4331-a1b9-2a349fc38424.jpeg', 1600),
  'lost-lake-beach': (R, 'Lost-Lake-Lodge-Summer-9-PS-120.webp', 2000),
  'resort-aerial': (R, 'Lost-Lake-Lodge-Summer-PS-120.webp', 2000),
  'resort-docks': (R, 'LLL-Exterior-25-PS-120-1620x1080.jpg', 1620),
  'beach-fall': (R, 'Scenic-5-605x465.jpg', 605),
  'restaurant-food': (R, 'Foood-13-605x465.jpg', 605),
}
os.makedirs(OUT, exist_ok=True)
for name, (folder, fn, maxw) in PICKS.items():
    im = ImageOps.exif_transpose(Image.open(os.path.join(SRC, folder, fn))).convert('RGB')
    if im.width > maxw:
        im = im.resize((maxw, round(im.height * maxw / im.width)), Image.LANCZOS)
    p = os.path.join(OUT, name + '.webp')
    im.save(p, 'WEBP', quality=74, method=6)
    print(f'{name:18} {im.width}x{im.height} {os.path.getsize(p)//1024} KB')
