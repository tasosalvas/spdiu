#!/usr/bin/env python
# Copyright (C) 2025 Tasos Alvas <tasos.alvas@qwertyuiopia.com>
# SPDX-License-Identifier: AGPL-3.0-or-later
"""Emojis and ASCII elements used in SpdIU terminal output."""

icons = {
    # Utility
    "_space": "\N{TAG SPACE}",
    "_cancel": "\N{CANCEL TAG}",
    # slot status
    "disc_a": "📀",
    "disc_b": "💿",
    # slot types
    "bak": "💾",
    "auto": "🤖",
    "game": "🕹️",
    # concepts
    "collection": "🧰",
    "task": "⚙️",
    "default": "🚏",
    "data": "🗂️",
    "package": "📦",
    "fork": "🍽️",
    "unknown": "👽",
    "warning": "☢️",
    # actions
    "clean": "🧹",
    "inspect": "🔎",
    # data types (type.__name__)
    "dict": "📖",
    "list": "📋",
    "int": "🧮",
    "float": "🍕",
    "str": "🔤",
    "bool": "💡",
    "NoneType": "🫙",
}

strings = {
    "bullet_a": " ||> ",
    "bullet_b": "  |> ",
}

colors = {
    # reference
    "black": "#202020",
    "white": "#d0d0d0",
    "green": "#7e8d50",
    "red": "#ac4142",
    "yellow": "#e5b566",
    "blue": "#6c99ba",
    "magenta": "#9e4e85",
    "cyan": "#7dd5cf",
    # concepts
    "task": "yellow",
    "collection": "red",
}
