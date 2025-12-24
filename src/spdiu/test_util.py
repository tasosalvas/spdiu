#!/usr/bin/env python
# Copyright (C) 2025 Tasos Alvas <tasos.alvas@qwertyuiopia.com>
# SPDX-License-Identifier: AGPL-3.0-or-later
"""Tests for the spdiu.util module."""

import pytest

import os
from time import gmtime
from invoke import MockContext

import gzip
import json

from . import util


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


def test_read_dat_bad_src(tmp_path) -> None:
    """Test that bad and nonexistent files raise the proper exceptions."""
    bad_gzip = tmp_path / "boo.dat"
    bad_gzip.write_text("boo!")

    with pytest.raises(FileNotFoundError):
        util.read_dat(tmp_path / "missing.dat")

    with pytest.raises(gzip.BadGzipFile):
        util.read_dat(bad_gzip)


def test_read_dat(tmp_path, game_data_dict) -> None:
    """Test reading gzipped SPD .dat files."""
    json_bin = str.encode(json.dumps(game_data_dict, separators=(",", ":")))
    df = tmp_path / "dummy.dat"

    with gzip.open(df, "wb") as f:
        f.write(json_bin)

    assert type(util.read_dat(df)) is dict
    assert util.read_dat(df).get("hero") is not None
    assert util.read_dat(df)["hero"]["HP"] == 130


def test_write_dat(tmp_path, game_data_dict) -> None:
    """Test writing gzipped .dat files."""
    df = tmp_path / "write.dat"

    util.write_dat(df, game_data_dict)

    assert type(util.read_dat(df)) is dict
    assert util.read_dat(df).get("hero") is not None
    assert util.read_dat(df)["hero"]["HP"] == 130


def test_read_xml(tmp_path, settings_xml) -> None:
    """Test reading SPD Settings XML files."""
    xf = tmp_path / "read.xml"
    xf.write_text(settings_xml)

    assert type(util.read_xml(xf)) is dict
    assert util.read_xml(xf)["scale"] == "3"
    assert util.read_xml(xf)["fullscreen"] == "false"


def test_write_xml(tmp_path, settings_dict) -> None:
    """Test writing SPD Settings XML files."""
    xf = tmp_path / "write.xml"

    util.write_xml(xf, settings_dict)

    assert type(util.read_xml(xf)) is dict
    assert util.read_xml(xf)["scale"] == "3"
    assert util.read_xml(xf)["fullscreen"] == "false"


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
