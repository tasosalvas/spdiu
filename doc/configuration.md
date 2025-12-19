<!-- Copyright (C) 2025 Tasos Alvas <tasos.alvas@qwertyuiopia.com> -->
<!-- SPDX-License-Identifier: AGPL-3.0-or-later                    -->
# SPDIU Configuration Manual

`inv info -c` displays all configuration variables as seen by the tasks.

The provided [invoke.yaml.example](./invoke.yaml.example) documents all available utility-specific configuration options, and will update together with the app.

You may copy it to `invoke.yaml` and edit it, or just set the values you want:
```yaml
spdiu:
  default_slot: 'mysave'
```

If your configuration overrides declare the `spdiu:` mapping, it's important for it to contain at least one value for merging to work correctly.


# Recommended directory structure

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


# The `invoke.yaml`

SPDIU uses [invoke's config system](https://docs.pyinvoke.org/en/stable/concepts/configuration.html) to allow the user to override the defaults it ships with. Specifically:

- The _Collection configuration_, defined near the top of `tasks.py`, contains the default values
- A project-level `invoke.yaml` may contain user overrides

All other config levels Invoke supports may be used, this is just a recommended setup for this project.


# What's next

- The [Tasks reference](./tasks.md) documents the available commands
- The [API manual](./api.md) explains how to write your own tasks
