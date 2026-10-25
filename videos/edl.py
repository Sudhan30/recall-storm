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


# ---------------------------------------------------------------- full demo (BUILD.md section 14)
S = {seg["id"]: seg for seg in BACKUP_CORE}
MATCHED_TABLE = {"kind": "table", "title": "Matched packages · same hidden tests (acceptance/)",
                 "cols": ["package", "A: written in-stream (core)", "B: written fresh (short calls)"],
                 "rows": [["rules", "{accept.accept_core.test_rules.passed} / {accept.accept_core.test_rules.tests}",
                           "{accept.accept_b_rules.test_rules.passed} / {accept.accept_b_rules.test_rules.tests}"],
                          ["allocate", "{accept.accept_core.test_allocate.passed} / {accept.accept_core.test_allocate.tests}",
                           "{accept.accept_b_allocate.test_allocate.passed} / {accept.accept_b_allocate.test_allocate.tests}"],
                          ["route", "not in the core (collection skipped)",
                           "{accept.accept_b_route.test_route.passed} / {accept.accept_b_route.test_route.tests}"]],
                 "note": "A is Argon's unedited core; with the 3 logged patches A's rules pass "
                         "{accept.accept_core_patched.test_rules.passed} / {accept.accept_core_patched.test_rules.tests}. "
                         "Source: reports/accept_core.xml, accept_core_patched.xml, accept_b_*.xml",
                 "w": 1}


def full(v):
    """v = 'exp1' (draft, numbers now) or 'exp2' (final cut, filled when expansion_v2 finishes)."""
    draft = v == "exp1"
    hook3 = ("You'll see a working system Argon wrote this morning, and an experiment where Argon wrote a "
             "{%s.visible}-token version in one continued generation." % v)
    segs = [
        dict(S["h1"]),
        {"id": "f_h2", "say": "This is a simulated drill on {core_patched.stores} California Walmart and Sam's Club locations, "
                              "where the dye hides under names like erythrosine and E127.",
         "shots": [{"kind": "ai", "src": "aisle_pull", "w": 0.6}, {"kind": "ai", "src": "scanner_shelf", "w": 0.4}]},
        {"id": f"f_h3_{v}", "say": hook3, "shots": [{"kind": "ai", "src": "dc_trucks", "w": 1}],
         "pending_text": "hook: v2 visible-token count"},
        dict(S["c1"]), dict(S["c2"]), dict(S["c3"]),
        {"id": "f_c4", "say": "Argon's unedited core: {core.hard_errors} hard errors, recall {core.recall}. After "
                              "{patches.core_count} small logged patches: {core_patched.hard_errors} hard errors, recall "
                              "{core_patched.recall}, precision {core_patched.precision}, {core_patched.decoys_pulled} of "
                              "{core_patched.decoys} decoys pulled.",
         "shots": [{"kind": "term", "src": "vp_core", "w": 0.34}, {"kind": "term", "src": "vp_core_patched", "w": 0.33},
                   {"kind": "panel", "srcs": ["vcard4", "vcard3"], "w": 0.33, "colw": 760, "stagger": False,
                    "heads": ["Argon core, unedited", "core + 3 logged patches"], "colors": ["red", "green"]}]},
        {"id": f"f_e1_{v}", "say": "The experiment: one continued generation over {%s.hops} hops, {%s.visible} visible tokens in "
                                   "{%s.minutes} minutes, about ${%s.cost_usd}. Seams, where one hop hands off mid-file: "
                                   "{%s.seams_pass} of {%s.seams_total} pass."
                                   % ((v,) * 6),
         "shots": [{"kind": "ai", "src": "dc_interior", "w": 0.25, "a": 0, "b": 5},
                   {"kind": "still", "src": "hops_expansion" if draft else "hops_expansion_v2", "w": 0.75, "zoom": 0.03}],
         "pending_text": "hops & seams: v2 visible tokens, hops, minutes, cost, seams"},
    ]
    if draft:
        segs.append({"id": "p_v2_hops", "pending_text": "second, larger expansion (runs/expansion_v2): tokens, hops, minutes, cost, seams",
                     "pending_secs": 3.5})
    segs += [
        {"id": f"f_e2_{v}", "say": "The code wall puts every file at its token position. All {%s.edges} cross-file references "
                                   "resolve. The longest passing call: ids.py at token {%s.longest_def.start_tok}, used by a "
                                   "test at token {%s.longest_use.start_tok}." % ((v,) * 3),
         "shots": [{"kind": "cap", "src": "codewall" if draft else "codewall_v2", "w": 0.35, "a": 0, "b": 4.6},
                   {"kind": "still", "src": "codewall_longest" if draft else "codewall_longest_v2", "w": 0.65, "zoom": 0.05}],
         "pending_text": "code wall: v2 files, references, longest call"},
        {"id": f"f_e3_{v}", "say": "We run both files' tests live. They pass.",
         "shots": [{"kind": "term", "src": "exp_longest_test" if draft else "exp_longest_test_v2", "w": 1}], "min": 5.0},
    ]
    if draft:
        segs.append({"id": "p_v2_code", "pending_text": "code wall: longest cross-file call in the v2 stream, and its live test",
                     "pending_secs": 3.5})
    segs += [
        {"id": f"f_e4_{v}", "say": "What broke as length grew: {%s.b0.files_failed} failing test files in the first 200 thousand "
                                   "tokens, {%s.b1.files_failed} after, and {%s.bad_literals_nontest} status strings outside "
                                   "the contract's enums."
                                   % ((v,) * 3),
         "shots": [{"kind": "still", "src": "gallery_expansion" if draft else "gallery_expansion_v2", "w": 1, "zoom": 0.06}],
         "pending_text": "failure gallery: v2 buckets"},
        {"id": "f_e5", "say": "A managed repair agent takes failing files: the core's pack_returns went to "
                              "{agent.core_pack_returns.after_passed} of {agent.core_pack_returns.after_passed} passing in "
                              "{agent.core_pack_returns.secs} seconds. On fresh package B's rules, round two cut failures from "
                              "{agent.b_rules_evaluator_r2.before_failed} to {agent.b_rules_evaluator_r2.after_failed}, fixed "
                              "{agent.b_rules_evaluator_r2.held_out_fixed} of {agent.b_rules_evaluator_r2.held_out} held-out "
                              "cases, with {agent.b_rules_evaluator_r2.new_failures} new failures.",
         "shots": [{"kind": "term", "src": "agent_log", "w": 1}]},
        {"id": "f_e6", "say": "Matched packages, same hidden tests. Rules written in-stream pass "
                              "{accept.accept_core.test_rules.passed} of {accept.accept_core.test_rules.tests}; written fresh, "
                              "{accept.accept_b_rules.test_rules.passed}. Allocate: both {accept.accept_b_allocate.test_allocate.passed} "
                              "of {accept.accept_b_allocate.test_allocate.tests}.",
         "shots": [MATCHED_TABLE]},
        {"id": "f_w1", "say": "RAG plus code is the right way to run a compliance pull, and it's what Argon wrote. We tested "
                              "whether one long generation can write it coherently, and you've just seen where it held and "
                              "where it broke.",
         "shots": [{"kind": "panel", "srcs": ["vcard1", "vcard2"], "w": 1, "colw": 760, "stagger": False,
                    "heads": ["baseline C: RAG + LLM + code (ours)", "baseline D: code only (ours)"],
                    "colors": ["blue", "blue"]}]},
        {"id": "f_x1", "say": "For compliance teams at any big retailer. Stores, stock and staffing are simulated, and every "
                              "number came from the verifier. Open source.",
         "shots": [{"kind": "ai", "src": "highway_trucks", "w": 0.55, "a": 0, "b": 4.5}, {"kind": "title", "src": "end_full", "w": 0.45}]},
    ]
    return segs


def one_minute(v):
    return [
        {"id": "o1", "say": "California bans Red No. 3 in food on January 1st, 2027. Gemini 4 Argon wrote a system, in one "
                            "generation, that finds it even as erythrosine or E127.",
         "shots": [{"kind": "ai", "src": "store_night", "w": 0.45}, {"kind": "ai", "src": "scanner_shelf", "w": 0.55}]},
        {"id": "o2", "say": "In a simulated drill on {core_patched.stores} California Walmart and Sam's Club locations, it plans "
                            "{core_patched.shelf_tasks} shelf tasks, and every store goes green.",
         "shots": [{"kind": "ai", "src": "aisle_pull", "w": 0.3, "a": 1, "b": 5},
                   {"kind": "cap", "src": "store3d", "w": 0.4, "a": 0, "b": 8, "crop": [0, 250, 1476, 830]},
                   {"kind": "cap", "src": "map_replay", "w": 0.3, "a": 3, "b": 12.5}]},
        {"id": "o3", "say": "Every verdict carries evidence: erythrosine pulled, a vague \"artificial color\" held, a Red 40 decoy kept.",
         "shots": [{"kind": "cards", "src": "card", "w": 1}]},
        {"id": "o4", "say": "After {patches.core_count} logged patches: {core_patched.hard_errors} hard errors, recall "
                            "{core_patched.recall}, {core_patched.decoys_pulled} of {core_patched.decoys} decoys pulled.",
         "shots": [{"kind": "panel", "srcs": ["vcard4", "vcard3"], "w": 1, "colw": 760, "stagger": False,
                    "heads": ["Argon core, unedited", "core + 3 logged patches"], "colors": ["red", "green"]}]},
        {"id": f"o5_{v}", "say": "The experiment: one continued generation, {%s.visible} visible tokens over {%s.hops} hops; "
                                 "{%s.seams_pass} of {%s.seams_total} seams pass." % ((v,) * 4) if v == "exp1" else
                                 "The experiment: one continued generation, {exp2.visible} visible tokens over {exp2.hops} hops, "
                                 "and {exp2.seams_pass} of {exp2.seams_total} seams pass.",
         "shots": [{"kind": "still", "src": "hops_expansion" if v == "exp1" else "hops_expansion_v2", "w": 0.6, "zoom": 0.03},
                   {"kind": "still", "src": "codewall_longest" if v == "exp1" else "codewall_longest_v2", "w": 0.4, "zoom": 0.04}],
         "pending_text": "v2 visible tokens, hops, seams", "pending_secs": 5.0},
        {"id": "o6", "say": "A managed agent repairs what breaks: {agent.core_pack_returns.after_passed} of "
                            "{agent.core_pack_returns.after_passed} tests passing in {agent.core_pack_returns.secs} seconds.",
         "shots": [{"kind": "term", "src": "agent_log", "w": 1}]},
        {"id": "o7", "say": "Stores, stock and staffing are simulated; every number came from the verifier.",
         "shots": [{"kind": "title", "src": "end_full", "w": 1}]},
    ]


VIDEOS = {"backup_core": BACKUP_CORE,
          "demo_full_draft": full("exp1"),          # expansion v1 numbers + "[v2 numbers pending]" cards
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
