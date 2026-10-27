# The lab

A place to build a new idea next to the app without touching the app. When the idea works, one command moves it in.

## Start

Double-click `lab.bat` (Windows), or from the main folder run `python build_and_test/lab/lab.py`. A menu opens:

1. **New idea**: makes `lab/<name>/` from the template.
2. **List ideas**: shows each idea and its status (idea, building, ready).
3. **Check an idea**: runs every test and rule. Says "Ready" or tells you what is wrong.
4. **Move an idea into the app (promote)**: copies the files in and prints the list to upload to GitHub.

Command line: `lab.bat short <name>` runs `check` and prints a report of at most 20 lines (verdict READY / NOT READY / NO TEST, the problems, and each failed test with its error line). `lab.bat check <name>` gives the full output. `lab.bat ask <name>` is `short` plus a copy to the clipboard. `lab.bat pack` builds `bgtools_src.zip` and shows its size. `lab.bat apply [zip]` unpacks a zip from Claude over the repo (backs up what it replaces), and `lab.bat go <name>` does `apply` then `ask`. These live in `_ai_harness/`: folders that start with `_` are lab tooling, not ideas, so `list`, `check` and `promote` ignore them.

## What an idea folder holds

```
lab/<name>/
  IDEA.md      goal, an example, where files go, hook-up edits, "done when"
  tests/       tests for this idea (start with the example from IDEA.md)
  fixtures/    sample data for this idea (see "Terminal drawings" below)
  bgtools/     the new code, in the SAME folders it will have in the app
               e.g. bgtools/analysis/pairs.py
```

Because the folders match the app, promoting is a plain copy. Nothing needs to be renamed or rewritten.

## Terminal drawings (headers, colors)

The maintainer keeps the terminal drawing pieces (headers, banners, colors) in a `fixtures/` folder in the lab, because they are meant to be promoted into `bgtools`. Check before relying on this: `lab.py promote` copies `fixtures/` to `build_and_test/tests/fixtures/<idea>/` (test data), not into `bgtools/`. Anything that must ship has to be a `.py` file under `<idea>/bgtools/ui/` (the `ui` layer may import only `core`). The drawings are a UI adapter (they only draw what a `Snapshot` holds). Open question: either move the drawings there, or change `promote` so a drawing folder goes to `bgtools/ui/`. The `bgtools_src.zip` uploaded on 2026-10-13 had no such folder, so its path is not recorded here.

## Promoting a change to files the app already has (a "v2")

`check` rejects any idea file that is a copy of an app file, so a v2 that rewrites `delta.py` cannot be promoted as is.
Worked example: `buyingdelta_v2` became `adapter_buy_delta` (2026-10-21). The recipe:

1. Make a normal idea folder (`lab.py new <name>`). Put the changed code at NEW paths (a renamed folder, `adapter_<name>/`)
   and the tests under NEW names (`test_<name>*.py`; promote refuses a test file that exists with different content).
2. In `IDEA.md` Hook-up, list every edit to an existing file (imports, the `ALLOWED` rows in `test_architecture.py`,
   `ARCHITECTURE.md`, `build_exe.bat`) and every file to delete (the old folder and old tests).
3. Write them as exact find-and-replace edits in `hookup_apply.py` (`--undo` restores). It must say "nothing to do" on a
   second run, and must change nothing if any edit does not match exactly once.
4. Run, from the repo root (the folder that holds `build_and_test`; one level too deep fails with "No such file"):
   `hookup_apply.py` -> `make_map.py` -> `lab.bat check <name>` -> `lab.bat promote <name>` -> `make_map.py` ->
   `python -m unittest discover -s build_and_test\tests`.
   `check` needs the `ALLOWED` row (so the hook-up goes first) and a map that matches the app (so `make_map.py` goes before it).
5. Add the changelog line `promote` prints. A folder you promoted by hand never moves itself: move it to `_promoted/`.

In PowerShell, unzip with the full path: `Expand-Archive -Force "C:\path\to\file.zip" .` (or `... build_and_test\lab` for an idea folder).

## The loop

1. `new` an idea. Fill in the Goal and Example in `IDEA.md`.
2. Turn the Example into a test in `tests/`. It fails.
3. Write the code under `bgtools/<layer>/` until it passes.
4. `check <name>`. Fix anything it lists.
5. `promote <name>`. Upload the files it lists. Add the changelog line it prints.

## What `check` looks at

- All app tests still pass with your idea laid over the app.
- Your idea has at least one real test (a skipped test does not count).
- Each file imports only from layers it is allowed to (see `docs/ARCHITECTURE.md`).
- Each `.py` file has the license header.
- No file is a copy of an app file (the lab cannot test edits to app files; add a new file instead).
- No files directly in `bgtools/` (those change how the app starts; write them under "Hook-up" in `IDEA.md` instead).

## Good to know

- `BACKLOG.md` is the list of ideas waiting their turn: one line each. When you start one, run `new`, then delete its line. It also lists plans for separate GitHub repositories (the lab itself, a BGIQ wiki); those are not lab ideas.
- `_template/` is the starting copy. `_promoted/` holds ideas already moved into the app (delete them any time).
- `pairs/` is a small finished example. You can promote it, or delete the folder.
- Besides `IDEA.md`, `tests/`, `fixtures/` and `bgtools/`, an idea can hold `preview.bat` / `preview.py` (a way to see it without a game, or `--live` with one) and `hookup_apply.py` (applies the Hook-up edits, `--undo` restores them). `promote` copies only `bgtools/`, `tests/` and `fixtures/`; anything else (such as a `<name>.bat` for the repo root) is listed in `IDEA.md` and moved by hand.
- The lab never ships in the `.exe`.
- Promote also copies your tests into `build_and_test/tests/`, so the app keeps checking the idea.
- Advice rules (`rule_<name>.py`) and commands (`cmd_<name>.py`) are picked up automatically, so they need no hook-up. A new screen piece still does.
- After promoting, run `python build_and_test/tools/make_map.py` to refresh `docs/MAP.md`.
- Edits to files the idea does not own (like adding a line to `__main__.py`) are written in `IDEA.md` under "Hook-up". Promote prints them for you to do by hand.

> Needs the bgtools app next to it to run (lab.py expects the app two folders above).
