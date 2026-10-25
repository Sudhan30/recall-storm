"""Edit decision lists: narration segments and the shots under them, per video.

Story spine (team lead, 12:40): the problem -> why it is hard for software -> why Argon (whole system in one
generation) -> consistent is not correct -> the fix loop + the working core -> why it matters.
Plain language only: no "precision", "recall", "hard errors"; no brand names (say "a large big-box retailer").

Narration text uses {key} placeholders filled from videos/numbers.json (fmt below). A segment whose text needs a
pending number (expansion_v2) or a missing asset is not spoken; build.py shows a "[v2 numbers pending]" card.
"beat" puts a short story title on screen at the start of the segment.

Shot kinds:
  ai     videos/raw/veo/<src>.mp4            AI-generated illustration (labelled on screen)
  cap    videos/raw/cap/<src>.mp4            real viewer capture (motion)
  still  videos/raw/cap/<src>.png            real viewer capture (still, slow push-in)
  cards  three evidence cards side by side   real viewer capture
  term   videos/assets/term/<src>.txt        real terminal output, typed on screen
  stats  big counters (ours, numbers from reports)
  bars   before -> after bars (ours, numbers from reports)
  title  text card (ours)
A shot's "w" is its share of the segment's narration time. crop = [x, y, w, h] on the 1920x1080 capture.
"""

MAP = {"kind": "cap", "src": "map_replay", "a": 0.5, "b": 12.5, "crop": [18, 276, 1422, 800]}      # map only, no store list
STORE = {"kind": "cap", "src": "store3d", "a": 0, "b": 11.5, "crop": [0, 318, 1355, 762]}         # 3D canvas, header cropped
STORE_WIDE = {"kind": "cap", "src": "store3d", "a": 12.5, "b": 17, "crop": [0, 318, 1355, 762]}

FOUND = {"kind": "stats", "items": [
    {"n": "core_patched.tp", "of": "core_patched.truth_pull", "label": "products with Red No. 3 found", "color": "green", "icon": "check"},
    {"n": "core_patched.decoys_pulled", "of": "core_patched.decoys", "label": "look-alikes like Red 40 pulled", "color": "green", "icon": "check"},
    {"n": "core_patched.pull_facings_tasked", "of": "core_patched.pull_facings", "label": "affected shelf spots with a pull task", "color": "green", "icon": "check"}]}
FOUND2 = {"kind": "stats", "items": [
    {"n": "core_patched.fp", "label": "extra item pulled, one our rules mark “check by hand”", "color": "amber"},
    {"n": "core_patched.hard_errors", "label": "plan mistakes: nobody double-booked, all done before midnight", "color": "green", "icon": "check"}]}
FIRST_DRAFT = {"kind": "bars", "title": "Argon's first draft → after 3 small logged fixes", "at": 0.45, "rows": [
    {"label": "Products with Red No. 3 missed", "before": "core.fn", "after": "core_patched.fn",
     "before_caption": "first draft: {core.fn} of {core.truth_pull} missed", "after_caption": "after the fixes (patches/LOG.md)"},
    {"label": "Shelf spots left with banned product", "before": "core.uncovered_facings", "after": "core_patched.uncovered_facings",
     "before_caption": "first draft", "after_caption": "after the fixes"}]}
MISTAKES = {"kind": "stats", "items": [
    {"n": "exp1plan.mistakes", "label": "plan mistakes found by the verifier", "color": "red"},
    {"n": "exp1plan.labor", "label": "of them: one associate booked in two places at once", "color": "red"}]}
FIXLOOP = {"kind": "bars", "title": "Managed agent: {agent.exp_root_causes} root causes fixed", "at": 0.3,
           "done": "0 mistakes, including {agent.exp_heldout_stores} stores the agent never saw", "rows": [
    {"label": "Plan mistakes", "before": "exp1plan.mistakes", "after": "exp1fixed.mistakes",
     "before_caption": "before (reports/expansion_plan.json)", "after_caption": "after (reports/expansion_agentpatched_plan.json)"}]}
END = {"kind": "title", "src": "end_full"}
PARTS = {"kind": "title", "src": "parts"}

# ---------------------------------------------------------------- beat 1: the problem (shared)
B1 = [
    {"id": "s1a", "beat": "One night to clear the shelves",
     "say": "On January 1st, 2027, California bans food with Red No. 3. There's no sell-through period.",
     "shots": [{"kind": "ai", "src": "store_night", "w": 1}]},
    {"id": "s1b", "say": "The dye hides under many names: erythrosine, E127, \"Red 3\", even scanning typos. It's in hundreds "
                         "of products, on thousands of shelf spots, and stores get one overnight shift to clear it.",
     "shots": [{"kind": "ai", "src": "scanner_shelf", "w": 0.5}, {"kind": "ai", "src": "aisle_pull", "w": 0.5}]},
    {"id": "s1c", "say": "Miss one, and it's a violation. Pull the wrong one, since Red 40 looks almost the same on a label, "
                         "and you empty shelves for nothing. Our simulated drill is for a large big-box retailer with nearly "
                         "300 California stores.",
     "shots": [{"kind": "cards", "src": "card", "w": 0.55}, {"kind": "ai", "src": "dc_trucks", "w": 0.45}]},
]

# ---------------------------------------------------------------- backup_core: beat 1 + the working core + close
BACKUP_CORE = B1 + [
    {"id": "k1b", "beat": "A working system, written this morning",
     "say": "Gemini 4 Argon wrote this working system this morning, in one generation. Here it runs on "
            "{core_patched.stores} of those stores, overnight.",
     "shots": [{**MAP, "w": 1}]},
    {"id": "k2", "say": "Inside a store, flashing tags are pulls still to do. Associates walk to each shelf, pull the product, "
                        "and put a substitute in its place.",
     "shots": [{**STORE, "w": 0.62}, {**STORE_WIDE, "w": 0.38}]},
    {"id": "k3b", "say": "Every decision shows its evidence: erythrosine found, a vague \"artificial color\" held for a person, "
                         "a Red 40 look-alike left on the shelf.",
     "shots": [{"kind": "cards", "src": "card", "w": 1}]},
    {"id": "k4b", "beat": "What the verifier found",
     "say": "It found all {core_patched.tp} products with Red No. 3, pulled {core_patched.decoys_pulled} of the "
            "{core_patched.decoys} look-alikes, and covered all {core_patched.pull_facings} shelf spots, with "
            "{core_patched.hard_errors} plan mistakes. {core_patched.fp} extra item was pulled, one our rules say to check by hand.",
     "shots": [{**FOUND, "w": 0.55}, {**FOUND2, "w": 0.25}, {"kind": "term", "src": "vp_core_patched", "w": 0.2}]},
    {"id": "k6b", "say": "Argon's first draft missed {core.fn} of the {core.truth_pull}, leaving {core.uncovered_facings} shelf "
                         "spots with banned product. Three small logged fixes closed the gap.",
     "shots": [{**FIRST_DRAFT, "w": 1}]},
    {"id": "z1b", "say": "Simulated drill, simulated operations, every number from the verifier.",
     "shots": [{**END, "w": 1}]},
]


# ---------------------------------------------------------------- full demo
def full(v):
    """v = 'exp1' (draft, numbers now) or 'exp2' (final cut, filled when expansion_v2 finishes)."""
    draft = v == "exp1"
    segs = list(B1) + [
        {"id": "s2", "beat": "Many parts that must agree",
         "say": "That's hard for software. A compliance pull isn't one program. It's many parts that must agree: reading "
                "labels, the law's dates, every shelf location, who works which shift, which substitute goes where, which "
                "truck takes the returns. Written in pieces, those pieces drift apart at the seams.",
         "shots": [{"kind": "ai", "src": "dc_interior", "w": 0.4}, {**PARTS, "w": 0.6}]},
        {"id": f"s3_{v}", "beat": "The whole system in one generation",
         "say": "Gemini 4 Argon can hold the whole system in one continued generation. In our experiment it wrote about "
                "{%s.visible_k} tokens of code, {%s.files_manifest} files, and every one of its {%s.edges} cross-file links "
                "lines up. That's the point of a million-token model: the whole system in one head." % ((v,) * 3),
         "shots": [{"kind": "still", "src": "hops_expansion" if draft else "hops_expansion_v2", "w": 0.4, "zoom": 0.03},
                   {"kind": "cap", "src": "codewall" if draft else "codewall_v2", "w": 0.25, "a": 0, "b": 4.6},
                   {"kind": "still", "src": "codewall_longest" if draft else "codewall_longest_v2", "w": 0.35, "zoom": 0.05}],
         "pending_text": "the whole system in one generation: v2 tokens, files, cross-file links"},
    ]
    if draft:
        segs.append({"id": "p_v2", "pending_text": "second, larger run (runs/expansion_v2): tokens, files, cross-file links",
                     "pending_secs": 3.5})
    segs += [
        {"id": f"s3b_{v}", "say": "Here's its longest link: a file written early, used by a test near the end. Its tests "
                                  "pass, live.",
         "shots": [{"kind": "term", "src": "exp_longest_test" if draft else "exp_longest_test_v2", "w": 1}], "min": 5.0},
        {"id": f"s4_{v}", "beat": "Consistent isn't correct",
         "say": "But consistent code isn't correct code. " + ("Our" if draft else "In the first run, our") +
                " verifier ran the plan and found {exp1plan.mistakes} mistakes, mostly one associate booked for two "
                "shelves at once.",
         "shots": [{**MISTAKES, "w": 0.6}, {"kind": "still", "src": "gallery_expansion", "w": 0.4, "zoom": 0.05}]},
        {"id": "s5a", "beat": "{exp1plan.mistakes} → {exp1fixed.mistakes}",
         "say": "A managed agent read the verifier's findings, found the {agent.exp_root_causes} root causes, and fixed them. "
                "Mistakes went from {exp1plan.mistakes} to {exp1fixed.mistakes}, including in {agent.exp_heldout_stores} "
                "stores it never saw.",
         "shots": [{"kind": "term", "src": "agent_log", "w": 0.3}, {**FIXLOOP, "w": 0.7}]},
        {"id": "s5b", "beat": "The working core",
         "say": "And the working core Argon wrote this morning, on {core_patched.stores} stores, overnight: tags flash, "
                "associates walk to each shelf, and every store goes green.",
         "shots": [{**STORE, "w": 0.55}, {**MAP, "w": 0.45, "a": 3}]},
        {"id": "s5c", "say": "With three small logged fixes to its first draft, it found all {core_patched.tp} products with "
                             "Red No. 3, pulled none of the {core_patched.decoys} look-alikes, covered every one of "
                             "{core_patched.pull_facings} shelf spots, and finished every task before midnight.",
         "shots": [{**FOUND, "w": 1}]},
        {"id": "s6a", "beat": "Why it matters",
         "say": "When a law changes overnight, a retailer needs the system built, checked and fixed fast. Argon writes the "
                "whole thing at once, the verifier proves it, the agent repairs it.",
         "shots": [{"kind": "ai", "src": "highway_trucks", "w": 1, "a": 0, "b": 8}]},
        {"id": "s6b", "say": "Simulated drill, simulated operations, every number from the verifier. Open source.",
         "shots": [{**END, "w": 1}]},
    ]
    return segs


# ---------------------------------------------------------------- one minute: beats 1, 3, 5, 6
def one_minute(v):
    draft = v == "exp1"
    return [
        {"id": "m1", "beat": "One night to clear the shelves",
         "say": "On January 1st, 2027, California bans food with Red No. 3. Stores get one overnight shift to clear it, "
                "even when it hides as erythrosine or E127.",
         "shots": [{"kind": "ai", "src": "store_night", "w": 0.45}, {"kind": "ai", "src": "scanner_shelf", "w": 0.55}]},
        {"id": f"m3_{v}", "beat": "The whole system in one generation",
         "say": "Gemini 4 Argon holds the whole system in one continued generation: about {%s.visible_k} tokens of code, "
                "and every one of its {%s.edges} cross-file links lines up." % (v, v),
         "shots": [{"kind": "still", "src": "hops_expansion" if draft else "hops_expansion_v2", "w": 0.5, "zoom": 0.03},
                   {"kind": "still", "src": "codewall_longest" if draft else "codewall_longest_v2", "w": 0.5, "zoom": 0.04}],
         "pending_text": "v2 tokens and cross-file links", "pending_secs": 5.0},
        {"id": "m5a", "beat": "{exp1plan.mistakes} → {exp1fixed.mistakes}",
         "say": "Our verifier still found {exp1plan.mistakes} plan mistakes. A managed agent fixed the "
                "{agent.exp_root_causes} root causes, and they went to {exp1fixed.mistakes}, even in "
                "{agent.exp_heldout_stores} stores it never saw.",
         "shots": [{**FIXLOOP, "w": 1}]},
        {"id": "m5b", "say": "The working core, on {core_patched.stores} stores, found all {core_patched.tp} products with "
                             "Red No. 3 and pulled none of the {core_patched.decoys} look-alikes.",
         "shots": [{**STORE, "w": 0.45, "b": 7}, {**FOUND, "w": 0.55}]},
        {"id": "m6", "beat": "Why it matters",
         "say": "Argon writes the whole thing at once, the verifier proves it, the agent repairs it. Simulated drill; every "
                "number from the verifier.",
         "shots": [{"kind": "ai", "src": "highway_trucks", "w": 0.45, "a": 0, "b": 4}, {**END, "w": 0.55}]},
    ]


VIDEOS = {"backup_core": BACKUP_CORE,
          "demo_full_draft": full("exp1"),          # expansion v1 numbers + "[v2 numbers pending]" card
          "demo_full_final": full("exp2"),          # final cut: v2 numbers; pending cards until runs/expansion_v2 finishes
          "one_minute": one_minute("exp1"),
          "one_minute_final": one_minute("exp2")}


def fmt(v):
    if isinstance(v, bool):
        return str(v)
    if isinstance(v, int):
        return f"{v:,}"
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
