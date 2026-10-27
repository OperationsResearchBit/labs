# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026 bgtools contributors
"""Tests for _ai_harness: check output -> short report, and the `short` command.

Run from the lab folder:  python -m unittest discover -s _ai_harness/tests
No app is needed.
"""

import contextlib
import io
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

_HARNESS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_HARNESS))
sys.path.insert(0, str(_HARNESS / "helpers"))

import short  # noqa: E402
from check_report import MAX_WIDTH, summarize  # noqa: E402

BAR = "=" * 70
DASH = "-" * 70

READY = f"""Checking 'pair_alert'  (2 file(s), status: building)
== App tests, with 'pair_alert' laid over the app
{DASH}
Ran 140 tests in 3.1s

OK

== Tests for 'pair_alert'
...
{DASH}
Ran 3 tests in 0.1s

OK

Ready. Next:  promote pair_alert
"""

NOTES_READY = READY.replace("\n== App tests", "\n  note: two files share a name\n== App tests", 1)

NO_TEST = f"""Checking 'pair_alert'  (1 file(s), status: idea)
== App tests, with 'pair_alert' laid over the app
Ran 140 tests in 3.1s

OK

== Tests for 'pair_alert'
{DASH}
Ran 0 tests in 0.0s

NO TESTS RAN

Not ready: no real test for this idea yet (skipped tests do not count).
"""

FAILING = f"""Checking 'pair_alert'  (2 file(s), status: building)
  PROBLEM: bgtools/analysis/pair_alert.py: missing the license header (copy it from any app file)
== App tests, with 'pair_alert' laid over the app
{DASH}
Ran 140 tests in 3.1s

OK

== Tests for 'pair_alert'
F..
{BAR}
FAIL: test_third_copy_warns (test_pair_alert.PairAlertTests.test_third_copy_warns)
{DASH}
Traceback (most recent call last):
  File "x.py", line 10, in test_third_copy_warns
    self.assertEqual(a, b)
  File "y.py", line 99, in helper
    pass
AssertionError: 'a' != 'b'

{DASH}
Ran 3 tests in 0.1s

FAILED (failures=1)

Not ready: some tests failed.

Not ready: fix the PROBLEM lines above.
"""

IMPORT_ERROR = f"""Checking 'pair_alert'  (1 file(s), status: building)
== App tests, with 'pair_alert' laid over the app
Ran 140 tests in 3.1s

OK

== Tests for 'pair_alert'
E
{BAR}
ERROR: test_pair_alert (unittest.loader._FailedTest.test_pair_alert)
{DASH}
ImportError: Failed to import test module: test_pair_alert
Traceback (most recent call last):
  File "/usr/lib/python3.12/unittest/loader.py", line 396, in _find_test_path
    module = self._get_module_from_name(name)
  File "/usr/lib/python3.12/unittest/loader.py", line 339, in _get_module_from_name
    __import__(name)
  File "tests/test_pair_alert.py", line 4, in <module>
    from bgtools.analysis.pair_alert import pairs
ModuleNotFoundError: No module named 'bgtools.analysis.pair_alert'

{DASH}
Ran 1 test in 0.0s

FAILED (errors=1)

Not ready: some tests failed.
"""

APP_FAILING = f"""Checking 'pair_alert'  (1 file(s), status: building)
== App tests, with 'pair_alert' laid over the app
F
{BAR}
FAIL: test_golden_screen (test_golden.GoldenTests.test_golden_screen)
{DASH}
Traceback (most recent call last):
  File "g.py", line 5, in test_golden_screen
    self.assertEqual(a, b)
AssertionError: 'x' != 'y'

{DASH}
Ran 140 tests in 3.1s

FAILED (failures=1)

== Tests for 'pair_alert'
{DASH}
Ran 3 tests in 0.1s

OK

Not ready: some tests failed.
"""

CRASH = """Traceback (most recent call last):
  File "lab.py", line 320, in <module>
    raise SystemExit(main())
  File "lab.py", line 311, in main
    return check(rest[0])
ValueError: boom
"""


class SummarizeTests(unittest.TestCase):
    def test_ready(self):
        out = summarize("pair_alert", READY)
        self.assertEqual(out.splitlines()[0], "ai_harness report: pair_alert")
        self.assertIn("verdict: READY", out)

    def test_no_test(self):
        self.assertIn("verdict: NO TEST", summarize("pair_alert", NO_TEST))

    def test_failing_names_the_problem_and_the_test(self):
        out = summarize("pair_alert", FAILING)
        self.assertIn("verdict: NOT READY", out)
        self.assertIn("problem: bgtools/analysis/pair_alert.py: missing the license header", out)
        self.assertIn("failed: test_third_copy_warns (test_pair_alert.PairAlertTests.test_third_copy_warns)", out)
        self.assertIn("AssertionError: 'a' != 'b'", out)

    def test_no_traceback(self):
        out = summarize("pair_alert", FAILING)
        self.assertNotIn("Traceback", out)
        self.assertNotIn('File "', out)

    def test_older_python_header_form(self):
        old = FAILING.replace("PairAlertTests.test_third_copy_warns)", "PairAlertTests)")
        self.assertIn("failed: test_third_copy_warns (test_pair_alert.PairAlertTests)", summarize("p", old))

    def test_import_error_shows_the_exception_line(self):
        out = summarize("pair_alert", IMPORT_ERROR)
        self.assertIn("verdict: NOT READY", out)
        self.assertIn("error: test_pair_alert (unittest.loader._FailedTest.test_pair_alert)", out)
        self.assertIn("ModuleNotFoundError: No module named 'bgtools.analysis.pair_alert'", out)
        self.assertNotIn("Failed to import test module", out)

    def test_notes_are_not_problems(self):
        out = summarize("pair_alert", NOTES_READY)
        self.assertIn("verdict: READY", out)
        self.assertIn("note: two files share a name", out)
        self.assertNotIn("problem:", out)

    def test_app_failure_is_labeled(self):
        out = summarize("pair_alert", APP_FAILING)
        self.assertIn("verdict: NOT READY", out)
        self.assertIn("app failed: test_golden_screen", out)
        self.assertIn("may have broken the app", out)

    def test_crash_shows_the_last_lines(self):
        out = summarize("pair_alert", CRASH)
        self.assertIn("verdict: NOT READY", out)
        self.assertIn("ValueError: boom", out)
        self.assertLessEqual(len(out.splitlines()), 7)

    def test_many_failures_are_capped(self):
        many = FAILING + "".join(
            f"{BAR}\nFAIL: test_{i} (m.C.test_{i})\n{DASH}\nTraceback (most recent call last):\n"
            f"  File \"x.py\", line 1, in f\nAssertionError: n{i}\n\n" for i in range(100))
        lines = summarize("pair_alert", many).splitlines()
        self.assertLessEqual(len(lines), 20)
        self.assertIn("dropped", lines[-1])

    def test_long_lines_are_cut(self):
        long_problem = READY.replace("Checking", "  PROBLEM: " + "x" * 500 + "\nChecking", 1)
        self.assertTrue(all(len(l) <= MAX_WIDTH for l in summarize("p", long_problem).splitlines()))


class ShortCommandTests(unittest.TestCase):
    def _run(self, argv, stdout="", code=0):
        buf = io.StringIO()
        with mock.patch.object(short.subprocess, "run",
                               return_value=SimpleNamespace(stdout=stdout, returncode=code)) as run:
            with contextlib.redirect_stdout(buf):
                result = short.main(argv)
        return result, buf.getvalue(), run

    def test_passes_the_exit_code_and_prints_the_report(self):
        result, text, run = self._run(["pair_alert"], READY, 0)
        self.assertEqual(result, 0)
        self.assertIn("verdict: READY", text)
        self.assertEqual(run.call_args.args[0][-2:], ["check", "pair_alert"])
        result, text, _ = self._run(["pair_alert"], FAILING, 1)
        self.assertEqual(result, 1)
        self.assertIn("verdict: NOT READY", text)

    def test_usage_on_bad_arguments(self):
        for argv in ([], ["a", "b"], ["--x"]):
            result, text, run = self._run(argv)
            self.assertEqual(result, 2)
            self.assertIn("Usage", text)
            run.assert_not_called()


if __name__ == "__main__":
    unittest.main()
