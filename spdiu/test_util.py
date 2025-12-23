#!/usr/bin/env python
# Copyright (C) 2025 Tasos Alvas <tasos.alvas@qwertyuiopia.com>
# SPDX-License-Identifier: AGPL-3.0-or-later
"""Tests for the spdiu.util module."""

import pytest

import os
from time import gmtime

import gzip
import json
# import xml.etree.ElementTree as ET

from invoke.context import MockContext
from invoke.config import Config

from . import util


@pytest.fixture
def mc():
    """Generate a MockContext with a Config.

    Contains a dirs.base value used in normalizing paths.
    """
    return MockContext(
        config=Config(
            {
                "spdiu": {
                    "dirs": {
                        "base": "~/mygames",
                    }
                }
            }
        )
    )


def test_path(mc):
    """Test the path function."""
    c = mc

    assert os.path.isabs(util.path(c, "shattered-pixel-dungeon"))
    assert os.path.isabs(util.path(c, "~/.config", "shattered", "pixel"))


def test_get_ts(tmp_path):
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


def test_read_dat(tmp_path):
    """Test reading gzipped SPD .dat files."""
    dummy_data = {
        "hero": {"HP": 130},
    }
    json_bin = str.encode(json.dumps(dummy_data, separators=(",", ":")))

    d = tmp_path / "dummy.dat"
    with gzip.open(d, "wb") as f:
        f.write(json_bin)

    with pytest.raises(FileNotFoundError):
        util.read_dat(tmp_path / "missing.dat")

    assert type(util.read_dat(d)) is dict
    assert util.read_dat(d).get("hero") is not None
    assert util.read_dat(d)["hero"]["HP"] == 130


# def test_write_dat():
#     """Test writing gzipped .dat files."""
#     pytest.fail("Test not ready yet")

# def test_read_xml():
#     """Test reading SPD Settings XML files."""
#     pytest.fail("Test not ready yet")

# def test_write_xml():
#     """Test writing SPD Settings XML files."""
#     pytest.fail("Test not ready yet")

# def test_replace():
#     """Test replacing directory trees."""
#     pytest.fail("Test not ready yet")

# def test_remove():
#     """Test removing directory trees."""
#     pytest.fail("Test not ready yet")

# def test_exists():
#     """Test path existence."""
#     pytest.fail("Test not ready yet")
