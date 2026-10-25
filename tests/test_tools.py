"""OURS. Regression tests for the verifier tools against tests/tools_fixtures (run: pytest tests/test_tools.py)."""
import json, pathlib, subprocess, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
FX = ROOT / "tests" / "tools_fixtures"
PY = sys.executable


def run(*args):
    return subprocess.run([PY, *map(str, args)], capture_output=True, text=True, cwd=ROOT)


def test_split_good(tmp_path):
    r = run("tools/split_stream.py", FX / "good_run/stream.txt", "--log", FX / "good_run/stream_log.jsonl",
            "--out", tmp_path)
    assert r.returncode == 0, r.stderr
    offs = [json.loads(l) for l in (tmp_path / "offsets.jsonl").read_text().splitlines()]
    assert [o["path"] for o in offs][:2] == ["recallstorm/__init__.py", "recallstorm/aliases/norm.py"]
    assert all(o["terminated"] for o in offs)
    assert offs[1]["fences_stripped"] == 2 and "```" not in (tmp_path / "recallstorm/aliases/norm.py").read_text()
    assert all(o["start_tok"] <= o["end_tok"] for o in offs)
    assert offs[-1]["end_tok"] == pytest_approx(len((FX / "good_run/stream.txt").read_bytes()) // 4)


def pytest_approx(v, tol=3):
    class A:
        def __eq__(self, o): return abs(o - v) <= tol
    return A()


def test_split_partial_flags_unterminated(tmp_path):
    run("tools/split_stream.py", FX / "partial/stream.txt", "--log", FX / "partial/stream_log.jsonl", "--out", tmp_path)
    meta = json.loads((tmp_path / "split_meta.json").read_text())
    assert meta["unterminated"] == ["recallstorm/rules/engine.py"]


def test_split_bg(tmp_path):
    run("tools/split_stream.py", FX / "bg/stream.txt", "--log", FX / "bg/events.jsonl", "--out", tmp_path)
    meta = json.loads((tmp_path / "split_meta.json").read_text())
    assert meta["token_map"]["source"] == "events" and meta["blocks"] == 4


def test_split_checkpoint_rewind(tmp_path):
    (tmp_path / "s.txt").write_text("x" * 40)
    (tmp_path / "l.jsonl").write_text('{"hop":0,"out_bytes":10,"visible_hop":3}\n{"hop":0,"out_bytes":30,"visible_hop":9}\n'
                                      '{"hop":0,"out_bytes":20,"visible_hop":6}\n{"hop":0,"out_by')
    r = run("tools/split_stream.py", tmp_path / "s.txt", "--log", tmp_path / "l.jsonl", "--out", tmp_path / "o")
    assert r.returncode == 0
    assert json.loads((tmp_path / "o/split_meta.json").read_text())["token_map"]["known_until_byte"] == 20


def test_seams():
    assert run("tools/seam_check.py", FX / "good_run").returncode == 0
    bad = run("tools/seam_check.py", FX / "bad_run")
    assert bad.returncode == 1 and "dup" in bad.stdout and "emitted twice" in bad.stdout
    assert run("tools/seam_check.py", FX / "bg").returncode == 0


def test_no_seams(tmp_path):
    r = run("tools/seam_check.py", tmp_path)
    assert r.returncode == 1 and "NO SEAMS" in r.stdout


def test_verify_code(tmp_path):
    run("tools/split_stream.py", FX / "good_run/stream.txt", "--log", FX / "good_run/stream_log.jsonl",
        "--out", tmp_path / "g")
    r = run("tools/verify_code.py", tmp_path / "g", "--report", tmp_path / "x_code.json")
    assert r.returncode == 0, r.stderr
    rep = json.loads((tmp_path / "x_code.json").read_text())
    bad = {(e["symbol"], e["status"]) for e in rep["d2"]["edges_bad"]}
    assert ("missing_fn", "missing_symbol") in bad and ("find_red3", "arity_mismatch") in bad
    assert [x["literal"] for x in rep["d3"]] == ["BOGUS_CODE"]
    assert rep["d4"][0]["status"] == "failed" and rep["d4"][0]["passed"] == 2
    assert [s["name"] for s in rep["d6"]["stubs"]] == ["todo_stub"]
    assert (tmp_path / "x_deps.jsonl").exists()
