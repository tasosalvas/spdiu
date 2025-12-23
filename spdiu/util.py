#!/usr/bin/env python
# Copyright (C) 2025 Tasos Alvas <tasos.alvas@qwertyuiopia.com>
# SPDX-License-Identifier: AGPL-3.0-or-later
"""
Common domain specific reading and writing helpers.

The idea is to abstract common operations, so they can be improved independently.
All of them run os.path.expanduser on their supplied paths.

File attribute methods deal with getting timestamps.

Parsing methods read and write game datafiles.

File manipulation methods unify disk io into relevant operations.
"""

import os
import shutil

import gzip
import json
import xml.etree.ElementTree as ET

from time import gmtime


# File attributes
def get_ts(dir_name):
    """Return a gmtime (seconds: float since epoch) timestamp for a directory."""
    return gmtime(os.stat(os.path.expanduser(dir_name)).st_mtime)


# Parsing
def read_dat(file_name):
    """Read an SPD .dat file into a python object."""
    if not os.path.exists(file_name):
        print("The .dat file requested does not exist:")
        print(file_name)
        raise FileNotFoundError

    try:
        with gzip.open(file_name, "rb") as f:
            content = f.read()
    except gzip.BadGzipFile:
        print(f'Trouble unpacking "{file_name}"')
        return {}

    return json.loads(content)


def write_dat(file_name, data):
    """Write a python object into an SPD .dat file.

    Formats the incoming json to minify separators.
    """
    json_bin = str.encode(json.dumps(data, separators=(",", ":")))

    with gzip.open(file_name, "wb") as f:
        f.write(json_bin)


def read_xml(file_name):
    """Read an xml file structured like SPD's settings.xml."""
    values = {}
    root = ET.parse(file_name).getroot()
    for i in root:
        values[i.attrib["key"]] = i.text

    return values


def write_xml(file_name, data):
    """Write an xml file structured like SPD's settings.xml."""
    raise NotImplementedError


# Folder manipulation
def replace(src_dir, dest_dir):
    """Copy a directory tree to a destination, replacing anything there.

    Expands user (~) on supplied paths.
    Raises `FileNotFoundError` if the source does not exist.
    """
    src = os.path.expanduser(src_dir)
    dest = os.path.expanduser(dest_dir)

    # Check if the source file exists
    if not os.path.exists(src):
        raise FileNotFoundError

    # Make sure the path up to the destination exists
    os.makedirs(dest, exist_ok=True)
    # This way prevents handling FileNotFound, and erases existing files.
    shutil.rmtree(dest)
    shutil.copytree(src, dest)


def remove(directory):
    """Ensure a directory tree is deleted.

    Expands user (~) on supplied paths.
    """
    try:
        shutil.rmtree(os.path.expanduser(directory))
    except FileNotFoundError:
        pass


def exists(path):
    """Check if a specified file or directory exists.

    Expands user (~) on supplied paths.
    """
    return os.path.exists(os.path.expanduser(path))


# Unified path handling
def path(c, path, *args):
    """Provide an absolute path for an operation, resolving config values.

    Accepts a base path, and appends any other arguments to it as subdirectories.

    If the path is relative, it is resolved in relation to spdiu.dirs.base.
    """
    cfg = c.config.spdiu
    path = os.path.expanduser(path)

    if not os.path.isabs(path):
        path = os.path.join(os.path.expanduser(cfg.dirs.base), path)

    for arg in args:
        path = os.path.join(path, arg)

    return path


# Unified slot/game selection
def select(c, slot="", game="", file="", entity="", default="latest"):
    """Parse command line arguments and return an object."""
    # see spdiu.display.dump for the latest take
    raise NotImplementedError
