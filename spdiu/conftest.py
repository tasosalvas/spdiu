#!/usr/bin/env python
# Copyright (C) 2025 Tasos Alvas <tasos.alvas@qwertyuiopia.com>
# SPDX-License-Identifier: AGPL-3.0-or-later
"""Common fixtures for spdiu tests."""

import pytest

from invoke.context import MockContext
from invoke.config import Config

from . import util
from .tasks import defaults as spdiu_defaults


@pytest.fixture
def c(tmp_path) -> MockContext:
    """Provide a MockContext with a Config that works for tmp_path.

    `dirs.base` is set to tmp_path / base
    `game.date` is set to tmp_path / data
    """
    config_dict = spdiu_defaults
    config_dict["spdiu"]["dirs"]["base"] = tmp_path / "base"
    config_dict["spdiu"]["game"]["data"] = tmp_path / "data"

    return MockContext(config=Config(config_dict))


@pytest.fixture
def settings_dict() -> dict:
    """Provide an example parsed settings dictionary.

    Equivalent to settings_xml.
    """
    return {
        "scale": "3",
        "fullscreen": "false",
    }


@pytest.fixture
def rankings_data_dict() -> dict:
    """Provide a dict of profile rankings data."""
    return {
        "won": 5,
        "total": 10,
        "records": [],
    }


@pytest.fixture
def journal_data_dict() -> dict:
    """Provide a dict of profile journal data."""
    return {
        "bestiary_classes": [],
        "bestiary_seen": [],
        "catalog_uses": [],
        "documents": [],
        "bestiary_encounters": [],
        "catalog_seen": [],
        "catalog_classes": [],
    }


@pytest.fixture
def game_data_dict() -> dict:
    """Provide a dict of game data."""
    return {
        "won": False,
        "hero": {"HP": 130},
    }


def _build_fake_slot(
    path,
    settings_data: dict,
    rankings_data: dict,
    journal_data: dict,
    game_data: dict,
    games: int = 0,
) -> None:
    """Create a fake user profile with n games at path."""
    path.mkdir(parents=True)

    settings_xml = path / "settings.xml"
    util.write_xml(settings_xml, settings_data)

    rankings_dat = path / "rankings.dat"
    util.write_dat(rankings_dat, rankings_data)

    journal_dat = path / "journal.dat"
    util.write_dat(journal_dat, journal_data)

    for i in range(games):
        gpath = path / f"game{str(i + 1)}"
        gpath.mkdir(parents=True)
        game_dat = gpath / "game.dat"
        util.write_dat(game_dat, game_data)


@pytest.fixture
def mock_game_data(
    c, tmp_path, settings_dict, rankings_data_dict, journal_data_dict, game_data_dict
):
    """Populate the mock data dir with mock save data."""
    cfg = c.config.spdiu
    data = cfg.game.data

    _build_fake_slot(
        data, settings_dict, rankings_data_dict, journal_data_dict, game_data_dict, 3
    )

    return [c, tmp_path]


@pytest.fixture
def mock_slots(
    c, tmp_path, settings_dict, rankings_data_dict, journal_data_dict, game_data_dict
):
    """Populate the mock base dir with mock slot data."""
    cfg = c.config.spdiu
    d_slots = util.path(c, cfg.dirs.slots)

    groups = ["manual", "backup"]
    saves = ["floor3", "floor12", "tengu"]

    for group in groups:
        d_group = d_slots / group
        for save in saves:
            slot = d_group / save
            _build_fake_slot(
                slot,
                settings_dict,
                rankings_data_dict,
                journal_data_dict,
                game_data_dict,
                2,
            )

    return [c, tmp_path]


@pytest.fixture
def settings_xml() -> str:
    """Provide example settings.xml content.

    Equivalent to settings_dict.
    """
    return "\n".join(
        [
            '<?xml version="1.0" encoding="UTF-8"?>',
            '<!DOCTYPE properties SYSTEM "http://java.sun.com/dtd/properties.dtd">',
            "<properties>",
            '<entry key="scale">3</entry>',
            '<entry key="fullscreen">false</entry>',
            "</properties>",
            "",
        ]
    )
