#!/usr/bin/env python
# Copyright (C) 2025 Tasos Alvas <tasos.alvas@qwertyuiopia.com>
# SPDX-License-Identifier: AGPL-3.0-or-later
"""siu: SpdIU's Invoke Program."""

from pathlib import Path

from invoke import Program, Argument, Collection, terminals
from invoke.util import debug, helpline
from invoke.exceptions import Exit, CollectionNotFound

from spdiu.util import color


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
    def _make_spdiu_items(self, coll: "Collection", ancestors=None) -> list:
        """Recurse into collection tasks and return names and help strings.

        Returns [("task", (optional) "help"), ] for printing task lists.
        """
        if ancestors is None:
            ancestors = []

        items = []
        task_items = []
        collection_items = []

        dot = color(self.config, ".", "separator")

        icon_default = self.config.spdiu.i.default
        icon_task = self.config.spdiu.i.task
        icon_collection = self.config.spdiu.i.collection

        for name, task in sorted(coll.tasks.items()):
            item = {
                "op": "task",
                "name": name.strip(),
                "ancestors": ancestors,
                "help": helpline(task).strip(),
                "first": False,
                "last": False,
            }

            aliases = list(map(coll.transform, sorted(task.aliases)))
            subcollection = bool(ancestors or self.list_root)

            str_title = color(self.config, name, "task")
            len_title = len(name)

            if subcollection:
                str_title = dot + str_title
                len_title += 1

            str_title = f"{icon_task} {str_title}"
            len_title += 3

            if name == coll.default:
                str_title += f" {icon_default}"
                len_title += 3

            len_alias = 0
            if aliases:
                len_alias += sum([len(i) for i in aliases])
                aliases = [color(self.config, i, "alias") for i in aliases]

            if aliases and subcollection:
                aliases = [dot + i for i in aliases]
                len_alias += len(item["aliases"])

            str_alias = f" ({', '.join(aliases)})" if aliases else ""
            len_alias += 3 if aliases else 0
            len_alias += (len(aliases) - 1) * 2 if len(aliases) > 1 else 0

            item["str_title"] = str_title
            item["len_title"] = len_title
            item["str_aliases"] = str_alias
            item["len_aliases"] = len_alias

            item["len_long"] = len_title + len_alias
            item["len_short"] = max(len_title, len_alias)

            task_items.append(item)
            items.append(item)

        # Determine whether we're at max-depth or not
        truncate = self.list_depth and (len(ancestors) + 1) >= self.list_depth

        for name, subcoll in sorted(coll.collections.items()):
            item = {
                "op": "collection",
                "name": name.strip(),
                "ancestors": ancestors,
                "subcollections": len(subcoll.collections),
                "help": helpline(subcoll).strip(),
                "first": False,
                "last": False,
            }

            str_title = color(self.config, item["name"], "collection")
            len_title = len(item["name"])

            str_title = f"{str_title} {icon_collection}"
            len_title += 3

            len_ancestors = 0
            if ancestors:
                len_ancestors += sum([len(i) for i in item["ancestors"]])
                ancestors = [color(self.config, i, "ancestor") for i in ancestors]

            str_ancestors = dot.join(ancestors) + " " if ancestors else ""
            len_ancestors += 1 if ancestors else 0
            len_ancestors += len(ancestors) - 1 if len(ancestors) > 1 else 0

            str_truncate = ""
            len_truncate = 0
            if truncate:
                tallies = []
                for attr in ("tasks", "collections"):
                    if getattr(subcoll, attr):
                        tally = str(len(getattr(subcoll, attr)))
                        len_truncate += len(attr) + tally

                        attr_col = "task" if attr == "task" else "collection"

                        name = color(self.config, attr, attr_col)
                        t_icon = icon_task if attr == "task" else icon_collection

                        tallies.append(f"{tally} {t_icon} {name}")
                        len_truncate += 4  # 2 spaces 1 emoji

                str_truncate += f" [{', '.join(tallies)}]"
                len_truncate += 5 if len(tallies) == 2 else 3

            item["str_ancestors"] = str_ancestors
            item["len_ancestors"] = len_ancestors
            item["str_title"] = str_title
            item["len_title"] = len_title
            item["str_truncate"] = str_truncate
            item["len_truncate"] = len_truncate

            item["len_long"] = len_ancestors + len_title + len_truncate
            item["len_short"] = max(len_ancestors, len_title, len_truncate)

            collection_items.append(item)
            items.append(item)

            # Recurse, if not already at max depth
            if not truncate:
                recursed_items = self._make_spdiu_items(
                    coll=subcoll, ancestors=ancestors + [name]
                )
                items.extend(recursed_items)

        if task_items:
            task_items[0]["first"] = True
            task_items[-1]["last"] = True

        if collection_items:
            collection_items[0]["first"] = True
            collection_items[-1]["last"] = True

        return items

    def display_with_items(self, lines, extra: str = "") -> None:
        """Output option dicts to the terminal.

        These are equivalent to the (option, text) tuples used by invoke,
        but they only contain values and defer rendering to this.

        Alternative to display_with_colums that solves or side-steps
        its alignment issues with control characters.
        """
        print(self.task_list_opener(extra=extra))
        print()
        root = self.list_root

        cols, rows = terminals.pty_size()

        def center_text(text, pad=" ", length=0):
            """Centers a line in the terminal.

            Accepts a canonical length to avoid miscounts with ansi chars.
            If length is left at 0, it uses len(text).
            """
            cols = terminals.pty_size()[0]

            if not length:
                length = len(text)

            if length >= cols:
                return text
            else:
                indent = int((cols - length) / 2) * pad
                return indent + text

        breadcrumb = []
        for item in lines:
            lead_width = self.leading_indent_width
            indent_width = self.indent_width * len(item["ancestors"])
            indent = ""
            borders = lead_width

            if item["op"] == "task":
                if item["ancestors"]:
                    borders = len(item["ancestors"])
                    indent += "│" * (borders - 1)

                    # discontinue extending the collection line
                    # if it's the last on its list.
                    last_parent = breadcrumb[-1]["last"]
                    indent += " " if last_parent else "│"

                    if item["last"] and not breadcrumb[-1]["subcollections"]:
                        indent += "└"
                    else:
                        indent += "├"

                    cap = ">"
                    pad = (indent_width - len(indent) - len(cap)) * "-"
                    indent += pad + cap

                else:
                    indent = " " * lead_width

                title = item["str_title"]
                aliases = item["str_aliases"]

                print(indent + title + aliases, end=self.col_padding * " ")

                # len_pad = len(indent) + self.col_padding
                # len_text = item['len_long']

                print(item["help"])

                if breadcrumb and item["last"]:
                    del breadcrumb[-1]

            elif item["op"] == "collection":
                if item["ancestors"]:
                    borders = len(item["ancestors"])
                    indent = "│" * borders

                if item["first"] and not item["last"]:
                    print(indent)
                    indent += "╒"
                elif item["last"]:
                    print(indent + "│")
                    indent += "╘"
                else:
                    print(indent + "│")
                    indent += "╞"

                indent += "╤"

                # if item['subcollections'] > 0:

                post_indent = "|>"

                ancestors = item["str_ancestors"]
                title = item["str_title"]
                truncate = item["str_truncate"]

                long = item["len_long"] + len(item["help"]) + 1

                margin = borders + len(indent) + len(post_indent)
                space = cols - margin

                if space > long:
                    text = post_indent + ancestors + title + truncate
                    text += f" {item['help']}"

                    len_text = long + len(post_indent)
                    str_text = center_text(text, pad="═", length=len_text)

                    print(indent + str_text)

                else:
                    print(ancestors)
                    print(title + truncate)
                    print(item["help"])

                breadcrumb.append(item)

            else:
                lpad = (lead_width + indent_width) * " "
                print(lpad + item["name"])
                print(lpad + item["help"])

        default = self.scoped_collection.default
        if default:
            specific = ""
            if root:
                specific = " '{}'".format(root)
                default = ".{}".format(default)

            # TODO: trim/prefix dots
            print("Default{} task: {}\n".format(specific, default))

    def task_list_opener(self, extra: str = "") -> str:
        """Generate the intro line to task list help."""
        root = self.list_root
        depth = self.list_depth

        i_c = self.config.spdiu.i["collection"]
        specifier = f" {i_c} {color(self.config, root, 'collection')}" if root else ""

        tail = ""
        if depth or extra:
            depthstr = "depth={}".format(depth) if depth else ""
            joiner = "; " if (depth and extra) else ""
            tail = " ({}{}{})".format(depthstr, joiner, extra)

        i_t = self.config.spdiu.i["task"]
        tasks = f"{i_t} {color(self.config, 'tasks', 'task')}"

        text = f"Available{specifier} {tasks}{tail}"
        return text

    def list_spdiu(self) -> None:
        """Format a task list, SpdIU style. Alternative to _nested and _flat.

        -F, --list-format STRING in the terminal defaults to this in SpdIU.
        """
        lines = self._make_spdiu_items(self.scoped_collection)

        # These are used by flat/nested too, overloading them only here.
        self.leading_indent_width = 1
        self.leading_indent = " " * self.leading_indent_width

        self.indent_width = 2
        self.indent = " " * self.indent_width

        self.col_padding = 2

        i_d = self.config.spdiu.i["default"]
        extra = f"{i_d}: default"

        self.display_with_items(lines=lines, extra=extra)

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
