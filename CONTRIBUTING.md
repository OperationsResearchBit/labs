# Contributing to labs

Labs helps people ship improvements to the core of a layered Python app. An idea lives in its own folder, has its own tests, and is checked by one command. If it passes, it can be moved into the app.

There are two ways to contribute:

1. **Improve the lab itself.** Most needed: make it work with any app, not only bgtools (configurable package name, folders and layer rules), a Mac/Linux launcher, a working example idea, and a GitHub Action that runs `check` on pull requests.
2. **Add an idea.** Ideas are built against an app. The example ideas in this repo use bgtools.

## What you need

- Python 3.9 or newer (standard library only, nothing to install)
- Git
- An app to run the lab against. Today that means bgtools, because the lab is not configurable yet (see the README's Status section)

## Set up

The lab runs on top of the app. It looks for the app two folders above itself.

```
git clone <your app repo URL> app
cd app
git clone <this repo URL> build_and_test/lab
python build_and_test/lab/lab.py list
```

If `list` prints the example ideas, you are set up. On Windows you can also double-click `build_and_test/lab/lab.bat`.

> Maintainer note: the public app export leaves out `build_and_test/` (see `make_export.bat`), so the app's own tests are not in a plain clone. Check that `lab.py check` works on a fresh clone before announcing this, and say here what a contributor must add if it does not.

## Make an idea

```
python build_and_test/lab/lab.py new my_idea
```

This creates `build_and_test/lab/my_idea/` from `_template/`:

```
my_idea/
  IDEA.md      goal, an example, where files go, hook-up edits, "done when"
  tests/       tests for this idea
  fixtures/    sample data for this idea
  bgtools/     new code, in the SAME folders it will have in the app
               e.g. bgtools/analysis/my_idea.py
```

The loop:

1. Fill in **Goal** and **Example** in `IDEA.md`.
2. Turn the Example into a test in `tests/`. It fails.
3. Write the code under `bgtools/<layer>/` until it passes.
4. Run `python build_and_test/lab/lab.py check my_idea`. Fix whatever it lists.
5. Open a pull request (below).

For a quick report of at most 20 lines, use `short my_idea` instead of `check`.

## What `check` requires

- All existing app tests still pass with your idea laid over the app.
- Your idea has at least one real test. A skipped test does not count.
- Every file imports only from the layers it is allowed to (`docs/ARCHITECTURE.md` in the app).
- Every `.py` file starts with the license header:

  ```python
  # SPDX-License-Identifier: AGPL-3.0-or-later
  # Copyright (C) 2026 bgtools contributors
  ```

- No file is a copy of an app file. The lab cannot test edits to app files, so add a new file instead.
- No files directly inside `bgtools/` (those change how the app starts). Describe that edit under **Hook-up** in `IDEA.md`.

## Open a pull request

1. Fork this repo and create a branch.
2. Add your idea folder only: `my_idea/`. Do not edit other ideas or `lab.py` in the same pull request.
3. In the pull request, say what the idea does and paste the result of `check my_idea`.
4. The maintainer reviews it. **Promoting** an idea into an app is the app owner's decision, because it changes the app.

Changes to the lab tooling itself (`lab.py`, `_template/`, `_ai_harness/`) are welcome as their own pull request. Keep them small and explain the problem they fix.

## Good first contributions

- Add a clear, working example idea that passes `check` end to end.
- Improve the docs where something confused you.
- Make the launcher work on Mac and Linux (`lab.bat` is Windows only).

## Rules for the code

- No outside dependencies. The app uses the standard library only.
- No automated play. Tools here show information to the player; they never click or send input to the game.
- Keep each change small enough to review in one sitting.

## License

By contributing you agree that your work is released under the same license as this repo (see `LICENSE`). If you run a modified version as a network service, the AGPL has extra obligations. Read the license, and ask if you are unsure.
