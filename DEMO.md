# Live demo script (3:00)

Every number below comes from `reports/`, `runs/*/hops.jsonl` or `patches/`. Say "simulated drill", "simulated
associates", "compliance pull". Never say "recall" for Red No. 3, a brand name, "1M tokens in one request", "no other
model can", or any number that isn't on this page.

## Before you go on (5 min)

```bash
cd ~/Desktop/recall-storm
python3 -m http.server -d . 8000 &          # if not already running
.venv/bin/python viewer/build_data.py && .venv/bin/python viewer/build_compare.py
```

Open in Chrome, in this tab order, and hard-reload each (Cmd+Shift+R):
1. Terminal, font size up, in `~/Desktop/recall-storm`
2. http://localhost:8000/viewer/ (tab 1, California map; replay speed set to **20 s**)
3. http://localhost:8000/viewer/compare.html
4. `videos/demo_full_final.mp4` paused at 0:00 (backup if anything live fails)

## 0:00–0:20 · One night to clear the shelves

> "On January 1st, 2027, California bans food with Red No. 3, with no sell-through period. The dye hides under a
> dozen names: erythrosine, E127, 'Red 3', scanning typos. Miss one and it's a violation; pull Red 40 by mistake
> and you empty a shelf for nothing. This is a simulated drill for a large retailer's nearly 300 California stores."

## 0:20–1:05 · A working system Argon wrote this morning

- Terminal: `./demo.sh` (3.6 s). It prints the verifier result and opens the map.
  > "Argon wrote this system this morning. Here it runs on 20 stores, overnight."
- Map: press **Space**. Dots go grey → amber → green in about 20 s. While it runs:
  > "It found all 467 products with Red No. 3 and pulled none of the 483 look-alikes. Every one of 6,718 shelf spots
  > has a task, every task ends before midnight: zero plan mistakes."
- Tab **2** (3D store): associates walk, tags flash. Click **Evidence: demo trio**.
  > "Every decision shows its evidence: erythrosine caught, a vague 'artificial color' held for a person, Red 40 left
  > on the shelf."
- If asked: Argon's first draft missed 25 of the 467; three small logged fixes closed it (`patches/LOG.md`).

## 1:05–1:50 · The whole system in one generation

- Tab **3** (Hops & seams), pick `expansion_v2`.
  > "Then we asked Argon for the whole platform in one continued generation: 646,825 tokens of code, 911 files,
  > over 10 hops — 92 minutes, about $14. Every seam where one hop hands off to the next joined cleanly."
- Tab **4** (Code wall), pick `expansion_v2_agentpatched` (v2 + the one-line fix), click **Longest passing cross-file call**.
  > "This test was written at token 641,687. It calls a function Argon wrote at token 89,603 — 552,000 tokens
  > earlier — and it passes." Optionally run it live:
  > `cd gen/expansion_v2_agentpatched && PYTHONPATH=.:../.. ../../.venv/bin/python -m pytest tests/integration/test_flow_09_analytics_governance.py -q`
  > "After one one-line fix, all 6,581 cross-file links resolve, with zero argument mismatches in 4,862 calls."

## 1:50–2:35 · Consistent isn't correct

- Tab **5** (Failures): v2's one break.
  > "One mis-indented line at token 132,000 took down the whole label-reading package. A managed agent fixed it in
  > 21 seconds."
- compare.html.
  > "Each row is one simulated associate. Red means Argon's plan sent the same person to two shelves at once:
  > 7,631 double-bookings in the 254K-token run." Switch **Run** to v2: "and 7,161 in the 647K-token run."
  > "A managed agent read the verifier's findings, found the root cause and fixed it — 7,631 to zero, including in
  > ten stores it never saw. The same flaw appeared at both lengths, and the agent fixed it both times: v2's plan
  > went from 21,459 mistakes to 175."

## 2:35–3:00 · Why it matters

> "When a law changes overnight, a retailer needs the system built, checked and fixed fast. Argon writes the whole
> thing at once, the verifier proves it, the agent repairs it. Simulated drill, simulated operations, every number
> from the verifier. It's open source."

## If something fails live

- `demo.sh` or the map: play `videos/backup_core.mp4`.
- Anything else: play `videos/demo_full_final.mp4` from the matching beat.

## Likely questions

- **Why not just RAG plus code?** It's what Argon wrote, and our baseline C is exactly that (0 plan mistakes).
  The experiment asks whether one long generation can write the whole system coherently.
- **Did you edit Argon's code?** No: `gen/` is unedited. Fixes live in `patches/` (3 hand fixes to the core; every
  agent patch logged in `patches/agent/LOG.jsonl`, including the ones that failed).
- **What didn't work?** The openFDA lot-code scenario: v1's lot code pulls 539 good lots; v2's never turns lots into
  shelf tasks. And the agent's fixes sometimes over-correct (2 of the attempts are NOT_FIXED in the log).
