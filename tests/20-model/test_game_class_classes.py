#!/usr/bin/env python
# Copyright (C) 2025 Tasos Alvas <tasos.alvas@qwertyuiopia.com>
# SPDX-License-Identifier: AGPL-3.0-or-later
"""Tests for the game class representation classes."""

from spdiu import model


class TestItem:
    """Tests Item, a helper class for modeling items."""

    def test_init(self):
        """Tests initializing an Item."""
        blank = model.Item()

        assert blank.item.get("__className") is not None
        assert blank.item.get("level") == 0

        plus = model.Item({"level": 2})
        assert plus.item.get("level") >= 0
