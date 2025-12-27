#!/usr/bin/env python
# Copyright (C) 2025 Tasos Alvas <tasos.alvas@qwertyuiopia.com>
# SPDX-License-Identifier: AGPL-3.0-or-later
"""siu: SpdIU's Invoke Program."""

from pathlib import Path

from invoke import Program, Argument, Collection
from invoke.util import debug, helpline
from invoke.exceptions import Exit, CollectionNotFound


class SpdIU(Program):
    """SpdIU Invoke wrapper. Aims at theming the output without breaking anything."""

    def core_args(self):
        """Add SpdIU's extra flags to core args."""
        core_args = super().core_args()

        update_args = [
            Argument(
                names=("list-format", "F"),
                help="Change the task list format. spdiu (default) | flat | nested | json",
                default="spdiu",
            ),
        ]

        extra_args = [
            Argument(
                names=("install", "i"),
                kind=str,
                default="",
                optional=True,
                help="Initialize a folder as a SpdIU instance.",
            ),
        ]

        up_names = [i.name for i in update_args]
        core_args = [i for i in core_args if i.name not in up_names]

        return core_args + update_args + extra_args

    def parse_core(self, argv) -> None:
        """Add SpdIU's base path installation to core args."""
        super().parse_core(argv)

        if self.args.install.value:
            debug("Saw --install, generating SpdIU tasks.py")
            i_value = self.args.install.value

            p = Path(i_value).resolve() if type(i_value) is str else Path.cwd()
            self.generate_tasks_py(p)
            self.generate_spdio_yaml(p)
            raise Exit

    def load_collection(self) -> None:
        """Load a task collection based on parsed core args, or die nagging.

        Overloaded to expand the "can't find collection" text.
        """
        start = self.args["search-root"].value
        loader = self.loader_class(  # type: ignore
            config=self.config, start=start
        )
        coll_name = self.args.collection.value

        try:
            module, parent = loader.load(coll_name)
            self.config.set_project_location(parent)
            self.config.load_project()
            self.collection = Collection.from_module(
                module,
                loaded_from=parent,
                auto_dash_names=self.config.tasks.auto_dash_names,
            )
        except CollectionNotFound as e:
            if e.name == "tasks":
                self.print_tasks_py_help()

            raise Exit("Can't find any collection named {!r}!".format(e.name))

    # Task list display
    def _make_spdiu_pairs(self, coll: "Collection", ancestors=None) -> list:
        """Recurse into collection tasks and return names and help strings.

        Returns [("task", (optional) "help"), ] for printing task lists.
        """
        if ancestors is None:
            ancestors = []
        pairs = []
        indent = len(ancestors) * self.indent

        # ancestor_path = ".".join(x for x in ancestors)

        for name, task in sorted(coll.tasks.items()):
            is_default = name == coll.default
            # Start with just the name and just the aliases, no prefixes or
            # dots.
            displayname = name

            aliases = list(map(coll.transform, sorted(task.aliases)))

            # If displaying a sub-collection (or if we are displaying a given
            # namespace/root), tack on some dots to make it clear these names
            # require dotted paths to invoke.
            if ancestors or self.list_root:
                displayname = ".{}".format(displayname)
                aliases = [".{}".format(x) for x in aliases]

            # NOTE: blank emoji: both _space and _cancel fix alignment in kitty.
            # I think probably any 0-width character would, and that it works
            # because it takes up no space but gets counted as a second character.
            i_b = self.config.spdiu.i["_space"]

            # mark the default task in the collection.
            i_t = self.config.spdiu.i["task"]
            prefix = indent + f"{i_t}{i_b} "

            i_d = self.config.spdiu.i["default"]
            if is_default:
                displayname += f" {i_d}{i_b}"

            # Generate full name and help columns and add to pairs.
            alias_str = f" ({', '.join(aliases)})" if aliases else ""

            full = prefix + displayname + alias_str
            pairs.append((full, helpline(task)))

        # Determine whether we're at max-depth or not
        truncate = self.list_depth and (len(ancestors) + 1) >= self.list_depth

        for name, subcoll in sorted(coll.collections.items()):
            displayname = name

            if ancestors or self.list_root:
                displayname = ".{}".format(displayname)

            if truncate:
                tallies = [
                    "{} {}".format(len(getattr(subcoll, attr)), attr)
                    for attr in ("tasks", "collections")
                    if getattr(subcoll, attr)
                ]

                displayname += " [{}]".format(", ".join(tallies))

            # silly blank line hack
            pairs.append(("", ""))

            i_c = self.config.spdiu.i["collection"]
            prefix = indent + f"{i_c}{i_b}{i_b} "
            pairs.append((prefix + displayname, helpline(subcoll)))

            # Recurse, if not already at max depth
            if not truncate:
                recursed_pairs = self._make_spdiu_pairs(
                    coll=subcoll, ancestors=ancestors + [name]
                )
                pairs.extend(recursed_pairs)
        return pairs

    def task_list_opener(self, extra: str = "") -> str:
        """Generate the intro text to task list help."""
        root = self.list_root
        depth = self.list_depth

        i_c = self.config.spdiu.i["collection"]
        specifier = " {} {}".format(i_c, root) if root else ""

        tail = ""
        if depth or extra:
            depthstr = "depth={}".format(depth) if depth else ""
            joiner = "; " if (depth and extra) else ""
            tail = " ({}{}{})".format(depthstr, joiner, extra)

        i_t = self.config.spdiu.i["task"]
        text = "Available{} {} tasks{}".format(specifier, i_t, tail)
        return text

    def list_spdiu(self) -> None:
        """Format a task list, SpdIU style. Alternative to _nested and _flat.

        -F, --list-format STRING in the terminal defaults to this in SpdIU.
        """
        # These are used by flat/nested too, overloading them only here.
        self.leading_indent_width = 1
        self.leading_indent = " " * self.leading_indent_width
        self.indent_width = 1
        self.indent = " " * self.indent_width
        self.col_padding = 2

        pairs = self._make_spdiu_pairs(self.scoped_collection)

        i_d = self.config.spdiu.i["default"]
        extra = f"{i_d}: default"

        self.display_with_columns(pairs=pairs, extra=extra)

    # Help system
    def print_help(self) -> None:
        """Print s[pd]iu's usage and documentation.

        The generic response to -h, --help.
        """
        usage_suffix = "task1 [--task1-opts] ... taskN [--taskN-opts]"

        if self.namespace is not None:
            usage_suffix = "<subcommand> [--subcommand-opts] ..."

        print("Usage: {} [--core-opts] {}".format(self.binary, usage_suffix))
        print("")
        print("Core options:")
        print("")

        self.print_columns(self.initial_context.help_tuples())

        if self.namespace is not None:
            self.list_tasks()

        self.print_version()

    def print_task_help(self, name: str) -> None:
        """Print help for a specific task."""
        return super().print_task_help(name)

    def print_version(self) -> None:
        """Print the version of SpdIU and the underlying Invoke."""
        print(f"SpdIU {self.version} running on Invoke {self.invoke_version}")

    # Folder instance initialization
    def print_tasks_py_help(self) -> None:
        """Print help for configuring a base dir as an SpdIU instance."""
        print("Seems like you are not in an initialized SpdIU folder.", "\n")
        print("siu --install will initialize the current one,")
        print("siu --install [target] will initialize the one provided.", "\n")
        # TODO: tasks.py explanation, doc link

    def generate_tasks_py(self, path: Path) -> None:
        """Generate a tasks.py from spdiu/templates/tasks.py."""
        path.mkdir(parents=True, exist_ok=True)

        src = Path(__file__).parent / "templates" / "tasks.py"
        file_path = path / "tasks.py"

        file_path.write_text(src.read_text())
        print(f"Generated {file_path}")

    def generate_spdio_yaml(self, path: Path) -> None:
        """Generate a tasks.py from spdiu/templates/tasks.py."""
        path.mkdir(parents=True, exist_ok=True)
        # src = Path(__file__).parent / "templates" / "spdiu.yaml"

        file_path = path / "spdiu.yaml"
        file_path.touch()

        print(f"Generated {file_path}")

    def __init__(self, *args, invoke_version: str = "", **kwargs):
        """Add SpdIU variables."""
        super().__init__(*args, **kwargs)
        self.invoke_version = invoke_version if invoke_version else "unknown"
