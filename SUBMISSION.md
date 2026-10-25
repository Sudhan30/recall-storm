# Submission form (copy each block into its field)

## Team Name*

Recall Storm

## Team Members

(already filled by the form: sudhan30)

## Project Description*

On January 1, 2027, California bans food containing Red No. 3, with no sell-through period. The dye hides under a
dozen names (erythrosine, E127, "Red 3", scanning typos), and a large retailer has one overnight shift to clear it
from thousands of shelf spots. That job is many parts that must agree: reading labels, the law's dates, every shelf,
every shift, substitutes and return trucks.

Recall Storm asks Gemini 4 Argon to write that whole compliance system in one continued generation, then proves where
it holds and fixes where it breaks. Our largest run wrote 646,825 tokens of code, 911 files, over 10 continuation hops
with every seam clean. After a one-line fix, all 6,581 cross-file links resolve with zero argument mismatches; a test
written at token 641,687 calls a function written 552,000 tokens earlier, and passes.

An independent verifier then runs the plan as a 20-store simulated drill and finds what consistent code can hide: the
same scheduling flaw appeared at 254K and 647K tokens, with people booked at two shelves at once. A managed agent,
given only the failing file and half of the failures, fixed the root cause both times, including in stores it never
saw (8,441 plan mistakes to 0 in the 254K run). Argon's working core finds all 467 affected products, pulls none of
483 look-alikes, and plans every task before midnight. Stores, stock and staffing are simulated; every number comes
from the verifier, and Argon's output is unedited in the repo, with every fix logged separately.

## Public Project GitHub Repository*

https://github.com/Sudhan30/recall-storm

## 1-Minute Demo Video*

(upload `videos/one_minute_final.mp4` to YouTube as Unlisted, then paste its link here)

## Describe your use of Google products to build the submitted project:*

- **Gemini 4 Argon (Gemini API, `google-genai` SDK):** wrote the system itself in three long generations (22,523,
  254,377 and 646,825 visible tokens), using manual continuation hops with continuation tokens and mid-stream
  checkpoints (`tools/argon_run.py`), plus short fresh calls as a baseline. Argon also drafted 123 of the larger run's
  module specs from our list of domains, and acts as the retrieval-plus-LLM step in one baseline.
- **Gemini Interactions API, Antigravity managed agent on gemini-4-argon:** a repair loop (`tools/repair_agent.py`)
  that gets one failing file plus failures, with half held out, in a sandbox with network disabled. 10 jobs: 5 fixed,
  2 improved, 3 not fixed, all logged. We also tested background mode with reconnects.
- **Gemini text-to-speech and the Gemini Omni video model:** narration and the AI-generated illustration shots in
  our demo videos (labelled as such).
- **Google AI Studio:** API key, quota and rate-limit monitoring.

## Do you have any feedback for the Google Deepmind team on Argon?*

Continuation worked very well: 21 of 21 seams across our runs joined cleanly, including one that split an
identifier mid-word, and at about 700K tokens of context Argon still resolved every one of 6,581 cross-file links.
Speed held at 112-130 visible tokens per second the whole time.

Things that would have helped:
- Argon ignores length targets, so sizing a long run is guesswork. We scaled by listing named functions instead;
  a way to request a rough length, or a documented tokens-per-function guide, would help.
- Each hop resends all prior output as input, so input cost grows with every hop (3.5M input tokens for our 647K run).
  Automatic caching of the shared prefix between hops would cut that sharply.
- Background interactions: we found no way to resume one that ends `incomplete`, so we used streaming hops instead.
- The Antigravity agent returned "Missing required field 'environment'" until we passed
  `{"type": "remote", "network": "disabled"}`; a documented minimal example would save time. One long agent job also
  outlived our client timeout, and re-attaching with `interactions.get` worked well.
- Usage reported thinking tokens as null on long streaming hops, but populated them on short calls; consistent
  reporting would make cost accounting easier.
- The Veo model IDs returned 404 ("no longer available") on our key and pointed to gemini-omni; clearer migration
  notes would help.
- Behaviourally, long generations were very consistent but not always correct: the same scheduling flaw appeared at
  254K and 647K tokens. Pairing long generation with a verifier and a repair agent is what made it work.
