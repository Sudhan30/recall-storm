"""OURS. Prove each continuation seam joined cleanly.

Usage: python tools/seam_check.py runs/<name>/ [--window 300] [--min-dup 40] [--strict] [--show]
                                               [--report reports/<name>_seams.json]

Seams come from hops.jsonl (every hop with finish CONTINUATION; plus checkpoint/hop-start resumes after a
dropped stream, recorded as {"resume": ..., "cut": byte}) or events.jsonl (every
interaction.status_update with has_token). For each seam, 300 bytes either side of seam_byte:

  dup        FAIL if text right after the seam repeats >= 40 chars already present just before it
             (resume restarted from an earlier point). A repeated >= 40-char run elsewhere in the window
             is shown as a note (it can be ordinary code repetition); --strict makes it a FAIL too.
  open_block FAIL if the file block open at the seam is not closed by <<<END FILE>>> before the next
             <<<FILE ...>>> header or end of stream (PENDING while the run is still live).
  manifest   FAIL if a manifest path is emitted before and again after the seam, or a second
             <<<MANIFEST>>> starts after the seam (the model restarted).

Prints one PASS/FAIL line per seam and a SUMMARY line. Exit 0 only if there is >= 1 seam and all PASS.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys

FILE_RE = re.compile(rb"<<<FILE\s+path\s*=\s*[\"']?([^\"'>\s]+)[\"']?\s*>>>")
END_FILE = b"<<<END FILE>>>"
MAN_OPEN = b"<<<MANIFEST>>>"


def read_jsonl(p: pathlib.Path) -> list[dict]:
    out = []
    if not p.exists():
        return out
    for line in p.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if line:
            try:
                out.append(json.loads(line))
            except json.JSONDecodeError:
                pass
    return out


def find_seams(run: pathlib.Path) -> tuple[list[dict], str, bool]:
    """Returns (seams, source, finished). Each seam: {byte, kind, label, tok}."""
    hops = read_jsonl(run / "hops.jsonl")
    events = read_jsonl(run / "events.jsonl")
    seams: list[dict] = []
    if hops:
        finished = False
        for r in hops:
            if "finish" in r:
                if r.get("finish") == "CONTINUATION" and r.get("seam_byte") is not None:
                    seams.append({"byte": int(r["seam_byte"]), "kind": "continuation",
                                  "label": f"hop {r.get('hop')}->{(r.get('hop') or 0) + 1}",
                                  "tok": r.get("visible_total"), "has_token": bool(r.get("has_token"))})
                elif r.get("finish") != "CONTINUATION" or not r.get("has_token"):
                    finished = True
            elif "resume" in r and r.get("cut") is not None:
                seams.append({"byte": int(r["cut"]), "kind": f"resume:{r['resume']}",
                              "label": f"hop {r.get('hop')} retry", "tok": None, "has_token": True})
        return seams, "hops.jsonl", finished
    if events:
        finished = any(e.get("type") in ("interaction.completed", "error") for e in events)
        seen = set()
        for e in events:
            if e.get("type") == "interaction.status_update" and e.get("has_token") and e.get("seam_byte") is not None:
                b = int(e["seam_byte"])
                if b in seen:
                    continue
                seen.add(b)
                u = e.get("usage") or {}
                seams.append({"byte": b, "kind": "status_update", "label": f"event {e.get('event_id')}",
                              "tok": u.get("total_output_tokens"), "has_token": True})
            if e.get("reconnect"):
                pass                                # reconnects do not rewrite text; nothing to check
        return seams, "events.jsonl", finished
    return [], "none", False


def longest_common(a: bytes, b: bytes) -> tuple[int, bytes]:
    """Longest common substring (DP, fine for 300x300)."""
    best, end = 0, 0
    prev = [0] * (len(b) + 1)
    for i in range(1, len(a) + 1):
        cur = [0] * (len(b) + 1)
        ai = a[i - 1]
        for j in range(1, len(b) + 1):
            if ai == b[j - 1]:
                v = prev[j - 1] + 1; cur[j] = v
                if v > best:
                    best, end = v, i
        prev = cur
    return best, a[end - best:end]


def anchored_dup(before: bytes, after: bytes, min_dup: int, slack: int = 8) -> tuple[int, bytes]:
    """Longest prefix of `after` (starting within `slack` bytes of the seam) that occurs in `before`."""
    best, txt = 0, b""
    for s in range(0, min(slack, len(after)) + 1):
        lo, hi = 0, len(after) - s                  # binary search on length (substring-closed property)
        while lo < hi:
            mid = (lo + hi + 1) // 2
            if after[s:s + mid] in before:
                lo = mid
            else:
                hi = mid - 1
        if lo > best and len(after[s:s + lo].strip()) >= min_dup:
            best, txt = lo, after[s:s + lo]
    return (best, txt) if best >= min_dup else (0, b"")


def check_seam(data: bytes, seam: int, window: int, min_dup: int, strict: bool, live: bool) -> dict:
    seam = max(0, min(seam, len(data)))
    before, after = data[max(0, seam - window):seam], data[seam:seam + window]
    fails, notes = [], []

    n, txt = anchored_dup(before, after, min_dup)
    if n:
        fails.append(f"dup {n}B resumed text repeats pre-seam: {txt[:60]!r}")
    else:
        n2, t2 = longest_common(before, after)
        if n2 >= min_dup and len(t2.strip()) >= min_dup:
            msg = f"repeated {n2}B run across seam (not anchored): {t2[:60]!r}"
            (fails if strict else notes).append(msg)

    # file block open at the seam
    heads = list(FILE_RE.finditer(data))
    open_hdr = None
    for m in heads:
        if m.start() >= seam:
            break
        end = data.find(END_FILE, m.end())
        nxt = next((h.start() for h in heads if h.start() > m.start()), len(data))
        if end < 0 or end >= nxt or end + len(END_FILE) > seam:
            open_hdr = (m, end, nxt)                # last one before the seam not closed before it
        else:
            open_hdr = None
    # a header split exactly across the seam is caught here too (regex runs on the joined bytes)
    if open_hdr:
        m, end, nxt = open_hdr
        path = m.group(1).decode(errors="replace")
        if end >= 0 and end < nxt:
            notes.append(f"seam inside {path}; closed at byte {end}")
        elif nxt < len(data):
            fails.append(f"open_block {path} never closed before next FILE header at byte {nxt}")
        elif live:
            notes.append(f"open_block {path} still open (run live) -> PENDING")
        else:
            fails.append(f"open_block {path} never closed (end of stream)")

    # manifest path emitted twice across the seam / manifest restarted
    pre = {m.group(1) for m in heads if m.start() < seam}
    post = [m.group(1) for m in heads if m.start() >= seam]
    twice = sorted({p.decode(errors="replace") for p in post if p in pre})
    if twice:
        fails.append("manifest path emitted twice: " + ", ".join(twice[:5]))
    if data.find(MAN_OPEN, seam) >= 0 and data.find(MAN_OPEN) < seam:
        fails.append("second <<<MANIFEST>>> after seam (restart)")

    pending = any("PENDING" in x for x in notes) and not fails
    return {"seam_byte": seam, "status": "FAIL" if fails else ("PENDING" if pending else "PASS"),
            "fails": fails, "notes": notes,
            "before_tail": before[-80:].decode(errors="replace"), "after_head": after[:80].decode(errors="replace")}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("run"); ap.add_argument("--window", type=int, default=300)
    ap.add_argument("--min-dup", type=int, default=40); ap.add_argument("--strict", action="store_true")
    ap.add_argument("--show", action="store_true", help="print 80 bytes either side of each seam")
    ap.add_argument("--report", help="write JSON results here (never inside runs/)")
    a = ap.parse_args(argv)
    run = pathlib.Path(a.run)
    data = (run / "stream.txt").read_bytes() if (run / "stream.txt").exists() else b""
    seams, source, finished = find_seams(run)
    results = []
    for i, s in enumerate(seams, 1):
        r = check_seam(data, s["byte"], a.window, a.min_dup, a.strict, live=not finished)
        r.update(n=i, kind=s["kind"], label=s["label"], tok=s["tok"], has_token=s["has_token"])
        if s["kind"] == "continuation" and not s["has_token"]:
            r["fails"].append("CONTINUATION without token"); r["status"] = "FAIL"
        results.append(r)
        tok = f" tok~{s['tok']}" if s["tok"] is not None else ""
        extra = "; ".join(r["fails"] + r["notes"])
        print(f"SEAM {i} [{s['kind']}] {s['label']} byte {r['seam_byte']}{tok}: {r['status']}"
              + (f"  ({extra})" if extra else ""))
        if a.show:
            print(f"    ...{r['before_tail']!r} || {r['after_head']!r}...")
    n_pass = sum(r["status"] == "PASS" for r in results)
    n_fail = sum(r["status"] == "FAIL" for r in results)
    n_cont = sum(not r["kind"].startswith("resume") for r in results)
    if not results:
        summary = f"NO SEAMS — continuation not proven (source: {source}, {len(data)} bytes, " \
                  f"{'finished' if finished else 'live/unknown'})"
    else:
        summary = (f"SUMMARY: {len(results)} seams ({n_cont} continuation, {len(results) - n_cont} resume), "
                   f"{n_pass} PASS, {n_fail} FAIL, {len(results) - n_pass - n_fail} PENDING "
                   f"(source: {source}, run {'finished' if finished else 'live'})")
    print(summary)
    if a.report:
        p = pathlib.Path(a.report); p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps({"run": str(run), "source": source, "finished": finished, "summary": summary,
                                 "seams": results}, indent=2) + "\n")
    return 0 if results and n_pass == len(results) else 1


if __name__ == "__main__":
    sys.exit(main())
