"""Copy viewer/ into a scratch dir and rebuild its data there from the current runs/ and reports/.

The repo's viewer/data/live/ is left alone (it is refreshed by the team's own build_data.py). Usage:
  .venv/bin/python videos/snapshot_viewer.py <scratch_dir>      # then: python3 -m http.server -d <scratch_dir> 8001
It runs a copy of viewer/build_data.py with only its ROOT and LIVE paths changed.
"""
import pathlib, re, shutil, subprocess, sys

REPO = pathlib.Path(__file__).resolve().parent.parent
dst = pathlib.Path(sys.argv[1]).resolve()
shutil.rmtree(dst / "viewer", ignore_errors=True)
shutil.copytree(REPO / "viewer", dst / "viewer", ignore=shutil.ignore_patterns("live"))
live = dst / "viewer" / "data" / "live"
live.mkdir(parents=True, exist_ok=True)
src = (REPO / "viewer" / "build_data.py").read_text()
src = re.sub(r"^ROOT = .*$", f"ROOT = pathlib.Path({str(REPO)!r})", src, count=1, flags=re.M)
src = re.sub(r"^LIVE = .*$", f"LIVE = pathlib.Path({str(live)!r})", src, count=1, flags=re.M)
(dst / "build_data_snap.py").write_text(src)
subprocess.run([sys.executable, str(dst / "build_data_snap.py")], cwd=REPO, check=True)
print(f"snapshot ready: python3 -m http.server -d {dst} 8001  ->  http://localhost:8001/viewer/")
