"""Render the videos from assets. Needs Python 3 with Pillow + numpy, and ffmpeg.

  python videos/build.py backup_core            # -> videos/backup_core.mp4
  python videos/build.py --all

Inputs (see videos/README.md): videos/edl.py (shots + narration), videos/numbers.json (make_numbers.py),
videos/assets/vo/index.json + WAVs (gen_tts.py), videos/raw/veo/*.mp4 (gen_veo.py),
videos/raw/cap/* (capture_viewer.py), videos/assets/term/*.txt (real terminal output).
Swap in new numbers: python3 videos/make_numbers.py && gen_tts.py <video> && build.py <video>.
"""
import json, math, pathlib, re, subprocess, sys, textwrap, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from edl import VIDEOS, fill  # noqa: E402

FF = "/opt/homebrew/bin/ffmpeg"
FP = "/opt/homebrew/bin/ffprobe"
W, H, FPS, SR = 1920, 1080, 30, 24000
LEAD, TAIL = 0.15, 0.30                     # silence before / after each narration segment
RAW, ASSETS = HERE / "raw", HERE / "assets"
BG = (11, 14, 19)
COL = {"red": (255, 77, 94), "amber": (245, 166, 35), "green": (61, 220, 132), "blue": (77, 163, 255),
       "text": (232, 237, 245), "dim": (141, 152, 171), "panel": (20, 25, 34), "panel2": (27, 34, 48),
       "magenta": (255, 43, 214)}
SF, MONO = "/System/Library/Fonts/SFNS.ttf", "/System/Library/Fonts/SFNSMono.ttf"


def font(size, weight="Regular", mono=False):
    f = ImageFont.truetype(MONO if mono else SF, size)
    try:
        f.set_variation_by_name(weight)
    except Exception:
        pass
    return f


def run(cmd, **kw):
    r = subprocess.run(cmd, capture_output=True, text=True, **kw)
    if r.returncode:
        sys.exit(f"ffmpeg failed: {' '.join(map(str, cmd))[:400]}\n{r.stderr[-2000:]}")
    return r


def probe_dur(p):
    return float(run([FP, "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(p)]).stdout)


# ---------------------------------------------------------------- PIL pieces
def rounded(draw, box, r, fill, outline=None, width=1):
    draw.rounded_rectangle(box, r, fill=fill, outline=outline, width=width)


def badge_png(text, kind, out):
    f = font(26, "Bold")
    tw = f.getbbox(text)[2]
    img = Image.new("RGBA", (tw + 44, 50), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    if kind == "ai":
        rounded(d, (0, 0, tw + 43, 49), 10, (0, 0, 0, 185), outline=COL["magenta"] + (255,), width=3)
        d.text((22, 9), text, font=f, fill=COL["magenta"] + (255,))
    else:
        rounded(d, (0, 0, tw + 43, 49), 10, (10, 40, 24, 225), outline=(31, 107, 64, 255), width=2)
        d.text((22, 9), text, font=f, fill=COL["green"] + (255,))
    img.save(out)
    return img.size


def caption_png(text, out):
    f = font(42, "Medium")
    lines = textwrap.wrap(text, 58)
    lh = 54
    widths = [f.getbbox(l)[2] for l in lines]
    w, h = max(widths) + 56, lh * len(lines) + 26
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    rounded(d, (0, 0, w - 1, h - 1), 14, (0, 0, 0, 175))
    for i, l in enumerate(lines):
        d.text(((w - widths[i]) // 2, 11 + i * lh), l, font=f, fill=(255, 255, 255, 255))
    img.save(out)
    return img.size


def chunk_caption(text, maxc=100):
    parts = re.split(r"(?<=[.!?])\s+", text.strip())
    out = []
    for p in parts:
        while len(p) > maxc:
            cut = p.rfind(", ", 0, maxc)
            cut = cut + 1 if cut > 30 else p.rfind(" ", 0, maxc)
            out.append(p[:cut].strip()); p = p[cut:].strip()
        if p:
            if out and len(out[-1]) + len(p) < 56:
                out[-1] += " " + p
            else:
                out.append(p)
    return out


def title_img(lines, sub=None):
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    for y in range(H):                                  # soft vertical vignette
        a = int(10 * (1 - abs(y - H / 2) / (H / 2)))
        d.line([(0, y), (W, y)], fill=(BG[0] + a, BG[1] + a, BG[2] + a + 4))
    y = H // 2 - 60 * len(lines)
    for text, size, weight, color in lines:
        f = font(size, weight)
        tw = f.getbbox(text)[2]
        d.text(((W - tw) // 2, y), text, font=f, fill=color)
        y += int(size * 1.35)
    if sub:
        f = font(30)
        tw = f.getbbox(sub)[2]
        d.text(((W - tw) // 2, y + 20), sub, font=f, fill=COL["dim"])
    return img


TITLES = {
    "end_core": lambda: title_img([("Recall Storm", 96, "Heavy", COL["text"]),
                                   ("Simulated compliance drill · measured numbers", 44, "Medium", COL["amber"])],
                                  "Stores, stock and staffing are simulated. Every number came from the verifier."),
}


CARD_HEADS = (["erythrosine caught", "“artificial color” held", "Red 40 decoy kept"], ["red", "amber", "green"])


def cards_frame(paths, shown, alpha, heads=None, colors=None, colw=None):
    img = Image.new("RGB", (W, H), BG)
    k = len(paths)
    gap, top = 30, 112
    colw = colw or min(600, (W - 120 - (k - 1) * gap) // k)
    x0 = (W - k * colw - (k - 1) * gap) // 2
    heads = heads or CARD_HEADS[0]
    hc = [COL[c] for c in (colors or CARD_HEADS[1])]
    d = ImageDraw.Draw(img)
    for i, p in enumerate(paths[:shown]):
        c = Image.open(p).convert("RGB")
        s = colw / c.width
        c = c.resize((colw, int(c.height * s)), Image.LANCZOS)
        maxh = H - top - 230
        if c.height > maxh:                             # long ingredient lists: crop and fade out
            c = c.crop((0, 0, colw, maxh))
            fade = Image.linear_gradient("L").resize((colw, 120))
            c.paste(Image.new("RGB", (colw, 120), BG), (0, maxh - 120), fade)
        a = alpha if i == shown - 1 else 1.0
        x = x0 + i * (colw + gap)
        if a < 1:
            base = img.crop((x, top + 50, x + colw, top + 50 + c.height))
            c = Image.blend(base, c, a)
        img.paste(c, (x, top + 50))
        f = font(30, "Bold")
        d.text((x, top), heads[i].upper(), font=f, fill=hc[i])
    return img


def term_lines(src):
    return (ASSETS / "term" / f"{src}.txt").read_text().rstrip("\n").split("\n")


def term_frame(lines, typed_line, typed_chars, shown):
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    X0, Y0, X1, Y1 = 70, 90, W - 70, 905
    rounded(d, (X0, Y0, X1, Y1), 18, (13, 17, 23), outline=(42, 51, 68), width=2)
    d.rounded_rectangle((X0, Y0, X1, Y0 + 46), 18, fill=COL["panel2"])
    d.rectangle((X0, Y0 + 30, X1, Y0 + 46), fill=COL["panel2"])
    for i, c in enumerate([(255, 95, 86), (255, 189, 46), (39, 201, 63)]):
        d.ellipse((X0 + 20 + i * 28, Y0 + 15, X0 + 36 + i * 28, Y0 + 31), fill=c)
    ft = font(22, "Medium")
    t = "zsh — recall-storm (repo root)"
    d.text(((W - ft.getbbox(t)[2]) // 2, Y0 + 11), t, font=ft, fill=COL["dim"])
    fm, fb = font(25, "Regular", mono=True), font(25, "Bold", mono=True)
    cw = fm.getbbox("M")[2]
    maxc = int((X1 - X0 - 60) / cw)
    rows = []
    for i in range(shown + 1):
        if i >= len(lines):
            break
        l = lines[i]
        if i == typed_line:
            l = l[:typed_chars]
        elif i > typed_line and typed_line >= 0:
            break
        is_cmd = lines[i].startswith("$ ")
        wrapped = textwrap.wrap(l, maxc, subsequent_indent="    ", drop_whitespace=False) or [""]
        for j, wl in enumerate(wrapped):
            rows.append((wl, is_cmd, j == 0, lines[i]))
    lh = 37
    maxrows = int((Y1 - Y0 - 80) / lh)
    rows = rows[-maxrows:]
    y = Y0 + 66
    for wl, is_cmd, first, full in rows:
        x = X0 + 30
        if is_cmd and first and wl.startswith("$"):
            d.text((x, y), "$", font=fb, fill=COL["green"]); d.text((x + 2 * cw, y), wl[2:], font=fb, fill=COL["text"])
        elif is_cmd:
            d.text((x, y), wl, font=fb, fill=COL["text"])
        else:
            col = (201, 209, 217)
            m = re.search(r"HARD ERRORS: (\d+)", full)
            if m:
                col = COL["green"] if m.group(1) == "0" else COL["red"]
            elif "precision" in full and "recall" in full:
                col = COL["amber"]
            elif "FIXED" in full or " passed" in full:
                col = COL["green"] if "failed" not in full else COL["amber"]
            d.text((x, y), wl, font=fm, fill=col)
        y += lh
    if typed_line >= 0 and rows:                          # cursor
        last = rows[-1][0]
        d.rectangle((X0 + 30 + len(last) * cw + 4, y - lh + 4, X0 + 30 + len(last) * cw + 4 + cw, y - 6), fill=COL["text"])
    return img


def term_schedule(lines, d):
    """Return list of (t, typed_line, typed_chars, shown) states, scaled to fit duration d."""
    ev, t = [], 0.3
    for i, l in enumerate(lines):
        if l.startswith("$ "):
            n = len(l)
            for k in range(0, n + 1, 3):
                ev.append((t, i, k, i)); t += 3 / 95
            ev.append((t, i, n, i)); t += 0.35
        else:
            ev.append((t, -1, 0, i)); t += 0.07
    scale = min(1.0, (d * 0.8) / max(t, 0.01))
    return [(e[0] * scale,) + e[1:] for e in ev]


# ---------------------------------------------------------------- shot rendering
def pipe_frames(out, n, frame_at):
    p = subprocess.Popen([FF, "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
                          "-i", "-", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "16", "-preset", "fast", str(out)],
                         stdin=subprocess.PIPE)
    last_key, last_bytes = None, None
    for i in range(n):
        key, make = frame_at(i)
        if key != last_key:
            last_bytes = make().convert("RGB").tobytes(); last_key = key
        p.stdin.write(last_bytes)
    p.stdin.close(); p.wait()


def still_clip(img_path, out, n, zoom=0.045):
    vf = (f"scale={W * 2}:{H * 2}:force_original_aspect_ratio=decrease,pad={W * 2}:{H * 2}:(ow-iw)/2:(oh-ih)/2:color=0x0b0e13,"
          f"zoompan=z='1+{zoom}*in/{n}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s={W}x{H}:fps={FPS},format=yuv420p")
    run([FF, "-v", "error", "-y", "-loop", "1", "-framerate", str(FPS), "-i", str(img_path), "-vf", vf, "-frames:v", str(n),
         "-c:v", "libx264", "-crf", "16", "-preset", "fast", str(out)])


def video_clip(src, out, n, a=0.0, b=None, speed=None, crop=None):
    d = n / FPS
    dur = probe_dur(src)
    if speed:
        b = min(dur, a + speed * d)
    b = min(dur, b if b is not None else dur)
    span = max(0.1, b - a)
    factor = d / span if (speed or span > d) else 1.0        # stretch/compress the span to the slot
    if not speed and span < d:
        factor = d / span                                     # AI clips shorter than the slot: slow down gently
    cr = f"crop={crop[2]}:{crop[3]}:{crop[0]}:{crop[1]}," if crop else ""
    vf = (f"trim=start={a}:end={b},setpts=(PTS-STARTPTS)*{factor:.5f},{cr}scale={W}:{H}:force_original_aspect_ratio=increase,"
          f"crop={W}:{H},fps={FPS},tpad=stop_mode=clone:stop_duration={d:.3f},format=yuv420p")
    run([FF, "-v", "error", "-y", "-i", str(src), "-an", "-vf", vf, "-frames:v", str(n), "-c:v", "libx264", "-crf", "16",
         "-preset", "fast", str(out)])


LABELS = {"ai": "AI-generated illustration", "cap": "REAL CAPTURE · project viewer",
          "still": "REAL CAPTURE · project viewer", "cards": "REAL CAPTURE · viewer evidence cards",
          "panel": "REAL CAPTURE · project viewer",
          "term": "REAL CAPTURE · terminal output", "pending": "PLACEHOLDER"}


def render_shot(shot, out, n):
    k, src = shot["kind"], shot.get("src") or "+".join(shot.get("srcs", []))
    if k == "ai":
        video_clip(RAW / "veo" / f"{src}.mp4", out, n, a=shot.get("a", 0.0), b=shot.get("b"))
    elif k == "cap":
        video_clip(RAW / "cap" / f"{src}.mp4", out, n, a=shot.get("a", 0.0), b=shot.get("b"), speed=shot.get("speed"),
                   crop=shot.get("crop"))
    elif k == "still":
        still_clip(RAW / "cap" / f"{src}.png", out, n, zoom=shot.get("zoom", 0.045))
    elif k == "title":
        p = RAW / "build" / f"title_{src}.png"
        TITLES[src]().save(p); still_clip(p, out, n, zoom=0.02)
    elif k == "pending":
        p = RAW / "build" / f"pending_{abs(hash(shot['text'])) % 10**8}.png"
        title_img([("[v2 numbers pending]", 84, "Heavy", COL["amber"]), (shot["text"], 40, "Medium", COL["text"])],
                  "Placeholder: filled from runs/expansion_v2/ when that run finishes").save(p)
        still_clip(p, out, n, zoom=0.01)
    elif k in ("cards", "panel"):
        if k == "cards":
            paths, heads, colors, colw = [RAW / "cap" / f"{src}{i}.png" for i in (1, 2, 3)], None, None, None
        else:
            paths = [RAW / "cap" / f"{p}.png" for p in shot["srcs"]]
            heads, colors, colw = shot["heads"], shot["colors"], shot.get("colw")
        m = len(paths)
        step = n / m if shot.get("stagger", True) else 1

        def at(i):
            shown = min(m, 1 + int(i // step)); fa = min(1.0, (i - (shown - 1) * step) / 9)
            fa = round(fa, 2)
            return (shown, fa), (lambda: cards_frame(paths, shown, fa, heads, colors, colw))
        pipe_frames(out, n, at)
    elif k == "term":
        lines = term_lines(src)
        sched = term_schedule(lines, n / FPS)

        def at(i):
            t = i / FPS
            st = sched[0][1:]
            for e in sched:
                if e[0] <= t:
                    st = e[1:]
                else:
                    break
            if t > sched[-1][0]:
                st = (-1, 0, len(lines) - 1)
            return st, (lambda: term_frame(lines, *st))
        pipe_frames(out, n, at)
    else:
        raise ValueError(k)


# ---------------------------------------------------------------- assembly
def build(video):
    edl = VIDEOS[video]
    numbers = json.loads((HERE / "numbers.json").read_text())
    vo = json.loads((ASSETS / "vo" / "index.json").read_text()).get(video, {})
    bdir = RAW / "build" / video
    bdir.mkdir(parents=True, exist_ok=True)
    segs, t = [], 0.0
    for seg in edl:
        text, missing = fill(seg.get("say", ""), numbers) if seg.get("say") else ("", [])
        if missing or (seg.get("say") and seg["id"] not in vo):
            shots = [{"kind": "pending", "src": "pending", "w": 1, "text": seg.get("pending_text", "expansion v2 numbers")}]
            segs.append({"id": seg["id"], "t0": t, "dur": seg.get("pending_secs", 4.0), "audio": None, "text": "",
                         "caption": "[v2 numbers pending]", "shots": shots, "pending": missing})
        else:
            wav = ASSETS / "vo" / vo[seg["id"]]["file"] if seg.get("say") else None
            alen = 0.0
            if wav:
                with wave.open(str(wav)) as w:
                    alen = w.getnframes() / w.getframerate()
            dur = max(seg.get("min", 0), alen + LEAD + TAIL) if wav else seg.get("secs", 3.0)
            segs.append({"id": seg["id"], "t0": t, "dur": dur, "audio": wav, "alen": alen, "text": text,
                         "caption": text, "shots": seg["shots"]})
        t += segs[-1]["dur"]
    total = t

    # shots -> clips (frame-exact)
    clips, shotlog, frame_t = [], [], 0
    for s in segs:
        nseg = round((s["t0"] + s["dur"]) * FPS) - round(s["t0"] * FPS)
        ws = [sh.get("w", 1) for sh in s["shots"]]
        alloc = [round(nseg * w / sum(ws)) for w in ws]
        alloc[-1] = nseg - sum(alloc[:-1])
        for j, (sh, n) in enumerate(zip(s["shots"], alloc)):
            out = bdir / f"{s['id']}_{j}.mp4"
            render_shot(sh, out, n)
            clips.append(out)
            shotlog.append({"t": round(frame_t / FPS, 2), "dur": round(n / FPS, 2), "seg": s["id"], "kind": sh["kind"],
                            "src": sh.get("src") or "+".join(sh.get("srcs", [])), "label": LABELS.get(sh["kind"])})
            frame_t += n
        print(f"  {s['id']}: {s['dur']:.1f}s, {len(s['shots'])} shot(s)", flush=True)
    lst = bdir / "concat.txt"
    lst.write_text("".join(f"file '{c}'\n" for c in clips))
    base = bdir / "base.mp4"
    run([FF, "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", str(base)])

    # narration track
    pcm = np.zeros(int(math.ceil(total * SR)) + SR, dtype=np.int16)
    for s in segs:
        if s["audio"]:
            with wave.open(str(s["audio"])) as w:
                a = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16)
            o = int((s["t0"] + LEAD) * SR)
            pcm[o:o + len(a)] = a[: len(pcm) - o]
    nar = bdir / "narration.wav"
    with wave.open(str(nar), "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm[: int(total * SR)].tobytes())

    # overlays: label badges per shot, captions per chunk
    ovs = []
    for i, sh in enumerate(shotlog):
        lab = sh["label"]
        if not lab:
            continue
        p = bdir / f"badge_{i}.png"
        bw, bh = badge_png(lab, "ai" if sh["kind"] == "ai" else "real", p)
        ovs.append((p, 36, 28 if sh["kind"] != "term" else 22, sh["t"], sh["t"] + sh["dur"]))
    for s in segs:
        chunks = chunk_caption(s["caption"]) if s["caption"] else []
        if not chunks:
            continue
        a0 = s["t0"] + (LEAD if s["audio"] else 0.2)
        span = s.get("alen") or (s["dur"] - 0.4)
        tot = sum(len(c) for c in chunks)
        tt = a0
        for j, c in enumerate(chunks):
            d = span * len(c) / tot
            p = bdir / f"cap_{s['id']}_{j}.png"
            cw, ch = caption_png(c, p)
            end = tt + d + (0.25 if j == len(chunks) - 1 else 0)
            ovs.append((p, (W - cw) // 2, H - ch - 34, tt, min(end, s["t0"] + s["dur"])))
            tt += d
    inputs, fc, last = [], [], "[0:v]"
    for k, (p, x, y, a, b) in enumerate(ovs):
        inputs += ["-loop", "1", "-framerate", str(FPS), "-t", f"{total:.3f}", "-i", str(p)]
        lab = f"[v{k}]"
        fc.append(f"{last}[{k + 2}:v]overlay={x}:{y}:enable='between(t,{a:.3f},{b:.3f})'{lab}")
        last = lab
    fc.append(f"{last}fade=t=in:st=0:d=0.6,fade=t=out:st={total - 0.8:.3f}:d=0.8,format=yuv420p[vout]")
    fc.append(f"[1:a]aresample=48000,afade=t=out:st={total - 0.8:.3f}:d=0.8[aout]")
    out = HERE / f"{video}.mp4"
    run([FF, "-v", "error", "-y", "-i", str(base), "-i", str(nar), *inputs, "-filter_complex", ";".join(fc),
         "-map", "[vout]", "-map", "[aout]", "-c:v", "libx264", "-crf", "19", "-preset", "medium", "-profile:v", "high",
         "-pix_fmt", "yuv420p", "-r", str(FPS), "-c:a", "aac", "-b:a", "192k", "-ac", "2", "-movflags", "+faststart",
         "-t", f"{total:.3f}", str(out)])
    meta = {"video": f"videos/{video}.mp4", "duration": round(total, 2), "shots": shotlog,
            "segments": [{"id": s["id"], "t": round(s["t0"], 2), "dur": round(s["dur"], 2), "say": s["text"],
                          "pending": s.get("pending")} for s in segs]}
    (HERE / f"{video}.shots.json").write_text(json.dumps(meta, indent=1))
    print(f"{out}  {total:.1f}s  {len(shotlog)} shots", flush=True)


if __name__ == "__main__":
    vids = list(VIDEOS) if "--all" in sys.argv else [a for a in sys.argv[1:] if not a.startswith("-")]
    for v in vids:
        build(v)
