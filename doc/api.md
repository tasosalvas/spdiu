<!-- Copyright (C) 2025 Tasos Alvas <tasos.alvas@qwertyuiopia.com> -->
<!-- SPDX-License-Identifier: AGPL-3.0-or-later                    -->
# The SpdIU API Manual

Just place a `local_tasks.py` in your SPDIO folder, and they will be loaded as invoke commands in the `u` namespace.

`spdiu.model` contains Python classes that represent game objects, allowing you to query and edit any part of a savegame in an object-oriented context.

- The `Item` class can initialize valid item dicts to allow you to craft your own
- The `Profile` and `Game` classes can manage all data in a game state
- `Slots` manager helps keep track of saved states

The `spdiu.util` module provides common utilities for working with the game's data folders and files, including reading and writing the `.dat` files containing the game's state. The classes use them and so can you.


# Adding your own tasks
The `tasks.py` file created in your initialized SpdIU directories is more than a way to initialize an SpdIU folder.

The utility of some of the functionality of SpdIU, such as unpacking save data, is not just the couple of lines it prints by default, but the fact that it makes the contents of a save available as Python objects.

Some obligatory links:
- The [Invoke documentation](https://docs.pyinvoke.org/en/stable/getting-started.html), for usage not covered in SpdIU's documentation and examples
- The [Python documentation](https://docs.python.org), the main and most important reference while we're working with it
- The [Invoke namespace documentation](https://docs.pyinvoke.org/en/stable/concepts/namespaces.html) can be helpful in adjusting your namespaces to access just the tasks you need.
- Finally, [SpdIU's main collection](../spdiu/spdiu.py) and [sub-collections](../spdiu/collections) should serve as good working examples.


# Accessing CLI arguments

> TODO: Until then, see the above invoke links or the spdiu source.


# Accessing configuration

The [Configuration Manual](./configuration.md) goes over configuring an instance from `spdiu.yaml`.

When the `siu` command runs, these values override the `invoke.Collection` defaults defined in `tasks.py`.


```py
from invoke import task

@task
def config_where(c):
    """This is our mantra!"""
    cfg = c.config.spdiu

    location = cfg.game.data
    dev = cfg['release']['project'].split('/')[-1]

    print(f"{dev}, all up in my {location}!")

```
`c` is the invoke [Context](https://docs.pyinvoke.org/en/stable/api/context.html). It's passed to all tasks on execution, and contains the state of this invoke call.

> The context also provides access to common invoke API calls, such as `c.run`, but ideally we want to do stuff in Python and not on the underlying shell, to be compatible with wherever it might run. It hasn't been unavoidable yet.
>
> Your code is your code, though! I have tons of tasks that would only run on Debian in other projects.

In it, there's the invoke [config](https://docs.pyinvoke.org/en/stable/api/config.html) object (Invoke [concepts/Configuration](https://docs.pyinvoke.org/en/stable/concepts/configuration.html) guide, for the newly acquainted).

`c.config` contains the configuration for this run, taking into account the defaults for the collection and like a bunch of layers of system and user configuration, including our `spdiu.yaml`.

All of SpdIU's tasks that deal with config begin with `cfg = c.config.spdiu`, then access the values as `cfg.value.value` with dot syntax.


# The `spdiu` module

## `spdiu.collections`

This submodule contains SpdIU's invoke task collections, documented at the [Task Collections Reference](./tasks.md).

Tasks are the user-facing side of SpdIU.
- They print out what steps they're taking and try to have it look nice
- Their docstrings are focused towards the end user on the terminal

Ideally, the actual work is abstracted in a generalized way in the other `spdiu` module, and tasks deal with putting things together into something helpful for the end user.

This way, the tasks can serve as examples and use the same utilities you can use to put together your own.

Collections may include their own internal utilities. Nothing stops you from using them from your own collections. If they are refactored there will be mention of it on the [changelog](../README.md#changelog).


## `spdiu.model`

This submodule contains classes that model the core concepts of the module. Currently these are:


### spdiu.model.Slots

The Slots object provides access to _save slots_ (copies of the game's data) in one or multiple directories.

SpdIU uses it to maintain `backup`, `auto` and `manual` groups of slots in the `slots` directory.

```py
from spdiu.util import path
from spdiu.model import Slots

@task
def show_earliest_save(c):
    """Bring all of my saves in mind."""
    s = Slots(path(cfg.dirs.slots), ['manual', 'auto'])
    # Now each of the states in the folders is a Profile.
    p = Slots.slots[-1]  # they are ordered by mod time already.

    print(f"Your oldest save is the one at {p.root_dir}")
    print(f"Your newest game in it was {p.games[0].ts} seconds since the epoch.")
```

When loaded in the `Slots` object, all save slots are in a flat list as [Profile](#spdiumodelprofile) objects, pre-sorted chronologically by the timestamp of their latest modified _file_.

`Slots.get_slot(str)` seeks and returns a slot by name. Accepts dot syntax for the category, so `slots/auto/floor5` can be requested as `auto.floor5`.


### spdiu.model.Profile

The Profile object represents the _user-level_ layer of the game data: Journal unlocks, rankings, everything that spans multiple games.


### spdiu.model.Game

The Game object represents a running game, with your character in it.


### spdiu.model.DataDir

Parent class of Profile and Game, represents a directory with `.dat` files, which both have.


## `spdiu.util`

Provides a single place to handle paths, filesystem operations on files and folders, and readers and writers for the game's data formats.
