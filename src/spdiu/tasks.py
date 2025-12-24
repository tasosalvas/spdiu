#!/usr/bin/env python
# Copyright (C) 2025 Tasos Alvas <tasos.alvas@qwertyuiopia.com>
# SPDX-License-Identifier: AGPL-3.0-or-later
"""
Shattered Pixel Dungeon Invoke Utility.

This file is the entry point to the SPDIU task collections:

'slots', imported at the root namespace:
  Tasks for saving, loading, and managing save slots.

'display', imported at the root namespace:
  Tasks for displaying information about the game state.

'get', imported at the 'get' namespace:
  Tasks for listing and downloading game releases.

'cheats', imported at the 'cheats' namespace:
  Tasks that affect gameplay.

Usage:
'inv info' for this general documentation.
'inv info -h [collection name]' for a collection's documentation.

'inv -l' for a list of tasks.
'inv -h [task name]' for a task's full docstring.
"""

from pathlib import Path

from invoke import Collection, task

import spdiu  # required to get docstrings for the info task

# collections imported at the root namespace
from spdiu.collections.slots import save, load, backup, clean, watch, ls

# The rest of the collections
from spdiu.collections import get, display, cheats


# Default SPDIU configuration. Override values in invoke.yaml.
defaults = {
    "spdiu": {
        "dirs": {
            # Internal variable, the location of the script.
            "base": Path(__file__).resolve().parent,
            "slots": "slots",
            "package": "packages",
            "game": "game",
        },
        # SPDIU config
        "default_slot": "default",
        "backup_slot": "bak",
        ## Game release info, used to download the game
        "release": {
            # Github specific, if they work elsewhere it's a miracle
            "gh_use_api": True,
            "project": "00-Evan/shattered-pixel-dungeon",
            # Release properties, used for fishing for the right release
            "version": None,
            "tag_name": None,
            "platform": "Linux",
            "extension": "zip",
            # Template expression, constructs a download url if automation can't
            "template": "https://github.com/{project}/releases/download/{tag_name}/ShatteredPD-{version}-{platform}.{ext}",
        },
        # The game installation
        "game": {
            "data": "~/.local/share/.shatteredpixel/shattered-pixel-dungeon",
            "cmd": "bin/Shattered Pixel Dungeon",
            "ns": "com.shatteredpixel.shatteredpixeldungeon",
        },
        # Fancy decorations
        "time_format": "🗓️ %Y %b %d 🕰️ %H:%M:%S",
        "bullet_a": " ||> ",
        "bullet_b": "  |> ",
        # Icons
        "i": {
            "disc_a": "📀",
            "disc_b": "💿",
            "bak": "💾",
            "auto": "🤖",
            "game": "🕹️",
            "data": "🗂️",
            "clean": "🧹",
            "package": "📦",
            "fork": "🍽️",
            "unknown": "👽",
            "warning": "☢️",
            "inspect": "🔎",
            # data types
            "dict": "📖",
            "list": "📋",
            "int": "🧮",
            "float": "🍕",
            "str": "🔤",
            "bool": "💡",
            "NoneType": "🫙",
        },
    }
}


# Documentation helper, everything else lives in collections
@task
def info(c, config=False, help=None):
    """
    Usage and documentation. -c to display active configuration.

    It displays the docstring of a task collection.

    -h, --help [collection] displays the collection's docstring instead.
    -c, --config displays the active SPDIU configuration.

    It supplements invoke core's 'inv -h' flag, which supplies task docstrings.
    """
    if config:
        cfg = c.config.spdiu
        d_cfg = defaults["spdiu"]

        print("Active SPDIU configuration:")
        print(f"{cfg.bullet_b}: default | {cfg.bullet_a}: overridden\n")

        for k, v in cfg.items():
            bullet = cfg.bullet_b if d_cfg[k] == v else cfg.bullet_a
            print(f"{bullet}{k}: {v}")

        return

    if help:
        if help in dir(spdiu.collections):
            print(getattr(spdiu.collections, help).__doc__)
            return
        else:
            print(f"Collection {help} not found. 'inv info' for general help.")
            return

    print(__doc__)
    print("'inv info -c' to display active SPDIU configuration.")
    return


# SPDIU root namespace
ns = Collection()
ns.configure(defaults)
ns.add_task(info)

# spdiu.collections.display tasks
ns.add_collection(display)

# spdiu.collections.slots tasks
ns.add_task(save)
ns.add_task(load)
ns.add_task(backup)
ns.add_task(clean)
ns.add_task(watch)
ns.add_task(ls)


# namespaced collections
ns.add_collection(get)
ns.add_collection(cheats)


# Conditionally import local project tasks
# try:
#     import local_tasks

#     if "ns" in dir(local_tasks):
#         ns.add_collection(local_tasks.ns)

#     else:
#         if "collection_name" in dir(local_tasks):
#             col_name = local_tasks.collection_name
#         else:
#             col_name = "u"

#         ns.add_collection(Collection.from_module(local_tasks, col_name))

# except ModuleNotFoundError:
#     pass
