"""OURS. Fetch + cache USDA FoodData Central Branded Foods search pages into data/raw/fdc/.

Source: USDA FoodData Central, Branded Foods (https://fdc.nal.usda.gov), public domain / CC0 1.0.
API: https://api.nal.usda.gov/fdc/v1/foods/search?dataType=Branded&pageSize=200&query=...
Key: $FDC_API_KEY if set, else DEMO_KEY (heavily rate limited). Responses are cached by query+page,
so re-runs make no network calls once data/raw/fdc/ is populated. data/raw/ is gitignored.

Usage: python data/fdc_fetch.py      (fetches whatever is not cached yet; stops cleanly on HTTP 429)
"""
import json, os, pathlib, re, sys, time, urllib.parse, urllib.request, urllib.error

D = pathlib.Path(__file__).parent
CACHE = D / "raw" / "fdc"
API = "https://api.nal.usda.gov/fdc/v1/foods/search"
# (query, pages). Order matters under DEMO_KEY limits: Red 3 sources first, controls last.
QUERIES = [("erythrosine", 1), ("red 3", 1), ("maraschino cherries", 1), ("sprinkles", 1),
           ("frosting", 1), ("candy", 1), ("gummies", 1), ("fruit cocktail", 1), ("cough syrup", 1),
           ("crackers", 1)]


def slug(q):
    return re.sub(r"[^a-z0-9]+", "_", q.lower()).strip("_")


def path(q, page):
    return CACHE / f"{slug(q)}_p{page}.json"


def fetch_all(verbose=True):
    CACHE.mkdir(parents=True, exist_ok=True)
    key = os.environ.get("FDC_API_KEY", "DEMO_KEY")
    missing = []
    for q, pages in QUERIES:
        for page in range(1, pages + 1):
            p = path(q, page)
            if p.exists():
                continue
            url = API + "?" + urllib.parse.urlencode({"api_key": key, "dataType": "Branded", "pageSize": 200,
                                                      "pageNumber": page, "query": q})
            try:
                with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "recall-storm/0.1"}),
                                            timeout=90) as r:
                    body = r.read()
                    left = r.headers.get("X-RateLimit-Remaining")
                json.loads(body)
                p.write_bytes(body)
                if verbose:
                    print(f"fetched {q!r} p{page} (ratelimit remaining {left})")
                time.sleep(1)
            except urllib.error.HTTPError as e:
                print(f"HTTP {e.code} on {q!r} p{page}; stopping (cached pages are still used)", file=sys.stderr)
                missing.append((q, page))
                if e.code == 429:
                    return missing + [(q2, pg) for q2, n in QUERIES for pg in range(1, n + 1)
                                      if not path(q2, pg).exists() and (q2, pg) not in missing]
    return missing


def cached_pages():
    for q, pages in QUERIES:
        for page in range(1, pages + 1):
            p = path(q, page)
            if p.exists():
                yield q, json.loads(p.read_text())


if __name__ == "__main__":
    m = fetch_all()
    print("missing:", m)
