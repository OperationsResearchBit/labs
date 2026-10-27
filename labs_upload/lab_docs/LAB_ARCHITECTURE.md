# Lab architecture (for AI assistants; short on purpose)

Read this instead of opening `lab.py`. Rules of work are in `lab/CLAUDE.md`; this file says how the lab is built.
Not the app's `docs/ARCHITECTURE.md` (that one is for people and is not needed for lab work).

## Idea in one line

A lab idea is a folder shaped like a small copy of the app. While you work, the lab lays that folder over the real `bgtools` package, so lab files import as if already promoted. `promote` copies the folder onto the app. No imports change.

## Layout

```
build_and_test/lab/
  lab.py / lab.bat        menu + commands: new NAME | list | check NAME | promote NAME | short, ask, pack, apply, go (from _ai_harness/)
  run_lab.py / .bat       run the real app with ONE idea laid over it (any bgtools command works)
  CLAUDE.md               work rules for AI (read first)
  lab_docs/               BACKLOG.md, BACKLOG_CLAUDE.md, STARTER_PROMPT.md, this file
  _template/              what `new` copies: IDEA.md + tests/test_idea.py
  _ai_harness/            lab tooling, not an idea: each <n>.py is a command `lab.bat <n>` (today: short, ask, pack, apply, go); helpers/, tests/, README.md
  _promoted/              created by `promote`: finished ideas are moved here (absent until first promote)
  <idea>/
    IDEA.md               Goal, Example, Files, Hook-up, Status (idea / building / ready)
    bgtools/<layer>/...   NEW files only, at the exact path they will have in the app
    tests/test_<idea>.py  the Example as a failing test first
    fixtures/             sample data (never a real Power.log)
```

Ideas are every folder in `lab/` whose name does not start with `_` or `.` (so `lab.py list` also shows `lab_docs/`; backlog `fix lab_list_counts_docs`). `_ai_harness/` is tooling, so `list`, `check` and `promote` skip it.

## What each command does (lab.py)

| Command | Behavior |
|---|---|
| `new NAME` | Copies `_template/` to `lab/NAME/`. |
| `list` | Lists ideas with the Status from each `IDEA.md`. |
| `check NAME` | Static checks first (layer rule via `test_architecture`, license lines, no copies of app files, no `.py` directly in `lab/<idea>/bgtools/`), then runs the idea's tests in a FRESH process with the overlay on, so nothing leaks. Only the user's pasted "Ready" output counts. |
| `short NAME` | In `_ai_harness/short.py`. Runs `check NAME` as a child process and prints at most 20 lines: verdict (READY / NOT READY / NO TEST), `problem:` and `note:` lines, failed tests with their exception line (no tracebacks), app failures marked `app failed:`. Same exit code as `check`. `main` in lab.py hands any unknown command `<n>` to `_ai_harness/<n>.py` (last, so a tool can never replace `new`, `list`, `check` or `promote`). Its READY counts the same as `check`'s Ready. |
| `ask NAME` | `short NAME` plus a copy of the report to the clipboard (`clip` on Windows). |
| `pack` | Builds `bgtools_src.zip` from the current folder (same rules as `onezip.txt`: skips venv, `_promoted`, `_orig`, `_apply_backup`, dist, data, samples; leaves out `combat_odds_log.txt` and the changelogs). Prints file count, size, rough tokens and the five biggest files; warns above 700 KB. |
| `apply [ZIP] [--dry]` | Unpacks a zip from Claude over the repo (paths start at the repo root). No ZIP: newest `.zip` in Downloads, not `bgtools_src*`. Replaced files go to `_apply_backup/<time>/`. Refuses the whole zip on an absolute path, `..`, `.git` or a top folder the repo lacks. |
| `go NAME [ZIP]` | `apply`, then `ask NAME`. Stops if `apply` refuses. |
| `promote NAME` | Copies `<idea>/bgtools/` onto `bgtools/`, `tests/` and `fixtures/` into `build_and_test/tests/` (fixtures to `tests/fixtures/<idea>/`), prints hook-up edits for the user to do by hand, moves the idea to `_promoted/`. Then the user runs `make_map.py`. |

## The overlay (`overlay()` in lab.py)

For `lab/<idea>/bgtools/` and each sub-folder, import the matching package and append the lab folder to its `__path__`. Packages with a `discover()` (`commands`, `analysis/recommender`) are then re-scanned, so `cmd_*.py` and `rule_*.py` from the lab register themselves. Consequences:
- A new command or rule needs NO hook-up.
- An edit to an existing app file cannot be overlaid; it must be listed under Hook-up in `IDEA.md`.
- A lab file with the same path as an app file is ignored in favor of the app's, so `check` rejects such copies.
- A new screen piece is not shown by `run_lab`; it needs hand edits (see `lab/CLAUDE.md`, "Where each kind of idea goes").

## Hook-up edits (`combat_sim` and `simpreview_visual` have a `hookup_apply.py`)

`<idea>/hookup_apply.py [--undo]` applies exact find-and-replace edits to app files. `simpreview_visual/hookup_apply.py` is the newer, smaller model to copy: it also handles Windows line endings and is safe to run twice. Each must match exactly once or nothing changes; already-applied edits are skipped. Originals go to `combat_sim/_orig/`. The `hookup_edits_*.py` files are data imported by it, never run directly. Lab-only extras there: `run_display.*`, `winlossapp/`, `combat_sim_docs/`.

## Where to look, by question

| Question | Open |
|---|---|
| What may I put in the lab, and how do I deliver it? | `lab/CLAUDE.md` |
| What should I work on? | `lab_docs/BACKLOG.md` (only when asked), run it with `BACKLOG_CLAUDE.md` |
| Why is the fight calculator built this way? | `combat_sim/combat_sim_docs/DECISIONS.md` |
| What are the combat_sim plan and next steps? | `combat_sim/combat_sim_docs/PLAN_AND_RESEARCH.md` |
| How does promote/check work in detail? | grep `def promote` / `def check` in `lab.py`; do not read the whole file |
| What is the AI harness and what is built? | `_ai_harness/README.md` (tests: `python -m unittest discover -s _ai_harness/tests`, from the lab folder) |
| Layer rules | root `CLAUDE.md` (enforced by `build_and_test/tests/test_architecture.py`) |

## Ideas in the lab (2026-10-26)

| Idea | State |
|---|---|
| `_ai_harness` | tooling, not an idea: `short`, `ask`, `pack` (run by the user, 2026-10-26) and `apply`, `go` (written, tests pass, not yet tried on a real zip); `status` is planned. See its README.md. Not run by the AI (see `lab/CLAUDE.md`) |
| `combat_sim` | partly shipped (preview part, and `cmd_combat_sim.py` now lives in the app); `short` says READY since the stale copies were archived outside the repo (2026-10-26), but do not `promote` it; see its IDEA.md "Promotion state" |
| `integrate_combatsim`, `exact_odds`, `display_template` | IDEA.md + failing test only, no code (Status says building) |
| `addons_menu` | IDEA.md + failing test only (Status idea) |
| `_promoted/` | `buy_delta`, `adapter_buy_delta`, `simpreview_visual`, `buyingdelta_v2` |

`promote` moves an idea to `_promoted/` but does not edit its `Status:` line, so the Status inside `_promoted/*/IDEA.md` can be stale (three of four say "building"). Trust this table, not those lines. The index and order of the combat_sim ideas is `combat_sim/combat_sim_docs/LABS_FROM_COMBAT_SIM.md`.

## Known drift (see BACKLOG "Housekeeping")

`lab/combat_sim/bgtools/analysis/combat_*.py` and `lab/combat_sim/bgtools/commands/cmd_combat_sim.py` are older than the live `simcore/` and `commands/` files. Do not copy from them. (No `_orig/` folder is in the current upload; `hookup_apply.py` writes originals there when it runs.)
