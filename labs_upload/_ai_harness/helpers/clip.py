# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026 bgtools contributors
"""Copy text to the clipboard with the tools the OS already has (standard library only)."""

from __future__ import annotations

import shutil
import subprocess
import sys


def copy(text: str) -> bool:
    """True if the text was copied. Never raises."""
    if sys.platform.startswith("win"):
        cmds, data = [["clip"]], text.encode("ascii", "replace")
    elif sys.platform == "darwin":
        cmds, data = [["pbcopy"]], text.encode("utf-8")
    else:
        cmds, data = [["wl-copy"], ["xclip", "-selection", "clipboard"]], text.encode("utf-8")
    for cmd in cmds:
        if shutil.which(cmd[0]) is None:
            continue
        try:
            subprocess.run(cmd, input=data, check=True, timeout=10)
            return True
        except (OSError, subprocess.SubprocessError):
            continue
    return False
