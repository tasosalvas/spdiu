#!/usr/bin/env python
# Copyright (C) 2025 Tasos Alvas <tasos.alvas@qwertyuiopia.com>
# SPDX-License-Identifier: AGPL-3.0-or-later
"""Tests for the s[pd]iu application."""

from importlib import metadata
from spdiu.cli import __version__


def test_version() -> None:
    """Test that the module's version is the one on pyproject."""
    assert __version__ == metadata.version("spdiu")


# smoke test mode
if __name__ == "__main__":
    test_version()
