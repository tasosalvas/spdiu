<!-- Copyright (C) 2025 Tasos Alvas <tasos.alvas@qwertyuiopia.com> -->
<!-- SPDX-License-Identifier: AGPL-3.0-or-later                    -->
# SPDIU Task Collections Reference

The tasks available in SPDIU are categorized into Python modules in `spdiu.collections`.

They are either imported as part of the base commands, or _namespaced_ in their own category.

For example:
- `save` is the imported _task_ `slots.save`, and can be ran by `inv save`
- `bones` is `cheats.bones`, and gets ran by `inv cheats.bones` from the imported _collection_.


## Interactive help

SPDIU's `info` task and invoke's interactive help system make it easy to get code documentation to the terminal.

- `inv -h task` provides **help text** for each _task_, are the Python docstrings of the functions themselves
- `inv info -h collection` **info text** for each collection is the docstring of the module itself

The `info` task looks in `spdiu.collections`, so you can still get documentation on modules that are not imported in a namespace.

> This approach of having documentation next to the code aims to make it easy to keep up to date. Automatic html / markdown generation is planned and doable. Until then, this page will provide a usage overview.
>
> If you can't currently run the interactive help, all of its content is in the docstrings of the [collection code](../spdiu/collections/).


# The `slots` collection
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

- `inv cheats.bones` can bless your next run with one out of a selection of care packages
- `inv cheats.consumables` gets you all consumable identities for the active game
- `inv cheats.gold` and `.energy` let you adjust your wealth appropriately


# The `get` collection
> Collection added as the `get` namespace.

Provides tasks related to getting information, primarily related to installing the game off the internet.

- `get.latest` returns the appropriate package to install for the latest version
- `get releases` returns a list of releases and allows you to filter it by a search pattern
- `get.install` gets you all consumable identities for the active game


# tasks.py
> This is the main entry point for SPDIU.

The `inv` command reads this. It contains the default configuration, merges it with your user config, loads all the collections, and contains only one task of its own:

- `info` task provides introductory documentation, `-c` displays config, `-h` provides overviews of the SPDIU collections

It will also load your own collections if you place them at `local_tasks.py`.


# The `dev` collection
> Not added automatically, but you can add it to your `local_tasks.py`. Exercise for the reader.

It has a task that prints a very pretty dump of the invoke config object using a function from `spdiu.display`.


# Where to go from here

- The [API manual](./api.md) explains how to write your own tasks
