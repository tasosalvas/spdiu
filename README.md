<!-- Copyright (C) 2025 Tasos Alvas <tasos.alvas@qwertyuiopia.com> -->
<!-- SPDX-License-Identifier: AGPL-3.0-or-later -->
# Shattered Pixel Dungeon Invoke Utility

> SPDIU is a collection of [Invoke](https://www.pyinvoke.org/) tasks that manage [Shattered Pixel Dungeon](https://shatteredpixel.com/) game data.

It's a library of tricks to make your SPD CLI experience as comfortable as the rest of your awesome terminal!


## Save slots

Saved states are copies of the game's data folder. They each may contain multiple games.

- `inv save`, `load`, `ls`, `backup` and `clean` tasks create and manage save state slots


## Game data parsing

- `inv show` displays an overview of a save slot, or `-a` the active game data.


# Quick Start

I build and use this on [Debian](https://www.debian.org/). The installation process should be identical for any `.deb` based distribution, and very similar for other package managers.

- **gzip** is used by the collection to unpack data files.
- **git** is the way you get (or maybe even contribute to) _SPDIU_.
- **Invoke** (and by extension Python) needs to be installed on your system. My preferred method is `pipx`.

```sh
$ sudo apt install gzip git pipx
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

Loading can be done while the game is on the main menu, unless your character just died, in which case you will need to restart SPD for it to look up the loaded game.

```sh
$ inv save
> State saved! 💿 default

# Save slots can have alphanumeric names.
$ inv save -s goo
> State saved! 💿 goo
```

Save slots by default are kept in a `saves` directory next to your active game data in `~/.local/share/.shatteredpixel/`, but can be configured through the `work_dir` setting.

Loading preserves the active data it substituted in the special `backup_slot`, in case you fat-fingered it and need to undo.

```sh
$ inv load
> Active state backup created! 💾 bak
> State loaded! 📀 default

# oops
$ inv load -s bak
> State loaded! 📀 bak
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
> [Basic tips and reminders for common commands.]
# With '-c' it can also list your active SPDIU configuration

$ inv -l
> [Lists all available tasks with a short help text.]

$ inv -h save
> [Full description and parameters of the 'save' task.]
```

The task help texts are the Python docstrings in [tasks.py](./tasks.py).
Their accepted parameters are the arguments in each task's definition.

While all of the utility's function is exposed through the interactive help system, it also aims to be easy to read so it can act as a reference for how each task is accomplished.

At least that's how I use it. Have a peek, maybe.


# Configuration

SPDIU uses [invoke's config system](https://docs.pyinvoke.org/en/stable/concepts/configuration.html) to allow the user to override the defaults it ships with. Specifically:

- The _Collection configuration_, defined near the top of `tasks.py`, contains the default values
- A project-level `invoke.yaml` may contain user overrides

All other config levels invoke supports may be used, this is just a recommended setup for this application.

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
├── bin          # SPD binary
├── lib          # SPD lib folder
├── invoke.yaml  # local user config
├── .git
├── .gitignore
├── invoke.yaml.example
├── LICENSE
├── README.md
└── tasks.py
```

If you wish to keep the script in different location, be sure to configure the `game_dir` and `game_cmd` variables in `invoke.yaml`.

Different flavors of SPD distribute the game in their own ways, so in those cases configuration will be required anyway.


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

**Windows when?** Uh, send patches? Python/Invoke shouldn't be hard to get to work and document. The basic linux commands used in tasks would need to be handled somehow, and I'm not sure I'd want it if it's not pretty. I certainly won't have a machine to test it.


# Changelog

The project uses [Semantic Versioning](https://semver.org/spec/v2.0.0.html) and roughly tries to abide with [Keep a Changelog 1.1.0](https://keepachangelog.com/en/1.1.0/).


## [Unrelased]


### Planned before the first release

- [x] Initial project structure and doc
- [x] Config hierarchy, allowing user configuration
- [ ] Allowing user-defined tasks without messing with the core `tasks.py`
- [x] Saving and loading
- [ ] Selectively loading games while leaving profile stats untouched
- [ ] Walking save dirs to find the true last modification time
- [x] Parsing profiles (journal etc) in slots and providing summaries
- [ ] Parsing saved games in slots and providing summaries
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
- [ ] OOP refactoring of saves and slots, encapsulating all game-specific code
- [ ] Extra Flavor management
    - [ ] Presets for installing common SPD forks
- [ ] linting (maybe black?)
- [ ] unit tests  while things are small
- [ ] Save editing


### Far future ideas

Maybe if there's collaboration and I don't run out of steam.

- [ ] Cloning the SPD code to get the complete mob and item lists for journal
- [ ] Adapting the process for SPD forks
- [ ] Templating a starter codebase for a fork from SPD source, documenting best practices


### Added

- `save`, `load`, `ls`, `backup` and `clean` tasks create and manage save state slots
- `show` task reads saves or active game data and displays details on their contents
- `info` task provides introductory documentation, `-c` displays config
