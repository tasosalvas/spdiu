#!/usr/bin/env python
# Copyright (C) 2025 Tasos Alvas <tasos.alvas@qwertyuiopia.com>
# SPDX-License-Identifier: AGPL-3.0-or-later
"""
Shattered Pixel Dungeon Invoke Utility.

This file is the entry point to the SPDIU task collections:

'saves', imported at the root namespace:
  Tasks for saving, loading, and managing save slots.

'display', imported at the root namespace:
  Tasks for displaying information about the game state.

'cheats', imported at the 'cheat' namespace:
  Tasks that affect gameplay.

Usage:
'inv info' for this general documentation.
'inv info -h [collection name]' for a collection's documentation.

'inv -l' for a list of tasks.
'inv -h [task name]' for a task's full docstring.
"""

import os

from invoke import Collection, task

import spdiu  # required to get docstrings for the info task

from spdiu.collections.saves import save, load, backup, clean, watch, ls
from spdiu.collections.display import show
from spdiu.collections import get, cheats


# Default SPDIU configuration. Override values in invoke.yaml.
defaults = {
    'spdiu': {
        # SPDIU config
        'base_dir': os.path.dirname(os.path.realpath(__file__)),
        'work_dir': '~/.local/share/.shatteredpixel/saves',
        'default_slot': 'default',
        'backup_slot': 'bak',


        # Game release info, used to download the game
        'release_packages': 'packages',
        'release_github': 'https://github.com/00-Evan/shattered-pixel-dungeon/releases',
        'release_template': 'download/{version}/ShatteredPD-{version}-{platform}.{ext}',
        'release_version': None,
        'release_platform': 'Linux',
        'release_extension': 'zip',


        # The game installation
        'game_dir': os.path.join(os.path.dirname(os.path.realpath(__file__)), 'spd'),
        'game_cmd': 'bin/Shattered Pixel Dungeon',
        'game_ns': 'com.shatteredpixel.shatteredpixeldungeon',


        # Game user data
        'data_dir': '~/.local/share/.shatteredpixel',
        'active_save': 'shattered-pixel-dungeon',


        # Fancy decorations
        'time_format': '🗓️ %Y %b %d 🕰️ %H:%M:%S',

        'bullet_a': ' ||> ',
        'bullet_b': '  |> ',

        'disc_a': '📀',
        'disc_b': '💿',

        # Icons
        # TODO: unified icon namespace for visual stuff?
        'i_bak': '💾',
        'i_auto': '🤖',
        'i_game': '🕹️',
        'i_data': '🗂️',
        'i_clean': '🧹',

        'i_dict': '📖',
        'i_list': '📋',
        'i_int': '🧮',
        'i_float': '🍕',
        'i_str': '🔤',
        'i_bool': '💡',
    }
}


# Documentation helper, everything else lives in collections
@task
def info(c, config=False, help=None):
    """
    Usage and documentation. -c to display active configuration.

    It displays the docstring of a task collection.

    -h, --help [collection name] displays the collection's docstring instead.
    -c, --config displays the active SPDIU configuration.

    It supplements invoke core's 'inv -h' flag, which supplies task docstrings.
    """
    if config:
        cfg = c.config.spdiu
        d_cfg = defaults['spdiu']

        print('Active SPDIU configuration:')
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
ns.add_task(show)

# spdiu.collections.saves tasks
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
try:
    import local_tasks

    if 'ns' in dir(local_tasks):
        ns.add_collection(local_tasks.ns)

    else:
        if 'collection_name' in dir(local_tasks):
            col_name = local_tasks.collection_name
        else:
            col_name = 'u'

        ns.add_collection(Collection.from_module(local_tasks, col_name))

except ModuleNotFoundError:
    pass
