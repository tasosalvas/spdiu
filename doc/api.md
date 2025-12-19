<!-- Copyright (C) 2025 Tasos Alvas <tasos.alvas@qwertyuiopia.com> -->
<!-- SPDX-License-Identifier: AGPL-3.0-or-later                    -->
# The SPDIU API Manual

Just place a `local_tasks.py` in your SPDIO folder, and they will be loaded as invoke commands in the `u` namespace.

`spdiu.model` contains Python classes that represent game objects, allowing you to query and edit any part of a savegame in an object-oriented context.

- The `Item` class can initialize valid item dicts to allow you to craft your own
- The `Profile` and `Game` classes can manage all data in a game state
- `Slots` manager helps keep track of saved states

The `spdiu.util` module provides common utilities for working with the game's data folders and files, including reading and writing the `.dat` files containing the game's state. The classes use them and so can you.


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


## Implicit namespaces

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


## Explicit namespaces

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
