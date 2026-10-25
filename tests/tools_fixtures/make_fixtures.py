"""OURS. Builds fake Argon run dirs for testing split_stream / seam_check / verify_code.

Usage: python tests/tools_fixtures/make_fixtures.py   (writes tests/tools_fixtures/<variant>/)
Variants: good_run (argon_run logs, 1 clean seam), bad_run (dup text at seam + manifest path twice),
          bg (argon_bg events.jsonl, 1 status_update seam), partial (stream cut mid-file, no hops finish).
"""
import json, pathlib

HERE = pathlib.Path(__file__).parent
MANIFEST = [
    {"path": "recallstorm/__init__.py", "purpose": "pkg", "public": [], "depends_on": []},
    {"path": "recallstorm/aliases/norm.py", "purpose": "normalize + detect",
     "public": ["normalize(text) -> str", "find_red3(text, aliases) -> tuple"], "depends_on": ["contract.py"]},
    {"path": "recallstorm/rules/engine.py", "purpose": "rules",
     "public": ["evaluate_sku(sku, rules, state, at, classifier) -> SkuDecision"],
     "depends_on": ["recallstorm/aliases/norm.py"]},
    {"path": "tests/unit/test_aliases_norm.py", "purpose": "tests", "public": [], "depends_on": []},
]
FILES = {
"recallstorm/__init__.py": '"""Recall Storm."""\n__version__ = "0.1"\n',
"recallstorm/aliases/norm.py": '''import re
from contract import Verdict


def normalize(text):
    """Lowercase and collapse whitespace."""
    t = text.lower().replace("1", "i")
    return re.sub(r"\\s+", " ", t)


def find_red3(text, aliases):
    """Return (start, end) of the first alias match or None."""
    n = normalize(text)
    for a in aliases:
        i = n.find(a.lower())
        if i >= 0:
            return (i, i + len(a))
    return None


def code():
    return "PULL" if Verdict.PULL else "BOGUS_CODE"
''',
"recallstorm/rules/engine.py": '''from contract import SkuDecision, Verdict, DecidedBy
from recallstorm.aliases.norm import find_red3, normalize, missing_fn


def evaluate_sku(sku, rules, state, at, classifier=None):
    m = find_red3(sku.ingredients)
    return SkuDecision(sku.sku_id, Verdict.KEEP, None, None, None, None, (), DecidedBy.RULE, "x")


def todo_stub():
    pass
''',
"tests/unit/test_aliases_norm.py": '''from recallstorm.aliases.norm import find_red3, normalize


def test_normalize():
    assert normalize("A  B") == "a b"


def test_find():
    assert find_red3("sugar, erythrosine", ["erythrosine"]) == (7, 18)


def test_fail():
    assert find_red3("salt", ["red 3"]) is not None
''',
}


def stream_text(fence_second=True):
    s = "<<<MANIFEST>>>\n" + "".join(json.dumps(m) + "\n" for m in MANIFEST) + "<<<END MANIFEST>>>\n"
    for i, m in enumerate(MANIFEST):
        body = FILES[m["path"]]
        if fence_second and i == 1:
            body = "```python\n" + body + "```\n"
        s += f"<<<FILE path={m['path']}>>>\n{body}<<<END FILE>>>\n"
    return s


def write_run(d, data: bytes, seam: int, finish_last="STOP", n_hops=2):
    d.mkdir(parents=True, exist_ok=True)
    (d / "stream.txt").write_bytes(data)
    log, hops, vis_done = [], [], 0
    cuts = [0, seam, len(data)] if n_hops == 2 else [0, len(data)]
    for h in range(len(cuts) - 1):
        a, b = cuts[h], cuts[h + 1]
        for ob in list(range(a + 150, b, 150)) + [b]:
            log.append({"hop": h, "t": ob / 100, "chars": 150, "out_bytes": ob,
                        "visible_hop": (ob - a) // 4, "thinking_hop": 10, "checkpoint": False})
        vh = (b - a) // 4; vis_done += vh
        hops.append({"hop": h, "finish": "CONTINUATION" if h < len(cuts) - 2 else finish_last,
                     "has_token": h < len(cuts) - 2, "secs": 1.0, "t": b / 100, "visible_hop": vh,
                     "thinking_hop": 10, "prompt_hop": 5000, "visible_total": vis_done,
                     "chars_hop": b - a, "seam_byte": b})
    (d / "stream_log.jsonl").write_text("".join(json.dumps(r) + "\n" for r in log))
    if finish_last is not None:
        (d / "hops.jsonl").write_text("".join(json.dumps(r) + "\n" for r in hops))
    else:
        (d / "hops.jsonl").write_text("".join(json.dumps(r) + "\n" for r in hops[:-1]))


def main():
    s = stream_text().encode()
    seam = s.index(b"def find_red3")              # seam lands mid-file
    write_run(HERE / "good_run", s, seam)

    # bad: the resumed hop repeats 60 chars from before the seam, and re-emits a manifest path
    dup = s[seam - 60:seam]
    extra = b"<<<FILE path=recallstorm/__init__.py>>>\n__version__ = '0.2'\n<<<END FILE>>>\n"
    bad = s[:seam] + dup + s[seam:] + extra
    write_run(HERE / "bad_run", bad, seam)

    # partial: cut in the middle of the third file, hop still running (no finish record)
    cut = s.index(b"def todo_stub")
    write_run(HERE / "partial", s[:cut], seam, finish_last=None)

    # bg: events.jsonl
    d = HERE / "bg"; d.mkdir(parents=True, exist_ok=True)
    (d / "stream.txt").write_bytes(s)
    ev = [{"t": 0, "type": "interaction.created", "event_id": "e0", "id": "int-1"}]
    k = 1
    for ob in list(range(200, len(s), 200)) + [len(s)]:
        ev.append({"t": k, "type": "step.delta", "event_id": f"e{k}", "chars": 200, "out_bytes": ob}); k += 1
        if ob >= seam and not any(e.get("type") == "interaction.status_update" for e in ev):
            ev.append({"t": k, "type": "interaction.status_update", "event_id": f"e{k}", "status": "in_progress",
                       "has_token": True, "usage": {"total_output_tokens": ob // 4, "total_thought_tokens": 50},
                       "seam_byte": ob}); k += 1
    ev.append({"t": k, "type": "interaction.status_update", "event_id": f"e{k}", "status": "completed",
               "has_token": False, "usage": {"total_output_tokens": len(s) // 4, "total_thought_tokens": 90},
               "seam_byte": len(s)})
    ev.append({"t": k + 1, "type": "interaction.completed", "event_id": f"e{k+1}", "detail": "done"})
    (d / "events.jsonl").write_text("".join(json.dumps(r) + "\n" for r in ev))
    print("fixtures written:", ", ".join(p.name for p in sorted(HERE.iterdir()) if p.is_dir()))


if __name__ == "__main__":
    main()
