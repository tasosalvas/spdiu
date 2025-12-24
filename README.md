<!-- Copyright (C) 2025 Tasos Alvas <tasos.alvas@qwertyuiopia.com> -->
<!-- SPDX-License-Identifier: AGPL-3.0-or-later                    -->
# Shattered Pixel Dungeon Invoke Utility

[![License: AGPL v3](https://img.shields.io/badge/License-AGPL_v3-blue.svg)](./LICENSE)
[![pytest](https://github.com/tasosalvas/spdiu/actions/workflows/main.yml/badge.svg?event=push)](https://github.com/tasosalvas/spdiu/actions/workflows/main.yml)

> SPDIU is a collection of [Invoke](https://www.pyinvoke.org/) tasks that manage [Shattered Pixel Dungeon](https://shatteredpixel.com/) game data.

It's a library of tricks to make your SPD CLI experience as comfortable as the rest of your awesome terminal!

- Run common tasks out of the box from your console
- Hook up your own Python tasks, leveraging the `spdiu` library


# Documentation

- [Installation](./doc/installation.md)
- [Configuration](./doc/configuration.md)
- [Usage guide](./doc/usage.md)
- [Task Collections reference](./doc/tasks.md)
- [API manual](./doc/api.md)
- [About SPDIU](./doc/about.md)


# What does it do?

## Save and Load the game

SPDIU keeps a directory of save slots, containing copies of the game's full data folder.

- `inv save` and `load` are all the commands you need to save-scum your way to 9-challenge
- Safety backups give you a chance to un-wreck your save if you fat-finger it


## Display Profile and Game data

Get overviews of every single thing stored in your save data.


## Cheat like it's 1989

Βless your next run with one out of a selection of care packages, or downright edit in that upgraded armor you wanted.

It's your game, after all!


## Check for updates or download older versions

On github releases, just pick your version.

Create an issue if you know of an SPD fork hosted elsewhere, and we'll try to enable that platform, too!


## Install flavors and remixes

With just a bit of configuration, you can use SPDIU to download any of the SPD forks available in the wild!


# Changelog

The project uses [Semantic Versioning](https://semver.org/spec/v2.0.0.html) and roughly tries to abide with [Keep a Changelog 1.1.0](https://keepachangelog.com/en/1.1.0/).


## [Unrelased]

### Planned before the first release

`main` is usable, no need to wait, that's just for when I announce.

- [ ] Migrate to pathlib, omg
- [ ] data object summaries
  - [x] Basic data mining with `recurse_dump()`
  - [ ] Some tidy setup for summary templating
  - [x] Parsing profiles (journal etc) in slots and providing summaries
  - [x] Parsing saved games in slots
  - [ ] Providing game summaries
- [ ] Expand doc
  - [x] Installation
  - [x] Configuration
  - [ ] Usage guide
    - [x] Interactive help
    - [x] Saves, backups
    - [ ] the autosave watcher
    - [x] Displaying game data
    - [ ] Cheats and save editing
  - [x] Task Collections
  - [x] API
    - [ ] The SPDIU object model cont
  - [ ] About
    - [ ] Standards and specifications
  - [ ] CONTRIBUTING document
- [x] Pytest configured
- [ ] base spdiu tests
  - [ ] util
  - [ ] model
- [ ] collection tests
- [ ] tasks.py/configuration tests
- [ ] Readme: Screenshots
- [ ] Logo n stuff


### Ideas for 2.0.0

- [ ] Checking for self updates? nah?
- [ ] Do stuff with SPD code
  - [ ] Cloning the SPD code to get the complete mob and item lists for journal
  - [ ] Adapting the process for digging into SPD forks
  - [ ] Templating a starter codebase for a fork from SPD source, documenting best practices
- [ ] Automatic SPDIU presets for remix installations, uh like a mod manager?
- [ ] Controlling the game?
- [ ] Memory stuff?
- [ ] releasing in pypi
- [ ] installing as a custom command
- [ ] fancier output?
- [ ] Sphinx for modules? Can we do it in markdown?


### Added

Python:
- The `spdiu.util` module provides helpers for common file operations
- The `spdiu.model` module holds class representations of `Slots` containing `Profile` and `Game` data.


Customization:
- Configuration overrides can be set in an `invoke.yaml` in the project folder
- Local user tasks can be defined in a `local_tasks.py`.
