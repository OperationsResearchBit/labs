# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026 bgtools contributors
"""Turn the long output of `lab.py check NAME` into a short report (text in, text out)."""

from __future__ import annotations

import re

MAX_LINES = 20
MAX_WIDTH = 260

_HEADER = re.compile(r"^(FAIL|ERROR): (\S.*)$")      # "FAIL: test_x (mod.Class.test_x)"
_PROBLEM = re.compile(r"^\s*PROBLEM:\s*(.*)$")
_NOTE = re.compile(r"^\s*note:\s*(.*)$")


def _parse(lines):
    """Return (problems, notes, failures). A failure is a dict: kind, title, section, exc."""
    problems, notes, failures = [], [], []
    section, cur, in_tb = "", None, False
    for i, line in enumerate(lines):
        if line.startswith("== App tests"):
            section, cur = "app", None
            continue
        if line.startswith("== Tests for"):
            section, cur = "idea", None
            continue
        m = _HEADER.match(line)
        if m and i and lines[i - 1].startswith("====="):
            cur = {"kind": m.group(1), "title": m.group(2), "section": section, "exc": ""}
            failures.append(cur)
            in_tb = False
            continue
        if line.startswith("=====") or line.startswith("Ran "):
            cur = None
            continue
        if cur is not None:
            if line.startswith("Traceback"):
                in_tb = True
            elif in_tb and line and not line[0].isspace() and not set(line) <= {"-", "="}:
                cur["exc"] = line              # the last traceback's exception line wins
                in_tb = False
            continue
        if section == "":                      # these lines print before the first "==" header
            p, n = _PROBLEM.match(line), _NOTE.match(line)
            if p:
                problems.append(p.group(1))
            elif n:
                notes.append(n.group(1))
    return problems, notes, failures


def _clip(line: str) -> str:
    return line if len(line) <= MAX_WIDTH else line[:MAX_WIDTH - 3] + "..."


def summarize(name: str, output: str) -> str:
    """Short report: verdict, problems, notes, failed tests (no tracebacks), at most 20 lines."""
    lines = output.splitlines()
    problems, notes, failures = _parse(lines)
    ready = any(l.startswith("Ready. Next:") for l in lines)
    no_test = any(l.startswith("Not ready: no real test") for l in lines)
    if ready:
        verdict = "READY"
    elif problems or failures:
        verdict = "NOT READY"
    elif no_test:
        verdict = "NO TEST"
    else:
        verdict = "NOT READY"

    out = [f"ai_harness report: {name}", f"verdict: {verdict}"]
    out += [f"problem: {p}" for p in problems]
    out += [f"note: {n}" for n in notes]
    for f in failures:
        who = "app " if f["section"] == "app" else ""
        out.append(f"{who}{'failed' if f['kind'] == 'FAIL' else 'error'}: {f['title']}")
        if f["exc"]:
            out.append(f"  {f['exc']}")
    if any(f["section"] == "app" for f in failures):
        out.append("  (an app test is red: this idea may have broken the app, or the app was already red)")
    if verdict == "NOT READY" and not problems and not failures:
        tail = [l for l in lines if l.strip()][-3:]      # a crash in lab.py, or output we did not recognise
        out.append("output (last 3 lines):")
        out += [f"  {l.strip()}" for l in tail]

    out = [_clip(l) for l in out]
    if len(out) > MAX_LINES:
        dropped = len(out) - (MAX_LINES - 1)
        out = out[:MAX_LINES - 1] + [f"... {dropped} more line(s) dropped"]
    return "\n".join(out)
