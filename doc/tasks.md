<!-- Copyright (C) 2025 Tasos Alvas <tasos.alvas@qwertyuiopia.com> -->
<!-- SPDX-License-Identifier: AGPL-3.0-or-later                    -->
# SPDIU Task Collections Reference

The tasks available in SPDIU are categorized into Python modules in `spdiu.collections`.

They are either imported as part of the base commands, or _namespaced_ in their own category.

For example:
- `save` is the imported _task_ `saves.save`, and can be ran by `inv save`
- `bones` is `cheats.bones`, and gets ran by `inv cheats.bones` from the imported _collection_.



# The `saves` collection
> Tasks imported at the root namespace.

Provides save state management tasks:

- `save` and `load` allow you to manage save slots for _backups_, _auto_ and _manual_ saves.
- `ls` will list your slots, and `clean` will wipe them all
- The `watch` task starts the game, autosaving after certain log events


# The `display` collection
> Tasks imported at the root namespace.

- `show` task reads saves or active game data and displays details on their contents


# The `cheats` collection
> Collection added as the `cheats` namespace.

- `inv cheat.bones` can bless your next run with one out of a selection of care packages
- `inv cheat.consumables` gets you all consumable identities for the active game
- `inv cheat.gold` and `.energy` let you adjust your wealth appropriately


# The `get` collection
> Collection added as the `get` namespace.

- `get.latest` provides a
- `get.install` gets you all consumable identities for the active game


# tasks.py
> This is the main entry point for SPDIU.

The `inv` command reads this. It contains the default configuration, merges it with your user config, loads all the collections, and contains only one task of its own:

- `info` task provides introductory documentation, `-c` displays config, `-h` provides overviews of the SPDIU collections

It will also load your own collections if you place them at `local_tasks.py`.


# Where to go from here

- The [API manual](./api.md) explains how to write your own tasks
