"""OURS. Baseline C classifier: BM25 retrieval over rules.jsonl clauses + gemini-4-argon, JSON answer.

Implements contract.Classifier: (sku, candidates) -> SkuDecision. Only consulted by rules.evaluate_sku for
items the hand-written rules mark HOLD_VERIFY (generic color only, unreadable label). Any error, malformed
answer or confidence below MIN_CONF -> HOLD_VERIFY. Responses are cached on disk keyed by the prompt hash,
so reruns are free and deterministic.
"""
from __future__ import annotations

import hashlib
import json
import math
import os
import pathlib
import re
import threading
from collections import Counter
from concurrent.futures import ThreadPoolExecutor

from contract import DecidedBy, Rule, Sku, SkuDecision, Verdict

from ._src import src_of

SRC = src_of(__file__)
MODEL = "gemini-4-argon"
MIN_CONF = 0.7
MAX_CALLS = 300
ROOT = pathlib.Path(__file__).resolve().parents[3]
CACHE = ROOT / "runs" / "baseline_c_cache"
_TOK = re.compile(r"[a-z0-9]+")


def _tokens(s: str) -> list[str]:
    return _TOK.findall((s or "").lower())


class BM25:
    """Tiny BM25 over rule clauses: each rule's source_text split into sentences, plus clause_ref/aliases."""

    def __init__(self, rules: list[Rule], k1: float = 1.5, b: float = 0.75):
        self.docs: list[tuple[Rule, str]] = []
        for r in rules:
            for sent in re.split(r"(?<=[.;])\s+", r.source_text):
                if sent.strip():
                    self.docs.append((r, sent.strip()))
            self.docs.append((r, f"{r.clause_ref}. Applies to {', '.join(r.applies_to)} in "
                                 f"{', '.join(r.jurisdictions)} from {r.effective.isoformat()}. "
                                 f"Also known as: {', '.join(r.aliases)}."))
        self.toks = [_tokens(f"{r.clause_ref} {t}") for r, t in self.docs]
        self.avg = sum(map(len, self.toks)) / max(1, len(self.toks))
        df = Counter(w for t in self.toks for w in set(t))
        n = len(self.toks)
        self.idf = {w: math.log(1 + (n - d + 0.5) / (d + 0.5)) for w, d in df.items()}
        self.k1, self.b = k1, b

    def search(self, query: str, k: int = 4, restrict: set[str] | None = None) -> list[tuple[Rule, str, float]]:
        q = _tokens(query)
        scored = []
        for (r, text), t in zip(self.docs, self.toks):
            if restrict is not None and r.rule_id not in restrict:
                continue
            tf = Counter(t)
            s = sum(self.idf.get(w, 0) * tf[w] * (self.k1 + 1) /
                    (tf[w] + self.k1 * (1 - self.b + self.b * len(t) / self.avg)) for w in q if w in tf)
            scored.append((r, text, s))
        scored.sort(key=lambda x: (-x[2], x[0].rule_id, x[1]))
        return scored[:k]


PROMPT = """You are a retail compliance analyst. Decide whether this product must be pulled from shelves
under the rules below. The additive of concern is FD&C Red No. 3 (erythrosine, E127), aliases: {aliases}.
Rules in force for this product at the evaluation time (retrieved clauses):
{clauses}

Product:
  name: {name}
  brand: {brand}
  category: {category}
  is_food: {is_food}; is_ingested_drug: {is_drug}
  ingredients: {ingredients}

Answer PULL only if the ingredient list shows Red No. 3 (under any name or spelling). Answer KEEP if the
ingredient list is readable and shows no Red No. 3 (e.g. a generic "artificial color" with no other sign of
Red No. 3 in a product that plainly does not use it). Answer HOLD_VERIFY if the label is unreadable or you
cannot tell from the text whether Red No. 3 is present.
Return JSON only: {{"verdict": "PULL"|"HOLD_VERIFY"|"KEEP", "confidence": 0.0-1.0,
"match_text": exact substring of the ingredients that shows Red No. 3 or null, "rationale": one sentence}}"""


class ArgonClassifier:
    def __init__(self, rules: list[Rule], max_calls: int = MAX_CALLS, cache_dir: pathlib.Path = CACHE):
        self.index = BM25(rules)
        self.rules = rules
        self.max_calls = max_calls
        self.cache = cache_dir
        self.cache.mkdir(parents=True, exist_ok=True)
        self.lock = threading.Lock()
        self.stats = Counter()
        self._client = None

    # ---------- prompt / cache
    def _prompt(self, sku: Sku, candidates: list[Rule]) -> str:
        restrict = {r.rule_id for r in candidates} or None
        q = f"{sku.category} {sku.ingredients} {'food' if sku.is_food else ''} {'drug' if sku.is_ingested_drug else ''}"
        hits = self.index.search(q + " red dye 3 food sell", k=4, restrict=restrict)
        clauses = "\n".join(f"  [{r.rule_id} | {r.clause_ref}] {t}" for r, t, _ in hits) or "  (none)"
        aliases = sorted({a for r in (candidates or self.rules) for a in r.aliases})
        return PROMPT.format(aliases=", ".join(aliases), clauses=clauses, name=sku.name, brand=sku.brand,
                             category=sku.category, is_food=sku.is_food, is_drug=sku.is_ingested_drug,
                             ingredients=sku.ingredients)

    def _key(self, prompt: str) -> str:
        return hashlib.sha256(f"{MODEL}\n{prompt}".encode()).hexdigest()[:32]

    def _call(self, prompt: str) -> dict:
        p = self.cache / f"{self._key(prompt)}.json"
        if p.exists():
            with self.lock:
                self.stats["cache_hits"] += 1
            return json.loads(p.read_text())
        with self.lock:
            if self.stats["live_calls"] >= self.max_calls:
                self.stats["capped"] += 1
                return {"error": "call cap reached"}
            self.stats["live_calls"] += 1
            if self._client is None:
                from google import genai
                self._client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
        from google.genai import types
        try:
            r = self._client.models.generate_content(
                model=MODEL, contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json", temperature=0,
                    thinking_config=types.ThinkingConfig(thinking_level="low"),
                    http_options=types.HttpOptions(timeout=120_000)))
            u = r.usage_metadata
            rec = {"text": r.text, "usage": {"prompt": u.prompt_token_count or 0,
                                              "output": u.candidates_token_count or 0,
                                              "thoughts": u.thoughts_token_count or 0}}
        except Exception as e:                       # noqa: BLE001 - any failure -> HOLD_VERIFY upstream
            with self.lock:
                self.stats["errors"] += 1
            return {"error": f"{type(e).__name__}: {e}"[:300]}
        p.write_text(json.dumps(rec))
        return rec

    def prefetch(self, items: list[tuple[Sku, list[Rule]]], workers: int = 8) -> None:
        with ThreadPoolExecutor(workers) as ex:
            list(ex.map(lambda it: self._call(self._prompt(*it)), items))

    # ---------- contract.Classifier
    def __call__(self, sku: Sku, candidates: list[Rule]) -> SkuDecision:
        rec = self._call(self._prompt(sku, candidates))
        with self.lock:
            self.stats["consulted"] += 1
            for k, v in (rec.get("usage") or {}).items():
                self.stats[f"tok_{k}"] += v
        hold = lambda why: SkuDecision(sku.sku_id, Verdict.HOLD_VERIFY, None, None, None, None,
                                       tuple(r.rule_id for r in candidates), DecidedBy.MODEL, why)
        if "error" in rec:
            return hold(f"model unavailable ({rec['error'][:80]}); hold for manual check")
        try:
            ans = json.loads(rec["text"])
            v = Verdict(str(ans["verdict"]).upper())
            conf = float(ans.get("confidence", 0))
        except Exception:                            # noqa: BLE001
            return hold("model answer not parseable; hold for manual check")
        why = f"[{MODEL} conf {conf:.2f}] {str(ans.get('rationale', ''))[:300]}"
        if conf < MIN_CONF or v == Verdict.HOLD_VERIFY:
            return hold(why)
        if v == Verdict.KEEP:
            return SkuDecision(sku.sku_id, Verdict.KEEP, None, None, None, None, (), DecidedBy.MODEL, why)
        mt = ans.get("match_text")
        i = sku.ingredients.lower().find(mt.lower()) if isinstance(mt, str) and mt else -1
        return SkuDecision(sku.sku_id, Verdict.PULL, "RED3", sku.ingredients[i:i + len(mt)] if i >= 0 else None,
                           i if i >= 0 else None, i + len(mt) if i >= 0 else None,
                           tuple(r.rule_id for r in candidates), DecidedBy.MODEL, why)
