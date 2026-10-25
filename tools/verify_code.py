"""OURS. Layer 1 verifier for generated code.

Usage: python tools/verify_code.py gen/<name>/ [--offsets gen/<name>/offsets.jsonl]
                                   [--report reports/<name>_code.json] [--no-tests] [--timeout 60] [--jobs 4]

Checks
  parse  every .py file parses (ast)
  D1     manifest promises vs files and public symbols, including argument counts
  D2     every import resolves (gen dir, repo root contract*.py, stdlib, installed); call arity of
         imported functions/classes matches the definition; edges carry (use_tok, def_tok, distance)
  D3     uppercase string literals not in the contract vocabulary
  D4     pytest per test file (PYTHONPATH=<gen>:<repo root>, timeout per file); collection errors vs failures
  D6     stubs / placeholders, duplicated normalized 8-line windows, near-duplicate test bodies
Buckets: by token position (0-200K, 200-400K, 400-600K, 600K+) and dep distance (0-50K, 50-200K, 200-400K, 400K+).

Writes the report JSON and deps.jsonl next to it:
  {from_path, to_path, symbol, use_tok, def_tok, distance, status}
One bad file never crashes the run: every per-file step is wrapped.
"""
from __future__ import annotations

import argparse
import ast
import concurrent.futures as cf
import hashlib
import json
import os
import pathlib
import re
import subprocess
import sys
import tempfile
import time
import traceback
import xml.etree.ElementTree as ET
from collections import defaultdict
from importlib.util import find_spec

ROOT = pathlib.Path(__file__).resolve().parent.parent
POS_BUCKETS = [(0, 200_000, "0-200K"), (200_000, 400_000, "200-400K"), (400_000, 600_000, "400-600K"),
               (600_000, 10**12, "600K+")]
DIST_BUCKETS = [(0, 50_000, "0-50K"), (50_000, 200_000, "50-200K"), (200_000, 400_000, "200-400K"),
                (400_000, 10**12, "400K+")]
RESOLVED = ("ok", "star", "arity_mismatch")         # import resolved (arity is reported separately)
SKIP_DIRS = {"__pycache__", ".pytest_cache", ".git"}


def bucket(v, table):
    if v is None:
        return "unknown"
    for lo, hi, name in table:
        if lo <= v < hi:
            return name
    return table[-1][2]


# ------------------------------------------------------------------ files and token positions
class GenFile:
    def __init__(self, gen: pathlib.Path, rel: str, off: dict | None):
        self.rel = rel
        self.path = gen / rel
        self.text = self.path.read_text(encoding="utf-8", errors="replace")
        self.off = off or {}
        self.tree = None
        self.parse_error = None
        try:
            self.tree = ast.parse(self.text, filename=rel)
        except SyntaxError as e:
            self.parse_error = {"msg": e.msg, "line": e.lineno, "col": e.offset}
        except Exception as e:                       # ValueError on NUL bytes etc.
            self.parse_error = {"msg": repr(e)[:200], "line": None, "col": None}
        b = self.text.encode("utf-8")
        self.nbytes = max(1, len(b))
        self.line_byte = [0]
        for line in self.text.split("\n"):
            self.line_byte.append(self.line_byte[-1] + len(line.encode("utf-8")) + 1)

    @property
    def start_tok(self):
        return self.off.get("start_tok")

    @property
    def end_tok(self):
        return self.off.get("end_tok")

    def tok(self, line: int | None):
        if self.start_tok is None or self.end_tok is None:
            return None
        if not line:
            return self.start_tok
        bo = self.line_byte[min(max(line - 1, 0), len(self.line_byte) - 1)]
        return int(round(self.start_tok + (self.end_tok - self.start_tok) * min(1.0, bo / self.nbytes)))

    @property
    def module(self):
        p = self.rel[:-3] if self.rel.endswith(".py") else self.rel
        parts = p.split("/")
        if parts[-1] == "__init__":
            parts = parts[:-1]
        return ".".join(parts)

    @property
    def is_pkg(self):
        return self.rel.endswith("__init__.py")

    @property
    def is_test(self):
        n = pathlib.PurePosixPath(self.rel).name
        return n.startswith("test_") and n.endswith(".py") or n.endswith("_test.py")


def load_offsets(p: pathlib.Path | None) -> dict[str, dict]:
    out = {}
    if p and p.exists():
        for line in p.read_text().splitlines():
            try:
                o = json.loads(line)
            except json.JSONDecodeError:
                continue
            key = o.get("written_as") or o.get("path")
            out[key] = o                             # last occurrence wins, matches split_stream
    return out


def load_manifest(gen: pathlib.Path) -> list[dict]:
    p = gen / "manifest.jsonl"
    rows = []
    if p.exists():
        for line in p.read_text().splitlines():
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                pass
    return rows


# ------------------------------------------------------------------ symbol tables
def sig_of(node) -> dict:
    """Signature summary for a FunctionDef/Lambda args (positional names, defaults, kwonly...)."""
    a = node.args
    pos = [x.arg for x in a.posonlyargs + a.args]
    return {"pos": pos, "n_def": len(a.defaults), "posonly": len(a.posonlyargs),
            "kwonly": [x.arg for x in a.kwonlyargs],
            "kwonly_req": [x.arg for x, d in zip(a.kwonlyargs, a.kw_defaults) if d is None],
            "vararg": a.vararg is not None, "kwarg": a.kwarg is not None, "line": node.lineno}


def is_dataclass(cls: ast.ClassDef) -> bool:
    for d in cls.decorator_list:
        f = d.func if isinstance(d, ast.Call) else d
        name = f.attr if isinstance(f, ast.Attribute) else getattr(f, "id", "")
        if name == "dataclass":
            return True
    return False


def class_sig(cls: ast.ClassDef) -> dict | None:
    """Constructor signature without self, or None when unknown (inherited / metaclass magic)."""
    for st in cls.body:
        if isinstance(st, (ast.FunctionDef, ast.AsyncFunctionDef)) and st.name == "__init__":
            s = sig_of(st)
            if s["pos"]:
                s["pos"] = s["pos"][1:]; s["posonly"] = max(0, s["posonly"] - 1)
            return s
    if is_dataclass(cls):
        pos, n_def = [], 0
        for st in cls.body:
            if isinstance(st, ast.AnnAssign) and isinstance(st.target, ast.Name):
                ann = ast.unparse(st.annotation) if st.annotation is not None else ""
                if "ClassVar" in ann:
                    continue
                if st.value is not None:
                    n_def += 1
                elif n_def:
                    pass
                pos.append(st.target.id)
        return {"pos": pos, "n_def": n_def, "posonly": 0, "kwonly": [], "kwonly_req": [], "vararg": False,
                "kwarg": False, "line": cls.lineno}
    if cls.bases or cls.keywords:
        return None
    return {"pos": [], "n_def": 0, "posonly": 0, "kwonly": [], "kwonly_req": [], "vararg": False,
            "kwarg": False, "line": cls.lineno}


def top_level_stmts(body):
    """Top-level statements, descending into if/try/with blocks but not defs."""
    for st in body:
        yield st
        if isinstance(st, (ast.If, ast.For, ast.While, ast.With)):
            yield from top_level_stmts(st.body); yield from top_level_stmts(getattr(st, "orelse", []))
        elif isinstance(st, ast.Try) or (hasattr(ast, "TryStar") and isinstance(st, getattr(ast, "TryStar"))):
            yield from top_level_stmts(st.body); yield from top_level_stmts(st.orelse)
            yield from top_level_stmts(st.finalbody)
            for h in st.handlers:
                yield from top_level_stmts(h.body)


class ModInfo:
    """Names defined at module top level: kind in def/class/var/import."""
    def __init__(self, tree: ast.Module | None, module: str, is_pkg: bool):
        self.defs: dict[str, dict] = {}
        self.imports: dict[str, tuple[str, str | None]] = {}   # local name -> (module, attr|None)
        self.star: list[str] = []
        if tree is None:
            return
        for st in top_level_stmts(tree.body):
            if isinstance(st, (ast.FunctionDef, ast.AsyncFunctionDef)):
                self.defs[st.name] = {"kind": "def", "sig": sig_of(st), "line": st.lineno, "node": st}
            elif isinstance(st, ast.ClassDef):
                self.defs[st.name] = {"kind": "class", "sig": class_sig(st), "line": st.lineno, "node": st}
            elif isinstance(st, ast.Assign):
                for t in st.targets:
                    for n in ast.walk(t):
                        if isinstance(n, ast.Name):
                            self.defs.setdefault(n.id, {"kind": "var", "sig": None, "line": st.lineno})
            elif isinstance(st, ast.AnnAssign) and isinstance(st.target, ast.Name):
                self.defs.setdefault(st.target.id, {"kind": "var", "sig": None, "line": st.lineno})
            elif isinstance(st, ast.Import):
                for a in st.names:
                    local = a.asname or a.name.split(".")[0]
                    self.imports[local] = (a.name if a.asname else a.name.split(".")[0], None)
            elif isinstance(st, ast.ImportFrom):
                base = resolve_relative(module, is_pkg, st.module, st.level)
                for a in st.names:
                    if a.name == "*":
                        self.star.append(base)
                    else:
                        self.imports[a.asname or a.name] = (base, a.name)


def resolve_relative(module: str, is_pkg: bool, mod: str | None, level: int) -> str:
    if not level:
        return mod or ""
    parts = module.split(".") if module else []
    pkg = parts if is_pkg else parts[:-1]
    if level > 1:
        pkg = pkg[: len(pkg) - (level - 1)] if level - 1 <= len(pkg) else []
    return ".".join(pkg + ([mod] if mod else []))


STDLIB = set(getattr(sys, "stdlib_module_names", ())) | {"__future__"}


class Index:
    def __init__(self, files: dict[str, GenFile]):
        self.files = files
        self.by_mod: dict[str, GenFile] = {}
        self.pkgs: set[str] = set()                    # namespace + regular packages (dirs)
        for f in files.values():
            self.by_mod[f.module] = f
            parts = f.module.split(".")
            for i in range(1, len(parts) + (0 if f.is_pkg else 0)):
                self.pkgs.add(".".join(parts[:i]))
            if f.is_pkg:
                self.pkgs.add(f.module)
        self.info = {m: ModInfo(f.tree, m, f.is_pkg) for m, f in self.by_mod.items()}
        self.ext_cache: dict[str, bool] = {}
        # repo-root modules the generated code may import (ours)
        self.root_files: dict[str, GenFile] = {}
        for name in ("contract", "contract_io"):
            p = ROOT / f"{name}.py"
            if p.exists() and name not in self.by_mod:
                gf = GenFile(ROOT, f"{name}.py", None)
                self.root_files[name] = gf
                self.info[name] = ModInfo(gf.tree, name, False)

    def kind(self, mod: str) -> str:
        """gen | pkg | root | stdlib | external | missing"""
        if mod in self.by_mod:
            return "gen"
        if mod in self.pkgs:
            return "pkg"
        if mod in self.root_files:
            return "root"
        top = mod.split(".")[0]
        if top in self.by_mod or top in self.pkgs:
            return "missing"                           # a gen package exists but this submodule does not
        if top in STDLIB:
            return "stdlib"
        if top not in self.ext_cache:
            try:
                self.ext_cache[top] = find_spec(top) is not None
            except Exception:
                self.ext_cache[top] = False
        return "external" if self.ext_cache[top] else "missing"

    def file_of(self, mod: str) -> GenFile | None:
        return self.by_mod.get(mod) or self.root_files.get(mod)

    def resolve(self, mod: str, name: str, depth: int = 0) -> tuple[str, dict | None, str]:
        """Find `name` in module `mod`. Returns (status, def_info, defining_module).
        status: ok | submodule | missing_symbol | opaque (ext/stdlib/star; cannot check)."""
        k = self.kind(mod)
        if k in ("stdlib", "external"):
            return "opaque", None, mod
        if k == "missing":
            return "unresolved_module", None, mod
        sub = f"{mod}.{name}"
        info = self.info.get(mod)
        if info is not None:
            if name in info.defs:
                return "ok", info.defs[name], mod
            if name in info.imports and depth < 6:
                m2, a2 = info.imports[name]
                if a2 is None:
                    return "ok", {"kind": "module", "sig": None, "line": None}, m2
                st, d, dm = self.resolve(m2, a2, depth + 1)
                if st in ("ok", "submodule", "opaque"):
                    return st, d, dm
            for sm in info.star:
                if depth < 6:
                    st, d, dm = self.resolve(sm, name, depth + 1)
                    if st in ("ok", "submodule"):
                        return st, d, dm
                    if st == "opaque":
                        return st, d, dm
        if sub in self.by_mod or sub in self.pkgs:
            return "submodule", {"kind": "module", "sig": None, "line": None}, sub
        if info is not None and info.star:
            return "opaque", None, mod
        return "missing_symbol", None, mod


# ------------------------------------------------------------------ arity
def check_call(sig: dict, call: ast.Call, is_method_bound=False) -> str | None:
    if sig is None:
        return None
    if any(isinstance(a, ast.Starred) for a in call.args) or any(k.arg is None for k in call.keywords):
        return None
    pos = sig["pos"]; n_req = len(pos) - sig["n_def"]
    n_pos = len(call.args)
    kws = [k.arg for k in call.keywords]
    if n_pos > len(pos) and not sig["vararg"]:
        return f"too many positional args: {n_pos} > {len(pos)}"
    for k in kws:
        if k not in pos[sig["posonly"]:] and k not in sig["kwonly"] and not sig["kwarg"]:
            return f"unexpected keyword {k!r}"
        if k in pos[:n_pos]:
            return f"keyword {k!r} duplicates a positional arg"
    missing = [p for p in pos[n_pos:n_req] if p not in kws]
    missing += [k for k in sig["kwonly_req"] if k not in kws]
    if missing:
        return "missing required args: " + ", ".join(missing)
    return None


def parse_public(item: str) -> tuple[str, int | None, bool]:
    """'name(a, b=1, *args) -> T' -> (name, n_args_excluding_self_and_star, has_varargs)."""
    item = item.strip()
    m = re.match(r"^(?:async\s+)?(?:def\s+|class\s+)?([A-Za-z_][\w.]*)\s*(\((.*)\))?", item, re.S)
    if not m:
        return item, None, False
    name = m.group(1)
    if m.group(2) is None:
        return name, None, False
    inner = m.group(3)
    # cut at the matching close paren
    depth, end = 0, len(inner)
    for i, ch in enumerate(inner):
        if ch in "([{":
            depth += 1
        elif ch in ")]}":
            if depth == 0:
                end = i; break
            depth -= 1
    inner = inner[:end]
    args, depth, cur = [], 0, ""
    for ch in inner:
        if ch in "([{":
            depth += 1
        elif ch in ")]}":
            depth -= 1
        if ch == "," and depth == 0:
            args.append(cur.strip()); cur = ""
        else:
            cur += ch
    if cur.strip():
        args.append(cur.strip())
    star = any(a.startswith("*") and a not in ("*",) for a in args)
    n = sum(1 for a in args if a not in ("self", "cls", "*", "/") and not a.startswith("*")
            and not a.startswith("self:") and not a.startswith("cls:"))
    return name, n, star


def sig_accepts(sig: dict, n: int) -> bool:
    total = len(sig["pos"]) + len(sig["kwonly"])
    pos = sig["pos"]
    if pos and pos[0] in ("self", "cls"):
        total -= 1
        n_req = len(pos) - 1 - sig["n_def"] + len(sig["kwonly_req"])
    else:
        n_req = len(pos) - sig["n_def"] + len(sig["kwonly_req"])
    if sig["vararg"] or sig["kwarg"]:
        return n >= n_req
    return n_req <= n <= total


# ------------------------------------------------------------------ D1
def check_d1(manifest, files: dict[str, GenFile], idx: Index) -> dict:
    items, file_rows = [], []
    for m in manifest:
        path = m.get("path", "")
        f = files.get(path)
        status = "ok" if f and not f.parse_error else ("missing_file" if f is None else "parse_error")
        if f and not f.off.get("terminated", True):
            status = "unterminated" if status == "ok" else status
        file_rows.append({"path": path, "status": status, "tok": f.start_tok if f else None})
        for pub in m.get("public") or []:
            if not isinstance(pub, str):
                continue
            name, n, star = parse_public(pub)
            row = {"path": path, "promise": pub, "symbol": name, "status": None, "detail": None,
                   "tok": f.start_tok if f else None}
            if f is None:
                row["status"] = "missing_file"
            elif f.parse_error:
                row["status"] = "parse_error"
            else:
                head, _, meth = name.partition(".")
                st, d, _dm = idx.resolve(f.module, head)
                if st not in ("ok", "submodule"):
                    row["status"] = "missing_symbol" if st != "opaque" else "ok_reexport_opaque"
                else:
                    sig = d.get("sig") if d else None
                    if meth and d and d.get("kind") == "class":
                        node = d.get("node"); sig = None; found = False
                        for st2 in node.body:
                            if isinstance(st2, (ast.FunctionDef, ast.AsyncFunctionDef)) and st2.name == meth:
                                sig, found = sig_of(st2), True
                        if not found:
                            row["status"] = "missing_symbol"; row["detail"] = f"no method {meth}"
                    if row["status"] is None:
                        if n is not None and sig is not None and d.get("kind") in ("def", "class") or (meth and sig):
                            if sig_accepts(sig, n) or star:
                                row["status"] = "ok"
                            else:
                                row["status"] = "arity_mismatch"
                                row["detail"] = f"promised {n} args; def has {sig['pos']} kwonly={sig['kwonly']}"
                        else:
                            row["status"] = "ok"
                    df = idx.by_mod.get(_dm)
                    if d and d.get("line") and df is not None:
                        row["tok"] = df.tok(d["line"])
            items.append(row)
    n_ok = sum(r["status"] in ("ok", "ok_reexport_opaque") for r in items)
    return {"files": file_rows, "symbols": items,
            "files_present": sum(r["status"] != "missing_file" for r in file_rows), "files_promised": len(file_rows),
            "symbols_ok": n_ok, "symbols_promised": len(items),
            "symbol_ok_rate": round(n_ok / len(items), 4) if items else None}


# ------------------------------------------------------------------ D2
def check_d2(files: dict[str, GenFile], idx: Index) -> tuple[list[dict], list[dict]]:
    edges, calls = [], []
    for rel, f in files.items():
        if f.tree is None:
            continue
        try:
            edges_f, calls_f = _d2_file(f, idx)
            edges += edges_f; calls += calls_f
        except Exception as e:                       # never crash on a weird file
            edges.append({"from_path": rel, "to_path": None, "symbol": None, "use_tok": None, "def_tok": None,
                          "distance": None, "status": "checker_error", "detail": repr(e)[:200]})
    return edges, calls


def _def_tok(idx: Index, mod: str, d: dict | None):
    gf = idx.by_mod.get(mod)
    if gf is None:
        return None, (f"{mod.replace('.', '/')}.py" if mod in idx.root_files else None)
    line = d.get("line") if d else None
    return gf.tok(line), gf.rel


def _d2_file(f: GenFile, idx: Index):
    edges, calls = [], []
    local: dict[str, tuple[str, str | None, int]] = {}      # name -> (module, attr, import line)
    for node in ast.walk(f.tree):
        if isinstance(node, ast.Import):
            for a in node.names:
                k = idx.kind(a.name)
                st = {"gen": "ok", "pkg": "ok", "root": "ok", "stdlib": "stdlib", "external": "external",
                      "missing": "unresolved_module"}[k]
                dtok, to = _def_tok(idx, a.name, None)
                if k == "root":
                    to = f"{a.name}.py"
                edges.append(_edge(f, to or a.name, a.name, node.lineno, dtok, st))
                local[a.asname or a.name.split(".")[0]] = (a.name if a.asname else a.name.split(".")[0], None,
                                                            node.lineno)
        elif isinstance(node, ast.ImportFrom):
            base = resolve_relative(f.module, f.is_pkg, node.module, node.level)
            for a in node.names:
                if a.name == "*":
                    k = idx.kind(base)
                    edges.append(_edge(f, base, "*", node.lineno, None,
                                       "unresolved_module" if k == "missing" else "star"))
                    continue
                st, d, dm = idx.resolve(base, a.name)
                status = {"ok": "ok", "submodule": "ok", "opaque": None, "missing_symbol": "missing_symbol",
                          "unresolved_module": "unresolved_module"}[st]
                if status is None:
                    status = "stdlib" if idx.kind(base) == "stdlib" else "external"
                dtok, to = _def_tok(idx, dm, d)
                if dm in idx.root_files:
                    to = f"{dm}.py"
                e = _edge(f, to or base, a.name, node.lineno, dtok, status)
                e["_mod"], e["_sig"], e["_kind"] = dm, (d or {}).get("sig"), (d or {}).get("kind")
                edges.append(e)
                local[a.asname or a.name] = (base, a.name, node.lineno)
    # call arity for imported names
    by_name = {}
    for e in edges:
        if e.get("_kind") in ("def", "class") and e["status"] == "ok":
            for loc, (m, attr, ln) in local.items():
                if attr == e["symbol"] and ln == e.get("_line"):
                    by_name[loc] = e
    for node in ast.walk(f.tree):
        if not isinstance(node, ast.Call):
            continue
        target = None
        if isinstance(node.func, ast.Name) and node.func.id in by_name:
            target = by_name[node.func.id]
        elif isinstance(node.func, ast.Attribute) and isinstance(node.func.value, ast.Name) \
                and node.func.value.id in local and local[node.func.value.id][1] is None:
            mod = local[node.func.value.id][0]
            st, d, dm = idx.resolve(mod, node.func.attr)
            if st == "ok" and d and d.get("kind") in ("def", "class"):
                dtok, to = _def_tok(idx, dm, d)
                target = {"_sig": d.get("sig"), "symbol": f"{node.func.value.id}.{node.func.attr}",
                          "to_path": to or (f"{dm}.py" if dm in idx.root_files else dm), "def_tok": dtok}
            elif st == "missing_symbol":
                calls.append({"from_path": f.rel, "line": node.lineno, "symbol": f"{mod}.{node.func.attr}",
                              "status": "missing_symbol", "use_tok": f.tok(node.lineno)})
                continue
        if target is None:
            continue
        err = check_call(target.get("_sig"), node)
        rec = {"from_path": f.rel, "to_path": target.get("to_path"), "symbol": target["symbol"],
               "line": node.lineno, "use_tok": f.tok(node.lineno), "def_tok": target.get("def_tok"),
               "status": "arity_mismatch" if err else "ok", "detail": err}
        calls.append(rec)
        if "_line" in target:                        # roll worst call status into the import edge
            target.setdefault("_calls", 0); target["_calls"] += 1
            if err and target["status"] == "ok":
                target["status"] = "arity_mismatch"; target["detail"] = f"line {node.lineno}: {err}"
                target["use_tok"] = f.tok(node.lineno)
    for e in edges:
        for k in ("_mod", "_sig", "_kind", "_line"):
            e.pop(k, None)
        e["calls"] = e.pop("_calls", 0)
        if e["use_tok"] is not None and e["def_tok"] is not None:
            e["distance"] = abs(e["use_tok"] - e["def_tok"])
    return edges, calls


def _edge(f: GenFile, to, sym, line, dtok, status):
    return {"from_path": f.rel, "to_path": to, "symbol": sym, "line": line, "use_tok": f.tok(line),
            "def_tok": dtok, "distance": None, "status": status, "_line": line}


# ------------------------------------------------------------------ D3
def contract_vocab() -> set[str]:
    v = set()
    try:
        tree = ast.parse((ROOT / "contract.py").read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and any(getattr(b, "id", "") == "Enum" or
                                                      getattr(b, "attr", "") == "Enum" for b in node.bases):
                for n in ast.walk(node):
                    if isinstance(n, ast.Constant) and isinstance(n.value, str):
                        v.add(n.value)
                    if isinstance(n, ast.Name) and n.id.isupper():
                        v.add(n.id)
    except Exception:
        pass
    v |= {"MOVE", "PULL", "PLACE", "DONE"}           # events.jsonl kinds from the contract comment
    # data identifiers that are legitimately uppercase
    try:
        for line in (ROOT / "data" / "rules.jsonl").read_text().splitlines():
            r = json.loads(line); v.add(r["rule_id"]); v.add(r["additive"]); v.update(r["jurisdictions"])
        for line in (ROOT / "data" / "stores.jsonl").read_text().splitlines():
            r = json.loads(line); v.add(r["dc_id"]); v.add(r["state"])
    except Exception:
        pass
    v |= {"CA", "US", "RED3", "UTC", "CONTINUATION", "STOP"}
    return v


UPPER_RE = re.compile(r"^[A-Z][A-Z0-9]*(?:_[A-Z0-9]+)+$|^[A-Z]{4,}[0-9]*$")


def check_d3(files: dict[str, GenFile], vocab: set[str]) -> list[dict]:
    out = []
    for rel, f in files.items():
        if f.tree is None:
            continue
        try:
            doc_ids = set()
            for node in ast.walk(f.tree):
                if isinstance(node, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                    b = node.body
                    if b and isinstance(b[0], ast.Expr) and isinstance(b[0].value, ast.Constant):
                        doc_ids.add(id(b[0].value))
            # skip f-string parts, os.environ keys, logging level names
            skip = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL", "UTF8", "ASCII", "JSON", "TRUE", "FALSE",
                    "NULL", "NONE", "TODO"}
            for node in ast.walk(f.tree):
                if isinstance(node, ast.JoinedStr):
                    for v in node.values:
                        doc_ids.add(id(v))
            for node in ast.walk(f.tree):
                if isinstance(node, ast.Constant) and isinstance(node.value, str) and id(node) not in doc_ids:
                    s = node.value
                    if UPPER_RE.match(s) and s not in vocab and s not in skip:
                        out.append({"path": rel, "line": node.lineno, "literal": s, "tok": f.tok(node.lineno),
                                    "is_test": f.is_test})
        except Exception as e:
            out.append({"path": rel, "line": None, "literal": None, "error": repr(e)[:200]})
    return out


# ------------------------------------------------------------------ D4
def run_one_test(gen: pathlib.Path, f: GenFile, timeout: int, tmp: pathlib.Path) -> dict:
    xml = tmp / (re.sub(r"[^\w]", "_", f.rel) + ".xml")
    env = dict(os.environ)
    env["PYTHONPATH"] = os.pathsep.join([str(gen.resolve()), str(ROOT)] +
                                        ([env["PYTHONPATH"]] if env.get("PYTHONPATH") else []))
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    cmd = [sys.executable, "-m", "pytest", str(f.path.resolve()), "-q", "-p", "no:cacheprovider",
           f"--junitxml={xml}", "-o", "addopts=", "--rootdir", str(gen.resolve()), "--no-header"]
    t0 = time.time()
    try:
        cp = subprocess.run(cmd, cwd=str(ROOT), env=env, capture_output=True, text=True, timeout=timeout)
        rc, out = cp.returncode, (cp.stdout + cp.stderr)
    except subprocess.TimeoutExpired as e:
        rc, out = "timeout", ((e.stdout or b"").decode(errors="replace") if isinstance(e.stdout, bytes)
                              else (e.stdout or ""))
    res = {"path": f.rel, "rc": rc, "secs": round(time.time() - t0, 1), "tok": f.start_tok,
           "tests": 0, "passed": 0, "failed": 0, "errors": 0, "skipped": 0, "cases": []}
    lines = {}
    if f.tree is not None:
        for n in ast.walk(f.tree):
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name.startswith("test"):
                lines.setdefault(n.name, n.lineno)
    collection_error = False
    if xml.exists():
        try:
            root = ET.parse(xml).getroot()
            for tc in root.iter("testcase"):
                name = tc.get("name", "")
                outcome, msg = "passed", None
                for child in tc:
                    if child.tag in ("failure", "error", "skipped"):
                        outcome = {"failure": "failed", "error": "error", "skipped": "skipped"}[child.tag]
                        msg = (child.get("message") or "")[:300]
                        if child.tag == "error" and "collection failure" in (child.get("message") or "").lower():
                            collection_error = True
                base = name.split("[")[0]
                res["cases"].append({"name": name, "outcome": outcome, "msg": msg,
                                     "tok": f.tok(lines.get(base)), "line": lines.get(base)})
        except ET.ParseError:
            pass
    for c in res["cases"]:
        res["tests"] += 1; res[c["outcome"] if c["outcome"] != "error" else "errors"] += 1
    if rc == "timeout":
        res["status"] = "timeout"
    elif rc in (2, 3, 4) or collection_error or (rc not in (0, 1, 5) and not res["cases"]):
        res["status"] = "collection_error"
    elif rc == 5:
        res["status"] = "no_tests"
    elif rc == 0:
        res["status"] = "passed"
    else:
        res["status"] = "failed" if res["failed"] else ("error" if res["errors"] else "failed")
    if res["status"] in ("collection_error", "timeout", "failed", "error"):
        tail = [l for l in out.splitlines() if l.strip()][-12:]
        res["output_tail"] = "\n".join(tail)[-1500:]
    return res


def check_d4(gen: pathlib.Path, files: dict[str, GenFile], timeout: int, jobs: int) -> list[dict]:
    tests = [f for f in files.values() if f.is_test]
    results = []
    with tempfile.TemporaryDirectory(prefix="vc_junit_") as td:
        tmp = pathlib.Path(td)
        with cf.ThreadPoolExecutor(max_workers=max(1, jobs)) as ex:
            futs = {ex.submit(run_one_test, gen, f, timeout, tmp): f for f in tests}
            for fu in cf.as_completed(futs):
                f = futs[fu]
                try:
                    results.append(fu.result())
                except Exception as e:
                    results.append({"path": f.rel, "status": "checker_error", "detail": repr(e)[:300],
                                    "tok": f.start_tok, "tests": 0, "passed": 0, "failed": 0, "errors": 0,
                                    "skipped": 0, "cases": []})
    return sorted(results, key=lambda r: (r.get("tok") or 0, r["path"]))


# ------------------------------------------------------------------ D6
PLACEHOLDER_RE = re.compile(r"#.*\b(TODO|FIXME|XXX|rest omitted|omitted for brevity|placeholder|implement (this|me)"
                            r"|left as an exercise|and so on)\b", re.I)


def is_stub_body(body) -> str | None:
    b = list(body)
    if b and isinstance(b[0], ast.Expr) and isinstance(b[0].value, ast.Constant) and isinstance(b[0].value.value, str):
        b = b[1:]
        if not b:
            return "docstring_only"
    if len(b) != 1:
        return None
    s = b[0]
    if isinstance(s, ast.Pass):
        return "pass"
    if isinstance(s, ast.Expr) and isinstance(s.value, ast.Constant) and s.value.value is Ellipsis:
        return "ellipsis"
    if isinstance(s, ast.Raise) and s.exc is not None:
        e = s.exc.func if isinstance(s.exc, ast.Call) else s.exc
        if getattr(e, "id", "") == "NotImplementedError":
            return "NotImplementedError"
    return None


def norm_line(l: str) -> str:
    l = l.strip()
    if not l or l.startswith("#"):
        return ""
    return re.sub(r"\s+", " ", l)


class _Norm(ast.NodeTransformer):
    def visit_Name(self, n):
        return ast.copy_location(ast.Name(id="_", ctx=n.ctx), n)

    def visit_Constant(self, n):
        return ast.copy_location(ast.Constant(value=0), n)

    def visit_arg(self, n):
        n.arg = "_"; n.annotation = None
        return n

    def visit_Attribute(self, n):
        self.generic_visit(n)
        return n


def check_d6(files: dict[str, GenFile]) -> dict:
    stubs, placeholders = [], []
    windows = defaultdict(list)
    test_bodies = defaultdict(list)
    total_lines = 0
    for rel, f in files.items():
        try:
            for i, line in enumerate(f.text.split("\n"), 1):
                if PLACEHOLDER_RE.search(line) or re.search(r"^\s*\.\.\.\s*$", line) and f.tree is None:
                    placeholders.append({"path": rel, "line": i, "text": line.strip()[:120], "tok": f.tok(i)})
            if f.tree is not None:
                for n in ast.walk(f.tree):
                    if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        k = is_stub_body(n.body)
                        if k:
                            # abstract methods / Protocol members are not padding
                            decos = {getattr(d, "id", getattr(d, "attr", "")) for d in n.decorator_list}
                            if "abstractmethod" in decos or "overload" in decos:
                                continue
                            stubs.append({"path": rel, "line": n.lineno, "name": n.name, "kind": k,
                                          "tok": f.tok(n.lineno), "is_test": f.is_test})
                        if f.is_test and n.name.startswith("test"):
                            try:
                                body = ast.Module(body=[_Norm().visit(ast.parse(ast.unparse(s)).body[0])
                                                        for s in n.body], type_ignores=[])
                                h = hashlib.sha1(ast.dump(body).encode()).hexdigest()
                                if len(n.body) >= 2:
                                    test_bodies[h].append({"path": rel, "name": n.name, "line": n.lineno,
                                                           "tok": f.tok(n.lineno)})
                            except Exception:
                                pass
            norm = [(i, norm_line(l)) for i, l in enumerate(f.text.split("\n"), 1)]
            norm = [(i, l) for i, l in norm if l]
            total_lines += len(norm)
            for k in range(0, max(0, len(norm) - 7)):
                win = norm[k:k + 8]
                text = "\n".join(l for _, l in win)
                if len(text) < 120:                  # trivial windows (imports, brackets) are noise
                    continue
                windows[hashlib.sha1(text.encode()).hexdigest()].append((rel, win[0][0], win[-1][0]))
        except Exception as e:
            placeholders.append({"path": rel, "line": None, "text": f"checker_error {e!r}"[:120], "tok": None})
    dup_lines = set(); dup_groups = []
    for h, locs in windows.items():
        distinct = {(p, s) for p, s, _ in locs}
        if len(distinct) < 2:
            continue
        # ignore overlapping self-repeats in the same place
        for p, s, e in locs[1:]:
            for ln in range(s, e + 1):
                dup_lines.add((p, ln))
        dup_groups.append({"locations": [{"path": p, "start": s, "end": e,
                                          "tok": files[p].tok(s) if p in files else None} for p, s, e in locs[:6]],
                           "count": len(locs)})
    near = [v for v in test_bodies.values() if len(v) > 1]
    dup_groups.sort(key=lambda g: -g["count"])
    return {"stubs": stubs, "placeholders": placeholders,
            "dup_window_groups": len(dup_groups), "dup_lines": len(dup_lines), "total_norm_lines": total_lines,
            "dup_share": round(len(dup_lines) / total_lines, 4) if total_lines else 0.0,
            "dup_examples": dup_groups[:25],
            "near_duplicate_tests": [{"count": len(v), "members": v[:8]} for v in near],
            "near_duplicate_test_count": sum(len(v) - 1 for v in near),
            "_dup_lines": dup_lines}


# ------------------------------------------------------------------ buckets
def build_buckets(files, d1, edges, calls, d3, d4, d6) -> dict:
    pos = defaultdict(lambda: defaultdict(int))
    for f in files.values():
        b = pos[bucket(f.start_tok, POS_BUCKETS)]
        b["files"] += 1; b["parsed"] += int(f.parse_error is None)
        b["unterminated"] += int(not f.off.get("terminated", True))
    for r in d1["symbols"]:
        b = pos[bucket(r.get("tok"), POS_BUCKETS)]
        b["d1_symbols"] += 1; b["d1_ok"] += int(r["status"] in ("ok", "ok_reexport_opaque"))
    for e in edges:
        if e["status"] in ("stdlib", "external"):
            continue
        b = pos[bucket(e.get("use_tok"), POS_BUCKETS)]
        b["d2_edges"] += 1; b["d2_ok"] += int(e["status"] in RESOLVED)
    for c in calls:
        b = pos[bucket(c.get("use_tok"), POS_BUCKETS)]
        b["d2_calls"] += 1; b["d2_calls_ok"] += int(c["status"] == "ok")
    for r in d3:
        pos[bucket(r.get("tok"), POS_BUCKETS)]["d3_bad_literals"] += 1
    for r in d4:
        b = pos[bucket(r.get("tok"), POS_BUCKETS)]
        b["d4_files"] += 1; b[f"d4_files_{r['status']}"] += 1
        for c in r.get("cases", []):
            cb = pos[bucket(c.get("tok") or r.get("tok"), POS_BUCKETS)]
            cb["d4_tests"] += 1; cb["d4_passed"] += int(c["outcome"] == "passed")
    for s in d6["stubs"]:
        pos[bucket(s.get("tok"), POS_BUCKETS)]["d6_stubs"] += 1
    for p in d6["placeholders"]:
        pos[bucket(p.get("tok"), POS_BUCKETS)]["d6_placeholders"] += 1
    for (p, ln) in d6["_dup_lines"]:
        if p in files:
            pos[bucket(files[p].tok(ln), POS_BUCKETS)]["d6_dup_lines"] += 1
    for f in files.values():
        pos[bucket(f.start_tok, POS_BUCKETS)]["norm_lines"] += sum(1 for l in f.text.split("\n") if norm_line(l))

    def rates(b):
        b = dict(b)
        for num, den, key in [("parsed", "files", "parse_rate"), ("d1_ok", "d1_symbols", "d1_rate"),
                              ("d2_ok", "d2_edges", "d2_resolve_rate"), ("d2_calls_ok", "d2_calls", "d2_arity_rate"),
                              ("d4_passed", "d4_tests", "d4_pass_rate"), ("d6_dup_lines", "norm_lines", "d6_dup_share")]:
            if b.get(den):
                b[key] = round(b.get(num, 0) / b[den], 4)
        return b

    dist = defaultdict(lambda: defaultdict(int))
    for e in edges + calls:
        if e.get("status") in ("stdlib", "external"):
            continue
        d = e.get("distance")
        if d is None and e.get("use_tok") is not None and e.get("def_tok") is not None:
            d = abs(e["use_tok"] - e["def_tok"])
        b = dist[bucket(d, DIST_BUCKETS)]
        kind = "calls" if "detail" in e and "calls" not in e else "edges"
        b[kind] += 1; b[f"{kind}_ok"] += int(e["status"] in ("ok", "star"))
    for b in dist.values():
        for k in ("edges", "calls"):
            if b.get(k):
                b[f"{k}_ok_rate"] = round(b.get(f"{k}_ok", 0) / b[k], 4)
    order = [n for _, _, n in POS_BUCKETS] + ["unknown"]
    dorder = [n for _, _, n in DIST_BUCKETS] + ["unknown"]
    return {"position": {k: rates(pos[k]) for k in order if k in pos},
            "distance": {k: dict(dist[k]) for k in dorder if k in dist}}


# ------------------------------------------------------------------ main
def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("gen"); ap.add_argument("--offsets"); ap.add_argument("--report")
    ap.add_argument("--no-tests", action="store_true"); ap.add_argument("--timeout", type=int, default=60)
    ap.add_argument("--jobs", type=int, default=4)
    ap.add_argument("--deps", help="deps.jsonl path (default: <report stem minus _code>_deps.jsonl next to report)")
    a = ap.parse_args(argv)
    gen = pathlib.Path(a.gen)
    name = gen.resolve().name
    offsets = load_offsets(pathlib.Path(a.offsets) if a.offsets else gen / "offsets.jsonl")
    report_p = pathlib.Path(a.report) if a.report else ROOT / "reports" / f"{name}_code.json"
    report_p.parent.mkdir(parents=True, exist_ok=True)
    t0 = time.time()

    files: dict[str, GenFile] = {}
    load_errors = []
    for p in sorted(gen.rglob("*.py")):
        if any(part in SKIP_DIRS for part in p.parts):
            continue
        rel = p.relative_to(gen).as_posix()
        try:
            files[rel] = GenFile(gen, rel, offsets.get(rel))
        except Exception as e:
            load_errors.append({"path": rel, "error": repr(e)[:200]})
    manifest = load_manifest(gen)
    idx = Index(files)

    def guarded(fn, default, label):
        try:
            return fn()
        except Exception:
            load_errors.append({"path": None, "error": f"{label} crashed: {traceback.format_exc()[-800:]}"})
            return default

    d1 = guarded(lambda: check_d1(manifest, files, idx), {"files": [], "symbols": [], "symbol_ok_rate": None}, "D1")
    edges, calls = guarded(lambda: check_d2(files, idx), ([], []), "D2")
    d3 = guarded(lambda: check_d3(files, contract_vocab()), [], "D3")
    d4 = [] if a.no_tests else guarded(lambda: check_d4(gen, files, a.timeout, a.jobs), [], "D4")
    d6 = guarded(lambda: check_d6(files), {"stubs": [], "placeholders": [], "_dup_lines": set(),
                                             "dup_share": 0.0, "near_duplicate_test_count": 0}, "D6")
    buckets = guarded(lambda: build_buckets(files, d1, edges, calls, d3, d4, d6), {}, "buckets")
    d6.pop("_dup_lines", None)

    internal = [e for e in edges if e["status"] not in ("stdlib", "external")]
    totals = {
        "files": len(files), "parsed": sum(f.parse_error is None for f in files.values()),
        "unterminated": sum(not f.off.get("terminated", True) for f in files.values()),
        "manifest_files": len(manifest), "manifest_files_present": d1.get("files_present"),
        "d1_symbol_ok_rate": d1.get("symbol_ok_rate"),
        "d2_edges": len(internal), "d2_resolved": sum(e["status"] in RESOLVED for e in internal),
        "d2_resolve_rate": round(sum(e["status"] in RESOLVED for e in internal) / len(internal), 4)
        if internal else None,
        "d2_calls_checked": len(calls), "d2_arity_mismatch": sum(c["status"] == "arity_mismatch" for c in calls),
        "d3_bad_literals": len(d3), "d3_bad_literals_nontest": sum(not r.get("is_test") for r in d3),
        "d4_files": len(d4), "d4_tests": sum(r.get("tests", 0) for r in d4),
        "d4_passed": sum(r.get("passed", 0) for r in d4),
        "d4_by_status": {s: sum(r["status"] == s for r in d4) for s in sorted({r["status"] for r in d4})},
        "d6_stubs": len(d6["stubs"]), "d6_placeholders": len(d6.get("placeholders", [])),
        "d6_dup_share": d6.get("dup_share"), "d6_near_dup_tests": d6.get("near_duplicate_test_count"),
        "max_tok": max([f.end_tok or 0 for f in files.values()] or [0]),
    }
    report = {"gen_dir": str(gen), "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S"), "secs": None,
              "totals": totals, "buckets": buckets,
              "parse_errors": [{"path": r, "tok": f.tok((f.parse_error or {}).get("line")), **f.parse_error}
                               for r, f in files.items() if f.parse_error],
              "files": [{"path": r, "start_tok": f.start_tok, "end_tok": f.end_tok,
                         "terminated": f.off.get("terminated", True), "parse_ok": f.parse_error is None,
                         "lines": f.text.count("\n")} for r, f in files.items()],
              "d1": d1, "d2": {"edges_bad": [e for e in edges if e["status"] not in ("ok", "stdlib", "external", "star")],
                               "calls_bad": [c for c in calls if c["status"] != "ok"], "calls_checked": len(calls)},
              "d3": d3, "d4": d4, "d6": d6, "errors": load_errors}
    for s in d1.get("symbols", []):
        s.pop("node", None)
    report["secs"] = round(time.time() - t0, 1)
    report_p.write_text(json.dumps(report, indent=2, default=str) + "\n")
    deps_p = pathlib.Path(a.deps) if a.deps else report_p.with_name(
        (report_p.stem[:-5] if report_p.stem.endswith("_code") else report_p.stem) + "_deps.jsonl")
    with open(deps_p, "w") as fh:
        for e in edges:
            fh.write(json.dumps({k: e.get(k) for k in ("from_path", "to_path", "symbol", "use_tok", "def_tok",
                                                       "distance", "status", "line", "detail")}) + "\n")
        for c in calls:
            if c["status"] != "ok":
                fh.write(json.dumps({"from_path": c["from_path"], "to_path": c.get("to_path"), "symbol": c["symbol"],
                                     "use_tok": c.get("use_tok"), "def_tok": c.get("def_tok"),
                                     "distance": abs(c["use_tok"] - c["def_tok"])
                                     if c.get("use_tok") is not None and c.get("def_tok") is not None else None,
                                     "status": c["status"], "line": c.get("line"), "detail": c.get("detail"),
                                     "kind": "call"}) + "\n")

    t = totals
    print(f"{gen}: {t['files']} files, {t['parsed']} parse, {t['unterminated']} unterminated, max tok ~{t['max_tok']}")
    print(f"  D1 manifest files {t['manifest_files_present']}/{t['manifest_files']}, symbols ok "
          f"{d1.get('symbols_ok')}/{d1.get('symbols_promised')}")
    print(f"  D2 internal imports {t['d2_resolved']}/{t['d2_edges']} resolve, {t['d2_arity_mismatch']} arity "
          f"mismatches in {t['d2_calls_checked']} calls")
    print(f"  D3 {t['d3_bad_literals']} uppercase literals outside the contract vocabulary "
          f"({t['d3_bad_literals_nontest']} outside tests)")
    if not a.no_tests:
        print(f"  D4 {t['d4_passed']}/{t['d4_tests']} tests pass in {t['d4_files']} files {t['d4_by_status']}")
    print(f"  D6 {t['d6_stubs']} stubs, {t['d6_placeholders']} placeholders, dup share {t['d6_dup_share']}, "
          f"{t['d6_near_dup_tests']} near-duplicate tests")
    for k, b in (buckets.get("position") or {}).items():
        print(f"  [{k}] files {b.get('files', 0)} parse {b.get('parse_rate')} D1 {b.get('d1_rate')} "
              f"D2 {b.get('d2_resolve_rate')}/{b.get('d2_arity_rate')} D4 {b.get('d4_pass_rate')}")
    if load_errors:
        print(f"  {len(load_errors)} checker errors (see report)")
    print(f"  report {report_p}  deps {deps_p}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
