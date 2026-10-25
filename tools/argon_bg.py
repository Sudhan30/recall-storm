"""Usage: python tools/argon_bg.py NAME PROMPT_FILE MAX_OUT"""
import json, sys, time, pathlib
from google import genai

name, prompt_file, max_out = sys.argv[1], sys.argv[2], int(sys.argv[3])
run = pathlib.Path("runs") / name; run.mkdir(parents=True, exist_ok=True)
client = genai.Client()
out = open(run / "stream.txt", "a", encoding="utf-8"); ev = open(run / "events.jsonl", "a")
t0, last_id, iid = time.time(), None, None
idfile = run / "interaction_id.txt"

def handle(e):
    global last_id, iid
    et = getattr(e, "event_type", None); last_id = getattr(e, "event_id", None) or last_id
    rec = {"t": round(time.time() - t0, 1), "type": et, "event_id": last_id}
    if et == "interaction.created":
        iid = e.interaction.id; idfile.write_text(iid); rec["id"] = iid
    elif et == "step.delta" and getattr(e.delta, "type", None) == "text":
        out.write(e.delta.text); out.flush(); rec["chars"] = len(e.delta.text); rec["out_bytes"] = out.tell()
    elif et == "interaction.status_update":
        rec.update(status=e.status, has_token=bool(e.continuation_token),
                   usage=e.usage.model_dump() if e.usage else None, seam_byte=out.tell())
    elif et in ("interaction.completed", "error"):
        rec["detail"] = str(e)[:500]
    ev.write(json.dumps(rec, default=str) + "\n"); ev.flush()
    return et

stream = client.interactions.create(
    model="gemini-4-argon", input=pathlib.Path(prompt_file).read_text(),
    background=True, stream=True,
    generation_config={"max_output_tokens": max_out, "thinking_level": "medium"})
done = False
while not done:
    try:
        for e in stream:
            if handle(e) in ("interaction.completed", "error"): done = True; break
        else:
            done = True
    except Exception as err:                    # laptop or Wi-Fi drop: reconnect after the last event
        ev.write(json.dumps({"t": round(time.time() - t0, 1), "reconnect": repr(err)[:200]}) + "\n"); ev.flush()
        time.sleep(5)
        stream = client.interactions.get(iid or idfile.read_text(), stream=True, last_event_id=last_id)
final = client.interactions.get(iid or idfile.read_text())
(run / "final.json").write_text(final.model_dump_json(indent=2))
print(final.status, final.usage)
