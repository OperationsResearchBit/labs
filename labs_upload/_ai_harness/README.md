# _ai_harness

Lab tooling, not an idea. The leading `_` makes `lab.py` ignore it (no `list`, no `check`, no `promote`).
Each `<name>.py` in this folder is a lab command: `lab.bat <name> ...`. Helpers go in `helpers/`.

## Commands
- `lab.bat short NAME` runs `check NAME` and prints at most 20 lines: verdict (READY / NOT READY / NO TEST),
  `problem:` and `note:` lines, failed tests with their exception line (no tracebacks), app failures marked
  `app failed:`. A crash in `lab.py` shows the last 3 lines. Same exit code as `check`.
- `lab.bat ask NAME` is `short NAME` plus a copy to the clipboard. Paste straight into the chat.
- `lab.bat go NAME [ZIP]` = `apply` then `ask NAME`: one command after you download a zip from Claude. Stops if `apply` refuses.
- `lab.bat pack` builds `bgtools_src.zip` (same rules as `build_and_test/onezip.txt`, so that file is now only a backup) and prints the file count,
  raw size, rough tokens and the five biggest files. Warns above 700 KB.
- `lab.bat apply [ZIP] [--dry]` unpacks a zip from Claude over the repo (paths in the zip start at the repo root). With no ZIP it takes the newest
  .zip in Downloads (not `bgtools_src*`) and says how old it is. Replaced files are copied to `_apply_backup/<time>/` in the repo root first.
  One unsafe path (absolute, `..`, `.git`) or a top folder the repo does not have (a stray zip) refuses the whole zip. `--dry` only lists. Not run yet.
- `lab.bat status` (planned, not built): one screen of ideas, last check verdicts and backlog. Plan: `aiharness_docs/STATUS_PLAN.md`.

## Files
- `CLAUDE.md` rules for AI assistants working in this folder.
- `aiharness_docs/` plans and notes for commands, built or not (`STATUS_PLAN.md`).
- `pack.py`, `apply.py`, `ask.py`, `go.py` the commands above; `helpers/zip_tools.py` (zip rules, safe unpack), `helpers/clip.py` (clipboard).
- `short.py` the command. Calls `lab.py check` as a child process; does not know where the app is.
- `helpers/check_report.py` `summarize(name, output)`: text in, text out, standard library only.
- `tests/test_harness_tools.py` tests for pack and apply. `tests/test_check_report.py` no app needed. Run from the lab folder:
  `python -m unittest discover -s _ai_harness/tests`

## Hook-up
`lab.bat` skips its "Press any key" when the variable `LAB_NOPAUSE` is set (PowerShell, once: `setx LAB_NOPAUSE 1`, then open a new window). It also keeps `lab.py`'s exit code.
Done: `lab.py` hands any unknown command `<n>` to `_ai_harness/<n>.py`, last. New commands here need no further hook-up.

## Rules for new commands here
Call `lab.py` as a child process; never compute the app path (the lab will move to its own repo).
Put shared code in `helpers/`. Add a test in `tests/`.

## Not built
`hookcheck` (run an idea's `hookup_apply.py` twice on a scratch copy) and `ziplint`: only if hook-ups hurt.

`_apply_backup/` (repo root) is run-time state made by `apply`: never commit it. The zip rules skip it.
