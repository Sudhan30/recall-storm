"""Usage: python tools/argon_run.py NAME PROMPT_FILE MAX_OUT [--no-stream] [--level medium] [--max-hops N]"""
import json, sys, time, pathlib
from google import genai
from google.genai import types

name, prompt_file, max_out = sys.argv[1], sys.argv[2], int(sys.argv[3])
stream = "--no-stream" not in sys.argv
max_hops = int(sys.argv[sys.argv.index("--max-hops") + 1]) if "--max-hops" in sys.argv else 10**6
level = sys.argv[sys.argv.index("--level") + 1] if "--level" in sys.argv else "medium"
run = pathlib.Path("runs") / name; run.mkdir(parents=True, exist_ok=True)
prompt = pathlib.Path(prompt_file).read_text()
client = genai.Client(http_options=types.HttpOptions(timeout=1_200_000))

out = open(run / "stream.txt", "a", encoding="utf-8")
log = open(run / "stream_log.jsonl", "a")
hops = open(run / "hops.jsonl", "a")
t0, hop, token, retries = time.time(), 0, None, 0
vis_done = 0                                   # visible tokens from finished hops

def cfg(tok):
    return types.GenerateContentConfig(
        max_output_tokens=max_out, automatic_continuation=False, continuation_token=tok,
        thinking_config=types.ThinkingConfig(thinking_level=level))

while True:
    h0, last, chars = time.time(), None, 0
    hop_start_byte, hop_start_token, got_ck = out.tell(), token, False
    try:
        if stream:
            for ch in client.models.generate_content_stream(model="gemini-4-argon", contents=prompt, config=cfg(token)):
                txt = ch.text or ""
                out.write(txt); out.flush(); chars += len(txt); last = ch
                u = ch.usage_metadata
                ck = ch.candidates[0].continuation_token if ch.candidates else None   # checkpoints every 5K after 32K
                log.write(json.dumps({"hop": hop, "t": round(time.time() - t0, 1), "chars": len(txt),
                    "out_bytes": out.tell(), "visible_hop": u.candidates_token_count if u else None,
                    "thinking_hop": u.thoughts_token_count if u else None, "checkpoint": bool(ck)}) + "\n"); log.flush()
                if ck:
                    (run / "last_checkpoint.bin").write_bytes(ck); got_ck = True
                    (run / "last_checkpoint_bytes.txt").write_text(str(out.tell()))
        else:
            last = client.models.generate_content(model="gemini-4-argon", contents=prompt, config=cfg(token))
            txt = last.text or ""; out.write(txt); out.flush(); chars = len(txt)
    except Exception as e:                      # dropped stream: resume from the last checkpoint, never duplicate text
        hops.write(json.dumps({"hop": hop, "error": repr(e)[:300], "t": round(time.time() - t0, 1)}) + "\n"); hops.flush()
        retries += 1
        if retries > 8: print("giving up after 8 errors", flush=True); sys.exit(1)
        if got_ck:                              # resume from this hop's last checkpoint
            token = (run / "last_checkpoint.bin").read_bytes(); cut = int((run / "last_checkpoint_bytes.txt").read_text())
        else:                                   # no checkpoint this hop: drop partial text, redo the hop
            token, cut = hop_start_token, hop_start_byte
        out.truncate(cut); out.seek(cut)
        hops.write(json.dumps({"hop": hop, "resume": "checkpoint" if got_ck else "hop_start", "cut": cut}) + "\n"); hops.flush()
        time.sleep(5 * retries); continue
    retries = 0
    c = last.candidates[0]; u = last.usage_metadata
    vis_done += (u.candidates_token_count or 0) if u else 0
    token = c.continuation_token
    rec = {"hop": hop, "finish": c.finish_reason.name if c.finish_reason else None, "has_token": bool(token),
           "secs": round(time.time() - h0, 1), "t": round(time.time() - t0, 1),
           "visible_hop": u.candidates_token_count, "thinking_hop": u.thoughts_token_count,
           "prompt_hop": u.prompt_token_count, "visible_total": vis_done, "chars_hop": chars,
           "seam_byte": out.tell()}
    hops.write(json.dumps(rec) + "\n"); hops.flush(); print(rec, flush=True)
    if rec["finish"] != "CONTINUATION" or not token:
        break
    if hop + 1 >= max_hops:
        (run / "resume_token.bin").write_bytes(token); print("stopping at --max-hops", flush=True)
        break
    hop += 1
