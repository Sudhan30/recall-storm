"""Narration with Gemini TTS, one WAV per segment, cached by text hash. Every call is logged to videos/usage.jsonl.

  set -a && source .env && set +a && .venv/bin/python videos/gen_tts.py backup_core [more videos]
Writes videos/assets/vo/<seg-hash>.wav (24 kHz mono) and videos/assets/vo/index.json {video: {seg: file}}.
Re-run after numbers.json changes: only segments whose filled text changed are re-synthesized.
"""
import hashlib, json, pathlib, sys, time, wave, concurrent.futures as cf
from google import genai
from google.genai import types

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from edl import VIDEOS, fill  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parent
VO = ROOT / "assets" / "vo"
MODEL = "gemini-3.8-flash-tts"
VOICE = "Charon"
STYLE = ""  # a style prefix roughly doubled durations with long pauses; plain text reads at a natural pace


def synth(client, text, out):
    t0 = time.time()
    r = client.models.generate_content(
        model=MODEL, contents=STYLE + text,
        config=types.GenerateContentConfig(
            response_modalities=["AUDIO"],
            speech_config=types.SpeechConfig(voice_config=types.VoiceConfig(
                prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name=VOICE)))))
    pcm = r.candidates[0].content.parts[0].inline_data.data
    with wave.open(str(out), "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(24000); w.writeframes(pcm)
    um = r.usage_metadata.model_dump() if r.usage_metadata else None
    with (ROOT / "usage.jsonl").open("a") as f:
        f.write(json.dumps({"ts": time.strftime("%H:%M:%S"), "api": "generate_content(audio)", "model": MODEL,
                            "voice": VOICE, "chars": len(text), "audio_secs": round(len(pcm) / 48000, 2),
                            "wall_secs": round(time.time() - t0, 1), "usage": um}, default=str) + "\n")
    return len(pcm) / 48000


def main():
    numbers = json.loads((ROOT / "numbers.json").read_text())
    VO.mkdir(parents=True, exist_ok=True)
    idx_p = VO / "index.json"
    idx = json.loads(idx_p.read_text()) if idx_p.exists() else {}
    client = genai.Client()
    jobs = []
    for vid in sys.argv[1:] or list(VIDEOS):
        idx[vid] = {}
        for seg in VIDEOS[vid]:
            if not seg.get("say"):
                continue
            text, missing = fill(seg["say"], numbers)
            if missing:
                print(vid, seg["id"], "pending", missing); continue
            h = hashlib.sha1(f"{MODEL}|{VOICE}|{STYLE}|{text}".encode()).hexdigest()[:12]
            out = VO / f"{seg['id']}_{h}.wav"
            idx[vid][seg["id"]] = {"file": out.name, "text": text}
            if not out.exists() and all(o != out for _, o in jobs):
                jobs.append((text, out))
    with cf.ThreadPoolExecutor(max_workers=4) as ex:
        for (text, out), secs in zip(jobs, ex.map(lambda j: synth(client, *j), jobs)):
            print(f"{out.name}: {secs:.1f}s  {text[:60]}")
    idx_p.write_text(json.dumps(idx, indent=1))


if __name__ == "__main__":
    main()
