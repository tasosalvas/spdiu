<!-- Copyright (C) 2025 Tasos Alvas <tasos.alvas@qwertyuiopia.com> -->
<!-- SPDX-License-Identifier: AGPL-3.0-or-later                    -->
# SPDIU Usage guide

> Follow the [Installation manual](./installation.md) to get SPDIU. This guide assumes you have a working installation.


SPDIU is meant to live in a terminal you keep open while you play.


```sh
$ cd ~/games/spdiu
```

The tasks load when there's a `tasks.py` in our current or parent directory.
Being in `~/games/spdiu/bin/bar/foo` would also work.


# Interactive help

This guide is intended to be an introduction, and it will be kept accurate, but the complete description of each task and its parameters is meant to be accessed through invoke's help system.

```sh
$ inv info
> ["Basic tips and reminders for common commands."]
# With '-c' it can also list your active SPDIU configuration

$ inv -l
> ["Lists all available tasks with a short help text"]

$ inv -h save
> ["Full description and parameters of the 'save' task"]
```

The code itself also aims to be easy to read so it can act as a reference for how each task is accomplished.

The task help texts are the Python docstrings in [tasks.py](./tasks.py).
Their accepted parameters are the arguments in each task's definition.

Anyway, here we go.


# Saving and Loading

The game automatically saves when taking certain actions, such as changing floors. The easiest way to force a save is to quit to menu. Afterwards you can use the script to back that state up.

```sh
$ inv save
> State saved! 💿 default

# Save slots can have alphanumeric names.
$ inv save -s goo
> State saved! 💿 goo
```

Save slots by default are kept in a `saves` directory next to your active game data in `~/.local/share/.shatteredpixel/`, but can be configured through the `work_dir` setting.

Loading can be done while the game is on the main menu, unless your character just died, in which case you will need to restart SPD for it to look up the loaded game.

```sh
$ inv load
> Active state backup created! 💾 bak
> State loaded! 📀 default

# oops
$ inv load -s bak
> State loaded! 📀 bak
```

Loading preserves the active data it substituted in the special `backup_slot`, in case you fat-fingered it and need to undo.

You can also selectively load a game, while keeping the player profile untouched.

```sh
$ inv load -g game1
> Active state backup created! 💾 bak
> Game loaded! 📀 default 🕹️ game1
```

You can list save slots with `ls`.

```sh
$ inv ls
> Displaying 3 save slots, oldest to newest:
> [...]
```
And you can clean up after you're done.

```sh
$ inv clean
> 🧹 3 saved states deleted.
> Active state backup created! 💾 bak
```


# Displaying game data

```sh
$ inv show -a
> Showing 📀 Active game data
> [...]
```


# Where to go from here

- The [Configuration manual](./configuration.md) covers overriding the default configuration in `invoke.yaml`, for adapting SPDIU to your preferences and having it run different SPD forks
- The [Tasks reference](./tasks.md) documents the available commands
- The [API manual](./api.md) explains how to write your own tasks
