# labs

A small workspace for building a new idea next to a Python project without touching the project. Each idea is a folder with its own tests. One command checks it. If it passes, one command moves it into the app.

It was built for [bgtools](https://github.com/OperationsResearchBit), a terminal tracker for Hearthstone Battlegrounds, and it is written so you can use it for your own project with a layered ("core architecture") design.

License: AGPL-3.0-or-later. See `LICENSE`.

## What it does

- **Keeps ideas separate.** A new idea lives in `lab/<name>/`, laid out like a small copy of the app. While you work, the lab lays your folder over the real package, so imports work before the code is in the app.
- **Checks the rules for you.** `check` runs the app's tests with your idea on top, requires a real test, enforces which layer may import which, and requires the license header.
- **Promotes by copying.** Because your folders match the app's, moving an idea in is a plain copy. Nothing gets renamed or rewritten.
- **Has an AI harness** (`_ai_harness/`) for working with an AI assistant: `pack` makes a small source zip to upload, `apply` unpacks a zip you get back, `short` prints a report of 20 lines or fewer, and `go` does `apply` then `ask`.

## Requirements

- Python 3.9 or newer. Standard library only.
- Git.
- The bgtools app.

## Quick start

The lab runs on top of the app and looks for it two folders above itself.

```
git clone <bgtools app repo URL> bgtools
cd bgtools
git clone https://github.com/OperationsResearchBit/labs build_and_test/lab
python build_and_test/lab/lab.py list
```

On Windows you can also double-click `build_and_test\lab\lab.bat`.

Try the loop:

```
python build_and_test/lab/lab.py new my_idea
python build_and_test/lab/lab.py check my_idea
```

A fresh idea says "No test". Write a test from the example in `IDEA.md`, then write the code until `check` says "Ready".

## Commands

| Command | What it does |
|---|---|
| `new <name>` | Creates `lab/<name>/` from `_template/` |
| `list` | Shows each idea and its status (idea, building, ready) |
| `check <name>` | Runs every test and rule, full output |
| `short <name>` | Same, as a report of at most 20 lines |
| `promote <name>` | Maintainer only. Copies the idea into the app and prints what to upload |
| `pack` | Builds `bgtools_src.zip` for uploading to an AI assistant |
| `apply [zip]` | Unpacks a zip over the repo (backs up what it replaces) |
| `ask <name>` / `go <name>` | `short` plus a copy to the clipboard / `apply` then `ask` |

On Windows, run these as `lab.bat <command>`. Elsewhere use `python build_and_test/lab/lab.py <command>`. The AI harness commands (`pack`, `apply`, `ask`, `go`, `short`) currently go through `lab.bat`, so they are Windows only for now.

## What an idea folder holds

```
lab/<name>/
  IDEA.md      goal, an example, where files go, hook-up edits, "done when"
  tests/       tests for this idea
  fixtures/    sample data
  bgtools/     new code, in the same folders it will have in the app
```

## What `check` looks at

1. All app tests still pass with your idea laid over the app.
2. Your idea has at least one real test. A skipped test does not count.
3. Each file imports only from the layers it is allowed to.
4. Each `.py` file has the license header.
5. No file is a copy of an app file. The lab cannot test edits to app files, so add a new file instead.
6. No files directly in `bgtools/`. Those change how the app starts, so describe them under **Hook-up** in `IDEA.md`.

## Contributing

Add an idea folder and open a pull request. The maintainer decides whether to promote it into the app. See [CONTRIBUTING.md](CONTRIBUTING.md) for the full flow.

## Status

Early. Known gaps:

- The harness commands are Windows only.
- The public app export has no `build_and_test/` folder, so a plain clone of the app has no tests for `check` to run. Until that is settled, ask the maintainer how to set up.
- There is no working example idea yet that passes `check` end to end.
- No automatic checks on pull requests yet.

## Scope

Tools built with this lab show information to the player. They do not play the game for them.
