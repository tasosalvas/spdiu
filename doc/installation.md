<!-- Copyright (C) 2025 Tasos Alvas <tasos.alvas@qwertyuiopia.com> -->
<!-- SPDX-License-Identifier: AGPL-3.0-or-later                    -->
# SPDIU Installation Manual

The intended way to install SPDIU is to keep an instance of it for every flavor of SPD you want it to manage.

For example:
```sh
games/spdiu-rearranged/
├── game/            # The installed SPD
├── spdiu/           # The spdiu python module
├── invoke.yaml      # local user config
├── local_tasks.py   # local user tasks
└── tasks.py
```


## Requirements

A nice, comfortable **terminal** and **font**. Ideally something that can show _ligatures_ and _emojis_.

> SPDIU is developed and enjoyed on [kitty](https://sw.kovidgoyal.net/kitty/), `zsh`, with [FiraCode](https://github.com/tonsky/FiraCode).


[git](https://git-scm.com/) is the easiest way to get _SPDIU_. Maybe even contribute to it.

> I will be releasing `.zip` packages on minor versions, but we're in the terminal anyway.
>
> `git` is fun and a nice skill to pick up. SPDIU is just a bunch of scripts that work off a single directory.


[Python](https://www.python.org/) and [Invoke](https://pyinvoke.org) need to be installed on your system.

> SPDIU tries to keep external requirements to a minimum.
> - Python is preferred to calling Linux commands, in hope of keeping things portable
> - Invoke is the only non-standard dependency, handling the shell and configuration
>
> Cross-platform compatibilty is yet untested, but the goal is to only need working Python and a terminal.


# Installing

## on Linux

SPDIU is developed and tested on [Debian](https://www.debian.org/). The installation process should be identical for any `.deb` based distribution, and very similar for other package managers.

First, **install `git` and `pipx`**. The `pipx` package should pull enough python
```sh
$ sudo apt install git pipx

# Recommended, configuration not included
$ sudo apt install kitty fonts-firacode
```

Now we can **install the `inv` command** through `pipx`.
```sh
$ pipx install invoke
```

Then **clone the `spdiu` project** from _your games directory_.

```sh
$ cd ~/games

# this will create a folder called "~/games/shattered"
$ git clone git@github.com:tasosalvas/spdiu.git shattered
```

Repeat this in a different folder when you want to install another SPD fork.

Assuming the `inv` command has been installed, calling it from the folder containing `tasks.py` should get you the SPDIU tasks.

```sh
$ cd spdiu
$ inv info
[
| Shattered Pixel Dungeon Invoke Utility.
|  [...]
| 'inv -l' for a list of tasks.
| 'inv -h [task name]' for a task's full docstring.
| 'inv info -c' to display active SPDIU configuration.
]
```

## Completions configuration

Adding this line to your `~/.bashrc` will enable shell autocompletions for invoke.
```sh
if [ -x "$(command -v inv)" ]; then
    eval "$(inv --print-completion-script bash)"
fi
```

They can be really helpful, as all our tasks are arguments to the `inv` command.

`zsh` and `fish` are also supported, just replace `bash` in the line above and adapt it to your respective shell init file.


# Further reading

- The [Usage Guide](./usage.md) covers SPDIU's basic usage and some recipes to interact with the game data
- The [Configuration manual](./configuration.md) covers overriding the default configuration in `invoke.yaml`, for adapting SPDIU to your preferences and having it run different SPD forks
- The [Tasks reference](./tasks.md) documents the available commands
