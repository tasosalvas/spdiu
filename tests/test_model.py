#!/usr/bin/env python
# Copyright (C) 2025 Tasos Alvas <tasos.alvas@qwertyuiopia.com>
# SPDX-License-Identifier: AGPL-3.0-or-later
"""Tests for the spdiu.model module."""

import pytest

import os
import time

from spdiu import util
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


class TestDataDir:
    """Tests DataDir, the parent class to Profile and Game."""

    def test_init(self, c, mock_game_data) -> None:
        """Test initializing a GameDir."""
        cfg = c.config.spdiu
        data = cfg.game.data

        with pytest.raises(AttributeError):
            model.DataDir("string")

        with pytest.raises(FileNotFoundError):
            model.DataDir(data / "nope")

        d = model.DataDir(data)
        assert len(d.dat_files) == 2
        assert d.name == data.name

    def test_ts(self, c, mock_game_data) -> None:
        """Test GameDir reports the timestamp of its newest modified file or folder."""
        cfg = c.config.spdiu
        data = cfg.game.data
        current_time = data.stat().st_mtime

        newer_time = current_time + 2000000
        os.utime(data, (newer_time, newer_time))

        nd = model.DataDir(data)
        assert nd.ts == time.gmtime(newer_time), "Newer dir's ts should be reported."

        data_file = data / "rankings.dat"

        newest_time = newer_time + 100000
        os.utime(data_file, (newest_time, newest_time))

        nf = model.DataDir(cfg.game.data)
        assert nf.ts == time.gmtime(newest_time), "Newest file's ts should be reported."

    def test_get_dat(self, c, mock_game_data) -> None:
        """Test reading and writing .dat files."""
        cfg = c.config.spdiu
        data = cfg.game.data

        rd = model.DataDir(data)

        with pytest.raises(FileNotFoundError):
            rd.get_dat("wrong.dat")

        rankings = rd.get_dat("rankings.dat")

        assert rankings["won"] == 5
        assert rankings["total"] == 10
        assert type(rankings["records"]) is list

    def test_set_dat(self, c, mock_game_data) -> None:
        """Test reading and writing .dat files."""
        cfg = c.config.spdiu
        data = cfg.game.data

        rd = model.DataDir(data)
        rankings = rd.get_dat("rankings.dat")
        rankings["won"] = 1024
        rankings["total"] = 4

        wd = model.DataDir(data)
        wd.set_dat("rankings.dat", rankings)

        rewritten = rd.get_dat("rankings.dat")

        assert rewritten["won"] == 1024
        assert rewritten["total"] == 4

    def test_repr(self, c, mock_game_data):
        """Tests the repr of DataDir."""
        cfg = c.config.spdiu
        data = util.path(c, cfg.game.data)

        d = model.DataDir(data)

        assert data.name in repr(d)
        assert "DataDir" in repr(d)


class TestGame:
    """Tests Game, the class representing active game dirs."""

    def test_init(self, c, mock_game_data) -> None:
        """Tests initializing a Game."""
        cfg = c.config.spdiu

        with pytest.raises(FileNotFoundError):
            model.Game(cfg.game.data)

        g = model.Game(cfg.game.data / "game1")

        assert hasattr(g, "ts"), "Game does not inherit DataDir attribute."
        assert g.name == "game1", "Name is not the name of the folder."

    def test_repr(self, c, mock_game_data):
        """Tests the repr of Game."""
        cfg = c.config.spdiu
        data = util.path(c, cfg.game.data, "game1")

        g = model.Game(data)

        assert data.name in repr(g)
        assert "Game" in repr(g)


class TestProfile:
    """Tests Profile, the class representing user data dirs."""

    def test_init(self, c, mock_game_data) -> None:
        """Tests initializing a Profile."""
        cfg = c.config.spdiu
        data = cfg.game.data

        with pytest.raises(FileNotFoundError):
            model.Profile(data / "game1")

        p = model.Profile(data)

        assert hasattr(p, "ts"), "Profile does not inherit DataDir attribute."
        assert p.name == data.name, "name is not the name of the folder."
        assert p.group == data.parent.name, (
            "group is not the name of the parent folder."
        )
        assert len(p.games) == 3, "The three games in the fixture were not detected."

    def test_get_settings(self, c, mock_game_data) -> None:
        """Tests reading a profile's settings.xml into a dict."""
        cfg = c.config.spdiu
        data = cfg.game.data
        p = model.Profile(data)
        settings = p.get_settings()

        assert settings["fullscreen"] == "false"
        assert settings["scale"] == "3"

    def test_get_game(self, c, mock_game_data) -> None:
        """Tests requesting a game by name."""
        cfg = c.config.spdiu
        data = cfg.game.data

        p = model.Profile(data)

        assert type(p.get_game("game1")) is model.Game, "Can't find an existing game."
        assert p.get_game("bupkis") is None, "Should return None for a non-Game."

    def test_ts_sorting(self, c, mock_game_data) -> None:
        """Tests whether games are correctly sorted by newest."""
        cfg = c.config.spdiu
        data = cfg.game.data

        current_time = data.stat().st_mtime
        newer_time = current_time + 2000000
        newer = data / "game2" / "game.dat"
        os.utime(newer, (newer_time, newer_time))

        nrp = model.Profile(data)
        assert nrp.ts == time.gmtime(newer_time), "Profile should report the file ts."
        assert nrp.games[0].name == "game2", "The newer game should be first."

        newest_time = newer_time + 1000000
        newest = data / "game3"
        os.utime(newest, (newest_time, newest_time))

        ntp = model.Profile(data)
        assert ntp.ts == time.gmtime(newest_time), (
            "Profile should report the game dir ts."
        )
        assert ntp.games[0].name == "game3", "The newest game should be first."

    def test_repr(self, c, mock_game_data):
        """Tests the repr of Profile."""
        cfg = c.config.spdiu
        data = util.path(c, cfg.game.data)

        p = model.Profile(data)

        assert data.name in repr(p)
        assert "Profile" in repr(p)


class TestSlots:
    """Tests Slots, manager handling savegame slots."""

    def test_init(self, c, mock_slots) -> None:
        """Tests initializing the Slots manager."""
        cfg = c.config.spdiu
        slots = util.path(c, cfg.dirs.slots)

        assert len(model.Slots(cfg.dirs.base).slots) == 0

        s = model.Slots(slots, ["manual", "auto", "backup"])

        assert s.name == "manual+auto+backup"
        assert len(s.slots) == 6

    def test_get_slot(self, c, mock_slots) -> None:
        """Tests getting a slot by name with dot syntax."""
        cfg = c.config.spdiu
        slots = util.path(c, cfg.dirs.slots)

        s = model.Slots(slots, ["manual", "auto"])

        assert len(s.slots) == 3
        assert s.get_slot("floor4") is None

        m_f3 = s.get_slot("floor3")
        assert type(m_f3) is model.Profile
        assert m_f3.name == "floor3"
        assert m_f3.group == "manual"

        nd = model.Slots(slots, ["manual", "backup"], "backup")
        assert nd.get_slot("floor3").group == "backup"
        assert nd.get_slot("manual.floor3").name == "floor3"
        assert nd.get_slot("manual.floor3").group == "manual"

    def test_ts_sorting(self, c, mock_slots) -> None:
        """Tests getting a slot by name with dot syntax."""
        cfg = c.config.spdiu
        slots = util.path(c, cfg.dirs.slots)

        newer = slots / "backup" / "floor12" / "game1" / "game.dat"
        current_time = newer.stat().st_mtime
        newer_time = current_time + 2000000

        os.utime(newer, (newer_time, newer_time))

        s = model.Slots(slots, ["manual", "backup"])
        assert s.slots[0].group == "backup"
        assert s.slots[0].name == "floor12"
        assert s.slots[0].ts == time.gmtime(newer_time)

    def test_repr(self, c, mock_slots):
        """Tests the repr of Slots."""
        cfg = c.config.spdiu
        slots = util.path(c, cfg.dirs.slots)

        s = model.Slots(slots, ["manual", "backup"])

        assert "manual+backup" in repr(s)
        assert "Slots" in repr(s)
