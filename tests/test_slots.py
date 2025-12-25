#!/usr/bin/env python
# Copyright (C) 2025 Tasos Alvas <tasos.alvas@qwertyuiopia.com>
# SPDX-License-Identifier: AGPL-3.0-or-later
"""Tests for the spdiu.scollections.slots module."""

import pytest  # noqa: F401

from spdiu.util import path
from spdiu.collections import slots


def test_backup_no_src(c, mock_slots) -> None:
    """Test that the backup task fails when there's no src."""
    assert slots.backup(c) is False, "The task must return False on failure."


def test_backup(c, mock_game_data, mock_slots) -> None:
    """Test the backup task."""
    cfg = c.config.spdiu
    saves = path(c, cfg.dirs.slots)

    bak_slot = saves / "backup" / cfg.backup_slot
    assert bak_slot.exists() is False, "The slot should not exist in the fixture."

    status = slots.backup(c)
    assert status is True, "The task must return True on success."
    assert bak_slot.exists(), "The backup save must be created."
    assert (bak_slot / "journal.dat").exists(), "The file must be copied."


def test_clean_no_src(c, mock_slots) -> None:
    """Test that the clean task fails when there's no src."""
    cfg = c.config.spdiu
    canary = path(c, cfg.dirs.slots) / "manual" / "floor12"

    assert slots.clean(c) is False, "The task must return False on failure."
    assert canary.exists(), "The slot must not be deleted."


def test_clean(c, mock_game_data, mock_slots) -> None:
    """Test the clean task."""
    cfg = c.config.spdiu
    saves = path(c, cfg.dirs.slots)

    canary = saves / "manual" / "floor12"
    status = slots.clean(c)

    assert status is True, "The task must return True on success."
    assert canary.exists() is False, "The slot save must be deleted."


def test_save_fail(c, mock_slots) -> None:
    """Test that the save task fails when there's no src or wrong arguments."""
    cfg = c.config.spdiu
    canary = path(c, cfg.dirs.slots) / "manual" / "yog"

    status = slots.save(c, slot=canary.name)
    assert status is False, "The task will not act without src."
    assert canary.exists() is False, "The save must not be created."
    assert slots.save(c, slot="*-*sd") is False, "Refuse non alphanumeric names."


def test_save(c, mock_game_data, mock_slots) -> None:
    """Test creating manual saves with the save task."""
    cfg = c.config.spdiu
    saves = path(c, cfg.dirs.slots, "manual")
    default = saves / cfg.default_slot

    assert slots.save(c) is True, "The task must run without parameters."
    assert default.exists() is True, "The default save slot must be created."

    backup = path(c, cfg.dirs.slots, "backup")
    status = slots.save(c)
    assert status is True, "The task will overwrite previous saves."
    assert (backup / cfg.default_slot).exists(), "A backup is created on overwrites."

    name = "king"
    named = saves / name
    status = slots.save(c, name)
    assert status is True, "The task will save named slots."
    assert named.exists() is True, "The save slot must be created."


def test_load_fail(c, mock_game_data, mock_slots) -> None:
    """Test that the load fails when there are wrong arguments."""
    assert slots.load(c, slot="default") is False, "Slot does not exist."
    assert slots.load(c, slot="manuel.tengu") is False, "Group does not exist."

    no_game = slots.load(c, slot="manual.tengu", game="game234")
    assert no_game is False, "Game does not exist."


def test_load_last_fail(c, mock_game_data) -> None:
    """Test that loading the last save fails when there's no src."""
    assert slots.load(c, last=True) is False, "There are no saves!"


def test_load(c, mock_slots) -> None:
    """Test the load task."""
    cfg = c.config.spdiu
    data = cfg.game.data
    saves = path(c, cfg.dirs.slots)

    assert slots.load(c, slot="tengu") is True, (
        "The task will load into an empty state."
    )
    assert data.exists() is True, "The active state must be created."

    game = data / "game1" / "game.dat"
    game.unlink()
    status = slots.load(c, slot="floor12", game="game1")

    assert status is True, "The task must succeed."
    assert game.exists() is True, "The game has been copied."

    backup = saves / "backup" / "floor12"
    assert backup.exists() is True, "A backup of the game data is made on load."


def test_ls_no_data(c, mock_slots) -> None:
    """Test the ls task without active game data."""
    assert slots.ls(c) is False


def test_ls_no_slots(c, mock_game_data) -> None:
    """Test the ls task without saved games."""
    assert type(slots.ls(c)) is dict


def test_ls(c, mock_game_data, mock_slots) -> None:
    """Test the ls task."""
    ls = slots.ls(c)

    assert type(ls) is dict
    assert len(ls["data"].games) == 3
    assert len(ls["slots"].slots[0].games) == 2


# def test_watch(c, mock_game_data, mock_slots) -> None:
#     """Test the watch task."""
#     pytest.fail("Not implemented")
