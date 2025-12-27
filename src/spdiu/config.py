#!/usr/bin/env python
# Copyright (C) 2025 Tasos Alvas <tasos.alvas@qwertyuiopia.com>
# SPDX-License-Identifier: AGPL-3.0-or-later
"""SpdIU's Default configuration and Config class."""

from pathlib import Path
from invoke.config import Config, merge_dicts

from spdiu.styles import icons, strings


class SpdIUConfig(Config):
    """SpdIU Invoke Config wrapper.

    Reads overrides from 'spdiu.yaml' files.
    """

    prefix = "spdiu"

    # Default SpdIU configuration. Override values in spdiu.yaml.
    defaults = {
        "spdiu": {
            "dirs": {
                # Internal variable, the location of the script.
                "base": Path(__file__).resolve().parent,
                "slots": "slots",
                "package": "packages",
                "game": "game",
            },
            # SpdIU config
            "default_slot": "default",
            "backup_slot": "bak",
            ## Game release info, used to download the game
            "release": {
                # Github specific, if they work elsewhere it's a miracle
                "gh_use_api": True,
                "project": "00-Evan/shattered-pixel-dungeon",
                # Release properties, used for fishing for the right release
                "version": None,
                "tag_name": None,
                "platform": "Linux",
                "extension": "zip",
                # Template expression, constructs a download url if automation can't
                "template": "https://github.com/{project}/releases/download/{tag_name}/ShatteredPD-{version}-{platform}.{ext}",
            },
            # The game installation
            "game": {
                "data": "~/.local/share/.shatteredpixel/shattered-pixel-dungeon",
                "cmd": "bin/Shattered Pixel Dungeon",
                "ns": "com.shatteredpixel.shatteredpixeldungeon",
            },
            # Config-overridable styles.
            "time_format": "🗓️ %Y %b %d 🕰️ %H:%M:%S",
            # Emojis used in terminal output
            "i": icons,
            # ASCII strings used in terminal output
            "s": strings,
        }
    }

    @staticmethod
    def global_defaults():
        """Append SpdIU defaults."""
        return merge_dicts(Config.global_defaults(), SpdIUConfig.defaults)
