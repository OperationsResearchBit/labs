# _ai_harness rules for AI assistants

Read `build_and_test/lab/CLAUDE.md` first (it reads the root `CLAUDE.md`). Its rules apply here, including "Do not run tests". This file adds only what is specific to `_ai_harness/`.

## What this folder is

Lab tooling, not an idea. The leading `_` makes `lab.py` skip it for `list`, `check` and `promote`. Each `<n>.py` here is a command: `lab.bat <n> ...` (`lab.py` runs it, last, so it can never replace `new`, `list`, `check` or `promote`). Today: `short`, `ask`, `pack`, `apply`, `go` (see its `README.md`). Planned: `status` (see `aiharness_docs/STATUS_PLAN.md`, not built).

## Read order (stay cheap)

1. `README.md` in this folder: commands, files, hook-up, what is not built.
2. Only the plan for the command you are touching, in `aiharness_docs/`.
3. Only the files that command uses (`short.py`, `helpers/*.py`, its test). Do not open `lab.py`; `lab/lab_docs/LAB_ARCHITECTURE.md` says how it works.

## Rules

- A command calls `lab.py` as a child process. Never compute the app path (the lab will move to its own repo).
- Shared code goes in `helpers/`: text in, text out, standard library only, no app imports.
- Every command gets a test in `tests/`. Tests need no app. Run from the lab folder by the user: `python -m unittest discover -s _ai_harness/tests`.
- Start every `.py` file with the two license lines the other files use.
- Read-only on everything outside this folder. A change to `lab.py`, `lab/CLAUDE.md`, `lab/README.md` or `lab_docs/` is a hook-up: list it, do not silently edit it.
- Output meant for pasting back into chat stays short: cap lines, clip long lines, no tracebacks, no colors.
- `last_check.json` (once `short` writes it) is run-time state: never commit it, never put it in a zip.
- A `short` result that says `verdict: READY` counts as "Ready" for the lab rule; `NO TEST` and `NOT READY` do not.

## Delivering a change

- Send ONE zip with paths from the repo root (for example `build_and_test/lab/_ai_harness/status.py`), plus the PowerShell commands, run from the repo root.
- Say "not run" for anything you did not run, and give the user the command: `lab.bat short <idea>` or the unittest line above.
- Update this folder's `README.md` (Commands, Files) in the same zip when you add or change a command.
- A new command's plan goes in `aiharness_docs/` before code, in the shape of `STATUS_PLAN.md` (Goal, Example, What it reads, Files, Hook-up, Rules, Done when, Not built).
