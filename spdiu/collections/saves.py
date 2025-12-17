#!/usr/bin/env python
# Copyright (C) 2025 Tasos Alvas <tasos.alvas@qwertyuiopia.com>
# SPDX-License-Identifier: AGPL-3.0-or-later
"""
SPDIU Saving and Loading task collection.

By convention, where applicable:
-s --slot is used to load a save slot by name
-g --game to pick a specific game in a slot
"""

import os
from invoke import task, Collection

from .. import util
from ..model import Slots


ns = Collection("io")


# File manipulation Tasks
@task
def backup(c):
    """
    Creates a backup of the active data.

    Automatically called by load and clean.
    """
    cfg = c.config.spdiu
    src = os.path.join(cfg.data_dir, cfg.active_save)
    dest = os.path.join(cfg.work_dir, cfg.backup_slot)

    try:
        util.replace(src, dest)

    except FileNotFoundError:
        print('Aborting! There seems to be no active data folder.')
        return


    print(f"Active state backup created! {cfg.i_bak} {cfg.backup_slot}")


@task(post=[backup])
def clean(c):
    """
    Removes all saved states, leaves a backup of the active data folder.
    """
    cfg = c.config.spdiu
    if not util.exists(os.path.join(data_dir, cfg.active_save)):
        print('Aborting! There seems to be no active data folder.')
        return


    s = Slots(cfg.work_dir)
    for p in s.slots:
        util.remove(p.root_dir)


    print(f"{cfg.i_clean} {len(s.slots)} saved states deleted.")


@task
def save(c, slot=None):
    """
    Saves a copy of the current savegame folder. -s [slot] to name a slot.

    Slot names can only be alphanumeric characters.

    When saving over an existing slot, a backup of the previous state is kept
    as bak.[slot name].

    Saves are kept in the game's data folder, with their slot as an extension.
    """
    cfg = c.config.spdiu

    if slot == None:
        slot = cfg.default_slot

    if slot and not slot.isalnum():
        print("Aborting! Names can only contain alphanumeric characters.")
        return


    src = os.path.join(cfg.data_dir, cfg.active_save)
    dest = os.path.join(cfg.work_dir, slot)
    bak = os.path.join(cfg.work_dir, f"{cfg.backup_slot}.{slot}")

    if util.exists(dest):
        util.replace(dest, bak)
        print(f"Previous save preserved as {cfg.i_bak} {cfg.backup_slot}.{slot}")


    try:
        util.replace(src, dest)
    except FileNotFoundError:
        print("No game data found to save!")


    print(f"State saved! {cfg.disc_b} {slot}")


@task
def load(c, last=False, slot=None, game=None):
    """
    Loads a save. -l for last save, -s [slot], -g [game] to only load a game.

    If -l, --last is provided, any slot named with -s is ignored.

    The -g, --game [game name] flag allows loading only a specific game,
    while leaving the player profile untouched (i.e. keeping unlocks).

    Loading will save a backup of the active save in the backup slot,
    unless the backup slot itself is being loaded.
    """

    cfg = c.config.spdiu
    s = Slots(cfg.work_dir)

    # determine the profile slot from the arguments
    if slot == None:
        slot = cfg.default_slot

    if last:
        if not s.slots:
            print("No saves found. Make some with 'inv save [-s slot name]'")
            return

        slot = s.slots[0].name


    # Get the instance of the profile to load, build the destination path
    p = s.get_slot(slot)
    ap_path = os.path.join(cfg.data_dir, cfg.active_save)

    if not p:
        print(f"Invalid slot name: {slot}. 'inv ls' to list existing slots.")


    # Load the requested profile and exit
    if game == None:
        if p.name != cfg.backup_slot:
            backup(c)

        util.replace(p.root_dir, ap_path)

        print(f"State loaded! {cfg.disc_a} {slot}")
        return


    # Get the instance of the requested game, build the destination path.
    g = p.get_game(game)
    agp = os.path.join(ap.root_dir, game)

    if not g:
        print('Game not found in slot.')
        print(f"'inv show -s {slot}' to list existing games.")
        return

    if  p.name != cfg.backup_slot:
        backup(c)

    util.replace(g.root_dir, agp)
    print(f"Game loaded! {cfg.disc_a} {slot} {cfg.i_game} {game}")


ns.add_task(backup)
ns.add_task(clean)
ns.add_task(save)
ns.add_task(load)
