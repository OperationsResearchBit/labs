# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026 bgtools contributors
"""lab.bat apply [ZIP] [--dry] : unpack a zip from Claude over the repo (paths start at the repo root).

No ZIP given: uses the newest .zip in your Downloads folder (not bgtools_src*). Replaced files are
copied to _apply_backup/<time>/ first. --dry only lists what would change.
"""

from __future__ import annotations

import sys
import time
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "helpers"))

from zip_tools import apply_zip, newest_zip  # noqa: E402

SHOW = 30


def _age(path: Path) -> str:
    mins = int((time.time() - path.stat().st_mtime) / 60)
    return f"{mins} min ago" if mins < 120 else f"{mins // 60} hours ago"


def _list(label: str, names) -> int:
    for n in names[:SHOW]:
        print(f"  {label}: {n}")
    if len(names) > SHOW:
        print(f"  ... {len(names) - SHOW} more {label}")
    return len(names)


def main(argv=None) -> int:
    a = list(sys.argv[1:] if argv is None else argv)
    dry = "--dry" in a
    a = [x for x in a if x != "--dry"]
    root = Path.cwd()
    if len(a) > 1 or not ((root / "bgtools").is_dir() and (root / "build_and_test").is_dir()):
        print("Usage:  lab.bat apply [PATH_TO_ZIP] [--dry]   (run through lab.bat, from the repo root)")
        return 2
    zip_path = Path(a[0]).expanduser() if a else newest_zip(Path.home() / "Downloads")
    if zip_path is None or not zip_path.is_file():
        print("No zip found. Give the path:  lab.bat apply C:\\path\\to\\file.zip")
        return 2
    print(f"zip: {zip_path.name} (saved {_age(zip_path)}){'  [dry run]' if dry else ''}")
    try:
        res = apply_zip(zip_path, root, dry=dry)
    except zipfile.BadZipFile:
        print("That file is not a valid zip.")
        return 2
    if res["refused"]:
        print("Refused, nothing written (unsafe path in the zip):")
        _list("path", res["refused"])
        return 1
    _list("new", res["new"])
    _list("changed", res["changed"])
    print(f"  {len(res['same'])} file(s) already identical")
    if res["backup"] and not dry:
        print(f"Replaced files were saved in {res['backup']}")
    if not (res["new"] or res["changed"]):
        print("Nothing to do.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
