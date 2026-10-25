"""OURS. Seeded generator for the simulated parts of the data pack.

Writes stores (placeholder until build_stores.py lands real CA locations), skus + labels
(placeholder until build_skus.py lands USDA FDC), and the fully simulated facings, associates,
trucks, dc_stock, substitutes and notes. Deterministic: seed 418.

Usage: python data/build_sim.py [--stores N]
"""
import csv, json, pathlib, random, sys
from datetime import datetime, timedelta, timezone

D = pathlib.Path(__file__).parent
R = random.Random(418)
PST = timezone(timedelta(hours=-8))
N_STORES = int(sys.argv[sys.argv.index("--stores") + 1]) if "--stores" in sys.argv else 20


def wj(name, rows):
    with open(D / name, "w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")


# ---------- stores (placeholder unless data/stores.jsonl already came from build_stores.py) ----------
CITIES = [("Sacramento", 38.58, -121.49), ("Fresno", 36.74, -119.79), ("Los Angeles", 34.05, -118.24),
          ("San Diego", 32.72, -117.16), ("San Jose", 37.34, -121.89), ("Bakersfield", 35.37, -119.02),
          ("Riverside", 33.95, -117.40), ("Stockton", 37.96, -121.29), ("Redding", 40.59, -122.39),
          ("Chico", 39.73, -121.84), ("Modesto", 37.64, -120.99), ("Anaheim", 33.84, -117.91),
          ("Oxnard", 34.20, -119.18), ("Santa Rosa", 38.44, -122.71), ("Visalia", 36.33, -119.29),
          ("Palmdale", 34.58, -118.12), ("Chula Vista", 32.64, -117.08), ("Eureka", 40.80, -124.16),
          ("Merced", 37.30, -120.48), ("Ontario", 34.06, -117.65)]
FORMATS = ["SUPERCENTER"] * 8 + ["NEIGHBORHOOD"] * 5 + ["DISCOUNT"] * 4 + ["SAMS"] * 3


def dc_for(lat):
    return "DC_NORTH" if lat >= 37.5 else ("DC_CENTRAL" if lat >= 35.0 else "DC_SOUTH")


stores_path = D / "stores.jsonl"
if stores_path.exists() and "--force-stores" not in sys.argv and json.loads(stores_path.read_text().splitlines()[0]).get("_real"):
    stores = [json.loads(l) for l in stores_path.read_text().splitlines()]
else:
    stores = []
    for i in range(N_STORES):
        city, lat, lon = CITIES[i % len(CITIES)]
        stores.append({"store_id": f"CA{1000 + i}", "format": FORMATS[i % len(FORMATS)], "state": "CA",
                       "city": city, "lat": round(lat + R.uniform(-.05, .05), 4),
                       "lon": round(lon + R.uniform(-.05, .05), 4), "district": f"D{i // 25 + 1:02d}",
                       "dc_id": dc_for(lat), "tz": "America/Los_Angeles"})
    wj("stores.jsonl", stores)

# ---------- skus + labels (placeholder unless build_skus.py wrote real ones) ----------
skus_path = D / "skus.jsonl"
BASE = "sugar, corn syrup, water, citric acid, natural flavor"
POS = [("FD&C Red No. 3", "candy"), ("Red 3", "frosting"), ("erythrosine", "maraschino cherries"),
       ("Red Dye 3", "sprinkles"), ("E127", "gummies"), ("Red No. 3", "fruit cocktail"),
       ("FD&C RED #3", "candy"), ("RED3", "sprinkles"), ("eritrosina", "candy"), ("erythros1ne", "gummies"),
       ("F D & C Red No. 3", "frosting"), ("FD&C Red No.3 (erythrosine)", "maraschino cherries")]
DECOYS = [("Red 40", "candy"), ("D&C Red No. 33", "candy"), ("FD&C Red No. 40 Lake", "gummies"),
          ("3 red apples", "snacks"), ("Red 3 Ranch seasoning blend (paprika)", "snacks")]
HOLD = [("artificial color", "candy"), ("color added", "frosting"), ("artificial colors", "sprinkles"),
        ("#####illegible####", "gummies")]
if skus_path.exists() and "--force-skus" not in sys.argv and json.loads(skus_path.read_text().splitlines()[0]).get("_real") is not None:
    skus = [json.loads(l) for l in skus_path.read_text().splitlines()]
else:
    skus, labels = [], []

    def gtin(n):
        body = f"{n:013d}"
        s = sum(int(c) * (3 if i % 2 == 0 else 1) for i, c in enumerate(reversed(body)))
        return body + str((10 - s % 10) % 10)

    def add(name, cat, ingr, truth, food=True, drug=False):
        i = len(skus)
        skus.append({"sku_id": f"SKU{i:05d}", "gtin": gtin(7800000000 + i), "name": name,
                     "brand": R.choice(["Sweetly", "Great Value", "Kandy Co", "Member's Mark", "Brite"]),
                     "category": cat, "ingredients": ingr, "is_food": food, "is_ingested_drug": drug,
                     "case_units": R.choice([6, 12, 24]), "case_cube_ft3": round(R.uniform(.5, 2.0), 2),
                     "case_weight_lb": round(R.uniform(4, 22), 1)})
        labels.append((skus[-1]["sku_id"], truth))

    for k in range(3):
        for alias, cat in POS:
            add(f"{cat.title()} {alias.split()[0]} #{k}", cat, f"{BASE}, {alias}, red 40", "PULL")
        for alias, cat in DECOYS:
            add(f"{cat.title()} decoy #{k}", cat, f"{BASE}, {alias}", "KEEP")
        for alias, cat in HOLD:
            add(f"{cat.title()} unclear #{k}", cat, f"{BASE}, {alias}", "HOLD_VERIFY")
    add("Cherry Lip Tint", "cosmetic", "castor oil, red 3", "KEEP", food=False)
    add("Cherry Cough Syrup", "cough syrup", f"{BASE}, dextromethorphan, FD&C Red No. 3", "KEEP", food=False, drug=True)
    add("Bundle: Holiday Cookie Kit (includes Red 3 sprinkles)", "baking", "kit: sugar cookies; sprinkles (sugar, red 3)", "PULL")
    for k in range(120):
        cat = R.choice(["snacks", "cereal", "beverages", "baking", "candy", "frozen"])
        add(f"{cat.title()} control #{k}", cat, f"{BASE}, salt", "KEEP")
    wj("skus.jsonl", skus)
    with open(D / "labels.csv", "w", newline="") as f:
        w = csv.writer(f); w.writerow(["sku_id", "truth"]); w.writerows(labels)

# ---------- facings (simulated) ----------
CARRY = {"SUPERCENTER": 1.0, "NEIGHBORHOOD": .6, "DISCOUNT": .5, "SAMS": .35}
facings = []
for st in stores:
    slot = 0
    for sk in skus:
        if R.random() > CARRY[st["format"]]:
            continue
        aisle = 1 + slot // 150
        facings.append({"store_id": st["store_id"], "sku_id": sk["sku_id"],
                        "loc": {"aisle": f"A{aisle:02d}", "bay": 1 + (slot // 30) % 5, "shelf": 1 + (slot // 6) % 5,
                                "pos": 1 + slot % 6}, "units": R.randint(4, 36)})
        slot += 1
wj("facings.jsonl", facings)

# ---------- associates (simulated): overnight Dec 30 22:00 -> Dec 31 06:00 local ----------
S0, S1 = datetime(2026, 12, 30, 22, tzinfo=PST), datetime(2026, 12, 31, 6, tzinfo=PST)
N_ASSOC = {"SUPERCENTER": 14, "NEIGHBORHOOD": 8, "DISCOUNT": 6, "SAMS": 10}
associates = []
for st in stores:
    for k in range(N_ASSOC[st["format"]]):
        associates.append({"associate_id": f"{st['store_id']}-A{k:02d}", "store_id": st["store_id"],
                           "district": st["district"], "is_floater": False,
                           "shift_start": S0.isoformat(), "shift_end": S1.isoformat()})
for dist in sorted({s["district"] for s in stores}):
    for k in range(3):
        associates.append({"associate_id": f"{dist}-F{k}", "store_id": None, "district": dist,
                           "is_floater": True, "shift_start": S0.isoformat(), "shift_end": S1.isoformat()})
wj("associates.jsonl", associates)

# ---------- trucks (simulated) ----------
DCS = sorted({s["dc_id"] for s in stores})
dep = datetime(2026, 12, 31, 8, tzinfo=PST).isoformat()
wj("trucks.jsonl", [{"truck_id": f"{dc}-T{k}", "dc_id": dc, "cube_ft3": 3400.0, "weight_lb": 40000.0, "depart": dep}
                    for dc in DCS for k in range(6)])

# ---------- substitutes + dc_stock (simulated, ~70% of demand) ----------
labels_map = dict(csv.reader(open(D / "labels.csv")))
affected = [s for s in skus if labels_map.get(s["sku_id"]) == "PULL"]
by_cat = {}
for s in skus:
    if labels_map.get(s["sku_id"]) == "KEEP" and s["is_food"]:
        by_cat.setdefault(s["category"], []).append(s["sku_id"])
fallback = by_cat.get("candy") or next(iter(by_cat.values()))
substitutes = {}
for s in affected:
    pool = by_cat.get(s["category"]) or fallback
    substitutes[s["sku_id"]] = sorted(R.sample(pool, min(len(pool), R.choice([1, 2]))))
(D / "substitutes.json").write_text(json.dumps(substitutes, indent=1) + "\n")
demand = {}
store_dc = {s["store_id"]: s["dc_id"] for s in stores}
aff_ids = {s["sku_id"] for s in affected}
for f in facings:
    if f["sku_id"] in aff_ids:
        for sub in substitutes[f["sku_id"]][:1]:
            k = (store_dc[f["store_id"]], sub)
            demand[k] = demand.get(k, 0) + 1
wj("dc_stock.jsonl", [{"dc_id": dc, "sku_id": sub, "cases": max(1, int(n * .7))}
                      for (dc, sub), n in sorted(demand.items())])

# ---------- notes (ours, written; templated per store) ----------
NOTE_T = [("Endcap {n} holds a vendor Halloween display; candy there is not on the planogram.", "ENDCAP_DISPLAY"),
          ("Frito-Lay DSD rep restocks Tuesdays; DSD items are vendor-pulled, do not pack for DC return.", "DSD_VENDOR_PULL"),
          ("Topstock above aisle {a} has overflow cases of baking decorations.", "TOPSTOCK"),
          ("Online pickup totes staged in backroom bay {n} may contain affected items.", "PICKUP_TOTES"),
          ("Aisle {a} moved to garden center during remodel; locations are not on planogram.", "NOT_ON_PLANOGRAM"),
          ("Store-brand frosting labels are smudged from a printer fault; check ingredients by hand.", "UNCLEAR_LABEL")]
notes = []
for i, st in enumerate(stores):
    for k in range(3):
        t, _ = NOTE_T[(i + k) % len(NOTE_T)]
        notes.append({"note_id": f"N{len(notes):04d}", "store_id": st["store_id"],
                      "text": t.format(n=R.randint(1, 20), a=R.randint(1, 12))})
wj("notes.jsonl", notes)
print(f"stores={len(stores)} skus={len(skus)} facings={len(facings)} associates={len(associates)} "
      f"subs={len(substitutes)} dc_stock_rows={len(demand)} notes={len(notes)}")
