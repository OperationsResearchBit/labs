# status: plan for `lab.bat status`

Put this file in `build_and_test/lab/_ai_harness/`. Nothing here is built yet.
Rules for new commands in this folder are in `README.md` ("Rules for new commands here"); this plan follows them.

## Goal

One screen that answers: what is in the lab, what is ready, what is stuck, what is next.
Today that means reading `lab.bat list`, each `IDEA.md`, `lab_docs/BACKLOG.md` and re-running tests by hand.
`lab.bat status` reads those once and prints at most 30 lines. Phase 2 adds `--html` (a static page, no server).

## Example

    lab status (2026-10-26)
    ideas (5)
      combat_sim          building   check: NOT READY (2d ago)   hook-up: 4 edits
      exact_odds          building   check: NO TEST   (never)    hook-up: none
      integrate_combatsim building   check: ?          (never)    hook-up: none
      addons_menu         idea       check: ?          (never)    hook-up: none
      display_template    building   check: READY      (1d ago)   hook-up: none
    stuck: exact_odds, integrate_combatsim (building, no READY check)
    stale status in _promoted/: buy_delta, adapter_buy_delta, buyingdelta_v2 (say "building")
    backlog next (5): buydelta_moves, effect_census, buydeltapreview_tiers, pair_alert, log_cache
    backlog fix (1): lab_stale_copies

(Names and numbers above are made up; this is the shape.)

## What it reads

| Source | What it takes | How |
|---|---|---|
| `lab/<idea>/IDEA.md` | `Status:` line (idea / building / ready) | first line that starts with `Status:` |
| `lab/<idea>/IDEA.md` | Hook-up: "none" or a count of edits | text under `## Hook-up`; starts with "none" means no hand edits |
| `lab/<idea>/bgtools/` | file count | count files, skip `__pycache__` and `.pyc` |
| `lab/_promoted/*/IDEA.md` | `Status:` line | flag any that is not "ready" (see `lab_docs/LAB_ARCHITECTURE.md`, "Ideas in the lab") |
| `lab/lab_docs/BACKLOG.md` | "Next" items, and `fix` items under "Housekeeping" | lines that start with `- [S|M|L] type name:` |
| `_ai_harness/last_check.json` | last `short` verdict and time per idea | written by `short.py` (see below) |

An idea is a folder in `lab/` whose name does not start with `_` or `.` and that holds an `IDEA.md`. (`lab.py` does not yet require the `IDEA.md`, so it also lists `lab_docs/`; backlog `fix lab_list_counts_docs`.)
`status` never runs tests and never calls the app. It only reads files under the lab folder.

## The one new thing to store

`short.py` records its verdict after each run, so `status` can show test state without re-running tests (which is slow).

    _ai_harness/last_check.json
    {"combat_sim": {"verdict": "NOT READY", "when": "2026-10-24T18:02:11"}, ...}

- Written by `short.py` only. `status` reads it and never writes it.
- Missing or unreadable file means every idea shows `?` / "never". `status` must not crash on it.
- Write it atomically (temp file, then rename), and keep only the last verdict per idea.
- It is run-time state: add it to `.gitignore` and leave it out of zips (the `.json` extension is already not in the zip command's `ok` list).
- A verdict goes stale when the idea's files change. Show the age ("2d ago") and let the reader judge; do not try to guess staleness.

## Files

- `status.py` the command: `lab.bat status [--html]`. Reads files, prints the report, exit code 0 (2 on bad arguments).
- `helpers/lab_status.py` `collect(lab_dir) -> dict` and `render_text(data) -> str`: standard library only, text and dicts in and out, so it needs no app.
- `helpers/check_report.py` unchanged.
- `short.py` one small addition: after printing, record the verdict into `last_check.json`.
- `tests/test_lab_status.py` no app needed. Builds a fake lab in a temp folder (a few idea folders, one `_promoted/`, a small `BACKLOG.md`, a `last_check.json`) and checks the text.

## Hook-up

None in `lab.py`. The dispatch added for `short` already runs any `_ai_harness/<n>.py`.
Docs to touch when built: this folder's `README.md` (Commands and Files), `lab_docs/LAB_ARCHITECTURE.md` (the `short NAME` row becomes a pair with `status`), `lab/README.md` (one line).

## Rules

- Call nothing in the app. Never compute the app path (the lab will move to its own repo, see BACKLOG `labs_repo`).
- A `Status:` line that is missing or not one of the three words shows as `?`, never an error.
- Cap the output at 30 lines. If there are more ideas than fit, show the first ones and say how many were dropped (same idea as `check_report.py`).
- A malformed `BACKLOG.md` line is skipped, not fatal.
- No colors or terminal tricks: Windows consoles and pasted output both stay clean.
- Add the test with the code, per the folder rules.

## Phase 2: `--html`

`lab.bat status --html` writes `lab_dashboard.html` in the lab folder and prints its path.

- One static, self-contained file (inline CSS, no scripts, no network). Open it in a browser; no server.
- Same data as the text report, as a table per section, with each idea name linking to its `IDEA.md` by a relative path.
- Generated, never edited by hand: add it to `.gitignore`.
- Do this only if the terminal version is not enough.

## Done when

- [ ] `python -m unittest discover -s _ai_harness/tests` passes (from the lab folder), including the new test
- [ ] `lab.bat status` on the real lab prints at most 30 lines and the numbers match `lab.bat list`
- [ ] `lab.bat short <idea>` then `lab.bat status` shows that idea's new verdict
- [ ] Deleting `last_check.json` does not break `status`
- [ ] Docs listed under Hook-up are updated

## Not built

- Running tests from `status` (slow; `short` does that).
- Editing `IDEA.md` or `BACKLOG.md` from `status`. It only reads.
- A live-updating or served dashboard. Revisit only if the static page is not enough.
- `hookcheck` and `ziplint` (see `README.md`, "Not built").
