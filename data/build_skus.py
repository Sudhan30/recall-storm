"""OURS. Builds data/skus.jsonl, data/labels.csv, data/labels_detail.csv and data/variants.jsonl.

Sources
-------
* Real SKUs: USDA FoodData Central, Branded Foods (public domain, CC0 1.0), via
  https://api.nal.usda.gov/fdc/v1/foods/search?dataType=Branded&pageSize=200&query=...
  Fetched and cached by data/fdc_fetch.py into data/raw/fdc/ (gitignored). This script never
  touches the network; it reads the cache only, so the pack rebuilds identically.
  Real fields: fdcId, gtinUpc, description (name), brandName/brandOwner, foodCategory, ingredients.
* SIMULATED (seeded per SKU): case_units, case_cube_ft3, case_weight_lb.
* OURS, seeded (seed 418): data/variants.jsonl -- adversarial copies of real Red 3 SKUs (alias swaps,
  OCR noise, bundle kits, unbranded store-brand clones), decoys (Red 40, D&C Red 33, "3 red apples",
  sodium erythorbate, a cosmetic, an ingested drug), and unreadable / generic-colour HOLD cases.
  Variants carry synthetic GTINs with the GS1 restricted-circulation prefix 02 so they can never
  collide with a real product. Every variant row has "_real": false; real rows "_real": true.

Ground truth (labels.csv: sku_id,truth)
---------------------------------------
Real rows: deterministic regex scan for Red No. 3 aliases (RED3 below), then HAND overrides for
items a reader flagged as ambiguous. HOLD_VERIFY when the label only says "artificial color(s)" /
"color added" / "certified color" with no specific dye named, or when the label is self-contradictory.
Variant rows: truth is set by construction (we know what we inserted) and cross-checked.
Scope: CA_AB418_RED3 applies to food only, so a cosmetic or an ingested drug with Red 3 is KEEP.

Usage: python data/fdc_fetch.py && python data/build_skus.py
"""
import csv, json, pathlib, random, re, sys
from collections import Counter

D = pathlib.Path(__file__).parent
sys.path.insert(0, str(D))
import fdc_fetch  # noqa: E402

SEED = 418
TARGET_REAL = 1000          # real SKUs kept (all PULL + HOLD, KEEP sampled to fill)

# ---------- deterministic Red 3 scan ----------
RED3 = re.compile(
    r"erythrosin(?:e)?\b|eritrosina|\bE\s?-?\s?127\b|\bRED3\b"
    r"|\bRED\s*(?:DYE\s*)?(?:NO\.?|NUMBER|#)?\s*3\b(?!\s*(?:\d|\.\d))",
    re.I)
SPECIFIC_DYE = re.compile(r"\b(?:red|yellow|blue|green|orange|citrus red)\s*(?:dye\s*)?(?:no\.?|#)?\s*\d"
                          r"|tartrazine|allura|sunset yellow|brilliant blue|indigo|erythros", re.I)
SWAP = re.compile(r"(?:F\.?\s*D\.?\s*&\s*C\.?\s*)?(?:" + RED3.pattern + r")(?:\s*dye)?"
                  r"(?:\s*[(\[]\s*erythrosine?\s*[)\]])?", re.I)
GENERIC_COLOR = re.compile(r"artificial(?:ly)? colou?r(?:s|ed|ing)?|colou?rs? added|certified colou?rs?|fd&c colou?rs?", re.I)

# HAND checks (real fdcIds). Reviewed by reading the full ingredient text.
HAND = {
    1879399: ("HOLD_VERIFY", "lists ERYTHROSIN '(for USA and Chile: FD&C Red 40...)': US formulation unclear"),
    2626075: ("PULL", "'FD&C RED #3 OR ERYTHROSINE': either reading is Red No. 3"),
}


def scan(ingr: str):
    """Returns (truth, reason, match) for a real ingredient string."""
    m = RED3.search(ingr)
    # 'RED 40 DYE (ERYTHROSINE)' style: the label names two different dyes for one slot
    if m and re.search(r"red\s*#?\s*40[^,;]{0,10}[(\[]\s*erythros", ingr, re.I) and not re.search(
            r"\bRED\s*(?:DYE\s*)?(?:NO\.?|#)?\s*3\b(?!\s*\d)", ingr, re.I):
        return "HOLD_VERIFY", "self-contradictory: 'Red 40 (erythrosine)'", m.group(0)
    if m:
        return "PULL", "regex alias match", m.group(0)
    g = unattributed_generic(ingr)
    if g and not SPECIFIC_DYE.search(ingr):
        return "HOLD_VERIFY", "generic colour statement, no dye named", g
    return "KEEP", "no Red 3 alias", None


def unattributed_generic(ingr: str):
    """First generic colour statement that is not tied to a named colorant. Attributed forms are
    'ARTIFICIAL COLOR (CARAMEL)', 'TITANIUM DIOXIDE [AN ARTIFICIAL COLORING]',
    'ARTIFICIAL COLORED RED WITH CARMINE'."""
    for m in GENERIC_COLOR.finditer(ingr):
        after, before = ingr[m.end():m.end() + 25], ingr[max(0, m.start() - 5):m.start()]
        if re.match(r"\s*[(\[:]", after) or re.search(r"[(\[]\s*an?\s*$", before, re.I) \
                or re.match(r"\s*(?:ed\s*)?\w*\s*with\s+\w", after, re.I):
            continue
        return m.group(0)
    return None


def gtin14(s: str):
    s = re.sub(r"\D", "", s or "")
    return s.zfill(14) if 8 <= len(s) <= 14 else None


def synth_gtin(n: int):
    body = "02" + f"{n:011d}"  # GS1 restricted-circulation prefix: never a real retail GTIN
    tot = sum(int(c) * (3 if i % 2 == 0 else 1) for i, c in enumerate(reversed(body)))
    return body + str((10 - tot % 10) % 10)


def case_dims(key):
    r = random.Random(f"{SEED}-case-{key}")
    units = r.choice([6, 8, 12, 12, 24, 24, 36])
    return {"case_units": units, "case_cube_ft3": round(r.uniform(0.4, 2.2), 2),
            "case_weight_lb": round(r.uniform(3.0, 24.0), 1)}


def title(s):
    return re.sub(r"\s+", " ", s.strip()).title().replace("'S ", "'s ")


def load_real():
    seen = {}
    for q, page in fdc_fetch.cached_pages():
        for f in page["foods"]:
            if f["fdcId"] in seen or not (f.get("ingredients") or "").strip() or not gtin14(f.get("gtinUpc")):
                continue
            f["_query"] = q
            seen[f["fdcId"]] = f
    gt = {}
    rows = []
    for f in sorted(seen.values(), key=lambda f: f["fdcId"]):
        g = gtin14(f["gtinUpc"])
        if g in gt:  # same GTIN published twice (label revisions): keep the newest fdcId
            rows = [r for r in rows if r["sku_id"] != gt[g]]
        ingr = re.sub(r"\s+", " ", f["ingredients"]).strip()
        if f["fdcId"] in HAND:
            truth, reason = HAND[f["fdcId"]]
            reason, match = "HAND: " + reason, (RED3.search(ingr) or GENERIC_COLOR.search(ingr) or [None])[0]
        else:
            truth, reason, match = scan(ingr)
        row = {"sku_id": f"FDC{f['fdcId']}", "gtin": g, "name": title(f["description"]),
               "brand": title(f.get("brandName") or f.get("brandOwner") or "Unbranded"),
               "category": (f.get("foodCategory") or f["_query"]).lower(), "ingredients": ingr,
               "is_food": True, "is_ingested_drug": False, **case_dims(f["fdcId"]),
               "_real": True, "_src": f"fdc:{f['fdcId']}", "_query": f["_query"],
               "_truth": truth, "_reason": reason, "_match": match}
        gt[g] = row["sku_id"]
        rows.append(row)
    return rows


def sample_real(rows):
    r = random.Random(SEED)
    keep = [x for x in rows if x["_truth"] != "KEEP"]
    neg = [x for x in rows if x["_truth"] == "KEEP"]
    r.shuffle(neg)
    return sorted(keep + neg[:max(0, TARGET_REAL - len(keep))], key=lambda x: x["sku_id"])


# ---------- variants (ours, seeded) ----------
PULL_ALIASES = [("erythrosine", 20, "alias"), ("E127", 12, "alias"), ("E-127", 4, "alias"),
                ("eritrosina", 12, "alias_es"), ("FD&C Rojo No. 3", 5, "alias_es"),
                ("FD&C Red #3", 12, "alias"), ("RED3", 12, "alias_compact"), ("Red Dye 3", 10, "alias"),
                ("F.D.&C. Red No. 3", 8, "alias"), ("red no 3", 6, "alias_case"),
                ("erythros1ne", 10, "ocr_noise"), ("RED N0. 3", 8, "ocr_noise"), ("Erythr0sine", 5, "ocr_noise")]
KIT_NAMES = ["Holiday Cookie Decorating Kit", "Gingerbread House Kit", "Cupcake Party Bundle",
             "Valentine Treat Box", "Birthday Baking Bundle", "Sundae Topping Trio", "Easter Basket Candy Pack"]
COSMETICS = [("Cherry Lip Tint", "castor oil, beeswax, flavor, FD&C Red No. 3"),
             ("Strawberry Lip Balm", "petrolatum, lanolin, fragrance, erythrosine (CI 45430)"),
             ("Kids Play Nail Polish", "water, acrylates copolymer, Red 3"),
             ("Pink Bath Bomb", "sodium bicarbonate, citric acid, fragrance, FD&C Red #3"),
             ("Bubblegum Toothpaste (non-ingested, rinse)", "sorbitol, silica, glycerin, E127"),
             ("Rose Face Mask", "kaolin, glycerin, red no. 3")]
DRUGS = [("Children's Cherry Cough Syrup", "Active: dextromethorphan HBr 7.5 mg. Inactive: glycerin, sucrose, "
          "flavor, FD&C Red No. 3, sodium benzoate"),
         ("Cherry Cough Drops", "Active: menthol 5.8 mg. Inactive: sugar, glucose syrup, flavor, red 3"),
         ("Cherry Chewable Antacid", "Active: calcium carbonate 750 mg. Inactive: dextrose, flavor, erythrosine"),
         ("Cherry Allergy Liquid", "Active: diphenhydramine HCl 12.5 mg. Inactive: water, sugar, FD&C Red #3"),
         ("Pink Bismuth Chewables", "Active: bismuth subsalicylate 262 mg. Inactive: mannitol, E127")]
HOLD_SWAPS = [("artificial color", 5, "generic_color"), ("color added", 3, "generic_color"),
              ("certified color", 2, "generic_color"), ("FD&C R#####", 3, "illegible"),
              ("[illegible]", 3, "illegible"), ("ERYTH▒▒▒▒▒", 2, "illegible")]


def build_variants(real_pull, real_keep):
    r = random.Random(SEED + 1)
    bases = [x for x in real_pull if x["_reason"] == "regex alias match" and len(RED3.findall(x["ingredients"])) >= 1]
    out = []

    def add(base, *, name=None, brand=None, ingredients, truth, kind, category=None, food=True, drug=False):
        n = len(out) + 1
        out.append({"sku_id": f"VAR{n:04d}", "gtin": synth_gtin(n), "name": name or base["name"],
                    "brand": brand or (base["brand"] if base else "Unbranded"),
                    "category": category or (base["category"] if base else "other"),
                    "ingredients": ingredients, "is_food": food, "is_ingested_drug": drug,
                    **case_dims(f"VAR{n}"), "_real": False, "_kind": kind,
                    "_base": base["sku_id"] if base else None, "_truth": truth})

    def swap(ingr, repl):  # replaces each Red 3 mention, including a leading "FD&C"
        return SWAP.sub(lambda m: repl, ingr)

    def drop_dyes(ingr):  # generic HOLD cases: no specific dye may remain anywhere
        ingr = re.sub(r"(?:lake\s+)?(?:F\.?\s*D\.?\s*&\s*C\.?\s*)?(?:" + SPECIFIC_DYE.pattern +
                      r")\w*(?:\s*(?:aluminum\s*)?lake|\s*dye)?", "", ingr, flags=re.I)
        ingr = re.sub(r"\s*(?:,\s*)+", ", ", ingr)
        ingr = re.sub(r"\s*,\s*([.;])", r"\1", ingr)
        ingr = re.sub(r"([(\[:])\s*,\s*", r"\1", ingr)
        ingr = re.sub(r",\s*([)\]])", r"\1", ingr)
        return re.sub(r"(?:\b(\w[\w ]*?)\b, )\1\b", r"\1", ingr)

    # PULL: every Red 3 mention swapped to one alias spelling
    for alias, n, kind in PULL_ALIASES:
        for b in r.sample(bases, n):
            add(b, ingredients=swap(b["ingredients"], alias), truth="PULL", kind=f"{kind}:{alias}")
    # PULL: unbranded store-brand clones (generic name, no brand, original ingredients)
    for i, b in enumerate(r.sample(bases, 10)):
        add(b, name="Store Brand " + b["name"].split(",")[0], brand="Unbranded",
            ingredients=b["ingredients"], truth="PULL", kind="store_brand_clone")
    # PULL: bundle kits -- one Red 3 component inside an otherwise clean kit
    for i in range(14):
        a, k = r.choice(bases), r.choice(real_keep)
        parts = [f"{a['name']}: {a['ingredients']}", f"{k['name']}: {k['ingredients']}"]
        r.shuffle(parts)
        add(a, name=f"{KIT_NAMES[i % len(KIT_NAMES)]} #{i + 1}", category="seasonal kits",
            ingredients="KIT CONTAINS: " + " | ".join(parts), truth="PULL", kind="bundle_kit")
    # KEEP decoys: Red 40, D&C Red 33, near-miss numbers
    for repl, n, kind in [("Red 40", 10, "decoy_red40"), ("FD&C Red No. 40 Lake", 4, "decoy_red40"),
                          ("D&C Red No. 33", 6, "decoy_red33"), ("Red 33", 3, "decoy_red33"),
                          ("Red #30", 2, "decoy_red30")]:
        for b in r.sample(bases, n):
            add(b, ingredients=swap(b["ingredients"], repl), truth="KEEP", kind=kind)
    for k in r.sample(real_keep, 4):
        add(k, name=k["name"] + " (Apple Pack)",
            ingredients=k["ingredients"].rstrip(".") + ", dried apple (3 red apples per bag)",
            truth="KEEP", kind="decoy_3_red_apples")
    for k in r.sample(real_keep, 3):
        add(k, name=k["name"] + " With Red 3-Bean Medley",
            ingredients=k["ingredients"].rstrip(".") + ", red 3-bean medley (kidney, pinto, black beans)",
            truth="KEEP", kind="decoy_red_3_bean")
    for k in r.sample(real_keep, 3):
        add(k, ingredients=k["ingredients"].rstrip(".") + ", sodium erythorbate", truth="KEEP",
            kind="decoy_erythorbate")
    # KEEP: Red 3 outside the food rule's scope
    for name, ingr in COSMETICS:
        add(None, name=name, brand="Unbranded", category="cosmetics", ingredients=ingr, truth="KEEP",
            kind="decoy_cosmetic", food=False)
    for name, ingr in DRUGS:
        add(None, name=name, brand="Unbranded", category="otc medicine", ingredients=ingr, truth="KEEP",
            kind="decoy_ingested_drug", food=False, drug=True)
    # HOLD_VERIFY: Red 3 mention replaced by a generic or unreadable statement
    for repl, n, kind in HOLD_SWAPS:
        for b in r.sample(bases, n):
            ingr = swap(b["ingredients"], repl)
            if kind == "generic_color":
                ingr = drop_dyes(ingr)
            add(b, ingredients=ingr, truth="HOLD_VERIFY", kind=f"{kind}:{repl}")
    return out


REGEX_HARD = {"alias_es:FD&C Rojo No. 3", "decoy_red_3_bean"}


def check_variants(vs):
    """Cross-check constructed truth against the scan where the scan should agree. REGEX_HARD kinds are
    deliberately beyond the naive scan (a Spanish alias it lacks; a decoy it wrongly flags)."""
    bad = []
    for v in vs:
        t, _, _ = scan(v["ingredients"])
        k = v["_kind"]
        if k in REGEX_HARD:
            continue
        if k.startswith(("alias", "store_brand", "bundle")) and t != "PULL":
            bad.append(v)
        if k.startswith("decoy") and k not in ("decoy_cosmetic", "decoy_ingested_drug") and t == "PULL":
            bad.append(v)
    if bad:
        for v in bad:
            print("VARIANT CHECK FAILED", v["sku_id"], v["_kind"], v["ingredients"][:160], file=sys.stderr)
        sys.exit(1)


def main():
    real = sample_real(load_real())
    pull = [x for x in real if x["_truth"] == "PULL"]
    keep = [x for x in real if x["_truth"] == "KEEP"]
    variants = build_variants(pull, keep)
    check_variants(variants)
    fields = ["sku_id", "gtin", "name", "brand", "category", "ingredients", "is_food", "is_ingested_drug",
              "case_units", "case_cube_ft3", "case_weight_lb"]

    def strip(x):  # contract fields first, then provenance extras (contract_io drops "_" keys)
        return {**{k: x[k] for k in fields}, "_real": x["_real"],
                **({"_src": x["_src"]} if x["_real"] else {"_kind": x["_kind"], "_base": x["_base"]})}

    allrows = real + variants
    with open(D / "variants.jsonl", "w") as f:
        for v in variants:
            f.write(json.dumps(strip(v)) + "\n")
    with open(D / "skus.jsonl", "w") as f:
        for x in allrows:
            f.write(json.dumps(strip(x)) + "\n")
    with open(D / "labels.csv", "w", newline="") as f:
        w = csv.writer(f); w.writerow(["sku_id", "truth"])
        w.writerows((x["sku_id"], x["_truth"]) for x in allrows)
    with open(D / "labels_detail.csv", "w", newline="") as f:
        w = csv.writer(f); w.writerow(["sku_id", "truth", "real", "how", "match"])
        for x in allrows:
            w.writerow((x["sku_id"], x["_truth"], x["_real"], x.get("_reason") or x["_kind"], x.get("_match") or ""))
    c_real = Counter(x["_truth"] for x in real)
    c_var = Counter(x["_truth"] for x in variants)
    print(f"real={len(real)} {dict(c_real)}  variants={len(variants)} {dict(c_var)}  total={len(allrows)}")
    print("variant kinds:", dict(Counter(v["_kind"].split(":")[0] for v in variants)))


if __name__ == "__main__":
    main()
