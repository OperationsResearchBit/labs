# Contributing to the lab

The lab is a place to build a new idea next to the bgtools app without touching the app. This repo holds the lab itself: the tooling (`_ai_harness/`), the starter examples (`_template/`, `display_template/`) and the docs. Ideas that work are promoted into the app by the maintainer.

Status: experimental. The lab needs the bgtools app to run, and there is no automatic check on pull requests yet.

## Setup

The lab expects to sit inside the app, at `build_and_test/lab/`.

1. Clone the bgtools app (link to the app repo).
2. From the app's main folder, clone this repo into `build_and_test/lab`:

   ```
   git clone https://github.com/OperationsResearchBit/labs build_and_test/lab
   ```

3. From the app's main folder, list the ideas to check it works:

   ```
   python build_and_test/lab/lab.py list
   ```

Windows users can also double-click `lab.bat`. `lab.bat` and the clipboard helper are Windows only. Everything else is plain Python.

## Adding an idea

1. Make the folder from the template: `python build_and_test/lab/lab.py new my_idea`
2. Fill in `IDEA.md`: the goal, one worked example, where the files go, and what is out of scope.
3. Write the test first, in `my_idea/tests/`, starting from the example in `IDEA.md`.
4. Put the new code in `my_idea/bgtools/...`, in the same folders it will have in the app (for example `my_idea/bgtools/analysis/pairs.py`).
5. Check it: `python build_and_test/lab/lab.py check my_idea`. It prints Ready, or what is wrong.
6. Open a pull request that changes only your idea's folder.

`check` rejects a file that is a copy of an app file, because the lab cannot test edits to app files. If your idea changes an existing app file, read "Promoting a change to files the app already has" in `README.md` and list those edits in the Hook-up section of `IDEA.md`.

## Rules

- Every `.py` file starts with these two lines:

  ```
  # SPDX-License-Identifier: AGPL-3.0-or-later
  # Copyright (C) 2026 bgtools contributors
  ```

- Keep a change to one idea per pull request. Do not edit another idea's folder.
- Tests are required. A pull request without a test for what it changes will not be merged.
- Do not commit personal data: usernames, local paths, logs (`combat_odds_log.txt`), zips or `venv/`.
- Changes to `_ai_harness/` use only the Python standard library, never import the app, and add or update a test in `_ai_harness/tests/`.

## What happens next

The maintainer runs `check` on your idea. If it is Ready and fits the app, the maintainer promotes it. Only the maintainer runs `promote`, so do not edit the app yourself.

## Using an AI assistant

`CLAUDE.md` and `_ai_harness/CLAUDE.md` hold the rules the maintainer gives an AI assistant when working in the lab. You can use them with any assistant. Whoever sends the pull request is responsible for the result, and it must pass the same `check`.

## License

By contributing you agree that your work is released under the AGPL-3.0-or-later, the same license as the project (see `LICENSE`).
