#!/usr/bin/env python
# Copyright (C) 2025 Tasos Alvas <tasos.alvas@qwertyuiopia.com>
# SPDX-License-Identifier: AGPL-3.0-or-later
"""Tests for the spdiu.util file and directory functions."""

import pytest

import os
from time import gmtime
from invoke import MockContext

from spdiu import util


def test_path(c: MockContext, tmp_path) -> None:
    """Test the path function."""
    assert util.path(c, "shattered-pixel-dungeon").is_absolute()
    assert util.path(c, "~/.config", "shattered", "pixel").is_absolute()


def test_get_ts(tmp_path) -> None:
    """Test retreiving a timestamp from a file."""
    old_time = 450000000  # Some time in 1984
    old_gmtime = gmtime(old_time)  # The expected result

    old_dir = tmp_path / "old_dir"
    old_dir.mkdir()
    os.utime(old_dir, (old_time, old_time))

    old_file = tmp_path / "old_file.txt"
    old_file.touch()
    os.utime(old_file, (old_time, old_time))

    new_file = tmp_path / "new_file.txt"
    new_file.touch()

    assert util.get_ts(old_file) == old_gmtime
    assert util.get_ts(old_dir) == old_gmtime
    assert util.get_ts(new_file) > old_gmtime


def test_replace_bad_src(tmp_path) -> None:
    """Test replacing directory trees."""
    bad_src = tmp_path / "nope"
    dest = tmp_path / "yup"

    with pytest.raises(FileNotFoundError):
        util.replace(bad_src, dest)


def test_replace(tmp_path) -> None:
    """Test replacing directory trees."""
    d_src = tmp_path / "a"
    d_src.mkdir()

    f_src = d_src / "src.txt"
    f_src.write_text("source")

    d_exists = tmp_path / "e"
    d_exists.mkdir()

    f_exists = tmp_path / "e" / "exists.txt"
    f_exists.touch()

    f_exists_src = d_exists / "src.txt"
    f_exists_src.write_text("preexisting")

    util.replace(d_src, d_exists)

    assert f_exists_src.exists(), "File did not get copied."
    assert not f_exists.exists(), "Old file not removed."
    assert f_exists_src.read_text() == "source", "Content is not as expected."


def test_remove(tmp_path) -> None:
    """Test removing directory trees."""
    d_top = tmp_path / "a"
    d_nested = tmp_path / "a" / "b"
    f = d_nested / "text.txt"

    d_nested.mkdir(parents=True)
    f.touch()

    util.remove(d_top)

    assert not d_top.exists()
