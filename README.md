# labs

Ship improvements to your app's core without breaking it.

Labs is a small workspace that sits next to a Python app built in layers ("core architecture"). You build each new idea in its own folder, with its own tests. One command checks it against your app's tests and layer rules. If it passes, one command moves it in.

Made by [OperationsResearchBit](https://github.com/OperationsResearchBit) while building [bgtools](https://github.com/OperationsResearchBit), its first user. It is meant for anyone who wants to start shipping improved apps, not only bgtools.

License: AGPL-3.0-or-later. See `LICENSE`.

## The idea

- **One folder per idea.** `lab/<name>/` looks like a small copy of your app, so code lives in the same folders it will have when shipped.
- **Safe to try.** While you work, the lab lays your folder over the real package. Your app is not touched.
- **Rules checked for you.** `check` runs your app's tests with the idea on top, requires a real test of its own, enforces which layer may import which, and requires a license header.
- **Promote by copying.** The folders match, so moving an idea in is a plain copy. No renames, no rewritten imports.
- **AI harness.** `_ai_harness/` helps you work with an AI assistant: `pack` makes a small source zip to upload, `apply` unpacks what you get back, `short` gives a report of 20 lines or fewer.

## Requirements

- Python 3.9 or newer, standard library only
- Git
- An app with a layered package and a test folder

## Status: read this first

Labs was built for one app, so today it expects that app's shape:

- The package is named `bgtools` and sits at the repo root.
- The lab lives at `build_and_test/lab/`.
- Layer rules come from the app's `build_and_test/tests/test_architecture.py` (an `ALLOWED` table of which layer may import which).
- The harness commands (`pack`, `apply`, `ask`, `go`) work through `lab.bat`, so they are Windows only.

Making the package name, folders and layer rules configurable is the first milestone, and the best first contribution. Until then, to use labs on your own app you rename `bgtools` in a handful of places in `lab.py` and `_ai_harness/`.

Other gaps: no example idea passes `check` end to end yet, and pull requests have no automatic checks.

## Try it

```
git clone <your app repo URL> app
git clone https://github.com/OperationsResearchBit/labs labs
mkdir -p app/build_and_test/lab
cp -r labs/labs_upload/. app/build_and_test/lab/
cd app
python build_and_test/lab/lab.py list
```

On Windows PowerShell, copy with `Copy-Item -Recurse labs\labs_upload\* app\build_and_test\lab\` (create the `lab` folder first if it does not exist).

The lab files live in the `labs_upload/` folder of this repo. Copy its contents into `build_and_test/lab/` of your app.

Then try the loop:

```
python build_and_test/lab/lab.py new my_idea
python build_and_test/lab/lab.py check my_idea
```

A new idea says "No test". Turn the example in its `IDEA.md` into a test, write the code until `check` says "Ready", then promote it.

Why is there a labs_upload/ folder?
This repo has two kinds of files. The ones at the top (README, CONTRIBUTING, LICENSE) are about the project. The ones in labs_upload/ are the lab: lab.py, the AI harness, the template and the example ideas. You copy the contents of labs_upload/ into build_and_test/lab/ of your app. Keeping them in their own folder stops this repo’s docs from landing inside your app, and it leaves room for tools that apply to the whole repo later, such as pull-request checks.

## Commands

| Command | What it does |
|---|---|
| `new <name>` | Creates `lab/<name>/` from `_template/` |
| `list` | Shows each idea and its status |
| `check <name>` | Runs every test and rule |
| `short <name>` | Same, as a report of at most 20 lines |
| `promote <name>` | Copies the idea into your app and prints what to upload |
| `pack` / `apply` / `ask` / `go` | AI harness (Windows, via `lab.bat`) |

## Contributing

Add an idea folder, or improve the lab itself, and open a pull request. See [CONTRIBUTING.md](CONTRIBUTING.md).
