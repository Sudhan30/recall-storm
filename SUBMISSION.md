# Submission text (Track 1: Million Token Engineering)

**Project name:** Recall Storm

**One-liner:** Gemini 4 Argon writes an entire retail compliance system in one continued generation, 646,825 tokens
and 911 files, and a verifier plus a managed agent prove where it holds and fix where it breaks.

**Description (≈150 words):**
On January 1, 2027, California bans food containing Red No. 3, with no sell-through period. The dye hides under a
dozen names, and a large retailer has one overnight shift to clear it from thousands of shelf spots. That job is
many parts that must agree: reading labels, the law's dates, every shelf, every shift, substitutes and trucks.

We asked Gemini 4 Argon to write the whole system in one continued generation. It wrote 646,825 tokens, 911 files,
over 10 hops with every seam clean; after a one-line fix, all 6,581 cross-file links resolve. Our verifier then ran
the plan on a 20-store simulated drill and found what consistency hides: scheduling flaws at both lengths. A managed
agent, given only the failing file and half the failures, fixed the root cause, and the fix held on stores it never
saw. The working core finds all 467 affected products and pulls none of 483 look-alikes.

**How we used Gemini 4 Argon:** one continued generation per run with manual continuation hops (`tools/argon_run.py`);
the core (22.5K tokens), expansion v1 (254K) and v2 (647K); short fresh calls as a baseline; Argon also drafted
123 of v2's module specs from our domain list.

**How we used Managed Agents:** an Antigravity agent on gemini-4-argon (`tools/repair_agent.py`), network disabled,
gets one failing file plus failures with half held out; we re-score everything locally. 10 jobs: 5 FIXED,
2 IMPROVED, 3 NOT_FIXED (one job hit our client timeout and was resumed; all logged in `patches/agent/LOG.jsonl`).

**What is real vs simulated:** real rule text, real USDA ingredient labels, real store locations (OpenStreetMap),
real FDA recall notices; simulated shelves, staff, stock and trucks.

**Repo:** https://github.com/Sudhan30/recall-storm  ·  **Demo:** `./demo.sh`, `viewer/`, `videos/one_minute_final.mp4`
