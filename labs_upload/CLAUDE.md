# Lab rules for AI assistants

Read the root `CLAUDE.md` first. These rules apply to work inside `build_and_test/lab/`.

## Do not run tests (saves tokens)

Do not run tests, `lab.py check` or `make_map.py` unless the user asks you to debug or to check. Write the code and tests, say "not run", and give the command for the user to run: `lab.bat ask <idea>` (the same 20-line report as `short`, copied to the clipboard so the user can paste it; `lab.bat check <idea>` gives the full output). If something is failing or unclear and running a test would help, you may suggest it and ask the user to paste the output. Never say "ready" or "passing" unless the user pasted `check` output that says Ready, or `short`/`ask` output that says `verdict: READY`. Exception: a `fix` item from `lab_docs/BACKLOG.md` may run the one check it names (see `lab_docs/BACKLOG_CLAUDE.md`).

## Work order

1. Work only inside `lab/<idea>/`. Do not edit `bgtools/` or `build_and_test/tests/` while an idea is in the lab.
2. Fill in `IDEA.md` (Goal, Example, Files, Hook-up).
3. Write the Example as a failing test in `lab/<idea>/tests/`. A skipped test does not count. Do not run it (see above); show it to the user. Stop here: show `IDEA.md` and the test and wait for a go-ahead before step 4 (`STARTER_PROMPT.md` asks for this).
4. Write code under `lab/<idea>/bgtools/<layer>/`, in the folder it will have in the app. Import with `from bgtools...` exactly as app files do.
5. Tell the user to run `lab.bat ask <idea>` and paste the result (`short` is the same without the copy). Report its result only if they paste it. `lab.bat check <idea>` still gives the full output (use it when `short` is not enough to see what failed).

## Delivering a new idea

When you send a new idea or project, create a folder for it: `<idea>/`, in the shape `lab.py new` makes, so the user can drop it into `build_and_test/lab/`:

```
<idea>/
  IDEA.md
  tests/test_<idea>.py
  bgtools/<layer>/...      new code, at the exact path it will have in the app
  fixtures/
```

- In chat, send it as one zip with paths from the repo root (`build_and_test/lab/<idea>/IDEA.md`, and so on), so `lab.bat go <idea>` can unpack it and run the check. Do not send loose files.
- Put every new file at its exact path inside the folder (for example `build_and_test/lab/<idea>/bgtools/analysis/<idea>.py` in the zip). `lab.bat apply` refuses a zip whose top folder the repo does not have.
- Edits to existing app files are not sent as changed copies. List them in `IDEA.md` under Hook-up.
- Set `Status:` in `IDEA.md` honestly (idea, building, ready). Use "ready" only after the user reports that `check` passed.

## Rules

- Respect the layers (root `CLAUDE.md`). `check` enforces them.
- Start every `.py` file with the two license lines used by app files.
- Never copy an app file into the lab to edit it. `check` rejects it (tests would still run the app's version).
- No `.py` files directly in `lab/<idea>/bgtools/`. Those change how the app starts; write them under "Hook-up" in `IDEA.md`.
- `fixtures/` is sample data. `promote` copies it to `build_and_test/tests/fixtures/<idea>/`, not into `bgtools/`. Terminal drawings (headers, colors, banners) that must ship are `.py` files under `<idea>/bgtools/ui/`; ask the maintainer where theirs live before moving or promoting them (see `lab/README.md`, "Terminal drawings").
- Never use a real `Power.log` in fixtures. Use `build_and_test/tests/fake_game.py` or a log with names scrubbed.
- Never name Stockfish (or its abbreviations) in docs, comments or replies. Describe an outside format by what it is.
- Files the app writes at run time go under `app_root()` from `core/paths.py`, never `Path(__file__)...` (the one-file .exe runs from a temporary folder).
- A hook-up is applied by `hookup_apply.py` only. Its `hookup_edits_*.py` files are imported parts, not scripts to run.
- A `hookup_apply.py` edit that adds to text an earlier edit inserted goes AFTER it and puts its text outside the earlier block. Otherwise the earlier edit's "already in" check stops matching and a second run applies it again (seen in `buy_delta`: helpers pasted twice). Check by running it twice on a scratch copy of the app: the second run must say "nothing to do".
- An idea may also carry `preview.bat` + `preview.py` (try it without the game, or `--live` on a real game; it applies the hook-up first) and `hookup_apply.py` (with `--undo`), beside `IDEA.md`. A `.bat` that must ship (for example `buydelta.bat`) is not under `bgtools/`, so `promote` does not copy it: list it in `IDEA.md` under Hook-up as a file for the repo root, and add it to the export lists in the root `CLAUDE.md` and `tools/make_export.py`.
- A number the sim cannot back (for example a "best move" percentage that needs economy) is not shown. Show a share of what the sim can measure, labeled as such, or nothing.
- Plans for separate GitHub repositories (the lab itself, a BGIQ wiki) are in `BACKLOG.md` as `repo` lines; they are not lab ideas, so never run `lab.py new` for them.
- A research idea (for example a storage format) produces notes and a measured experiment first, in the idea's `PLAN_AND_RESEARCH.md`, and no code until the experiment says it is worth it.
- If the screen changes, say so in `IDEA.md`. Golden files must be regenerated and the diff reviewed after promoting.

## Where each kind of idea goes (v2.1+)

- **Advice rule:** one new file, `bgtools/analysis/recommender/rule_<name>.py`: `from bgtools.analysis.recommender.rules import rule`, then decorate the function with `@rule`. No hook-up. Test it through `pick_marks` or `RULES`.
- **Command:** one new file, `bgtools/commands/cmd_<name>.py`, using `@command("name", "help", configure, menu="Menu label")` from `bgtools.commands.registry`. No hook-up. Do not reuse the names `hello` (a registry test uses it).
- **Analysis function** (like `pairs`): one new file under `bgtools/analysis/`. No hook-up until it is shown on screen.
- **Screen piece:** still needs hand edits, so list them all in `IDEA.md` under Hook-up: `Snapshot` field in `core/domain.py`, `build_snapshot` in `modes/live_tracker.py`, `REGISTRY` in `ui/components/__init__.py`, `_build` in `ui/layout.py`, and the golden files. `ui` may import only `core`, so the value must arrive through `Snapshot`.
- `promote` prints hook-up edits for you to do by hand, then run `python build_and_test/tools/make_map.py`. These are steps for the user to run.

## Changing files the app already has (keep it cheap)

- Do not build a v2 as copies of app files in the lab (`check` rejects them). Use the recipe in `lab/README.md`, "Promoting a change to files the app already has": new paths and test names, edits and deletions in `hookup_apply.py`.
- Do not run `promote` or the full flow yourself. Verify once on a scratch copy only if the user asks; otherwise give the user the command list.
- Send ONE zip with paths from the repo root, and the exact PowerShell commands, including that they run from the repo root.
- If the user ran commands one folder too deep, nothing is applied: `hookup_apply.py` reads every file before writing any. Have them `cd ..`, delete the stray `build_and_test`, and rerun.
