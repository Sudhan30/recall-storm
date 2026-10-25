"""OURS. Split an Argon stream.txt into files + manifest.jsonl + offsets.jsonl.

Usage: python tools/split_stream.py STREAM_TXT --log LOG --out OUTDIR [--hops HOPS_JSONL] [--quiet]

LOG is either runs/<name>/stream_log.jsonl (argon_run.py; hops.jsonl next to it is used when present)
or runs/<name>/events.jsonl (argon_bg.py). The format is auto-detected from its contents.

Outputs under OUTDIR:
  <path>             each emitted file (fences stripped; a re-emitted contract.py/contract_io.py is
                     written as <name>.argon_reemitted so it never shadows ours on PYTHONPATH)
  manifest.jsonl     manifest entries, one JSON per line
  offsets.jsonl      {path, start_byte, end_byte, start_tok, end_tok, terminated, ...} per file block
  split_meta.json    summary: counts, unterminated blocks, duplicates, token-map source, warnings

Safe on partial, still-growing streams: an unterminated last block is written and flagged.
"""
from __future__ import annotations

import argparse
import bisect
import json
import pathlib
import re
import sys

MAN_OPEN = b"<<<MANIFEST>>>"
MAN_CLOSE = b"<<<END MANIFEST>>>"
FILE_RE = re.compile(rb"<<<FILE\s+path\s*=\s*[\"']?([^\"'>\s]+)[\"']?\s*>>>")
END_FILE = b"<<<END FILE>>>"
FENCE_RE = re.compile(r"^\s*```[\w+.-]*\s*$")
PROTECTED = {"contract.py", "contract_io.py"}


# ---------------------------------------------------------------- token map
def _read_jsonl(p: pathlib.Path) -> list[dict]:
    rows = []
    if not p or not p.exists():
        return rows
    with open(p, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                continue                         # partial last line of a live log
    return rows


def detect_log_kind(rows: list[dict]) -> str:
    for r in rows[:200]:
        if "type" in r and ("event_id" in r or str(r.get("type", "")).startswith(("step.", "interaction."))):
            return "bg"
        if "visible_hop" in r or "hop" in r:
            return "run"
    return "unknown"


def _monotone_add(points: list[list[float]], b: float, t: float) -> None:
    """Append (bytes, tok); on a byte rewind (checkpoint truncation) drop points past it."""
    while points and points[-1][0] > b:
        points.pop()
    if points and t < points[-1][1]:
        t = points[-1][1]
    if points and points[-1][0] == b:
        points[-1][1] = max(points[-1][1], t)
    else:
        points.append([b, t])


def token_points_run(log_rows: list[dict], hop_rows: list[dict]) -> tuple[list[list[float]], dict]:
    """argon_run: cumulative tokens = visible tokens of finished earlier hops + visible_hop."""
    finished = {}                                   # hop -> finish record (last one wins)
    for r in hop_rows:
        if "finish" in r and "hop" in r:
            finished[r["hop"]] = r
    base_cache: dict[int, float] = {}
    last_vis_in_log: dict[int, float] = {}
    for r in log_rows:
        if r.get("visible_hop") is not None:
            last_vis_in_log[r.get("hop", 0)] = r["visible_hop"]

    def base(h: int) -> float:
        if h in base_cache:
            return base_cache[h]
        if h <= 0:
            v = 0.0
        elif (h - 1) in finished and finished[h - 1].get("visible_total") is not None:
            v = float(finished[h - 1]["visible_total"])
        else:
            prev = finished.get(h - 1, {}).get("visible_hop") or last_vis_in_log.get(h - 1, 0) or 0
            v = base(h - 1) + float(prev)
        base_cache[h] = v
        return v

    points: list[list[float]] = [[0, 0]]
    events = []                                     # merge log rows and hop finishes in order
    for i, r in enumerate(log_rows):
        events.append(("log", i, r))
    for r in hop_rows:
        if "finish" in r and r.get("seam_byte") is not None:
            events.append(("hop", r.get("hop", 0), r))
    # log rows are chronological; insert each hop finish after the last log row of that hop
    ordered = []
    hop_fin = {r.get("hop", 0): r for k, _, r in events if k == "hop"}
    last_idx_of_hop = {}
    for i, r in enumerate(log_rows):
        last_idx_of_hop[r.get("hop", 0)] = i
    emitted = set()
    for i, r in enumerate(log_rows):
        ordered.append(r)
        h = r.get("hop", 0)
        if last_idx_of_hop.get(h) == i and h in hop_fin:
            ordered.append({"_fin": True, **hop_fin[h]}); emitted.add(h)
    for h, r in sorted(hop_fin.items()):           # non-stream runs: no log rows at all
        if h not in emitted:
            ordered.append({"_fin": True, **r})
    n_used = 0
    for r in ordered:
        if r.get("_fin"):
            vt = r.get("visible_total")
            if vt is None:
                vt = base(r.get("hop", 0)) + float(r.get("visible_hop") or 0)
            _monotone_add(points, float(r["seam_byte"]), float(vt)); n_used += 1
            continue
        ob = r.get("out_bytes")
        if ob is None:
            continue
        vh = r.get("visible_hop")
        if vh is None:
            # still record a rewind if bytes went backwards
            while len(points) > 1 and points[-1][0] > ob:
                points.pop()
            continue
        _monotone_add(points, float(ob), base(r.get("hop", 0)) + float(vh)); n_used += 1
    return points, {"source": "stream_log+hops" if hop_rows else "stream_log", "points": n_used}


def token_points_bg(rows: list[dict], total_bytes: int) -> tuple[list[list[float]], dict]:
    """argon_bg: tokens known at status updates (usage), bytes known at every delta/status."""
    raw = []
    for r in rows:
        if r.get("type") == "interaction.status_update" and isinstance(r.get("usage"), dict):
            u = r["usage"]; out = u.get("total_output_tokens"); th = u.get("total_thought_tokens") or 0
            if out is None or r.get("seam_byte") is None:
                continue
            raw.append((float(r["seam_byte"]), float(out), float(th)))
    mode = "output"
    if raw:
        b, o, th = raw[-1]
        # if total_output_tokens evidently includes thoughts (implausibly few bytes per token), subtract them
        if th > 0 and o > th and b / max(o, 1) < 2.0 and b / max(o - th, 1) >= 2.0:
            mode = "output_minus_thoughts"
    points: list[list[float]] = [[0, 0]]
    for b, o, th in raw:
        _monotone_add(points, b, o - th if mode == "output_minus_thoughts" else o)
    return points, {"source": "events", "points": len(raw), "bg_visible_mode": mode}


class TokMap:
    def __init__(self, points: list[list[float]]):
        self.b = [p[0] for p in points]; self.t = [p[1] for p in points]
        last_b, last_t = (self.b[-1], self.t[-1]) if points else (0, 0)
        self.ratio = (last_t / last_b) if last_b > 0 else 0.25    # tokens per byte; ~4 bytes/token default
        self.known_until = last_b

    def __call__(self, byte: int) -> tuple[int, bool]:
        """(token offset, estimated?) estimated = beyond the last logged point (extrapolated)."""
        if len(self.b) < 2:
            return int(round(byte * self.ratio)), True
        if byte >= self.b[-1]:
            return int(round(self.t[-1] + (byte - self.b[-1]) * self.ratio)), byte > self.b[-1]
        i = bisect.bisect_right(self.b, byte)
        b0, b1, t0, t1 = self.b[i - 1], self.b[i], self.t[i - 1], self.t[i]
        if b1 == b0:
            return int(t0), False
        return int(round(t0 + (t1 - t0) * (byte - b0) / (b1 - b0))), False


# ---------------------------------------------------------------- parsing
def strip_fences(text: str) -> tuple[str, int]:
    lines = text.split("\n")
    n = 0
    # leading fence
    i = 0
    while i < len(lines) and not lines[i].strip():
        i += 1
    if i < len(lines) and FENCE_RE.match(lines[i]):
        del lines[i]; n += 1
    j = len(lines) - 1
    while j >= 0 and not lines[j].strip():
        j -= 1
    if j >= 0 and FENCE_RE.match(lines[j]):
        del lines[j]; n += 1
    return "\n".join(lines), n


def parse_manifest(data: bytes) -> tuple[list[dict], dict]:
    info = {"found": False, "terminated": False, "bad_lines": 0, "start_byte": None, "end_byte": None}
    s = data.find(MAN_OPEN)
    if s < 0:
        return [], info
    info["found"] = True; info["start_byte"] = s
    body_start = s + len(MAN_OPEN)
    e = data.find(MAN_CLOSE, body_start)
    fstart = FILE_RE.search(data, body_start)
    if e >= 0 and (fstart is None or e < fstart.start()):
        info["terminated"] = True; body_end = e; info["end_byte"] = e + len(MAN_CLOSE)
    else:
        body_end = fstart.start() if fstart else len(data); info["end_byte"] = body_end
    entries = []
    for line in data[body_start:body_end].decode("utf-8", errors="replace").splitlines():
        line = line.strip().rstrip(",")
        if not line or line.startswith("```"):
            continue
        try:
            obj = json.loads(line)
            if isinstance(obj, dict) and obj.get("path"):
                entries.append(obj)
            elif isinstance(obj, list):
                entries.extend(o for o in obj if isinstance(o, dict) and o.get("path"))
        except json.JSONDecodeError:
            info["bad_lines"] += 1
    return entries, info


def parse_blocks(data: bytes) -> list[dict]:
    """Every FILE block: header byte, content span, terminated flag. Never raises."""
    heads = list(FILE_RE.finditer(data))
    blocks = []
    for k, m in enumerate(heads):
        path = m.group(1).decode("utf-8", errors="replace").strip()
        cstart = m.end()
        if data[cstart:cstart + 2] == b"\r\n":
            cstart += 2
        elif data[cstart:cstart + 1] == b"\n":
            cstart += 1
        nxt = heads[k + 1].start() if k + 1 < len(heads) else len(data)
        e = data.find(END_FILE, cstart, nxt)
        if e >= 0:
            terminated, cend, block_end = True, e, e + len(END_FILE)
            reason = None
        else:
            terminated, cend, block_end = False, nxt, nxt
            reason = "next_file_header" if k + 1 < len(heads) else "end_of_stream"
        blocks.append({"path": path, "start_byte": m.start(), "content_start": cstart, "content_end": cend,
                       "end_byte": block_end, "terminated": terminated, "unterminated_reason": reason})
    return blocks


def safe_rel(path: str) -> str | None:
    p = path.replace("\\", "/")
    while p.startswith("./"):
        p = p[2:]
    pp = pathlib.PurePosixPath(p)
    if pp.is_absolute() or ".." in pp.parts or not pp.parts:
        return None
    return str(pp)


def split(stream: pathlib.Path, log: pathlib.Path | None, out: pathlib.Path,
          hops: pathlib.Path | None = None) -> dict:
    data = stream.read_bytes() if stream.exists() else b""
    out.mkdir(parents=True, exist_ok=True)
    warnings = []

    # token map
    log_rows = _read_jsonl(log) if log else []
    kind = detect_log_kind(log_rows) if log_rows else "none"
    if kind == "bg":
        points, tinfo = token_points_bg(log_rows, len(data))
    elif kind == "run" or (hops and hops.exists()):
        if hops is None and log is not None:
            hops = log.parent / "hops.jsonl"
        points, tinfo = token_points_run(log_rows, _read_jsonl(hops) if hops else [])
    else:
        points, tinfo = [[0, 0]], {"source": "none"}
        warnings.append("no usable log: token offsets estimated at 4 bytes/token")
    tinfo["kind"] = kind
    tm = TokMap(points)

    manifest, minfo = parse_manifest(data)
    if not minfo["found"]:
        warnings.append("no <<<MANIFEST>>> block found")
    elif not minfo["terminated"]:
        warnings.append("manifest block not terminated")
    with open(out / "manifest.jsonl", "w", encoding="utf-8") as f:
        for m in manifest:
            f.write(json.dumps(m) + "\n")

    blocks = parse_blocks(data)
    seen: dict[str, int] = {}
    offsets = []
    n_fences = 0
    for b in blocks:
        raw = data[b["content_start"]:b["content_end"]].decode("utf-8", errors="replace")
        text, nf = strip_fences(raw)
        n_fences += nf
        rel = safe_rel(b["path"])
        written_as = None
        if rel is None:
            warnings.append(f"unsafe path skipped: {b['path']!r}")
        else:
            written_as = rel + ".argon_reemitted" if rel in PROTECTED else rel
            try:
                dst = out / written_as
                dst.parent.mkdir(parents=True, exist_ok=True)
                if text and not text.endswith("\n"):
                    text += "\n"
                dst.write_text(text, encoding="utf-8")
            except OSError as e:
                warnings.append(f"write failed {rel}: {e}"); written_as = None
        st, st_est = tm(b["start_byte"]); et, et_est = tm(b["end_byte"])
        seen[b["path"]] = seen.get(b["path"], 0) + 1
        offsets.append({"path": b["path"], "start_byte": b["start_byte"], "end_byte": b["end_byte"],
                        "start_tok": st, "end_tok": et, "terminated": b["terminated"],
                        "unterminated_reason": b["unterminated_reason"], "fences_stripped": nf,
                        "occurrence": seen[b["path"]], "written_as": written_as,
                        "tok_estimated": bool(st_est or et_est), "lines": text.count("\n")})
    with open(out / "offsets.jsonl", "w", encoding="utf-8") as f:
        for o in offsets:
            f.write(json.dumps(o) + "\n")

    man_paths = [m["path"] for m in manifest]
    emitted = set(seen)
    dups = sorted(p for p, n in seen.items() if n > 1)
    unterminated = [o["path"] for o in offsets if not o["terminated"]]
    # text outside blocks (protocol rule 3), ignoring whitespace
    outside = 0; cur = minfo["end_byte"] or 0
    if minfo["start_byte"]:
        outside += len(data[:minfo["start_byte"]].strip())
    for b in blocks:
        outside += len(data[cur:b["start_byte"]].strip()) if b["start_byte"] > cur else 0
        cur = max(cur, b["end_byte"])
    outside += len(data[cur:].strip())
    total_tok, _ = tm(len(data))
    meta = {"stream": str(stream), "stream_bytes": len(data), "total_tok_est": total_tok,
            "token_map": {**tinfo, "known_until_byte": tm.known_until, "points_kept": len(points)},
            "manifest": {**minfo, "entries": len(manifest)},
            "blocks": len(blocks), "files_written": sum(1 for o in offsets if o["written_as"]),
            "unterminated": unterminated, "duplicates": dups, "fences_stripped": n_fences,
            "manifest_missing_emitted": [p for p in man_paths if p not in emitted],
            "emitted_not_in_manifest": sorted(p for p in emitted if p not in set(man_paths)),
            "manifest_done_pct": round(100 * len([p for p in man_paths if p in emitted]) / len(man_paths), 1)
            if man_paths else 0.0,
            "bytes_outside_blocks": outside, "warnings": warnings}
    (out / "split_meta.json").write_text(json.dumps(meta, indent=2) + "\n")
    return meta


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("stream"); ap.add_argument("--log"); ap.add_argument("--out", required=True)
    ap.add_argument("--hops", help="hops.jsonl (default: next to --log)")
    ap.add_argument("--quiet", action="store_true")
    a = ap.parse_args(argv)
    meta = split(pathlib.Path(a.stream), pathlib.Path(a.log) if a.log else None, pathlib.Path(a.out),
                 pathlib.Path(a.hops) if a.hops else None)
    if not a.quiet:
        print(f"{meta['stream_bytes']} bytes, ~{meta['total_tok_est']} visible tok "
              f"(map: {meta['token_map']['source']}, {meta['token_map']['points_kept']} pts) | "
              f"manifest {meta['manifest']['entries']} entries"
              f"{'' if meta['manifest']['terminated'] else ' (UNTERMINATED)'} | "
              f"{meta['blocks']} blocks, {meta['manifest_done_pct']}% of manifest emitted")
        if meta["unterminated"]:
            print("  unterminated:", ", ".join(meta["unterminated"]))
        if meta["duplicates"]:
            print("  DUPLICATE paths:", ", ".join(meta["duplicates"]))
        if meta["fences_stripped"]:
            print(f"  stripped {meta['fences_stripped']} ``` fence lines")
        if meta["bytes_outside_blocks"]:
            print(f"  {meta['bytes_outside_blocks']} non-whitespace bytes outside blocks")
        for w in meta["warnings"]:
            print("  warning:", w)
    return 0


if __name__ == "__main__":
    sys.exit(main())
