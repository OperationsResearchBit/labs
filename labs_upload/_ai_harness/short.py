# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026 bgtools contributors
"""lab.bat short NAME : run `check NAME` and print a report of at most 20 lines.

Same exit code as `check`. It only calls lab.py as a child process, so it does not know
where the app is: whatever lab.py uses, this uses too.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
LAB_PY = HERE.parent / "lab.py"
sys.path.insert(0, str(HERE / "helpers"))

from check_report import summarize  # noqa: E402


def main(argv=None) -> int:
    a = list(sys.argv[1:] if argv is None else argv)
    if len(a) != 1 or a[0].startswith("-"):
        print("Usage:  lab.bat short NAME    (runs `check NAME`, prints at most 20 lines)")
        return 2
    name = a[0]
    # unbuffered: keeps the "==" headers in order with unittest's own output; utf-8 for Windows pipes
    env = dict(os.environ, PYTHONUNBUFFERED="1", PYTHONIOENCODING="utf-8")
    proc = subprocess.run([sys.executable, str(LAB_PY), "check", name], env=env, text=True,
                          encoding="utf-8", errors="replace",
                          stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(errors="replace")
    print(summarize(name, proc.stdout))
    return proc.returncode


if __name__ == "__main__":
    raise SystemExit(main())
