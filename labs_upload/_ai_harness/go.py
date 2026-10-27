# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026 bgtools contributors
"""lab.bat go NAME [ZIP] : apply the newest zip from Claude (see `apply`), then run `ask NAME`."""

from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE / "helpers"))

import apply as apply_cmd  # noqa: E402
import ask as ask_cmd  # noqa: E402


def main(argv=None) -> int:
    a = list(sys.argv[1:] if argv is None else argv)
    if not a or len(a) > 2 or a[0].startswith("-"):
        print("Usage:  lab.bat go NAME [ZIP]    (applies the newest zip in Downloads, then runs `ask NAME`)")
        return 2
    name, rest = a[0], a[1:]
    code = apply_cmd.main(rest)
    if code != 0:
        print("Stopped: nothing was checked.")
        return code
    print()
    return ask_cmd.main([name])


if __name__ == "__main__":
    raise SystemExit(main())
