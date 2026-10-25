"""OURS. Assembles a full prompt from a body file plus the shared context blocks.

Usage: python tools/build_prompt.py BODY_FILE OUT_FILE [--signatures FILE]
"""
import json, pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
D = ROOT / "data"
body, out = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])

CONVENTIONS = """CONVENTIONS (facts about the environment you are writing into)
- contract.py and contract_io.py exist at the repo root. Import with `from contract import ...`.
  Load data with `from contract import load_datapack; pack = load_datapack(data_dir)`.
- Rule.effective is a NAIVE wall-clock datetime, interpreted in each store's local tz (Store.tz).
  `at` passed to evaluate_sku is tz-aware; compare at.astimezone(ZoneInfo(store_tz)).replace(tzinfo=None)
  against rule.effective when you know the tz, else at.replace(tzinfo=None). Sale is prohibited when
  local(at) >= effective. evaluate_sku with state="CA" applies rules whose jurisdictions include "CA" or "US".
- Datetimes in plan.jsonl and events.jsonl are ISO 8601 with offset.
- The scenario file is data/scenario_<id>.json (fields: scenario_id, state, rule_ids, as_of, deadline).
- The deadline for every task window is the scenario deadline; windows must end strictly before it.
- data/labels.csv is ground truth and you will NOT see it. Do not read it from code.
"""


def sample(name, n=20):
    rows = [l for l in (D / name).read_text().splitlines() if l.strip()]
    step = max(1, len(rows) // n)
    return "\n".join(rows[::step][:n])


parts = [body.read_text().strip(), CONVENTIONS,
         "=== contract.py ===\n" + (ROOT / "contract.py").read_text(),
         "=== data/rules.jsonl ===\n" + (D / "rules.jsonl").read_text(),
         "=== data/scenario_ca_red3.json ===\n" + (D / "scenario_ca_red3.json").read_text()]
for f in ["skus.jsonl", "stores.jsonl", "facings.jsonl", "associates.jsonl", "trucks.jsonl",
          "dc_stock.jsonl", "notes.jsonl"]:
    parts.append(f"=== data/{f} (20 sample rows) ===\n" + sample(f))
subs = json.loads((D / "substitutes.json").read_text())
parts.append("=== data/substitutes.json (sample) ===\n" + json.dumps(dict(list(subs.items())[:20])))
if "--signatures" in sys.argv:
    parts.append("=== existing core public signatures ===\n" +
                 pathlib.Path(sys.argv[sys.argv.index("--signatures") + 1]).read_text())
parts.append((ROOT / "prompts" / "protocol.md").read_text())
out.write_text("\n\n".join(parts) + "\n")
print(f"{out}: {len(out.read_text())} chars (~{len(out.read_text()) // 4} tokens)")
