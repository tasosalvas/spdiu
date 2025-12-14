<!-- Copyright (C) 2025 Tasos Alvas <tasos.alvas@qwertyuiopia.com> -->
<!-- SPDX-License-Identifier: AGPL-3.0-or-later -->
# Shattered Pixel Dungeon Invoke Utility

> SPDIU is a collection of [Invoke](https://www.pyinvoke.org/) tasks that manage [Shattered Pixel Dungeon](https://shatteredpixel.com/) game data.

It's a library of tricks to make your SPD CLI experience as comfortable as the rest of your awesome terminal!

- Run common tasks out of the box from your console
- Hook up your own Python tasks, leveraging the `spdiu` library


## Quick and easy: Tasks


### Save and Load the game

SPDIU keeps a directory of save slots, containing copies of the game's full data folder.

- `inv save` and `load` are all the commands you need to save-scum your way to 9-challenge
- Safety backups give you a chance to un-wreck your save if you fat-finger it
- `inv ls` will list your slots, and `clean` will wipe them all


### Display Profile and Game data

`inv show` displays an overview of a save slot (or with `-a`, the active game data).


### Cheat like it's 1989

There isn't some big library of cheats (yet), but the `ch` namespace is where they live:

- `inv ch.bones` can bless your next run with an item up to +3 in your pile of bones. More to come!


## A bit deeper: Write your own

Just place a `local_tasks.py` in your SPDIO folder, and they will be loaded as invoke commands in the `u` namespace.

`spdiu.model` contains Python classes that represent game objects, allowing you to query and edit any part of a savegame in an object-oriented context.

- The `Item` class can initialize valid item dicts to allow you to craft your own
- The `Profile` and `Game` classes can manage all data in a game state

The `spdiu.util` module provides common utilities for working with the game's data folders and files, including reading and writing the `.dat` files containing the game's state. The classes use them and so can you.


# Quick Start

I build and use this on [Debian](https://www.debian.org/). The installation process should be identical for any `.deb` based distribution, and very similar for other package managers.

- **git** is the way you get (or maybe even contribute to) _SPDIU_.
- **Invoke** (and by extension Python) needs to be installed on your system. My preferred method is `pipx`.

```sh
$ sudo apt install git pipx
$ pipx install invoke
```

Then clone the `spdiu` project into the directory you are going to run it from.
The directory must be either non-existent or empty for the initial clone, but afterwards you can place your SPD installation in there.

```sh
# this will clone the main branch
$ git clone https://github.com/tasosalvas/spdiu.git ~/games/spdiu
```

And that's it. Assuming the `inv` command has been installed and your SPD saves are in the default location, you can try things out.


# Usage

SPDIU is primarily meant to live in a terminal you keep open while you play.


```sh
$ cd ~/games/spdiu
```

The tasks load when there's a tasks.py in our current or parent directory.
Being in `~/games/spdiu/bin/bar/foo` would also work.


```sh
$ inv show -a
> Showing 📀 Active game data
> [...]
```

## Saving and Loading

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


## Interactive help

This documentation is intended to be an overview and will be kept accurate, but the complete description of each task and its parameters is meant to be accessed through invoke's help system.

```sh
$ inv info
> ["Basic tips and reminders for common commands."]
# With '-c' it can also list your active SPDIU configuration

$ inv -l
> ["Lists all available tasks with a short help text"]

$ inv -h save
> ["Full description and parameters of the 'save' task"]
```

The task help texts are the Python docstrings in [tasks.py](./tasks.py).
Their accepted parameters are the arguments in each task's definition.

While all of the utility's function is exposed through the interactive help system, it also aims to be easy to read so it can act as a reference for how each task is accomplished.

At least that's how I use it. Have a peek, maybe.


# Configuration

SPDIU uses [invoke's config system](https://docs.pyinvoke.org/en/stable/concepts/configuration.html) to allow the user to override the defaults it ships with. Specifically:

- The _Collection configuration_, defined near the top of `tasks.py`, contains the default values
- A project-level `invoke.yaml` may contain user overrides

All other config levels Invoke supports may be used, this is just a recommended setup for this project.

`inv info -c` displays all configuration variables as seen by the tasks.

The provided [invoke.yaml.example](./invoke.yaml.example) documents all available utility-specific configuration options, and will update together with the app.

You may copy it to `invoke.yaml` and edit it, or just set the values you want:
```yaml
spdiu:
  default_slot: 'mysave'
```

If your configuration overrides declare the `spdiu:` mapping, it's important for it to contain at least one value for merging to work correctly.


## Recommended directory structure

> The collection doesn't currently act on the game installation, but since installing, updating and watching logs are possible future features, it does have configuration variables that track the location of the game.
>
> It doesn't matter if they're set correctly at the moment.

The default configuration assumes the following directory structure:

```sh
spd/
├── bin             # SPD binary
├── lib             # SPD lib folder
├── invoke.yaml     # local user config
├── invoke.yaml.example
├── local_tasks.py  # local user tasks
├── local_tasks.py.example
├── .git
├── .gitignore
├── LICENSE
├── README.md
└── tasks.py
```

The project's `git` configuration only includes its own files explicitly, so it will not touch any other files you put in there.

If you wish to keep the script in different location, be sure to configure the `game_dir` and `game_cmd` variables in `invoke.yaml`.

Different flavors of SPD distribute the game in their own ways, so in those cases configuration will be required anyway.


# Defining your own tasks

The utility of some of the functionality of SPDIU, such as unpacking save data, is not the couple of lines it prints by default, but the fact that it makes the contents of a save available as Python objects.

Some obligatory links:
- The [Invoke documentation](https://docs.pyinvoke.org/en/stable/getting-started.html), for usage not covered in SPDIU's documentation and examples
- The [Python documentation](https://docs.python.org), the main and most important reference while we're working with it

[local_tasks.py.example](./local_tasks.py.example) contains an annotated demo, which experienced users might find enough to get started. [tasks.py](./tasks.py) itself is meant to be easy to read and borrow things from.

> A refactoring exposing a stable API for dealing with game files is planned.
>
> Currently you can call existing tasks and utility functions from your own tasks, or borrow code from them to get you started.
>
> After version `1.0.0`, potentially breaking changes will only happen on major releases (i.e. `2.0.0`) and will be listed on the changelog.


## Namespaces

SPDIU needs `tasks.py` as an entry point and updates are going to overwrite it with a newer version, so a `local_tasks.py` meant for your own tasks will be imported if found.

Minimal example of `local_tasks.py`:
```py
#!/usr/bin/env python
from invoke import task

@task
def explosion(c):
    """
    A nice docstring is easy to show off in Invoke.

    These later lines will only appear with 'inv -h u.explosion'
    """
    # 'c' is the Context. It's passed to tasks on execution.

    # It contains the config,
    cfg = c.config.spdiu

    # and provides api calls, such as running terminal commands.
    # Ideally we want to do stuff in python, to be compatible wherever it runs.
    # i.e. this would probably only work on linux. But it's your task.
    c.run(f"du -h {cfg.work_dir}")

    print(f"Your {cfg.work_dir} just went BOOM!")
```

The above file will be automatically turned into a task collection and imported with a default namespace of `u` (for "user"), so our task will be included and can be ran with `inv u.explosion`.

If a `collection_name` variable is set in `local_tasks`, `tasks.py` will call it by than name instead. Note that future SPDIU collections might use obvious short names too, so if you can live with the default it might be more convenient to keep it.


### Explicit namespaces

Finally, if a collection is _explicitly_ declared and `tasks.py` detects an `ns` variable in your module, it is imported as it is, ignoring the `collection_name` variable above and using the one declared in it instead.

```py
from invoke import task, Collection

# Create a new collection named 'my'
ns = Collection('my')

@task
def greeting(c):
    """ It's only an example but we don't like skipping docstrings. """
    print('Well, hello.')

# an explicit collection needs its tasks added to it
ns.add_task(greeting)
```

You might want to use this option if you're importing more collections from your local tasks, as it will allow you to structure them just the way you want them. The Invoke [namespace](https://docs.pyinvoke.org/en/stable/concepts/namespaces.html) documentation can help you take full advantage of this.


# Philosophy and Goals

I love Pixel Dungeon and SPD as free software cultural staples now spanning decades. I think they're worth nerding out on, and the abundance of forks sharing the same core makes these recipes applicable to many of them with very little effort.

- Features that **can apply to most forks** are preferred to digging into a single flavor's specifics

Currently the project is _developed_ for my own use, more during playtime than work time. I might have fun getting into save editing or refactoring and structuring just to make things pretty. Or I might be playing something else. I'll be around, though

- I can make **no promises of frequent updates**, but I hope to develop and maintain this code in a way that allows the user to adapt to future changes in the games through configuration

SPDIU is _published_ more with the intention to be educational than to achieve any specific function. Following that:

- **Form** matters. For this project it's more important to do it properly than to get the thing to work at all. This includes complying with FOSS standards and following best practices for any tools involved
- **Readability** is a primary goal. This includes having a structure that can be easily reasoned about, but also allows a user peeking into the source to quickly audit the part they're interested in without digging into layers of architecture
- **Documentation** aims to be welcoming and be comprehensive on _intention_, _utility_ and _structure_, but to ultimately guide the user to the interactive help system for specifics, and to the (purposefully readable) code for implementation details

I consider messing around with the game a great entryway to the nuances of the relationship a user can have with free software, and SPD a shining example of remix culture. Let's have fun in the terminal.

I'm not saying that any of this is perfect, and I'll be happy to consider and curate improvements that align with these specific goals.


## On Tools

**Why Python?** Because it's very expressive and readable and we're not building rocket kernels.

**Why Invoke?** Because it's fun to do it in Python, and I already use it and [Fabric](https://www.fabfile.org/) for work stuff. It makes it easy to add and chain little local tasks and keep them structured as they pile up. Self-documenting automation. It does have internals we sometimes need to know about, but it's generally good at getting out of the way and letting task logic be business logic.

**Why no UI?** Because obviously **IU** is the opposite of UI, duh.

**Windows when?** Uh, send patches? Python/Invoke shouldn't be hard to get to work and document. There's also a chance the way windows file access works will make the tool clunkier to use. I'll be happy to add instructions, if you figure them out. I certainly won't have a machine to test it.


# Changelog

The project uses [Semantic Versioning](https://semver.org/spec/v2.0.0.html) and roughly tries to abide with [Keep a Changelog 1.1.0](https://keepachangelog.com/en/1.1.0/).


## [Unrelased]

### Planned before the first release

- [x] Initial project structure and doc
- [x] Config hierarchy, allowing user configuration
- [x] Allowing user-defined tasks without messing with the core `tasks.py`
- [x] Saving and loading
- [x] Selectively loading games while leaving profile stats untouched
- [ ] Walking save dirs to find the true last modification time
- [x] Parsing profiles (journal etc) in slots and providing summaries
- [x] Parsing saved games in slots
- [ ] Providing game summaries
- [x] Save editing API
- [ ] OOP refactoring of saves and slots, encapsulating all save-reading code and decoupling it from tasks
  - [x] saves
  - [ ] slots
- [ ] CONTRIBUTING document
- [ ] Readme: Screenshots
- [ ] Readme: Example of editing config to work with forks, i.e. ReARrangedPD


### Cool future ideas

Not planned yet but viable, loosely in the order I'm considering them.

- [ ] Checking for self updates
- [ ] Logo n stuff
- [ ] Game binary management
    - [ ] Getting all releases from the SPD github
    - [ ] Installing a chosen version of SPD in the spdiu folder
    - [ ] Checking for SPD updates
- [ ] Extra Flavor management
    - [ ] Presets for installing common SPD forks
- [ ] linting (maybe black?)
- [ ] unit tests while things are small


### Far future ideas

Maybe if there's collaboration and I don't run out of steam.

- [ ] Cloning the SPD code to get the complete mob and item lists for journal
- [ ] Adapting the process for SPD forks
- [ ] Templating a starter codebase for a fork from SPD source, documenting best practices


### Added

Tasks:
- `save`, `load`, `ls`, `backup` and `clean` tasks create and manage save state slots
- `show` task reads saves or active game data and displays details on their contents
- `info` task provides introductory documentation, `-c` displays config

Python:
- The `spdio.util` module provides helpers for common file operations
- The `spdio.model` module holds class representations of `Profile` and `Game` data.

Customization:
- Configuration overrides can be set in an `invoke.yaml` in the project folder
- Local user tasks can be defined in a `local_tasks.py`.
