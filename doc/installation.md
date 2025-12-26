<!-- Copyright (C) 2025 Tasos Alvas <tasos.alvas@qwertyuiopia.com> -->
<!-- SPDX-License-Identifier: AGPL-3.0-or-later                    -->
# SpdIU Installation Manual

## Requirements

A nice, comfortable **terminal** and **font**. Ideally something that can show _ligatures_ and _emojis_.

> SpdIU is developed and enjoyed on [kitty](https://sw.kovidgoyal.net/kitty/), `zsh`, with [FiraCode](https://github.com/tonsky/FiraCode).

[Python](https://www.python.org/) needs to be installed on your system, preferrably with a tool that lets you install command line tools, such as `uv` or `pipx`.

> SpdIU tries to keep external requirements to a minimum.
> - Python is preferred to calling Linux commands, in hope of keeping things portable
> - Invoke is the only non-standard dependency, handling the shell and configuration
>
> Cross-platform compatibilty is yet untested, but the goal is to only need working Python and a terminal.


# Installing

## on Linux

SpdIU is developed and tested on [Debian](https://www.debian.org/). The installation process should be identical for any `.deb` based distribution, and very similar for other package managers.

First, **install `pipx`**. The `pipx` package should pull enough python
```sh
$ sudo apt install pipx

# Recommended, configuration not included (yet)
$ sudo apt install kitty fonts-firacode
```

Now you can **install the `s[pd]iu` command** through `pipx`.
```sh
$ pipx install spdiu
```

Assuming your `~/.local/bin/` (where `pipx` places its installed binaries) is in `$PATH`, the `spdiu` and shortened `siu` commands should be available to you:

```sh
$ siu --version
```

or, if you have `uv`, you can use it without explicitly installing:
```sh
$ uvx run spdiu --version
```
You'll want to install it for the completions, though.


## Completions configuration

Adding this line to your `~/.bashrc` will enable shell autocompletions for SpdIU.
```sh
if [ -x "$(command -v siu)" ]; then
    eval "$(siu --print-completion-script bash)"
fi
```

They can be really helpful, as all our tasks are arguments to the `s[pd]iu` command.

`zsh` and `fish` are also supported, just replace `bash` in the line above and adapt it to your respective shell init file.



## Setting up a game folder

Then **initialize an SpdIU directory**. For example:
```sh
$ cd ~/games
$ siu --install shattered
> Generated /home/[user]/games/shattered/tasks.py
```

The shattered folder now contains a `tasks.py` and an (empty) `spdiu.yaml`. We'll call that an **initialized** SpdIU folder.

- `tasks.py` is the entry point for the SpdIU task collections. By default, it imports `spdiu` and configures its `base_path` to the directory. It is also your entry point to adding your own tasks and collections.
- `spdiu.yaml` can be used to override SpdIU's default settings for the current instance, ranging from changing icons to downloading and managing a different Pixel Dungeon game.

Repeat this in a different folder when you want to install another SPD fork.

Assuming the `siu` command has been installed, calling it from the folder containing `tasks.py` should get you the SpdIU tasks.

```sh
$ cd shattered
$ siu info
[
| Shattered Pixel Dungeon Invoke Utility.
|  [...]
| 'siu -l' for a list of tasks.
| 'siu -h [task name]' for a task's full docstring.
| 'siu info -c' to display active SpdIU configuration.
]
```

# Further reading

- The [Usage Guide](./usage.md) covers SpdIU's basic usage and some recipes to interact with the game data
- The [Configuration manual](./configuration.md) covers overriding the default configuration in `spdiu.yaml`, for adapting SpdIU to your preferences and having it run different SPD forks
- The [Tasks reference](./tasks.md) documents the available commands
