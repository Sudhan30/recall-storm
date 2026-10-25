"""OURS. Builds the second drill scenario (fda_lots): real openFDA food recall notices, simulated shelf lots.

Writes data/recalls_fda.jsonl, data/skus_fda.jsonl, data/lots.jsonl, data/labels_fda.csv and
data/scenario_fda_lots.json. Does not touch any other data file.

Sources
-------
* REAL: openFDA Food Enforcement Reports, https://api.fda.gov/food/enforcement.json (no key; openFDA
  allows ~240 requests/min/IP without one). Query used (5 pages of 1,000, cached raw in
  data/raw/openfda/page_<skip>.json, gitignored):
      search=report_date:[20240101 TO 20261025]&sort=report_date:asc&limit=1000&skip=0..4000
  then filtered locally to status Ongoing or Completed. openFDA data is public domain (CC0, see
  https://open.fda.gov/license/); use is subject to https://open.fda.gov/terms/. openFDA's own
  disclaimer: "Do not rely on openFDA to make decisions regarding medical care ... you should assume
  all results are unvalidated." meta.last_updated of the fetch is recorded in scenario_fda_lots.json.
  Real fields kept verbatim: recall_number, event_id, status, recalling_firm, product_description,
  reason_for_recall, classification, report_date, distribution_pattern, code_info.
* OURS: the code_info parser below (lots, lot ranges, best-by/use-by/expiry dates and date windows,
  "all lots" scope) and parse_confidence.
* SIMULATED (seed 418): one SKU per recall in data/skus_fda.jsonl (synthetic GTINs with the GS1
  restricted-circulation prefix 02, so they never collide with a real product; name/brand/category
  from the recall text; real UPCs from the notice kept only as "_upc_real" provenance), which of the
  20 demo stores carry each SKU, where it sits, and which lots / best-by dates are on the shelf
  (data/lots.jsonl). Recalled lots are mixed with non-recalled lots of the same SKU, including
  near-miss lots (adjacent numbers just outside a range, best-by one day outside a window) and
  shelf lot strings rendered with different punctuation / case / a "LOT " prefix.
* The recall -> SKU cross-reference (recalls_fda.jsonl: sim_sku_id, sim_gtin) is SIMULATED: it stands in
  for the retailer's item master mapping vendor UPCs to its own items.

Distribution: all 20 demo stores are in CA. A recall's SKU is stocked only when its
distribution_pattern names CA / California or is nationwide / U.S.-wide; recalls distributed only
elsewhere get a catalog SKU but no shelf lots (a planner must create no tasks for them).

Ground truth (labels_fda.csv: store_id,sku_id,lot,best_by,truth,recall_number,basis)
----------------------------------------------------------------------------------
Derived deterministically from the parsed recall terms, per shelf lot:
  norm(lot) = uppercase, drop a leading "LOT"/"BATCH"/"#" word, drop every non-alphanumeric char.
  1. parse_confidence == "low" (ambiguous code_info: multi-product numbered lists, lot-format
     descriptions, purchase-date windows, lot-like tokens we could not attribute) -> HOLD_VERIFY
     for every lot of that SKU (basis "ambiguous").
  2. scope "all" (notice says all lots / all codes / all dates)            -> PULL  (basis "all_lots")
  3. the recall lists lots: PULL iff norm(lot) equals a listed lot (basis "lot_exact") or lies in a
     listed range (same length, string compare; basis "lot_range"); otherwise KEEP ("not_listed").
     When a notice lists lots, lots decide; dates on the notice are not used.
  4. otherwise the recall lists dates: PULL iff best_by is inside a date window (inclusive; single
     dates are one-day windows; "all dates through X" / "and all prior" are open-start windows;
     month-only dates cover the whole month) (basis "date_window"); otherwise KEEP.
A KEEP lot with a PULL task is a "non-recalled lot pulled" (must be 0 in tools/verify_lots.py).

Usage: python data/build_fda_lots.py [--fetch]   (--fetch refreshes the cache; default reads the cache)
"""
from __future__ import annotations

import calendar
import csv
import json
import pathlib
import random
import re
import sys
import urllib.request
from collections import Counter
from datetime import date, timedelta

D = pathlib.Path(__file__).parent
RAW = D / "raw" / "openfda"
SEED = 418
API = ("https://api.fda.gov/food/enforcement.json?search=report_date:[20240101+TO+20261025]"
       "&sort=report_date:asc&limit=1000&skip={skip}")
QUOTA = {"lot_list": 12, "lot_range": 5, "date_list": 7, "date_range": 7, "all": 3}  # CA-stocked, high/medium
N_NONCA = 6          # parsed fine but not distributed to CA: catalog only, no shelf stock
N_LOW = 6            # CA-stocked, ambiguous code_info -> HOLD_VERIFY
SCENARIO = {"scenario_id": "fda_lots", "state": "CA",
            "as_of": "2026-12-29T08:00:00-08:00", "deadline": "2026-12-31T08:00:00-08:00"}


# ---------------------------------------------------------------- fetch (cached)
def fetch(force: bool = False) -> tuple[list[dict], dict]:
    RAW.mkdir(parents=True, exist_ok=True)
    rows, meta = [], {}
    for skip in range(0, 5000, 1000):
        p = RAW / f"page_{skip}.json"
        if force or not p.exists():
            with urllib.request.urlopen(API.format(skip=skip), timeout=60) as r:
                p.write_bytes(r.read())
        d = json.loads(p.read_text())
        meta = d.get("meta", meta)
        rows += d.get("results", [])
    return rows, meta


# ---------------------------------------------------------------- parser (ours)
MONTHS = {m.lower(): i for i, m in enumerate(calendar.month_abbr) if m}
MONTHS.update({m.lower(): i for i, m in enumerate(calendar.month_name) if m})
MONTHS["sept"] = 9
MON = r"(jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|jul(?:y)?|aug(?:ust)?|sep(?:t(?:ember)?)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)"
DATE_RES = [  # (regex, kind) -> tried in order; matched spans are masked
    (re.compile(r"\b(20\d{2})[-/](\d{1,2})[-/](\d{1,2})\b"), "ymd"),
    (re.compile(r"\b(\d{1,2})/(\d{1,2})/(\d{4}|\d{2})\b"), "mdy"),
    (re.compile(r"\b(\d{1,2})-(\d{1,2})-(20\d{2})\b"), "mdy"),
    (re.compile(r"\b(\d{1,2})\s*" + MON + r"\.?\s*,?\s*(20\d{2}|\d{2})\b", re.I), "dmy_t"),
    (re.compile(r"\b" + MON + r"\.?\s+(\d{1,2}),?\s+(20\d{2})\b", re.I), "mdy_t"),
    (re.compile(r"\b(20\d{2})\s+" + MON + r"\s+(\d{1,2})\b", re.I), "ymd_t"),
    (re.compile(r"\b(\d{1,2})[/-](20\d{2})\b"), "my"),
    (re.compile(r"\b" + MON + r"\.?\s+(20\d{2})\b", re.I), "my_t"),
]
DATE_KW = re.compile(r"best|use[ds]?\s*by|used by|exp|bb\b|sell|before|enjoy|freeze|date", re.I)
RANGE_SEP = re.compile(r"^\s*(?:-|–|to|through|thru|until|up to and including)\s*$", re.I)
OPEN_BEFORE = re.compile(r"(?:all|any)\s+(?:\w+\s+){0,4}(?:dates?|codes?|lots?|product)\s+(?:through|thru|up to|prior to|before)\s*$",
                         re.I)
OPEN_AFTER_TAIL = re.compile(r"^\s*(?:,?\s*)?(?:and|&)\s+(?:all\s+)?(?:prior|earlier|before)", re.I)
ALL_SCOPE = re.compile(r"\ball\s+(?:lots?|lot codes|codes|production codes|products?|best[- ]by dates|dates|"
                       r"expiration dates)\b(?!\s*(?:through|thru|up to|prior|before|from|between|with|of|listed|below|ending))",
                       re.I)
OPEN_UPTO = re.compile(r"(?:up to and including|on or before|up to|prior to|(?<!best )\bbefore)\s*:?\s*$", re.I)
DMY_HINT = re.compile(r"\b(1[3-9]|2\d|3[01])/(0?[1-9]|1[0-2])/(20\d{2}|\d{2})\b")
PROD_FLAGS = re.compile(r"dates? of production|production dates?|pack(?:ed)? dates?|julian|manufactur\w* dates?|\bmfg\b", re.I)
BESTBY_KW = re.compile(r"best|use[ds]?[\s-]*by|used by|exp\w*|\bbb\b|sell|enjoy", re.I)
LOW_FLAGS = re.compile(r"format\s*=|purchased|no lot|does not (?:have|implement|use)|not have any code|"
                       r"\bnone\b|unknown|n/a|not coded|not lot", re.I)
LOT_KW = re.compile(r"\b(?:lot|batch)(?:es)?(?:\s*(?:#|nos?\.?|numbers?|codes?|ids?|\(s\)|s)\b\.?)*\s*[:#]?\s*", re.I)
STOP = re.compile(r"\b(?:best|use[ds]?|exp\w*|bb|sell|upc|item|size|product|sku|enjoy|packed|pack|manufactur\w*|"
                  r"net|sold|lot|batch|date|code date|plu|case|count|ct|oz|lb|man|mfg|retest|span\w*)\b", re.I)
UPC_RE = re.compile(r"(?:UPC|GTIN|EAN)\s*(?:code|#|no\.?|number)?s?\s*[:#]?\s*((?:[\dXx][\d\s\-]{6,18}\d)(?:\s*[,;&]\s*[\d][\d\s\-]{6,18}\d)*)",
                    re.I)


PRODNO_RE = re.compile(r"\b(?:product|item|sku|style|model)\s*(?:number|no\.?|#)?\s*[:#]?\s*[A-Z0-9][A-Z0-9\-]{2,}", re.I)


def _yr(y: str) -> int:
    y = int(y)
    return y + 2000 if y < 100 else y


def _mk(y, m, d):
    try:
        return date(y, m, d)
    except ValueError:
        return None


def find_dates(text: str):
    """[(start, end, lo_date, hi_date, kind)] non-overlapping, in text order. Month-only -> whole month."""
    taken = [False] * len(text)
    out = []
    for rx, kind in DATE_RES:
        for m in rx.finditer(text):
            if any(taken[m.start():m.end()]):
                continue
            g = m.groups()
            lo = hi = None
            if kind == "ymd":
                lo = _mk(int(g[0]), int(g[1]), int(g[2]))
            elif kind == "mdy":
                lo = _mk(_yr(g[2]), int(g[0]), int(g[1]))
            elif kind == "dmy_t":
                lo = _mk(_yr(g[2]), MONTHS[g[1].lower()[:3]], int(g[0]))
            elif kind == "mdy_t":
                lo = _mk(int(g[2]), MONTHS[g[0].lower()[:3]], int(g[1]))
            elif kind == "ymd_t":
                lo = _mk(int(g[0]), MONTHS[g[1].lower()[:3]], int(g[2]))
            elif kind in ("my", "my_t"):
                mo, y = (int(g[0]), int(g[1])) if kind == "my" else (MONTHS[g[0].lower()[:3]], int(g[1]))
                if 1 <= mo <= 12:
                    lo, hi = date(y, mo, 1), date(y, mo, calendar.monthrange(y, mo)[1])
            if lo is None or not (2015 <= lo.year <= 2032):
                continue
            hi = hi or lo
            for i in range(m.start(), m.end()):
                taken[i] = True
            out.append((m.start(), m.end(), lo, hi, kind))
    out.sort()
    return out, taken


def norm_lot(s: str) -> str:
    s = re.sub(r"^\s*(?:lot|batch)\b\s*[#:\-]?\s*|^\s*#\s*", "", str(s), flags=re.I)
    return re.sub(r"[^A-Za-z0-9]", "", s).upper()


def _lotlike(tok: str) -> bool:
    n = norm_lot(tok)
    return 3 <= len(n) <= 30 and any(c.isdigit() for c in n)


def parse_code_info(ci: str) -> dict:
    """OURS. code_info -> {lots, lot_ranges, date_windows, scope, parse_confidence, notes, upcs}."""
    text = re.sub(r"[\r\n\t]", " ", ci or "").strip()
    notes = []
    upcs = []
    for m in UPC_RE.finditer(text):
        for u in re.split(r"[,;&]", m.group(1)):
            d = re.sub(r"\D", "", u)
            if 8 <= len(d) <= 14:
                upcs.append(d)
    masked = UPC_RE.sub(lambda m: " " * len(m.group(0)), text)
    masked = PRODNO_RE.sub(lambda m: " " * len(m.group(0)), masked)   # product/item numbers are not lots
    dates, taken = find_dates(masked)
    # date windows (ranges / open ranges / singletons)
    windows, used = [], set()
    for i, (s, e, lo, hi, k) in enumerate(dates):
        if i in used:
            continue
        if i + 1 < len(dates) and RANGE_SEP.match(masked[e:dates[i + 1][0]]):
            windows.append([lo.isoformat(), dates[i + 1][3].isoformat()]); used |= {i, i + 1}
            continue
        before = masked[max(0, s - 70):s]
        if (OPEN_BEFORE.search(before) or OPEN_UPTO.search(before)
                or OPEN_AFTER_TAIL.match(masked[e:e + 40])):
            excl = bool(re.search(r"(?<!or )(?<!best )\bbefore\s*:?\s*$|prior to\s*:?\s*$", before, re.I))
            h = hi - timedelta(days=1) if excl else hi
            windows.append([None, h.isoformat()]); used.add(i)
            notes.append("open-start window" + (" (strictly before)" if excl else ""))
            continue
        windows.append([lo.isoformat(), hi.isoformat()]); used.add(i)
        if k in ("my", "my_t"):
            notes.append("month-only date")
    # lots: spans after a lot keyword, until a stop word / date
    no_dates = "".join(" " if taken[i] else ch for i, ch in enumerate(masked))
    lots, ranges, spans = [], [], []
    for m in LOT_KW.finditer(no_dates):
        start = m.end()
        stop = STOP.search(no_dates, start)
        end = stop.start() if stop else len(no_dates)
        spans.append((m.start(), end))
        seg = no_dates[start:end]
        for rm in re.finditer(r"([A-Za-z0-9][A-Za-z0-9\-]*)\s+(?:through|thru|to)\s+([A-Za-z0-9][A-Za-z0-9\-]*)", seg, re.I):
            a, b = norm_lot(rm.group(1)), norm_lot(rm.group(2))
            if _lotlike(a) and len(a) == len(b) and a <= b:
                ranges.append([a, b])
        seg2 = re.sub(r"([A-Za-z0-9][A-Za-z0-9\-]*)\s+(?:through|thru|to)\s+([A-Za-z0-9][A-Za-z0-9\-]*)", " ; ", seg, flags=re.I)
        for chunk in re.split(r"[,;]|\band\b|\s{2,}|\s/\s|\.\s|\s-\s", seg2):
            chunk = chunk.strip(" .:()[]#")
            if not chunk:
                continue
            parts = chunk.split()
            if len(parts) > 1 and all(p.isdigit() for p in parts) and len({len(p) for p in parts}) == 1 and len(parts[0]) >= 4:
                cands = parts
            else:
                cands = [chunk]
            for c in cands:
                if _lotlike(c) and len(c) <= 30:
                    n = norm_lot(c)
                    if n not in lots:
                        lots.append(n)
    if any(" " in l for l in lots):
        notes.append("lot with spaces")
    # residual lot-like tokens we could not attribute (outside lot spans, not dates/UPCs)
    resid_text = list(no_dates)
    for a, b in spans:
        for i in range(a, b):
            resid_text[i] = " "
    resid = [t for t in re.findall(r"[A-Za-z0-9][A-Za-z0-9\-]{3,}", "".join(resid_text))
             if any(c.isdigit() for c in t) and not re.fullmatch(r"\d{1,2}|20\d{2}", t)]
    numbered = len(re.findall(r"(?:^|\s)[1-9]\s*[.)]\s", " " + text)) >= 2
    scope, conf = None, "high"
    if ALL_SCOPE.search(text) and not lots and not ranges and not windows:
        scope = "all"
    elif ALL_SCOPE.search(text) and windows and all(w[0] is None for w in windows):
        scope = "dates"
    elif lots or ranges:
        scope = "lots"
    elif windows:
        scope = "dates"
    if DMY_HINT.search(text):
        conf = "low"; notes.append("day/month order ambiguous (DD/MM dates present)")
    elif scope is None or LOW_FLAGS.search(text) or numbered or (PROD_FLAGS.search(text) and not BESTBY_KW.search(text)):
        conf = "low"
        notes.append("numbered multi-product list" if numbered else "no parseable terms / flagged wording")
    elif scope == "lots" and resid:
        conf = "low"; notes.append(f"unattributed lot-like tokens {resid[:4]}")
    elif scope == "dates" and resid:
        conf = "low"; notes.append(f"unattributed lot-like tokens {resid[:4]}")
    elif scope == "dates" and not DATE_KW.search(text):
        conf = "medium"; notes.append("dates without a best-by/use-by keyword")
    elif notes:
        conf = "medium"
    if scope == "all" and conf != "low":
        conf = "high"
    return {"lots": lots, "lot_ranges": ranges, "date_windows": windows, "scope": scope,
            "parse_confidence": conf, "parse_notes": notes, "upcs": upcs}


CA_RE = re.compile(r"\bCA\b|california|nation\s*wide|\bUSA?\b|U\.S\.|united states|all (?:50 )?states|throughout the us",
                   re.I)


def ships_to_ca(pattern: str) -> bool:
    return bool(CA_RE.search(pattern or ""))


def kind_of(p: dict) -> str:
    if p["scope"] == "all":
        return "all"
    if p["scope"] == "lots":
        return "lot_range" if p["lot_ranges"] else "lot_list"
    if p["scope"] == "dates":
        return "date_range" if any(w[0] != w[1] for w in p["date_windows"]) else "date_list"
    return "none"


# ---------------------------------------------------------------- truth rule
def in_lot_range(n: str, rng) -> bool:
    a, b = rng
    return len(n) == len(a) == len(b) and a <= n <= b


def truth_for(rec: dict, lot: str, best_by: str) -> tuple[str, str]:
    if rec["parse_confidence"] == "low":
        return "HOLD_VERIFY", "ambiguous"
    if rec["scope"] == "all":
        return "PULL", "all_lots"
    n = norm_lot(lot)
    if rec["scope"] == "lots":
        if n in rec["lots"]:
            return "PULL", "lot_exact"
        if any(in_lot_range(n, r) for r in rec["lot_ranges"]):
            return "PULL", "lot_range"
        return "KEEP", "not_listed"
    bb = date.fromisoformat(best_by)
    for lo, hi in rec["date_windows"]:
        if (lo is None or date.fromisoformat(lo) <= bb) and bb <= date.fromisoformat(hi):
            return "PULL", "date_window"
    return "KEEP", "not_listed"


# ---------------------------------------------------------------- simulation
def synth_gtin(n: int) -> str:
    body = "02" + f"{n:011d}"  # GS1 restricted-circulation prefix: never a real retail GTIN
    tot = sum(int(c) * (3 if i % 2 == 0 else 1) for i, c in enumerate(reversed(body)))
    return body + str((10 - tot % 10) % 10)


CATS = [("cheese|milk|yogurt|cream|dairy|butter", "dairy"), ("ice cream|frozen", "frozen"),
        ("salad|lettuce|spinach|sprout|produce|cucumber|onion|vegetable|fruit|berr|apple|melon", "produce"),
        ("chicken|beef|pork|meat|sausage|crab|fish|seafood|salmon|shrimp|tuna", "meat & seafood"),
        ("cookie|cracker|chip|snack|pretzel|popcorn|candy|chocolate|bar\\b|gummy", "snacks & candy"),
        ("bread|bagel|tortilla|cake|muffin|bakery|pastry|pie\\b", "bakery"),
        ("supplement|capsule|tablet|vitamin|powder", "supplements"),
        ("sauce|spice|seasoning|soup|noodle|rice|pasta|flour|oil|honey|syrup", "pantry"),
        ("juice|water|tea|coffee|drink|beverage|soda", "beverages")]


def category(desc: str) -> str:
    for pat, c in CATS:
        if re.search(pat, desc, re.I):
            return c
    return "grocery"


def sku_name(desc: str) -> str:
    s = re.split(r"\s+(?:UPC|Net\s*W|NET\s*WT|SKU|Item)\b|[;\n]", desc, flags=re.I)[0]
    return re.sub(r"\s+", " ", s).strip(" ,.")[:90] or desc[:90]


def render(lot: str, r: random.Random) -> str:
    """Shelf rendering of a lot string: punctuation / case / prefix noise."""
    k = r.choice(["as", "as", "lower", "nopunct", "dash", "prefix"])
    if k == "lower":
        return lot.lower()
    if k == "nopunct":
        return re.sub(r"[^A-Za-z0-9]", "", lot)
    if k == "dash" and len(lot) >= 4 and lot.isalnum():
        i = len(lot) // 2
        return lot[:i] + "-" + lot[i:]
    if k == "prefix":
        return "LOT " + lot
    return lot


def bump(n: str, k: int) -> str | None:
    """Change the last digit run of a normalized lot by k, keeping length."""
    m = list(re.finditer(r"\d+", n))
    if not m:
        return None
    m = m[-1]
    v = int(m.group(0)) + k
    if v < 0 or len(str(v)) > len(m.group(0)):
        return None
    return n[:m.start()] + str(v).zfill(len(m.group(0))) + n[m.end():]


def lot_candidates(rec: dict, r: random.Random):
    """-> (recalled lots, non-recalled lots) as (lot_string, best_by) pairs, before rendering."""
    def rdate():
        return (date(2027, 1, 15) + timedelta(days=r.randint(0, 300))).isoformat()
    def synth_lot():
        return f"{r.choice('ABCDEFGHJKLMNPRSTUVWXYZ')}{r.randint(24, 26)}{r.randint(1, 365):03d}{r.choice('ABC')}"
    pos, neg = [], []
    if rec["scope"] == "all" or rec["parse_confidence"] == "low":
        clean = [l for l in rec["lots"] if re.fullmatch(r"[A-Z0-9]{3,16}", l) and "LOT" not in l]
        src = clean[:3] + [synth_lot() for _ in range(4)]
        for l in src[:6]:
            pos.append((l, rdate()))
        return pos, pos[:]  # every lot of an ALL / ambiguous recall gets the same label
    if rec["scope"] == "lots":
        for l in rec["lots"]:
            pos.append((l, rdate()))
        for a, b in rec["lot_ranges"]:
            pos += [(a, rdate()), (b, rdate())]
            mids = [x for x in (bump(a, 1), bump(b, -1)) if x and a < x < b]
            pos += [(x, rdate()) for x in mids]
            for x in (bump(a, -1), bump(b, 1)):
                if x:
                    neg.append((x, rdate()))
        for l in rec["lots"]:
            for k in (1, 2, -1, 7):
                x = bump(l, k)
                if x:
                    neg.append((x, rdate())); break
        neg.append((synth_lot(), rdate()))
    else:
        for lo, hi in rec["date_windows"]:
            h = date.fromisoformat(hi)
            l0 = date.fromisoformat(lo) if lo else h - timedelta(days=60)
            span = (h - l0).days
            for d in {l0, h, l0 + timedelta(days=span // 2)}:
                pos.append((synth_lot(), d.isoformat()))
            neg.append((synth_lot(), (h + timedelta(days=r.choice([1, 2, 5, 14]))).isoformat()))
            if lo:
                neg.append((synth_lot(), (l0 - timedelta(days=r.choice([1, 3, 10]))).isoformat()))
    # keep only candidates whose truth matches the side we put them on
    pos = [p for p in pos if truth_for(rec, p[0], p[1])[0] == "PULL"]
    neg = [p for p in neg if truth_for(rec, p[0], p[1])[0] == "KEEP"]
    return pos, neg


CARRY = {"SUPERCENTER": 0.8, "NEIGHBORHOOD": 0.5, "DISCOUNT": 0.5, "SAMS": 0.4}


def main(argv=None) -> int:
    force = "--fetch" in (argv or sys.argv[1:])
    raw, meta = fetch(force)
    cand = [x for x in raw if x.get("status") in ("Ongoing", "Completed")]
    parsed = []
    for x in cand:
        p = parse_code_info(x.get("code_info", ""))
        parsed.append((x, p))
    stats = {"fetched": len(raw), "ongoing_or_completed": len(cand),
             "parse_confidence": dict(Counter(p["parse_confidence"] for _, p in parsed)),
             "parsed_terms_high_or_medium": sum(p["parse_confidence"] != "low" for _, p in parsed)}
    stats["parse_rate"] = round(stats["parsed_terms_high_or_medium"] / max(1, len(cand)), 4)

    # ---- selection: one recall per event, deterministic
    r = random.Random(SEED)
    by_event = {}
    for x, p in sorted(parsed, key=lambda t: t[0]["recall_number"]):
        by_event.setdefault(x.get("event_id"), []).append((x, p))
    events = sorted(by_event)
    r.shuffle(events)
    picked, quota, nonca, low = [], dict(QUOTA), 0, 0
    for ev in events:
        opts = by_event[ev]
        x, p = opts[r.randrange(len(opts))]
        if len(x.get("code_info", "")) > 700:      # keep notices readable on an evidence card
            continue
        ca = ships_to_ca(x.get("distribution_pattern", ""))
        k = kind_of(p)
        if ca and p["parse_confidence"] != "low" and quota.get(k, 0) > 0:
            quota[k] -= 1; picked.append((x, p))
        elif not ca and p["parse_confidence"] == "high" and k != "none" and nonca < N_NONCA:
            nonca += 1; picked.append((x, p))
        elif ca and p["parse_confidence"] == "low" and k != "none" and low < N_LOW:
            low += 1; picked.append((x, p))
    picked.sort(key=lambda t: t[0]["recall_number"])

    recalls, skus = [], []
    for i, (x, p) in enumerate(picked):
        sid = "FDA" + re.sub(r"\W", "", x["recall_number"])
        g = synth_gtin(7_000_000 + i)
        cr = random.Random(f"{SEED}-case-{sid}")
        rec = {"recall_number": x["recall_number"], "event_id": x.get("event_id"), "status": x.get("status"),
               "recalling_firm": x.get("recalling_firm"), "product_description": x.get("product_description"),
               "reason_for_recall": x.get("reason_for_recall"), "classification": x.get("classification"),
               "report_date": x.get("report_date"), "distribution_pattern": x.get("distribution_pattern"),
               "code_info": x.get("code_info"),
               "lots": p["lots"], "lot_ranges": p["lot_ranges"], "date_windows": p["date_windows"],
               "scope": p["scope"], "kind": kind_of(p), "parse_confidence": p["parse_confidence"],
               "parse_notes": p["parse_notes"], "upcs_in_notice": p["upcs"],
               "ships_to_ca": ships_to_ca(x.get("distribution_pattern", "")),
               "sim_sku_id": sid, "sim_gtin": g, "_real": True, "_src": f"openfda:{x['recall_number']}"}
        recalls.append(rec)
        skus.append({"sku_id": sid, "gtin": g, "name": sku_name(x.get("product_description", "")),
                     "brand": x.get("recalling_firm", ""), "category": category(x.get("product_description", "")),
                     "ingredients": "", "is_food": True, "is_ingested_drug": False,
                     "case_units": cr.choice([6, 8, 12, 12, 24]), "case_cube_ft3": round(cr.uniform(0.4, 2.2), 2),
                     "case_weight_lb": round(cr.uniform(3.0, 24.0), 1), "_real": False,
                     "_src": f"simulated from openfda:{x['recall_number']}", "_upc_real": p["upcs"][:3]})

    stores = [json.loads(l) for l in (D / "stores.jsonl").read_text().splitlines() if l.strip()]
    stores.sort(key=lambda s: s["store_id"])
    lots_out, labels = [], []
    for st in stores:
        sr = random.Random(f"{SEED}-store-{st['store_id']}")
        slot = 0
        for rec in recalls:
            if not rec["ships_to_ca"] and st["state"] == "CA":
                continue
            if sr.random() > CARRY.get(st["format"], 0.5):
                continue
            pos, neg = lot_candidates(rec, sr)
            pick = []
            if rec["scope"] == "all" or rec["parse_confidence"] == "low":
                pick = sr.sample(pos, min(len(pos), sr.randint(2, 3)))
            else:
                if pos and sr.random() < 0.6:
                    pick += sr.sample(pos, min(len(pos), sr.randint(1, 2)))
                if neg:
                    pick += sr.sample(neg, min(len(neg), sr.randint(1, 2) if pick else sr.randint(2, 3)))
            seen, rows = set(), []
            for lot, bb in pick:
                if norm_lot(lot) in seen:
                    continue
                seen.add(norm_lot(lot)); rows.append((render(lot, sr), bb))
            if not rows:
                continue
            aisle, bay, shelf = f"F{1 + slot // 10:02d}", 1 + (slot % 10) // 5, 1 + slot % 5
            slot += 1
            for j, (lot, bb) in enumerate(rows, 1):
                t, basis = truth_for(rec, lot, bb)
                assert norm_lot(lot) and t, (rec["recall_number"], lot)
                loc = {"aisle": aisle, "bay": bay, "shelf": shelf, "pos": j}
                lots_out.append({"store_id": st["store_id"], "sku_id": rec["sim_sku_id"], "loc": loc, "lot": lot,
                                 "best_by": bb, "units": sr.randint(2, 18), "_real": False})
                labels.append({"store_id": st["store_id"], "sku_id": rec["sim_sku_id"], "lot": lot, "best_by": bb,
                               "truth": t, "recall_number": rec["recall_number"], "basis": basis})
    # uniqueness checks
    assert len({(x["store_id"], x["sku_id"], norm_lot(x["lot"])) for x in lots_out}) == len(lots_out)
    assert len({(x["store_id"], json.dumps(x["loc"], sort_keys=True)) for x in lots_out}) == len(lots_out)

    def wj(name, rows_):
        (D / name).write_text("".join(json.dumps(x, ensure_ascii=False) + "\n" for x in rows_))
    wj("recalls_fda.jsonl", recalls)
    wj("skus_fda.jsonl", skus)
    wj("lots.jsonl", lots_out)
    with open(D / "labels_fda.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["store_id", "sku_id", "lot", "best_by", "truth", "recall_number", "basis"])
        w.writeheader(); w.writerows(labels)
    scen = {**SCENARIO, "recall_numbers": [x["recall_number"] for x in recalls],
            "note": ("Drill replay of real openFDA food recall notices (public domain) against SIMULATED shelf lots "
                     "in 20 CA demo stores: pull only affected lots, every window must end before the deadline "
                     "(48h after the notice batch lands). openFDA meta.last_updated "
                     f"{meta.get('last_updated')}; terms {meta.get('terms')}; license {meta.get('license')}."),
            "build_stats": stats}
    (D / "scenario_fda_lots.json").write_text(json.dumps(scen, indent=2) + "\n")
    lc = Counter(x["truth"] for x in labels)
    print(f"recalls {len(recalls)} kinds {dict(Counter(x['kind'] for x in recalls))} "
          f"conf {dict(Counter(x['parse_confidence'] for x in recalls))} ships_to_ca {sum(x['ships_to_ca'] for x in recalls)}")
    print(f"lots {len(lots_out)} labels {dict(lc)} bases {dict(Counter(x['basis'] for x in labels))}")
    print(f"parse stats {stats}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
