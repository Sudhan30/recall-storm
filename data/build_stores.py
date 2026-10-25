"""OURS. Real California Walmart / Sam's Club locations -> data/stores_all.jsonl + data/stores.jsonl.

Sources
-------
* Store locations: OpenStreetMap, via the Overpass API, every node/way/relation tagged
  brand:wikidata=Q483551 (Walmart) or Q1972120 (Sam's Club) in a California bounding box.
  (c) OpenStreetMap contributors, Open Database License (ODbL) 1.0, https://www.openstreetmap.org/copyright
  The BUILD.md source (Kaggle "US Walmart Store Locations", jackogozaly, CC0) was not used: no Kaggle
  credentials on the build machine. OSM is the open substitute.
* City fallback: US Census Bureau 2024 Gazetteer, California places (public domain).
  Used only when an OSM store has neither a walmart.com store URL nor addr:city.
  Coordinates come straight from OSM (node position or way/relation centre), so no zip geocoding is needed.

What is real vs simulated
-------------------------
Real: store existence, store number (ref:walmart / walmart.com URL), city, lat/lon, format (from the
OSM name: "Supercenter", "Neighborhood Market", plain "Walmart" = DISCOUNT, Sam's Club = SAMS).
SIMULATED: dc_id (3 DCs split at latitude tertiles) and district (~25 stores, chunked by latitude
within each DC). Walmart's real DC network and district map are not public and are not used.

Outputs
-------
data/raw/osm_walmart_bbox.json   raw Overpass response (gitignored)
data/raw/stores_ca_osm.csv       flattened CA rows incl. address (gitignored)
data/stores_all.jsonl            every CA store, contract Store fields + "_real"/"_src" extras
data/stores.jsonl                20-store demo subset spanning all formats and all 3 DCs

Usage: python data/build_stores.py [--refresh]
"""
import csv, json, math, pathlib, re, sys, urllib.parse, urllib.request

D = pathlib.Path(__file__).parent
RAW = D / "raw"
OSM = RAW / "osm_walmart_bbox.json"
GAZ = RAW / "gaz_place_06_2024.txt"
GAZ_URL = "https://www2.census.gov/geo/docs/maps-data/data/gazetteer/2024_Gazetteer/2024_gaz_place_06.txt"
OVERPASS = ["https://overpass-api.de/api/interpreter", "https://overpass.kumi.systems/api/interpreter",
            "https://overpass.private.coffee/api/interpreter"]
QUERY = ('[out:json][timeout:90];(nwr["brand:wikidata"~"^(Q483551|Q1972120)$"](32.4,-124.5,42.1,-114.1););'
         'out center tags;')
UA = {"User-Agent": "recall-storm-hackathon/0.1 (data build)"}
STORE_SHOPS = {"supermarket", "department_store", "wholesale"}

# Coarse California outline (lon, lat), used only for OSM rows with no addr:state. Generous on the
# coast, tight (pulled ~2 km inside) on the NV/AZ/Mexico borders, where the bbox picks up
# out-of-state and Walmart de Mexico stores (e.g. Tecate, BC).
CA_POLY = [(-124.6, 42.0), (-120.0, 42.0), (-120.0, 39.0), (-114.63, 35.0), (-114.63, 34.87),
           (-114.13, 34.27), (-114.43, 34.08), (-114.53, 33.03), (-114.72, 32.74), (-117.13, 32.555),
           (-118.5, 32.4), (-124.6, 40.0)]


def fetch():
    RAW.mkdir(parents=True, exist_ok=True)
    if not OSM.exists() or "--refresh" in sys.argv:
        body = urllib.parse.urlencode({"data": QUERY}).encode()
        for url in OVERPASS:
            try:
                with urllib.request.urlopen(urllib.request.Request(url, body, UA), timeout=150) as r:
                    raw = r.read()
                json.loads(raw)["elements"]
                OSM.write_bytes(raw)
                break
            except Exception as e:  # busy mirror: try the next one
                print(f"overpass {url}: {e}", file=sys.stderr)
        else:
            sys.exit("all Overpass mirrors failed; retry later")
    if not GAZ.exists():
        with urllib.request.urlopen(urllib.request.Request(GAZ_URL, headers=UA), timeout=60) as r:
            GAZ.write_bytes(r.read())


def in_poly(lon, lat, poly=CA_POLY):
    inside, j = False, len(poly) - 1
    for i in range(len(poly)):
        xi, yi = poly[i]; xj, yj = poly[j]
        if (yi > lat) != (yj > lat) and lon < (xj - xi) * (lat - yi) / (yj - yi) + xi:
            inside = not inside
        j = i
    return inside


def km(a, b):
    la1, lo1, la2, lo2 = map(math.radians, (a[0], a[1], b[0], b[1]))
    h = math.sin((la2 - la1) / 2) ** 2 + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2
    return 12742 * math.asin(math.sqrt(h))


def places():
    out = []
    with open(GAZ, encoding="latin-1") as f:
        for r in csv.DictReader(f, delimiter="\t"):
            r = {k.strip(): v.strip() for k, v in r.items()}
            name = re.sub(r" (city|town|CDP)$", "", r["NAME"])
            out.append((name, float(r["INTPTLAT"]), float(r["INTPTLONG"])))
    return out


def fmt(tags):
    n = (tags.get("name") or "").lower()
    if tags.get("brand") == "Sam's Club" or "sam's" in n:
        return "SAMS"
    if "neighborhood" in n:
        return "NEIGHBORHOOD"
    if "supercenter" in n:
        return "SUPERCENTER"
    return "DISCOUNT"


def main():
    fetch()
    els = json.loads(OSM.read_text())["elements"]
    gaz = places()
    rows, seen = [], {}
    for e in els:
        t = e.get("tags", {})
        if t.get("shop") not in STORE_SHOPS:
            continue  # pharmacies, fuel, garden centres, auto care are parts of a store, not stores
        lat = e.get("lat", e.get("center", {}).get("lat"))
        lon = e.get("lon", e.get("center", {}).get("lon"))
        st = t.get("addr:state")
        if st not in (None, "CA") or (st is None and not in_poly(lon, lat)):
            continue
        web = t.get("website", "")
        m = re.search(r"/(?:store|club)/(\d+)-([a-z0-9-]+)-ca\b", web)
        ref = t.get("ref:walmart") or t.get("ref") or (m.group(1) if m else None)
        city = t.get("addr:city") or (m.group(2).replace("-", " ").title() if m else None)
        if not city:
            city = min(gaz, key=lambda p: km((lat, lon), (p[1], p[2])))[0]
        f = fmt(t)
        prefix = "SAMS" if f == "SAMS" else "WM"
        sid = f"{prefix}{ref}" if ref and ref.isdigit() else f"OSM{e['type'][0].upper()}{e['id']}"
        row = {"store_id": sid, "format": f, "state": "CA", "city": city, "lat": round(lat, 5),
               "lon": round(lon, 5), "_real": True, "_src": f"osm:{e['type']}/{e['id']}",
               "_name": t.get("name"), "_addr": " ".join(x for x in (t.get("addr:housenumber"),
                                                                       t.get("addr:street")) if x) or None}
        # de-duplicate: same store number, or the same format within 250 m (node + building outline)
        dup = seen.get(sid) or next((r for r in rows if r["format"] == f and
                                     km((r["lat"], r["lon"]), (lat, lon)) < 0.25), None)
        if dup:
            if dup["store_id"].startswith("OSM") and not sid.startswith("OSM"):
                dup.update({k: v for k, v in row.items() if k in ("store_id", "_src")})
                seen[sid] = dup
            continue
        seen[sid] = row
        rows.append(row)

    # SIMULATED: three DCs at latitude tertiles, districts of ~25 stores within each DC.
    lats = sorted(r["lat"] for r in rows)
    cut_s, cut_n = lats[len(lats) // 3], lats[2 * len(lats) // 3]
    for r in rows:
        r["dc_id"] = "DC_NORTH" if r["lat"] >= cut_n else ("DC_CENTRAL" if r["lat"] >= cut_s else "DC_SOUTH")
    dnum = 0
    for dc in ("DC_NORTH", "DC_CENTRAL", "DC_SOUTH"):
        grp = sorted((r for r in rows if r["dc_id"] == dc), key=lambda r: (-r["lat"], r["lon"], r["store_id"]))
        k = max(1, round(len(grp) / 25))
        size = math.ceil(len(grp) / k)
        for i, r in enumerate(grp):
            r["district"] = f"D{dnum + i // size + 1:02d}"
        dnum += k
    order = ["store_id", "format", "state", "city", "lat", "lon", "district", "dc_id", "tz"]
    out = []
    for r in sorted(rows, key=lambda r: r["store_id"]):
        r["tz"] = "America/Los_Angeles"
        out.append({**{k: r[k] for k in order}, **{k: v for k, v in r.items() if k.startswith("_")}})

    with open(RAW / "stores_ca_osm.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0])); w.writeheader(); w.writerows(out)
    wj("stores_all.jsonl", out)

    # Demo subset: 20 stores, all 4 formats, all 3 DCs, concentrated in one or two districts per DC so
    # floaters and substitute transfers have neighbours to work with.
    QUOTA = {"DC_NORTH": {"SUPERCENTER": 3, "NEIGHBORHOOD": 1, "DISCOUNT": 1, "SAMS": 2},
             "DC_CENTRAL": {"SUPERCENTER": 3, "NEIGHBORHOOD": 2, "DISCOUNT": 1, "SAMS": 1},
             "DC_SOUTH": {"SUPERCENTER": 3, "NEIGHBORHOOD": 1, "DISCOUNT": 1, "SAMS": 1}}
    demo = []
    for dc, quota in QUOTA.items():
        grp = [r for r in out if r["dc_id"] == dc]
        dists = sorted({r["district"] for r in grp},
                       key=lambda d: (-len({r["format"] for r in grp if r["district"] == d}), d))
        rank = {d: i for i, d in enumerate(dists)}
        for f, n in quota.items():
            cands = sorted((r for r in grp if r["format"] == f), key=lambda r: (rank[r["district"]], r["store_id"]))
            demo += cands[:n]
    demo.sort(key=lambda r: r["store_id"])
    wj("stores.jsonl", demo)
    from collections import Counter
    print(f"CA stores={len(out)} formats={dict(Counter(r['format'] for r in out))} "
          f"dcs={dict(Counter(r['dc_id'] for r in out))} districts={dnum} lat cuts={cut_s},{cut_n}")
    print(f"demo={len(demo)} formats={dict(Counter(r['format'] for r in demo))} "
          f"dcs={dict(Counter(r['dc_id'] for r in demo))} districts={sorted({r['district'] for r in demo})}")


def wj(name, rows):
    with open(D / name, "w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")


if __name__ == "__main__":
    main()
