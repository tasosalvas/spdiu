#!/usr/bin/env python
# Copyright (C) 2025 Tasos Alvas <tasos.alvas@qwertyuiopia.com>
# SPDX-License-Identifier: AGPL-3.0-or-later
"""
Common domain specific reading and writing helpers.

The idea is to abstract common operations, so they can be improved independently.

util.path accepts path strings from config and returns Path objects.
It also ensures they are absolute and that user paths are expanded.

It requires context, so it's only really available to tasks.
All other functions assume valid pathlib.Path objects.

File attribute methods deal with getting timestamps.

Parsing methods read and write game datafiles.

File manipulation methods unify disk io into relevant operations.
"""

import shutil

import gzip
import json
import xml.etree.ElementTree as ET

from pathlib import Path
from time import gmtime


# File attributes
def get_ts(target: Path):
    """Return a gmtime (seconds: float since epoch) timestamp for a directory."""
    return gmtime(target.stat().st_mtime)


# Parsing
def read_dat(file: Path):
    """Read an SPD .dat file into a python object."""
    if not file.exists():
        print("The .dat file requested does not exist:")
        print(file)
        raise FileNotFoundError

    try:
        with gzip.open(file, "rb") as f:
            content = f.read()
    except gzip.BadGzipFile:
        print(f'Trouble unpacking "{file}"')
        raise

    return json.loads(content)


def write_dat(file: Path, data):
    """Write a python object into an SPD .dat file.

    Formats the incoming json to minify separators.
    """
    json_bin = str.encode(json.dumps(data, separators=(",", ":")))

    with gzip.open(file, "wb") as f:
        f.write(json_bin)


def read_xml(file: Path):
    """Read an xml file structured like SPD's settings.xml."""
    values = {}
    root = ET.parse(file).getroot()
    for i in root:
        values[i.attrib["key"]] = i.text

    return values


def write_xml(file: Path, data):
    """Write an xml file structured like SPD's settings.xml."""
    xml_start = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<!DOCTYPE properties SYSTEM "http://java.sun.com/dtd/properties.dtd">',
        "<properties>",
    ]
    xml_end = ["</properties>", ""]

    xml_lines = xml_start
    for key, val in data.items():
        xml_lines.append(f'<entry key="{str(key)}">{str(val)}</entry>')

    xml_txt = "\n".join(xml_lines + xml_end)
    file.write_text(xml_txt)


# Folder manipulation
def replace(src: Path, dest: Path):
    """Copy a directory tree to a destination, replacing anything there.

    Raises `FileNotFoundError` if the source does not exist.
    """
    # Check if the source file exists
    if not src.exists():
        raise FileNotFoundError

    # Make sure the path up to the destination exists
    dest.mkdir(parents=True, exist_ok=True)
    # This way prevents handling FileNotFound, and erases existing files.
    shutil.rmtree(dest)
    shutil.copytree(src, dest)


def remove(directory: Path):
    """Ensure a directory tree is deleted."""
    try:
        shutil.rmtree(directory)
    except FileNotFoundError:
        pass


# Unified path handling
def path(c, base, *args) -> Path:
    """Provide an absolute path for an operation, resolving config values.

    Accepts a base path, and appends any other arguments to it as subdirectories.
    If the path is relative, it is resolved in relation to spdiu.dirs.base.

    It can accept a Path or try to cast a provided str into one.
    """
    cfg = c.config.spdiu

    p = Path(base) if type(base) is str else base
    p = p.expanduser()

    if not p.is_absolute() and base != cfg.dirs.base:
        p = path(c, cfg.dirs.base) / p

    for arg in args:
        p = p / arg

    return p


# Unified slot/game selection
def select(c, slot="", game="", file="", entity="", default="latest"):
    """Parse command line arguments and return an object."""
    # see spdiu.display.dump for the latest take
    raise NotImplementedError


def resolve_color(color_name: str, color_dict) -> str:
    """Look up a color in the provided dict until you get hex.

    Will keep looking if the result is another name.
    """
    color = color_dict.get(color_name)
    if not color:
        return ""
    elif color[0] == "#":
        return color
    else:
        return resolve_color(color, color_dict)


def hex_to_ansi(hex_color: str) -> str:
    """Return a color string usable in ansi escape sequences."""
    color = hex_color.lstrip("#")
    rgb_str = (color[0:2], color[2:4], color[4:6])
    rgb_dec = [str(int(c, 16)) for c in rgb_str]
    return ";".join(rgb_dec)


def apply_color(text, foreground: str = "", background: str = ""):
    """Return a string colorized by the hex color provided.

    Values starting with "#" will be converted to the appropriate ANSI escape sequence.
    Otherwise they'll be looked up in the 'spdiu.c' color list.
    """
    if not foreground and not background:
        return text

    spec = "2"  # Truecolor. 5 would be 256 color.
    color = ""
    if foreground:
        color += f"\x1b[38;{spec};{hex_to_ansi(foreground)}m"

    if background:
        color += f"\x1b[48;{spec};{hex_to_ansi(background)}m"

    escape = "\x1b[0m"
    return color + text + escape


def color(c, text, fg_color_name: str = "", bg_color_name: str = "") -> str:
    """Return a colorized string by the color names provided.

    Also accepts a raw config object, so it can be used without context.
    """
    if "spdiu" in c:
        cfg = c.spdiu
    else:
        cfg = c.config.spdiu

    colors = cfg.c
    return apply_color(
        text, resolve_color(fg_color_name, colors), resolve_color(bg_color_name, colors)
    )
