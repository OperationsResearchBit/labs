# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026 bgtools contributors
"""The lab: build a new idea next to the app, then move it in when it works.

Run with no arguments for a menu:   python build_and_test/lab/lab.py
Or directly:  new NAME | list | check NAME | promote NAME

A lab feature is a folder, lab/NAME/, that looks like a small copy of the app:

    lab/NAME/IDEA.md        what it is, an example, the hook-up lines, "done when"
    lab/NAME/bgtools/...    new files, in the same folders they will have in the app
    lab/NAME/tests/         tests for this idea
    lab/NAME/fixtures/      sample data for this idea

While you work, the lab lays your folder over the real bgtools package, so
`from bgtools.analysis.foo import bar` works for a file that is not in the app yet.
Promoting copies lab/NAME/bgtools/ onto the app's bgtools/. No imports change.
"""

from __future__ import annotations

import importlib
import os
import shutil
import subprocess
import sys
import unittest
from pathlib import Path

LAB = Path(__file__).resolve().parent
ROOT = LAB.parents[1]                      # repo root (the folder with run_bgtools.bat)
APP = ROOT / "bgtools"
TESTS = ROOT / "build_and_test" / "tests"
TEMPLATE = LAB / "_template"
PROMOTED = LAB / "_promoted"
LICENSE_LINE = "# SPDX-License-Identifier: AGPL-3.0-or-later"
EXIT_NO_TESTS = 3


# --- helpers -----------------------------------------------------------------

def features():
    return sorted(p for p in LAB.iterdir() if p.is_dir() and not p.name.startswith(("_", ".")))


def feature_dir(name: str) -> Path:
    d = LAB / name
    if not d.is_dir() or name.startswith("_"):
        sys.exit(f"No lab feature named '{name}'. Try:  list")
    return d


def files_of(feature: Path):
    src = feature / "bgtools"
    return sorted(p for p in src.rglob("*") if p.is_file() and "__pycache__" not in p.parts
                  and p.suffix != ".pyc") if src.exists() else []


def status_of(feature: Path) -> str:
    idea = feature / "IDEA.md"
    if idea.exists():
        for line in idea.read_text(encoding="utf-8").splitlines():
            if line.lower().startswith("status:"):
                return line.split(":", 1)[1].strip().split()[0] if line.split(":", 1)[1].strip() else "?"
    return "?"


def section(feature: Path, title: str) -> str:
    """Text under '## title' in IDEA.md (up to the next '## ')."""
    idea = feature / "IDEA.md"
    if not idea.exists():
        return ""
    out, on = [], False
    for line in idea.read_text(encoding="utf-8").splitlines():
        if line.startswith("## "):
            on = line[3:].strip().lower().startswith(title.lower())
            continue
        if on:
            out.append(line)
    return "\n".join(out).strip()


# --- overlay: lay the feature's folder over the real package -----------------

def overlay(feature: Path) -> None:
    """Make lab/NAME/bgtools/** importable as if it were inside bgtools/."""
    sys.path.insert(0, str(ROOT))
    src = feature / "bgtools"
    dirs = [src] + sorted((p for p in src.rglob("*") if p.is_dir() and p.name != "__pycache__"),
                          key=lambda p: len(p.parts))
    pkgs = []
    for d in dirs:
        module = ".".join(d.relative_to(feature).parts)
        pkg = importlib.import_module(module)
        if str(d) not in pkg.__path__:
            pkg.__path__.append(str(d))
        pkgs.append(pkg)
    for pkg in pkgs:                          # packages that auto-import rule_*.py / cmd_*.py
        found = getattr(pkg, "discover", None)
        if callable(found):
            found()


# --- static checks -----------------------------------------------------------

def static_checks(feature: Path):
    """Return (problems, notes) about the feature's files."""
    sys.path.insert(0, str(TESTS))
    import test_architecture as arch          # reuse the app's own layer rule
    problems, notes = [], []
    for f in files_of(feature):
        rel = f.relative_to(feature)           # bgtools/<layer>/...
        parts = rel.parts
        if len(parts) == 2 and f.suffix == ".py":
            problems.append(f"{rel}: files directly in bgtools/ belong in IDEA.md 'Hook-up', "
                            "not in the lab (they change how the app starts)")
            continue
        if f.suffix == ".py":
            text = f.read_text(encoding="utf-8")
            if text.strip() and not text.startswith(LICENSE_LINE):
                problems.append(f"{rel}: missing the license header (copy it from any app file)")
            layer = parts[1] if len(parts) > 2 else None
            if layer in arch.ALLOWED:
                for target in arch.bgtools_imports(f):
                    if target != layer and target not in arch.ALLOWED[layer]:
                        problems.append(f"{rel}: layer '{layer}' may not import bgtools.{target}")
            elif layer:
                problems.append(f"{rel}: unknown layer '{layer}'")
        if (ROOT / rel).exists():
            problems.append(f"{rel}: is a copy of an app file. The lab cannot test edits to app "
                            "files (tests would still run the app's version). Put new code in a "
                            "NEW file (rule_<name>.py, cmd_<name>.py, ...) and list the edit "
                            "under 'Hook-up' in IDEA.md")
    return problems, notes


# --- running tests (in a fresh process so the overlay never leaks) -----------

def run_tests_inner(name: str) -> int:
    feature = feature_dir(name)
    overlay(feature)
    sys.path.insert(0, str(TESTS))
    ftests = feature / "tests"
    if ftests.exists():
        sys.path.insert(0, str(ftests))
    loader = unittest.TestLoader()
    print(f"== App tests, with '{name}' laid over the app")
    app = unittest.TextTestRunner(verbosity=0).run(loader.discover(str(TESTS), top_level_dir=str(TESTS)))
    print(f"\n== Tests for '{name}'")
    mine = unittest.TextTestRunner(verbosity=1).run(
        loader.discover(str(ftests), top_level_dir=str(ftests)) if ftests.exists()
        else unittest.TestSuite())
    if not (app.wasSuccessful() and mine.wasSuccessful()):
        return 1
    return 0 if mine.testsRun - len(mine.skipped) > 0 else EXIT_NO_TESTS


def check(name: str) -> int:
    feature = feature_dir(name)
    problems, notes = static_checks(feature)
    print(f"Checking '{name}'  ({len(files_of(feature))} file(s), status: {status_of(feature)})")
    for n in notes:
        print("  note:", n)
    for p in problems:
        print("  PROBLEM:", p)
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    code = subprocess.call([sys.executable, str(Path(__file__).resolve()), "_test", name],
                           cwd=str(ROOT), env=env)
    if code == EXIT_NO_TESTS:
        print("\nNot ready: no real test for this idea yet (skipped tests do not count).")
    elif code != 0:
        print("\nNot ready: some tests failed.")
    if problems:
        print("\nNot ready: fix the PROBLEM lines above.")
    ok = code == 0 and not problems
    if ok:
        print("\nReady. Next:  promote", name)
    return 0 if ok else 1


# --- commands ----------------------------------------------------------------

def new(name: str) -> int:
    name = name.strip().lower().replace(" ", "_").replace("-", "_")
    if not name.isidentifier():
        print("Use letters, numbers and underscores only, for example: pair_alert")
        return 2
    dest = LAB / name
    if dest.exists():
        print(f"'{name}' already exists.")
        return 2
    shutil.copytree(TEMPLATE, dest, ignore=shutil.ignore_patterns("__pycache__"))
    for p in dest.rglob("*"):
        if p.is_file() and p.suffix in {".md", ".py"}:
            p.write_text(p.read_text(encoding="utf-8").replace("{{name}}", name), encoding="utf-8")
    (dest / "tests" / "test_idea.py").rename(dest / "tests" / f"test_{name}.py")
    for sub in ("bgtools", "fixtures"):
        (dest / sub).mkdir(exist_ok=True)
    print(f"Created build_and_test/lab/{name}/")
    print("1. Fill in IDEA.md (goal, example, where the files go).")
    print("2. Write the example as a test in tests/.")
    print(f"3. Put new code under lab/{name}/bgtools/<layer>/ and run:  check {name}")
    return 0


def list_features() -> int:
    items = features()
    if not items:
        print("No ideas in the lab yet. Create one with:  new NAME")
    for f in items:
        print(f"  {f.name:<24} {status_of(f):<10} {len(files_of(f))} file(s)")
    if PROMOTED.exists() and any(PROMOTED.iterdir()):
        print("  (already moved into the app: " + ", ".join(sorted(p.name for p in PROMOTED.iterdir())) + ")")
    return 0


def promote(name: str, assume_yes: bool = False) -> int:
    feature = feature_dir(name)
    if check(name) != 0:
        print("\nNot promoted. Fix the problems above first.")
        return 1
    files = files_of(feature)
    n_tests = len(list((feature / "tests").glob("test_*.py"))) if (feature / "tests").exists() else 0
    print(f"\nThis copies {len(files)} file(s) into the app's bgtools/ folder"
          f" and {n_tests} test file(s) into build_and_test/tests/:")
    for f in files:
        rel = f.relative_to(feature)
        print("  ", rel, "(replaces existing)" if (ROOT / rel).exists() else "(new)")
    if not assume_yes and input("Go ahead? (y/n): ").strip().lower() != "y":
        print("Cancelled. Nothing changed.")
        return 1
    tests = sorted((feature / "tests").glob("test_*.py")) if (feature / "tests").exists() else []
    clash = [t.name for t in tests if (TESTS / t.name).exists()
             and (TESTS / t.name).read_bytes() != t.read_bytes()]
    if clash:
        print("\nNot promoted: these test files already exist in the app with different content:",
              ", ".join(clash), "\nRename yours in lab/%s/tests/ and try again." % name)
        return 1
    changed = []
    for t in tests:
        dest = TESTS / t.name
        if not dest.exists():
            shutil.copy2(t, dest)
            changed.append(dest.relative_to(ROOT))
    fx = feature / "fixtures"
    for f in (sorted(p for p in fx.rglob("*") if p.is_file() and p.name != ".gitkeep") if fx.exists() else []):
        dest = TESTS / "fixtures" / name / f.relative_to(fx)
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(f, dest)
        changed.append(dest.relative_to(ROOT))
    for f in files:
        rel = f.relative_to(feature)
        dest = ROOT / rel
        if dest.exists() and dest.read_bytes() == f.read_bytes():
            continue
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(f, dest)
        changed.append(rel)
    PROMOTED.mkdir(exist_ok=True)
    target = PROMOTED / name
    n = 2
    while target.exists():
        target = PROMOTED / f"{name}_{n}"
        n += 1
    shutil.move(str(feature), str(target))
    print(f"\nDone. The idea folder moved to lab/_promoted/{target.name}/ (delete it any time).")
    print("\nUpload these files to GitHub:")
    for rel in changed:
        print("  ", rel)
    hook = section(target, "Hook-up")
    if hook and not hook.lower().lstrip(" .-*").startswith("none"):
        print("\nStill to do by hand (from IDEA.md, Hook-up):\n" + hook)
    line = section(target, "Changelog line")
    if line:
        print("\nAdd to docs/CHANGELOG.md:\n  " + line)
    print("\nRegenerate the repo map:  python build_and_test/tools/make_map.py")
    print("Then run the app tests once more:  python -m unittest discover -s build_and_test/tests")
    return 0


def menu() -> int:
    while True:
        print("\nBGTOOLS LAB\n  1  New idea\n  2  List ideas\n  3  Check an idea\n"
              "  4  Move an idea into the app (promote)\n  q  Quit")
        pick = input("> ").strip().lower()
        if pick in {"q", ""}:
            return 0
        if pick == "1":
            new(input("Name for the idea (e.g. pair_alert): "))
        elif pick == "2":
            list_features()
        elif pick in {"3", "4"}:
            list_features()
            name = input("Which one? ").strip()
            if name:
                (check if pick == "3" else promote)(name)


def main(argv=None) -> int:
    a = list(sys.argv[1:] if argv is None else argv)
    if not a:
        return menu()
    cmd, rest = a[0], a[1:]
    if cmd == "_test" and rest:
        return run_tests_inner(rest[0])
    if cmd == "new" and rest:
        return new(rest[0])
    if cmd == "list":
        return list_features()
    if cmd == "check" and rest:
        return check(rest[0])
    if cmd == "promote" and rest:
        return promote(rest[0], assume_yes="--yes" in rest)
    tool = LAB / "_ai_harness" / f"{cmd}.py"
    if cmd.isidentifier() and tool.exists():
        return subprocess.call([sys.executable, str(tool), *rest])
    print(__doc__)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())