# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026 bgtools contributors
"""Tests for pack / apply helpers. Run from the lab folder:  python -m unittest discover -s _ai_harness/tests
No app is needed."""

import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

_HARNESS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_HARNESS / "helpers"))

from zip_tools import apply_zip, build_zip, newest_zip, source_files  # noqa: E402


def _write(root: Path, rel: str, text: str = "x") -> None:
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")


class SourceZipTests(unittest.TestCase):
    def test_keeps_source_and_skips_the_rest(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            for rel in ["bgtools/a.py", "build_and_test/x.md", "LICENSE", "run.bat"]:
                _write(root, rel)
            for rel in ["venv/big.py", "docs/CHANGELOG.md", "x/CHANGELOG_ARCHIVE.md", "data/h.txt",
                        "notes.json", "combat_odds_log.txt", "_apply_backup/1/a.py", "a/__pycache__/b.py"]:
                _write(root, rel)
            got = sorted(p.as_posix() for p in source_files(root))
            self.assertEqual(got, ["LICENSE", "bgtools/a.py", "build_and_test/x.md", "run.bat"])

    def test_build_zip_writes_relative_paths(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _write(root, "bgtools/a.py", "hello")
            count, zipped, sizes = build_zip(root)
            self.assertEqual(count, 1)
            self.assertEqual(sizes[0], (5, "bgtools/a.py"))
            self.assertEqual(zipfile.ZipFile(root / "bgtools_src.zip").namelist(), ["bgtools/a.py"])
            self.assertEqual(len(source_files(root)), 1)      # the zip itself is not counted


class ApplyTests(unittest.TestCase):
    def _zip(self, root: Path, files: dict) -> Path:
        path = root / "in.zip"
        with zipfile.ZipFile(path, "w") as z:
            for name, text in files.items():
                z.writestr(name, text)
        return path

    def test_new_changed_same_and_backup(self):
        with tempfile.TemporaryDirectory() as d, tempfile.TemporaryDirectory() as w:
            dest, work = Path(d), Path(w)
            _write(dest, "bgtools/old.py", "old")
            _write(dest, "bgtools/same.py", "same")
            z = self._zip(work, {"bgtools/old.py": "new text", "bgtools/same.py": "same", "bgtools/fresh.py": "f"})
            res = apply_zip(z, dest, stamp="T1")
            self.assertEqual(res["new"], ["bgtools/fresh.py"])
            self.assertEqual(res["changed"], ["bgtools/old.py"])
            self.assertEqual(res["same"], ["bgtools/same.py"])
            self.assertEqual((dest / "bgtools/old.py").read_text(), "new text")
            self.assertEqual((dest / "_apply_backup/T1/bgtools/old.py").read_text(), "old")
            self.assertEqual(res["backup"], "_apply_backup/T1")

    def test_dry_run_writes_nothing(self):
        with tempfile.TemporaryDirectory() as d, tempfile.TemporaryDirectory() as w:
            dest = Path(d)
            _write(dest, "a.py", "old")
            z = self._zip(Path(w), {"a.py": "new", "b.py": "b"})
            res = apply_zip(z, dest, dry=True)
            self.assertEqual((res["changed"], res["new"]), (["a.py"], ["b.py"]))
            self.assertEqual((dest / "a.py").read_text(), "old")
            self.assertFalse((dest / "b.py").exists())
            self.assertFalse((dest / "_apply_backup").exists())

    def test_unsafe_path_refuses_everything(self):
        for bad in ["../evil.txt", "/abs.txt", "C:/evil.txt", "a/../../evil.txt", ".git/config"]:
            with self.subTest(bad=bad), tempfile.TemporaryDirectory() as d, tempfile.TemporaryDirectory() as w:
                dest = Path(d)
                z = self._zip(Path(w), {"ok.py": "fine", bad: "bad"})
                res = apply_zip(z, dest)
                self.assertEqual(res["refused"], [bad])
                self.assertFalse((dest / "ok.py").exists())       # nothing was written

    def test_unknown_top_folder_refused_but_new_subfolder_ok(self):
        with tempfile.TemporaryDirectory() as d, tempfile.TemporaryDirectory() as w:
            dest = Path(d)
            _write(dest, "bgtools/a.py")
            res = apply_zip(self._zip(Path(w), {"photos/a.jpg": "x"}), dest)
            self.assertEqual(res["refused"], ["photos/a.jpg"])
            self.assertFalse((dest / "photos").exists())
            res = apply_zip(self._zip(Path(w), {"bgtools/new/b.py": "b", "top.md": "t"}), dest)
            self.assertEqual(res["refused"], [])
            self.assertEqual(sorted(res["new"]), ["bgtools/new/b.py", "top.md"])

    def test_go_needs_a_name(self):
        import contextlib, io
        sys.path.insert(0, str(_HARNESS))
        import go
        with contextlib.redirect_stdout(io.StringIO()) as out:
            self.assertEqual(go.main([]), 2)
        self.assertIn("Usage", out.getvalue())

    def test_newest_zip_ignores_our_own(self):
        import os
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            for name, t in [("a.zip", 100), ("b.zip", 200), ("bgtools_src_1.zip", 300)]:
                _write(root, name)
                os.utime(root / name, (t, t))
            self.assertEqual(newest_zip(root).name, "b.zip")
            self.assertIsNone(newest_zip(root / "nothing"))


if __name__ == "__main__":
    unittest.main()
