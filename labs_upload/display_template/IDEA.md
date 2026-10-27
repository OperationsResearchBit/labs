# display_template

Status: building
<!-- idea -> building -> ready.  Change it by hand; `list` shows it. -->

## Goal
A "hello world" display adapter that people copy to build their own screen for the tracker. It prints one line (turn, tier, gold) and the board, so a new contributor sees how a `Snapshot` becomes text and how a command hands that text to the tracker. Once promoted it ships as the folder `bgtools/adapter_display_template/` with a tutorial `README.md`.

## Not in this idea
- No change to `simcore/`, `analysis/` or the existing tracker screen.
- The odds screen look is `simpreview_visual`, not this. This one stays tiny on purpose.

## Example
`render(snap, show_text=False, rows=0) -> str` reads only `Snapshot.status` and `Snapshot.board`:

    Status(turn=7, tier=3, gold 6/7)  ->  first line  "Hello, Battlegrounds!  turn 7 · tier 3 · gold 6/7"
    any value unknown                 ->  "Hello, Battlegrounds!  turn ? · tier ? · gold ?/?"
    second line                       ->  "Board: <minion names, comma separated>"   ("Board: (empty)" with no minions)
    rows=1                            ->  only the first line (a display must respect the window height)

The command `hellodisplay` passes `render` to `live_tracker.run(..., render=render)`, modeled on `simpreview` (`commands/cmd_simpreview.py`).

## Files
- bgtools/adapter_display_template/render.py   - `render(snap, show_text, rows)`; imports `bgtools.core` only
- bgtools/adapter_display_template/README.md   - the tutorial: copy the folder, rename it, which `Snapshot` fields to read, how to run (`python -m bgtools hellodisplay --replay PATH`), how to add colors via `bgtools.ui.bgui`, the layer rule
- bgtools/commands/cmd_hello_display.py        - the `hellodisplay` command (found automatically)

## Hook-up
1. `build_and_test/tests/test_architecture.py`: add `"adapter_display_template": {"core"}` to `ALLOWED`, and add `"adapter_display_template"` to the set for `commands`. Without this the new folder is not checked at all.
2. Root `CLAUDE.md` layer table: one row for adapter folders (may import `core`; a command connects them).
3. `docs/ARCHITECTURE.md`: one row in the dependency table. `make_map.py` needs no edit (it scans folders).
4. Check that `run_lab.bat display_template hellodisplay --replay PATH` works; the command file is found by the overlay.

## Changelog line
New `hellodisplay` command and an `adapter_display_template` folder: a tiny example screen with a tutorial for building your own display.

## Done when
- [ ] The example above is a passing test
- [ ] `check display_template` says Ready
- [ ] The README tutorial was followed once by someone who did not write it
- [ ] Architecture test and docs rows added
