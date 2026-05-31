# getweb recipe: mathnet.mit.edu
#
# MathNet is a single-page app. Its problem data is fetched at runtime by
# js/data.js from data_v2/ using paths COMPUTED in JavaScript from manifest.json
# (full/<source>/<slug>.json.gz, chunks/<source>/<year>.json.gz). A generic
# crawler can't reconstruct those, so this recipe enumerates them from the site's
# own manifest. getweb sources this file and calls recipe_expand().
#
# Available env when sourced: SAVE_DIR, ORIGIN, HOST.

recipe_expand() {
  local base="$ORIGIN/data_v2"
  local mf="$SAVE_DIR/data_v2/manifest.json.gz"

  mkdir -p "$SAVE_DIR/data_v2"
  # Need the manifest to expand; fetch it if we don't have it yet.
  [ -s "$mf" ] || curl -fsSL --compressed --retry 3 -o "$mf" "$base/manifest.json.gz" 2>/dev/null || return 0

  # Site-level metadata files (plain names; the app appends ?v=<hash> at runtime).
  local f
  for f in version.json manifest.json.gz sources.json.gz competitions.json.gz \
           topics.json.gz topic_index.json.gz stats.json.gz landing.json.gz; do
    echo "$base/$f"
  done

  # Every problem (full/) and every (source,year) list (chunks/).
  python3 - "$mf" "$base" <<'PY'
import sys, gzip, json
mf, base = sys.argv[1], sys.argv[2]
try:
    m = json.loads(gzip.open(mf, "rb").read())
except Exception:
    sys.exit(0)
seen = set()
for r in m.get("rows", []):
    slug, src, year = r[0], r[1], (r[2] or 0)
    if (src, year) not in seen:
        seen.add((src, year)); print(f"{base}/chunks/{src}/{year}.json.gz")
    print(f"{base}/full/{src}/{slug}.json.gz")
PY
}
