# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026 bgtools contributors
"""Tests for the 'display_template' idea: the Example from IDEA.md."""

import dataclasses
import unittest

from bgtools.adapter_display_template.render import render
from bgtools.core.domain import Status
from bgtools.ui.sandbox.demo import fake_snapshot


def with_status(turn, tier, now, mx):
    return dataclasses.replace(fake_snapshot(), status=Status(turn, tier, now, mx))


class Render(unittest.TestCase):
    def test_first_line_reads_status(self):
        first = render(with_status(7, 3, 6, 7)).split("\n")[0]
        self.assertEqual(first, "Hello, Battlegrounds!  turn 7 · tier 3 · gold 6/7")

    def test_unknown_values_show_question_marks(self):
        first = render(with_status(None, None, None, None)).split("\n")[0]
        self.assertEqual(first, "Hello, Battlegrounds!  turn ? · tier ? · gold ?/?")

    def test_second_line_lists_the_board(self):
        snap = with_status(7, 3, 6, 7)
        names = ", ".join(m.name for m in snap.board)
        self.assertEqual(render(snap).split("\n")[1], "Board: " + names)

    def test_empty_board(self):
        snap = dataclasses.replace(with_status(7, 3, 6, 7), board=())
        self.assertEqual(render(snap).split("\n")[1], "Board: (empty)")

    def test_respects_the_window_height(self):
        self.assertEqual(len(render(with_status(7, 3, 6, 7), rows=1).split("\n")), 1)


if __name__ == "__main__":
    unittest.main()
