"""Edit decision lists: narration segments and the shots under them, per video.

Narration text uses {key} placeholders filled from videos/numbers.json (fmt below). A segment whose text
needs a pending number (expansion_v2) is not spoken; build.py shows a "[v2 numbers pending]" card instead.

Shot kinds:
  ai     videos/raw/veo/<src>.mp4            AI-generated illustration (labelled on screen)
  cap    videos/raw/cap/<src>.mp4            real viewer capture (motion)
  still  videos/raw/cap/<src>.png            real viewer capture (still, slow push-in)
  cards  three evidence cards side by side   real viewer capture
  term   videos/assets/term/<src>.txt        real terminal output, typed on screen
  title  text card                           (ours)
A shot's "w" is its share of the segment's narration time. "speed" plays a capture faster.
"""

# fmt: off
BACKUP_CORE = [
    {"id": "h1", "say": "On January 1st, 2027, California bans Red No. 3 in food, with no sell-through period.",
     "shots": [{"kind": "ai", "src": "store_night", "w": 1}]},
    {"id": "h2", "say": "This is a simulated compliance drill on {core_patched.stores} California Walmart and Sam's Club "
                        "locations, where the dye hides under names like erythrosine and E127.",
     "shots": [{"kind": "ai", "src": "aisle_pull", "w": 0.6}, {"kind": "ai", "src": "scanner_shelf", "w": 0.4}]},
    {"id": "h3", "say": "You'll see a working system that Gemini 4 Argon wrote this morning, in one generation.",
     "shots": [{"kind": "ai", "src": "dc_trucks", "w": 1}]},
    {"id": "c1", "say": "Here's the drill. We run the core on all {core_patched.stores} stores: {core_patched.shelf_tasks} shelf "
                        "tasks, replayed overnight against the midnight deadline. Each dot turns green when its store is done.",
     "shots": [{"kind": "term", "src": "run_core_patched", "w": 0.22},
               {"kind": "cap", "src": "map_replay", "w": 0.78, "a": 0.5, "b": 12.5}]},
    {"id": "c2", "say": "Click a Supercenter and you're inside it. Flashing tags are pulls still pending. Associates walk "
                        "to each facing, pull the product, and place a substitute.",
     "shots": [{"kind": "cap", "src": "store3d", "w": 0.62, "a": 0, "b": 11.5, "crop": [0, 250, 1476, 830]},
               {"kind": "cap", "src": "store3d", "w": 0.38, "a": 12.5, "b": 17}]},
    {"id": "c3", "say": "Every verdict carries its evidence. Erythrosine: caught and pulled. A vague \"artificial color\": "
                        "held to verify. A Red 40 decoy: kept on the shelf.",
     "shots": [{"kind": "cards", "src": "card", "w": 1}]},
    {"id": "c4", "say": "Then the verifier. Argon's unedited core: {core.hard_errors} hard errors, and recall {core.recall}. "
                        "It missed {core.fn} products spelled like \"F D and C\" with spaces, or Spanish \"rojo\".",
     "shots": [{"kind": "term", "src": "vp_core", "w": 1}]},
    {"id": "c5", "say": "After {patches.core_count} small logged patches: {core_patched.hard_errors} "
                        "hard errors, recall {core_patched.recall}, precision {core_patched.precision}, and "
                        "{core_patched.decoys_pulled} of {core_patched.decoys} decoys pulled.",
     "shots": [{"kind": "term", "src": "vp_core_patched", "w": 0.55}, {"kind": "panel", "srcs": ["vcard4", "vcard3"], "w": 0.45, "colw": 760, "stagger": False,
                "heads": ["Argon core, unedited", "core + 3 logged patches"], "colors": ["red", "green"]}]},
    {"id": "c6", "say": "Stores, stock and staffing are simulated. Every number came from the verifier.",
     "shots": [{"kind": "title", "src": "end_core", "w": 1}]},
]
# fmt: on

VIDEOS = {"backup_core": BACKUP_CORE}


def fmt(v):
    if isinstance(v, bool):
        return str(v)
    if isinstance(v, int):
        return f"{v:,}" if v >= 10000 else str(v)
    if isinstance(v, float):
        return f"{v:.1f}" if v == round(v, 1) and v >= 1 else f"{v}"
    return str(v)


def fill(text, numbers):
    """Return (filled_text, missing_keys)."""
    import re
    missing = []

    def rep(m):
        e = numbers.get(m.group(1))
        if e is None or e.get("value") is None:
            missing.append(m.group(1)); return "[pending]"
        return fmt(e["value"])
    return re.sub(r"\{([a-zA-Z0-9_.]+)\}", rep, text), missing
