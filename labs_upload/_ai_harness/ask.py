# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026 bgtools contributors
"""lab.bat ask NAME : same report as `short NAME`, and it is copied to the clipboard, ready to paste to Claude."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "helpers"))

from clip import copy  # noqa: E402


def main(argv=None) -> int:
    a = list(sys.argv[1:] if argv is None else argv)
    if len(a) != 1 or a[0].startswith("-"):
        print("Usage:  lab.bat ask NAME    (runs `short NAME` and copies the report)")
        return 2
    env = dict(os.environ, PYTHONUNBUFFERED="1", PYTHONIOENCODING="utf-8")
    proc = subprocess.run([sys.executable, str(HERE / "short.py"), a[0]], env=env, text=True,
                          encoding="utf-8", errors="replace",
                          stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    print(proc.stdout)
    print("(copied to the clipboard: paste it into the chat)" if copy(proc.stdout)
          else "(could not copy: select the text above)")
    return proc.returncode


if __name__ == "__main__":
    raise SystemExit(main())
