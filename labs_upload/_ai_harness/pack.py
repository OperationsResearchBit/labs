# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026 bgtools contributors
"""lab.bat pack : build bgtools_src.zip (the one you upload to Claude) and print what is in it."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "helpers"))

from zip_tools import OUT_NAME, build_zip  # noqa: E402

WARN_RAW = 700_000


def main(argv=None) -> int:
    root = Path.cwd()                      # lab.bat moves to the repo root before it runs anything
    if not ((root / "bgtools").is_dir() and (root / "build_and_test").is_dir()):
        print("Run this through lab.bat (from the repo root: the folder with bgtools and build_and_test).")
        return 2
    count, zipped, sizes = build_zip(root)
    raw = sum(s for s, _ in sizes)
    print(f"{OUT_NAME}: {count} files, {raw // 1024} KB raw (about {round(raw / 3500)}k tokens), "
          f"{zipped // 1024} KB zipped")
    print("biggest:")
    for size, rel in sizes[:5]:
        print(f"  {size // 1024:>3} KB  {rel}")
    if raw > WARN_RAW:
        print(f"warning: over {WARN_RAW // 1000} KB raw. Look at the list above for something that should not be in it.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
