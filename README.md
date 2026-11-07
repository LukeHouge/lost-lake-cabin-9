# Cottage 9 at Lost Lake Lodge

Marketing site for Cottage 9, a 4BR/3BA lake house at Lost Lake Lodge on Gull Lake (Nisswa, MN).

- **Live:** https://lukehouge.github.io/lost-lake-cabin-9/ (GitHub Pages, deploys from `main` root)
- **Design versions for review:** https://lukehouge.github.io/lost-lake-cabin-9/versions/
- **Photos:** [images/README.md](images/README.md) (shot list). Process new ones with `tools/process_photos.py` (needs Pillow).
- **Lake map:** `python3 tools/build_map.py tools/data/osm-water.json`, then paste the output between the MAP markers in `index.html`. Map data © OpenStreetMap contributors.
- **Theme preview:** add `?season=summer|fall|winter` to any URL.

## Local preview

```sh
python3 -m http.server 8000
# open http://localhost:8000
```

Plain static HTML/CSS/JS, no build step.

> This repo is public. Keep planning notes, pricing discussions and research out of it.
