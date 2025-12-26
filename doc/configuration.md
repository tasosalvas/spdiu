<!-- Copyright (C) 2025 Tasos Alvas <tasos.alvas@qwertyuiopia.com> -->
<!-- SPDX-License-Identifier: AGPL-3.0-or-later                    -->
# SpdIU Configuration Manual

`siu info -c` displays all configuration variables as seen by the tasks.

The provided [spdiu.yaml.example](./spdiu.yaml.example) documents all available utility-specific configuration options, and will update together with the app.

You may copy it to `spdiu.yaml` and edit it, or just set the values you want:
```yaml
spdiu:
  default_slot: 'mysave'
```

If your configuration overrides declare a mapping, such as `spdiu:` or `dirs:`, it's important for it to contain at least one value for merging to work correctly.


# Installing SPD flavors
Different flavors of SPD distribute the game in different ways, and keep their own play data.

> They also are applications from third party developers that might mess up your computer. We do not review them.
>
> SpdIU's code is available, and so is that of the downloaded projects. Whether you came to trust each game (and using SpdIU to install it) blindly or after carefully auditing the source, the responsibility is yours.

SpdIU's `get.install` aims to be flexible enough to get you any of them, but you might have to sweat for it.


## Automatic release detection
Let's see an example of configuration adapted to [Re-ARranged-Pixel-Dungeon by Hoto-Mocha](https://github.com/Hoto-Mocha/Re-ARranged-Pixel-Dungeon).

First of all, the release information:

```yaml
spdiu:
  release:
    gh_use_api: true
    project: Hoto-Mocha/Re-ARranged-Pixel-Dungeon
    platform: desktop
    extension: jar
```

This is enough for `get.install` to query Github for the game's latest release and retrieve a file fitting the platform and extension.

Note that `dekstop` is just a word _Hoto-Mocha_ uses to describe the platform, and we had to visit the project to know it. _00-Evan_ in SPD would call their `.jar` release `Java`, and has different ones for `Linux`, `Windows`, and `macOS` desktops.

The current system uses the Github API to get the packages available, and only uses the platform and extension as hints to narrow down the files. If it's unambiguous, it downloads it.


## Manual download template

If all else fails, we have the template. A python f-string template to generate the download path.

> I would have loved to use an example that wasn't on Github, as it would have actually needed the template. If you know of a fork on a different provider, I'd be happy implement or accept PRs for helpers for that too.

The template is only used if `release.gh_use_api` is `false`. Let's try to recreate our previous example:

```yaml
spdiu:
  release:
    gh_use_api: false
    project: Hoto-Mocha/Re-ARranged-Pixel-Dungeon
    platform: desktop
    extension: jar
    tag_name: v3.2.0_based_v3.40.0-FINAL
    version: v3.40.0
    template: https://github.com/{project}/releases/download/{tag_name}/{version}-{platform}.{ext}
```
The template gets evaluated as a python f-string, with access to the variables listed above.

You can change the variables or expression to whatever you need to point to, and any fields not on the filename itself are not going to matter once the download is done.

Now we can move on to configuring SpdIU to work on the game.


## Game configuration

The following fields, in the `game` mapping, have to do with properties of the game.

```yaml
spdiu:
  game:
    data: ~/.local/share/.rearrangedpixel/rearranged-pixel-dungeon

    # TODO: either store the jar name of the bin or link it
    cmd: java -jar v3.40.0-desktop.jar

    # The java namespace of the game.
    ns: com.rearrangedpixel.rearrangedpixeldungon
```

`data` is the game data directory. It needs to be an absolute path after user expansion. You point it to the save. It's absolutely required if you want to be able to uh, save.

`cmd` is the command to run the executable from `dirs.game`. In shattered it's always the same no matter the version.

`ns` is the java namespace of the game. It can be found in the game's source (i.e. in `/build.gradle`). It allows data-mining tasks to use it as a hint and hide it so it doesn't spam the log.

> It's not unthinkable to get the values above by automatically analyzing the soure, but that's what we have for now.


# Selecting and pinning versions

By default, on a github-hosted project such as SPD, `siu get.install` will request the latest release and pick the appropriate package.

`siu get install -v [version]` will instead look into the project's releases and find a package from the version you requested. If there is an unambiguous one, it will install it.

The version check is just a substring search on the download URL, as are the `extension`, `platform`, `version` and `tag_name` variables in the `spdiu.release` configuration.

Setting more of them can help narrow down a release to a specific package.

Setting `spdiu.version` on your `spdiu.yaml` will **pin** your preferred version, so that `get.install` does not get the latest one, but the one you specified instead.

You can still manually install a different version by `siu get.install -v [version]`


# Directory structure

The default configuration creates the following directory structure:

```sh
spdiu/
├── slots/          # Saved games
├── game/           # Game binary installation
├── packages/       # Downloaded game packages
├── spdiu.yaml     # Local user configuration
├── local_tasks.py  # Local user tasks
└── tasks.py        # SpdIU entry point
```

This is controlled by the `spdiu.dirs` dictionary / mapping.


```yaml
spdiu:
  dirs:
    # core paths
    base: ~/my-spdio-data  # but why?

    # functionality-specific paths
    slots: my_saves
    # -> they can be multiple dirs deep
    package: tmp/packages
    # -> or they can be absolute
    game: '~/games/spd'
```

The `base` dir is the absolute filename (after user expansion) where the SpdIU instance is installed. It defaults to the detecting the location of the `tasks.py` file.

Any relative path will be appended to the `base` dir, while absolute paths will be used as they are.

- `slots` is where saves made by spdiu are kept. It defaults to `slots` in the base directory.
- `package` is where release packages are downloaded. It defaults to `packages` in the base directory.
- `game` is where the game is installed. It defaults to `game` in the base directory.

Overall, the default configuration ensures a copy of spdiu keeps to its own folder, with the exception of dealing with the game's active data.


# How the `spdiu.yaml` works

SpdIU uses [invoke's config system](https://docs.pyinvoke.org/en/stable/concepts/configuration.html) to allow the user to override the defaults it ships with. Specifically:

- The _Collection configuration_, defined near the top of `tasks.py`, contains the default values
- A project-level `spdiu.yaml` may contain user overrides
- All SpdIU configuration is contained in the `spdiu:` mapping

All other config levels Invoke supports may be used, this is just the setup assumed in this documentation, and used when testing and developing SpdIU.


# What's next

- The [Tasks reference](./tasks.md) documents the available commands
- The [API manual](./api.md) explains how to write your own tasks
