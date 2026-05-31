#!/usr/bin/env bash
# getweb.sh - mirror a website to a local directory, including JS-loaded data.
#
# Version: 0.4
# Author:  Baohua Yang@THU
# Created: May 27, 2011
# Updated: 2026  (v0.4: incremental re-runs, data-layer discovery, headless render)
#
# Classic wget --mirror only follows links written in the HTML. Modern sites
# fetch much of their content at runtime with JavaScript (fetch/XHR), which wget
# never sees. v0.4 layers three cooperating phases on top of the wget core:
#
#   Phase 1  static mirror   wget, now with proper *incremental* re-runs
#                            (timestamping: only changed files are re-downloaded)
#   Phase 2  --data          after mirroring, discover same-origin resources the
#                            static crawl missed - sitemap.xml entries, manifest/
#                            JSON files, and URL strings embedded in the saved
#                            HTML/JS/CSS/JSON - and fetch them (recursively)
#   Phase 3  --render[=N]    drive headless Chrome to actually RUN the page's JS,
#                            capture every URL it requests (Chrome netlog) plus
#                            the rendered DOM, and fetch those too. This is what
#                            lets it mirror real JS single-page apps.
#
#   recipes/<host>.sh        optional per-host hook for sites whose data URLs are
#                            computed in JS and can't be found generically. If it
#                            defines recipe_expand(), its echoed URLs are fetched.
#                            A ready-made mathnet.mit.edu recipe ships alongside.
#
# Re-run any time: already-downloaded files are skipped; only new/changed content
# is fetched. State lives in <save_dir>/.getweb/.
#
# Usage:   getweb.sh [options] URL
# Options:
#   -d DIR         save directory            (default: $HOME/Downloads/sync_web)
#   --data         enable Phase 2 discovery  (DEFAULT ON)
#   --no-data      disable Phase 2; plain static mirror only (classic behavior)
#   --render[=N]   enable Phase 3 headless-Chrome rendering of up to N pages
#                  (default 40); implies --data; needs Google Chrome / Chromium
#   --jobs N       parallel download concurrency for phases 2/3   (default 12)
#   --convert      also run wget link conversion (-k) for file:// browsing
#                  (trade-off: makes re-runs re-download converted pages)
#   --refresh      re-check already-downloaded data files instead of skipping
#   --all-hosts    allow fetching discovered resources from other hosts too
#   --max N        safety cap on discovered files to fetch        (default 100000)
#   -h, --help     show this help

set -uo pipefail

# ----------------------------------------------------------------------------- config / args
SAVE_DIR="$HOME/Downloads/sync_web"
AGENT="Mozilla/5.0 (compatible; getweb/0.4)"
DATA=1; RENDER=0; RENDER_N=40; JOBS=12; CONVERT=0; REFRESH=0; ALL_HOSTS=0; MAXFETCH=100000
URL=""

# Print the leading comment block (lines 2.. up to the first non-comment line).
print_help() { awk 'NR==1{next} /^#/{sub(/^# ?/,""); print; next} {exit}' "$0"; }

args=()
while [ $# -gt 0 ]; do
  case "$1" in
    -d) SAVE_DIR="$2"; shift 2;;
    -d*) SAVE_DIR="${1#-d}"; shift;;
    --data) DATA=1; shift;;
    --no-data) DATA=0; shift;;
    --render) RENDER=1; DATA=1; shift;;
    --render=*) RENDER=1; DATA=1; RENDER_N="${1#--render=}"; shift;;
    --jobs) JOBS="$2"; shift 2;;
    --jobs=*) JOBS="${1#--jobs=}"; shift;;
    --convert) CONVERT=1; shift;;
    --refresh) REFRESH=1; shift;;
    --all-hosts) ALL_HOSTS=1; shift;;
    --max) MAXFETCH="$2"; shift 2;;
    --max=*) MAXFETCH="${1#--max=}"; shift;;
    -h|--help) print_help; exit 0;;
    -*) echo "Unknown option: $1" >&2; exit 2;;
    *) args+=("$1"); shift;;
  esac
done
[ "${#args[@]}" -gt 0 ] && URL="${args[0]}"
[ -z "$URL" ] && { echo "URL is not given. Try: getweb.sh --help" >&2; exit 1; }

command -v wget >/dev/null 2>&1 || { echo "wget is not installed." >&2; exit 1; }
command -v curl >/dev/null 2>&1 || { echo "curl is not installed." >&2; exit 1; }
command -v python3 >/dev/null 2>&1 || { echo "python3 is not installed." >&2; exit 1; }

mkdir -p "$SAVE_DIR" || { echo "[Error] cannot create $SAVE_DIR" >&2; exit 1; }
[ -w "$SAVE_DIR" ] || { echo "[Error] $SAVE_DIR is not writable" >&2; exit 1; }

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
STATE="$SAVE_DIR/.getweb"; mkdir -p "$STATE/rendered"
SEEN="$STATE/seen.txt"; : >>"$SEEN"

# Host / scheme of the entry URL.
read -r SCHEME HOST < <(python3 - "$URL" <<'PY'
import sys
from urllib.parse import urlsplit
u = urlsplit(sys.argv[1])
print(u.scheme or "https", u.netloc)
PY
)
ORIGIN="$SCHEME://$HOST"
echo "=== getweb 0.4  |  $URL"
echo "    save_dir=$SAVE_DIR  host=$HOST  data=$DATA render=$RENDER jobs=$JOBS"

# ----------------------------------------------------------------------------- helpers (python)
# Extract same-host (unless --all-hosts) absolute URLs referenced by a set of
# local files. Reads file paths from stdin, prints unique absolute URLs.
extract_urls() {  # args: <allowed_host> <origin> <all_hosts 0/1>
  python3 - "$1" "$2" "$3" <<'PY'
import sys, re
from urllib.parse import urljoin, urlsplit
host, origin, allhosts = sys.argv[1], sys.argv[2], sys.argv[3] == "1"
TEXT = (".html",".htm",".js",".mjs",".json",".css",".xml",".txt",".svg",".map",".webmanifest")
ASSET = re.compile(r'\.(json|js|mjs|css|png|jpe?g|gif|svg|webp|avif|ico|woff2?|ttf|otf|'
                   r'eot|gz|br|zip|xml|txt|md|pdf|mp4|webm|mp3|wav|wasm|csv|tsv)(\?|#|$)', re.I)
ABS = re.compile(r'(?:https?:)?//[^\s"\'`<>(){}\[\]]+')
REL = re.compile(r'''["'(]\s*(/[^\s"'`<>(){}]+)''')
out = []
seen = set()
def emit(u):
    if not u: return
    u = u.split('#')[0]
    if u.startswith('//'): u = 'https:' + u
    try: sp = urlsplit(u)
    except Exception: return
    if sp.scheme not in ('http','https'): return
    if '..' in sp.path: return
    if not allhosts and sp.netloc != host: return
    if u not in seen:
        seen.add(u); out.append(u)
for line in sys.stdin:
    fp = line.strip()
    if not fp: continue
    low = fp.lower()
    try:
        with open(fp, 'r', errors='ignore') as f: text = f.read()
    except Exception:
        continue
    is_text = low.endswith(TEXT)
    if low.endswith(".xml"):                       # sitemap-style <loc> entries
        for m in re.findall(r'<loc>\s*([^<\s]+)\s*</loc>', text):
            emit(m)
    for m in ABS.findall(text):
        if ASSET.search(m) or low.endswith((".html",".htm")):
            emit(m)
    if is_text:
        for rel in REL.findall(text):
            seg = rel.split('?')[0].rsplit('/',1)[-1]
            if ASSET.search(rel) or ('.' in seg):  # looks like a file, not a route
                emit(urljoin(origin + '/', rel.lstrip('/')))
print("\n".join(out))
PY
}

# Map a URL to a local file path under SAVE_DIR (query stripped: a local static
# server ignores ?v=... cache-busters and serves the bare file). Stdin: URLs.
# Stdout: "url<space>localpath" for files that should be fetched now.
plan_fetch() {  # args: <save_dir> <seen_file> <refresh 0/1>
  python3 - "$1" "$2" "$3" <<'PY'
import sys, os
from urllib.parse import urlsplit
save, seenfile, refresh = sys.argv[1], sys.argv[2], sys.argv[3] == "1"
seen = set()
if os.path.exists(seenfile):
    seen = set(l.strip() for l in open(seenfile) if l.strip())
done = set()
for line in sys.stdin:
    u = line.strip()
    if not u or u in done: continue
    done.add(u)
    if not refresh and u in seen: continue
    sp = urlsplit(u)
    p = sp.path
    if p.endswith('/') or p == '': p += 'index.html'
    if '..' in p: continue
    local = os.path.join(save, p.lstrip('/'))
    if (not refresh) and os.path.exists(local) and os.path.getsize(local) > 0:
        continue
    print(u + " " + local)
PY
}

# Download a "url localpath" list (stdin) in parallel; record attempts in SEEN.
fetch_list() {  # reads TSV-ish lines on stdin
  local tmp; tmp="$(mktemp)"
  cat > "$tmp"
  local n; n=$(wc -l < "$tmp" | tr -d ' ')
  [ "$n" -eq 0 ] && { rm -f "$tmp"; return 1; }
  if [ "$n" -gt "$MAXFETCH" ]; then
    echo "    capping $n -> $MAXFETCH (raise with --max)"; head -n "$MAXFETCH" "$tmp" > "$tmp.cap"; mv "$tmp.cap" "$tmp"
    n="$MAXFETCH"
  fi
  echo "    fetching $n file(s) ..."
  AGENT="$AGENT" xargs -P "$JOBS" -n2 sh -c '
    url=$1; out=$2
    [ -s "$out" ] && exit 0
    mkdir -p "$(dirname "$out")"
    curl -fsSL --compressed --retry 3 --max-time 90 -A "$AGENT" -o "$out" "$url" \
      || { echo "    MISS $url" >&2; rm -f "$out"; }
  ' sh < "$tmp"
  awk "{print \$1}" "$tmp" >> "$SEEN"            # remember attempts (success or 404)
  awk "{print \$2}" "$tmp"                       # echo local paths fetched this round
  rm -f "$tmp"
  return 0
}

# Given a urls file, plan -> fetch -> return text files for the next round.
fetch_round() {  # args: <urls_file> <out_textfiles>
  local urls="$1" outtext="$2"
  plan_fetch "$SAVE_DIR" "$SEEN" "$REFRESH" < "$urls" > "$STATE/plan.txt"
  : > "$outtext"
  [ -s "$STATE/plan.txt" ] || return 1
  fetch_list < "$STATE/plan.txt" \
    | grep -Ei '\.(html?|js|mjs|json|css|xml|txt|svg|map|webmanifest)$' >> "$outtext" || true
  return 0
}

# ----------------------------------------------------------------------------- Phase 1: static mirror
echo "=== [1] static mirror (incremental)"
WOPT=(-e robots=off -x -nH -p -np -nv -t 3 -E -m --compression=auto -U "$AGENT" -P "$SAVE_DIR")
# -m implies -N (timestamping) -r -l inf: re-runs skip unchanged files.
# (We intentionally drop the old -c, which only resumes partial files.)
[ "$CONVERT" -eq 1 ] && WOPT+=(-k -K)
wget "${WOPT[@]}" "$URL" || echo "    (wget exited non-zero; continuing)"

# ----------------------------------------------------------------------------- Phase 3a: render
# (run before generic discovery so netlog/DOM-discovered URLs feed Phase 2)
find_chrome() {
  local c
  for c in "$CHROME" google-chrome google-chrome-stable chromium chromium-browser brave-browser \
           "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
           "/Applications/Chromium.app/Contents/MacOS/Chromium" \
           "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser" \
           "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge"; do
    [ -n "${c:-}" ] || continue
    if command -v "$c" >/dev/null 2>&1; then command -v "$c"; return 0; fi
    [ -x "$c" ] && { echo "$c"; return 0; }
  done
  return 1
}
run_timeout() {  # <secs> <cmd...>
  local t="$1"; shift
  if command -v timeout >/dev/null 2>&1; then timeout "$t" "$@"; return $?; fi
  if command -v gtimeout >/dev/null 2>&1; then gtimeout "$t" "$@"; return $?; fi
  "$@" & local pid=$!
  ( sleep "$t"; kill -9 "$pid" 2>/dev/null ) & local w=$!
  wait "$pid" 2>/dev/null; local rc=$?; kill -9 "$w" 2>/dev/null; return $rc
}

CHROME="${CHROME:-}"
if [ "$RENDER" -eq 1 ]; then
  echo "=== [3] headless-Chrome render"
  if CHROME_BIN="$(find_chrome)"; then
    echo "    using $CHROME_BIN"
    : > "$STATE/render_urls.txt"
    # Pages to render: the entry URL + a sample of mirrored .html pages.
    { echo "$URL"
      find "$SAVE_DIR" -type f \( -name '*.html' -o -name '*.htm' \) 2>/dev/null \
        | head -n "$RENDER_N" \
        | python3 - "$SAVE_DIR" "$ORIGIN" <<'PY'
import sys, os
save, origin = sys.argv[1], sys.argv[2]
for line in sys.stdin:
    fp = line.strip()
    rel = os.path.relpath(fp, save)
    print(origin + "/" + rel.replace(os.sep, "/"))
PY
    } | awk '!seen[$0]++' | head -n "$RENDER_N" > "$STATE/render_pages.txt"

    i=0
    while IFS= read -r page; do
      [ -z "$page" ] && continue
      i=$((i+1))
      prof="$(mktemp -d)"; net="$STATE/net.$i.json"; dom="$STATE/rendered/$i.html"
      run_timeout 45 "$CHROME_BIN" --headless=new --disable-gpu --no-sandbox \
        --no-first-run --hide-scrollbars --user-data-dir="$prof" \
        --virtual-time-budget=10000 --run-all-compositor-stages-before-draw \
        --log-net-log="$net" --net-log-capture-mode=Everything \
        --dump-dom "$page" > "$dom" 2>/dev/null \
        || echo "    render timeout/err: $page"
      rm -rf "$prof"
      # URLs Chrome actually requested (from netlog) + links in rendered DOM.
      [ -s "$net" ] && grep -oE 'https?://[^"]+' "$net" 2>/dev/null >> "$STATE/render_urls.txt" || true
      [ -s "$dom" ] && echo "$dom"
      rm -f "$net"
    done < "$STATE/render_pages.txt" | extract_urls "$HOST" "$ORIGIN" "$ALL_HOSTS" >> "$STATE/render_urls.txt" || true

    sort -u "$STATE/render_urls.txt" \
      | { [ "$ALL_HOSTS" -eq 1 ] && cat || grep -E "^https?://$HOST/" || true; } \
      > "$STATE/render_urls.f"; mv "$STATE/render_urls.f" "$STATE/render_urls.txt"
    echo "    discovered $(wc -l < "$STATE/render_urls.txt" | tr -d ' ') URL(s) via render"
    fetch_round "$STATE/render_urls.txt" "$STATE/round_text.txt" || true
  else
    echo "    Chrome not found - skipping render. Install with:"
    echo "        brew install --cask google-chrome"
    echo "    (continuing with --data discovery only)"
  fi
fi

# ----------------------------------------------------------------------------- Phase 2: data discovery
if [ "$DATA" -eq 1 ]; then
  echo "=== [2] data-layer discovery (sitemap / manifest / JSON / URL strings)"

  # Recipe hook: site-specific URL expansion (e.g. MathNet manifest -> all problems).
  RECIPE="$SCRIPT_DIR/recipes/$HOST.sh"
  if [ -f "$RECIPE" ]; then
    echo "    recipe: $RECIPE"
    # shellcheck disable=SC1090
    SAVE_DIR="$SAVE_DIR" ORIGIN="$ORIGIN" HOST="$HOST" . "$RECIPE"
    if command -v recipe_expand >/dev/null 2>&1; then
      recipe_expand > "$STATE/recipe_urls.txt" 2>/dev/null || true
      echo "    recipe yielded $(wc -l < "$STATE/recipe_urls.txt" | tr -d ' ') URL(s)"
      fetch_round "$STATE/recipe_urls.txt" "$STATE/round_text.txt" || true
    fi
  fi

  # Always-try well-known endpoints.
  { echo "$ORIGIN/sitemap.xml"; echo "$ORIGIN/sitemap_index.xml"
    echo "$ORIGIN/robots.txt"; echo "$ORIGIN/manifest.json"; } > "$STATE/wellknown.txt"
  fetch_round "$STATE/wellknown.txt" "$STATE/round_text.txt" || true

  # Recursive discovery from everything mirrored so far.
  round=0
  find "$SAVE_DIR" -type f \( -name '*.html' -o -name '*.htm' -o -name '*.js' -o -name '*.mjs' \
       -o -name '*.json' -o -name '*.css' -o -name '*.xml' -o -name '*.svg' \) \
       ! -path "$STATE/*" 2>/dev/null > "$STATE/scan.txt"
  while [ "$round" -lt 6 ]; do
    round=$((round+1))
    extract_urls "$HOST" "$ORIGIN" "$ALL_HOSTS" < "$STATE/scan.txt" > "$STATE/disc.txt" || true
    sort -u "$STATE/disc.txt" -o "$STATE/disc.txt"
    if ! fetch_round "$STATE/disc.txt" "$STATE/round_text.txt"; then
      echo "    round $round: nothing new"; break
    fi
    new=$(wc -l < "$STATE/round_text.txt" | tr -d ' ')
    echo "    round $round: +$new text file(s) to re-scan"
    [ "$new" -eq 0 ] && break
    cp "$STATE/round_text.txt" "$STATE/scan.txt"
  done
fi

# ----------------------------------------------------------------------------- summary
echo "=== done -> $SAVE_DIR"
TOTAL=$(find "$SAVE_DIR" -type f ! -path "$STATE/*" 2>/dev/null | wc -l | tr -d ' ')
SIZE=$(du -sh "$SAVE_DIR" 2>/dev/null | cut -f1)
echo "    $TOTAL files, $SIZE total"
echo "    browse offline:  cd \"$SAVE_DIR\" && python3 -m http.server 8000"
