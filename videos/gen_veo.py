"""Generate the AI-generated illustration shots. Every call is logged to videos/usage.jsonl.

Veo 3.1 (veo-3.1-*-generate-preview) returns 404 "no longer available" on this key and points to
gemini-omni-1.1-flash via the Interactions API, so that is what this uses.

Usage (from repo root):
  set -a && source .env && set +a && .venv/bin/python videos/gen_veo.py [shot_id ...]
Outputs land in videos/raw/veo/<shot_id>.mp4 (gitignored). Existing outputs are skipped.
"""
import base64, json, sys, time, pathlib, concurrent.futures as cf
from google import genai

ROOT = pathlib.Path(__file__).resolve().parent
OUT = ROOT / "raw" / "veo"
USAGE = ROOT / "usage.jsonl"
MODEL = "gemini-omni-1.1-flash"

STYLE = ("Photorealistic, cinematic, shallow depth of field, cool teal night tones with warm practical lights. "
         "Completely generic and unbranded: no logos, no brand names, no readable signage, no readable text "
         "anywhere, blank signs and plain packaging. People are anonymous generic workers seen from behind "
         "or at a distance, no recognizable faces. No on-screen text, no subtitles. No dialogue.")

SHOTS = {
    "store_night": "Slow aerial drone push-in toward a huge generic big-box retail store at night in California, "
                   "palm trees, mostly empty parking lot, glowing entrance, plain blank facade with no sign.",
    "aisle_pull": "Inside a generic big-box grocery aisle after closing, two associates in plain navy vests "
                  "remove brightly colored red candy and snack boxes from a shelf into gray plastic totes, "
                  "smooth tracking shot down the aisle, plain unbranded packaging.",
    "dc_trucks": "Wide dawn shot of a generic regional distribution center, a row of plain white semi trailers "
                 "backed into loading dock doors, a forklift moving pallets, light fog, slow lateral dolly.",
    "dc_interior": "Interior of a vast generic warehouse distribution center at night, tall pallet racks, "
                   "a forklift carrying a pallet of plain cardboard cases down a lit aisle, slow crane shot.",
    "scanner_shelf": "Close-up of a gloved hand holding a generic handheld barcode scanner to a plain shelf "
                     "of unbranded red-colored candy packages, a small red light blinks, screen out of focus.",
    "highway_trucks": "Aerial dusk shot of plain white box trucks driving on a California freeway toward a city, "
                      "golden hour, long shadows, slow forward drone motion.",
}


def log(rec):
    with USAGE.open("a") as f:
        f.write(json.dumps(rec, default=str) + "\n")


def gen(client, sid, prompt):
    out = OUT / f"{sid}.mp4"
    if out.exists():
        return sid, "exists"
    t0 = time.time()
    it = client.interactions.create(
        model=MODEL, input=prompt + " " + STYLE, response_modalities=["video"],
        response_format={"type": "video", "aspect_ratio": "16:9", "resolution": "1080p", "duration": "8s",
                         "delivery": "inline"},
        background=True)
    while it.status not in ("completed", "failed", "cancelled", "incomplete"):
        time.sleep(10)
        it = client.interactions.get(it.id)
    secs = round(time.time() - t0, 1)
    usage = it.usage.model_dump() if getattr(it, "usage", None) else None
    v = getattr(it, "output_video", None)
    ok = bool(v and (v.data or v.uri))
    if ok and v.data:
        data = v.data
        out.write_bytes(base64.b64decode(data) if isinstance(data, str) else data)
    elif ok and v.uri:
        import urllib.request, os
        req = urllib.request.Request(v.uri, headers={"x-goog-api-key": os.environ["GEMINI_API_KEY"]})
        out.write_bytes(urllib.request.urlopen(req).read())
    log({"ts": time.strftime("%H:%M:%S"), "api": "interactions.create(video)", "model": MODEL, "shot": sid,
         "ok": ok, "status": it.status, "wall_secs": secs, "video_secs": 8 if ok else 0, "usage": usage})
    return sid, ("ok" if ok else f"FAILED status={it.status}")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    client = genai.Client()
    ids = sys.argv[1:] or list(SHOTS)
    with cf.ThreadPoolExecutor(max_workers=6) as ex:
        futs = {ex.submit(gen, client, s, SHOTS[s]): s for s in ids}
        for f in cf.as_completed(futs):
            try:
                print(*f.result(), flush=True)
            except Exception as e:
                print("ERR", futs[f], e, flush=True)
                log({"ts": time.strftime("%H:%M:%S"), "api": "interactions.create(video)", "model": MODEL,
                     "shot": futs[f], "ok": False, "error": str(e)[:400], "video_secs": 0})


if __name__ == "__main__":
    main()
