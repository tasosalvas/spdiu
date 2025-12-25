#!/usr/bin/env python
# Copyright (C) 2025 Tasos Alvas <tasos.alvas@qwertyuiopia.com>
# SPDX-License-Identifier: AGPL-3.0-or-later
"""sui: SpdIU's template installer and invoke wrapper."""

from importlib import metadata
from pathlib import Path

from invoke import Program, Argument, Config
from invoke.util import debug
from invoke.exceptions import Exit

from invoke.main import __version__ as invoke_version

__version__ = metadata.version("spdiu")


class SpdIUConfig(Config):
    """SpdIU Invoke Config wrapper.

    Reads overrides from 'spdiu.yaml' files.
    """

    prefix = "spdiu"


class SpdIU(Program):
    """SpdIU Invoke wrapper."""

    def core_args(self):
        """Add SpdIU's extra flags to core args."""
        core_args = super().core_args()
        extra_args = [
            Argument(
                names=("install", "i"),
                kind=str,
                default="",
                optional=True,
                help="Install SpdIU instance files in the current folder.",
            ),
        ]
        return core_args + extra_args

    def parse_core(self, argv) -> None:
        """Add SpdIU's base path installation to core args."""
        super().parse_core(argv)

        if self.args.install.value:
            debug("Saw --install, generating SpdIU tasks.py")
            i_value = self.args.install.value

            if type(i_value) is str:
                p = Path(i_value).resolve()
            else:
                p = Path.cwd()

            p.mkdir(parents=True, exist_ok=True)
            target = p / "tasks.py"
            self.generate_spdiu_py(target)
            raise Exit

    def print_version(self) -> None:
        """Print the version of SpdIU and the underlying Invoke."""
        print(f"SpdIU {__version__} running on Invoke {invoke_version}")

    def generate_spdiu_py(self, file_path) -> None:
        """Generate a tasks.py from spdiu/templates/tasks.py."""
        src = Path(__file__).parent / "templates" / "tasks.py"

        file_path.write_text(src.read_text())
        print(f"Generated {file_path}")


def main() -> None:
    """Install local configuration, otherwise invokes inv."""
    program = SpdIU(version=__version__, config_class=SpdIUConfig)
    program.run()
