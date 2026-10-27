# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026 bgtools contributors
"""Build the source zip and unpack a zip from Claude (standard library only, no app imports)."""

from __future__ import annotations

import time
import zipfile
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Tuple

OUT_NAME = "bgtools_src.zip"
SKIP = {"venv", ".venv", "build", "release", ".git", "__pycache__", "data", "samples",
        "_promoted", "_orig", "dist", ".pytest_cache", "_apply_backup"}
KEEP_SUFFIX = {".py", ".md", ".bat", ".toml", ".txt", ".yml"}
KEEP_NAMES = {"LICENSE", ".gitignore", ".gitattributes"}
LEAVE_OUT = {"combat_odds_log.txt", "CHANGELOG.md", "CHANGELOG_ARCHIVE.md"}


def source_files(root) -> List[Path]:
    """Paths (relative to root) that go into bgtools_src.zip. Same rules as onezip.txt."""
    root = Path(root)
    found = []
    for p in sorted(root.rglob("*")):
        if not p.is_file():
            continue
        rel = p.relative_to(root)
        if set(rel.parts) & SKIP:
            continue
        if p.suffix not in KEEP_SUFFIX and p.name not in KEEP_NAMES:
            continue
        if p.name in LEAVE_OUT:
            continue
        found.append(rel)
    return found


def build_zip(root, out_name: str = OUT_NAME) -> Tuple[int, int, List[Tuple[int, str]]]:
    """Write the zip in root. Returns (file count, zip bytes, [(raw bytes, path)] biggest first)."""
    root = Path(root)
    files = source_files(root)
    out = root / out_name
    tmp = root / (out_name + ".tmp")
    with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for rel in files:
            z.write(root / rel, rel.as_posix())
    tmp.replace(out)
    sizes = sorted(((root / r).stat().st_size, r.as_posix()) for r in files)
    sizes.reverse()
    return len(files), out.stat().st_size, sizes


def newest_zip(folder, ignore_prefix: str = "bgtools_src") -> Optional[Path]:
    """The most recently saved .zip in folder, ignoring the ones we build ourselves."""
    zips = [p for p in Path(folder).glob("*.zip") if not p.name.lower().startswith(ignore_prefix)]
    return max(zips, key=lambda p: p.stat().st_mtime) if zips else None


def _safe_rel(name: str) -> Optional[Path]:
    n = name.replace("\\", "/")
    parts = n.split("/")
    if not n or n.startswith("/") or ":" in parts[0] or ".." in parts or ".git" in parts:
        return None
    return Path(*parts)


def apply_zip(zip_path, dest, dry: bool = False, stamp: Optional[str] = None) -> Dict[str, object]:
    """Unpack a zip over dest (paths in the zip start at dest).

    All or nothing: one unsafe path (absolute, '..', '.git') or a top folder the repo does not have refuses the whole zip.
    A file that already exists with different content is copied to dest/_apply_backup/<stamp>/ first.
    dry=True writes nothing. Returns {"new", "changed", "same", "refused": [paths], "backup": str}.
    """
    dest = Path(dest).resolve()
    stamp = stamp or time.strftime("%Y%m%d_%H%M%S")
    res: Dict[str, object] = {"new": [], "changed": [], "same": [], "refused": [], "backup": ""}
    with zipfile.ZipFile(zip_path) as z:
        plan = []
        for info in z.infolist():
            if info.filename.endswith("/"):
                continue
            rel = _safe_rel(info.filename)
            target = (dest / rel).resolve() if rel else None
            ok = (rel is not None and dest in target.parents
                  and (len(rel.parts) == 1 or (dest / rel.parts[0]).is_dir()))
            if not ok:                                     # also refuses a top folder the repo does not have
                res["refused"].append(info.filename)       # type: ignore[union-attr]
                continue
            plan.append((info, rel, target))
        if res["refused"]:
            return res
        for info, rel, target in plan:
            data = z.read(info)
            name = rel.as_posix()
            if target.exists():
                if target.read_bytes() == data:
                    res["same"].append(name)               # type: ignore[union-attr]
                    continue
                res["changed"].append(name)                # type: ignore[union-attr]
                if not dry:
                    backup = dest / "_apply_backup" / stamp / rel
                    backup.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(target, backup)
                    res["backup"] = f"_apply_backup/{stamp}"
            else:
                res["new"].append(name)                    # type: ignore[union-attr]
            if not dry:
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(data)
    return res
