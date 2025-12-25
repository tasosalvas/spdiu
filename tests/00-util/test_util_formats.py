#!/usr/bin/env python
# Copyright (C) 2025 Tasos Alvas <tasos.alvas@qwertyuiopia.com>
# SPDX-License-Identifier: AGPL-3.0-or-later
"""Tests for the spdiu.util game data readers and writers."""

import pytest

import gzip
import json

from spdiu import util


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
