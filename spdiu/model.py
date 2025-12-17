#!/usr/bin/env python
# Copyright (C) 2025 Tasos Alvas <tasos.alvas@qwertyuiopia.com>
# SPDX-License-Identifier: AGPL-3.0-or-later
"""
Classes that represent the user data of an SPD installation.
"""

import os
from operator import attrgetter

from . import util


# Game data representation classes
class Item():
    """
    An inventory item with an initialized dict.
    """

    def __init__(self, itemdict={}):
        self.item = {
            'cursedKnown': True,
            'quantity': 1,
            'levelKnown': False,
            'cursed': False,
            'level': 0,
            'uses_left_to_id': 10,
            '__className': 'com.shatteredpixel.shatteredpixeldungeon.items.armor.LeatherArmor',
            'kept_lost': False,
            'curse_infusion_bonus': False,
            'augment': 'NONE',
            'glyph_hardened': False,
            'mastery_potion_bonus': False,
            'available_uses': 5
        }

        for k, v in itemdict.items():
            self.item[k] = v


# Save directory management classes
class DataDir():
    """
    A directory of game data. Inherited by Profile and Game.

    It has a list of the .dat files it contains and methods for reading them.
    It can dig up the newest timestamp in the files and directories under it.
    """

    def set_dat(self, dat_file, contents):
        """
        Writes a python object into a dat file.
        """
        util.write_dat(os.path.join(self.root_dir, dat_file), contents)


    def get_dat(self, dat_file):
        """
        Returns the contents of a dat file as a python object.
        """
        try:
            return util.read_dat(os.path.join(self.root_dir, dat_file))

        except FileNotFoundError:
            return None


    def __init__(self, base_dir):
        self.root_dir = os.path.expanduser(base_dir)
        self.name = os.path.split(base_dir)[1]

        self.dat_files = [
            i for i in os.listdir(self.root_dir)      \
            if os.path.splitext(i)[1] == '.dat'       \
        ]

        # Get the newest timestamp between the directory and its files.
        ts_list = [util.get_ts(self.root_dir)]

        for f in os.listdir(self.root_dir):
            p = os.path.join(self.root_dir, f)
            if not os.path.isdir(p):
                ts_list.append(util.get_ts(p))

        self.ts = sorted(ts_list, reverse=True)[0]


    def __repr__(self):
        return f"<{self.__class__.__name__}> {self.name}"


class Game(DataDir):
    """
    An active game of SPD. A Profile can have multile Games.
    """

    def __init__(self, game_dir):
        super().__init__(game_dir)

        if 'game.dat' not in self.dat_files:
            raise FileNotFoundError


    def __repr__(self):
        return f"<{self.__class__.__name__}> {self.name}"


class Profile(DataDir):
    """
    An SPD data folder. Includes settings, profile stats, and games.

    games contains Game objects sorted by modification time.
    """

    def get_settings(self):
        """
        Returns the values from settings.xml as a dict.
        """
        try:
            return util.read_xml(os.path.join(self.root_dir, 'settings.xml'))

        except FileNotFoundError:
            return {}


    def get_game(self, game_name):
        """
        Returns a game by the requested name.
        """
        for g in self.games:
            if g.name == game_name:
                return g

        return None


    def __init__(self, base_dir):
        """
        Accepts a group: str, which represents its parent
        """

        super().__init__(base_dir)
        self.group = os.path.split(os.path.split(self.root_dir)[0])[1]

        # Detect if this is a game data folder:
        # settings.xml appears at first launch
        # journal.dat the moment the dungeon is first loaded
        if 'journal.dat' not in self.dat_files:
            raise FileNotFoundError

        games = []
        for i in os.listdir(self.root_dir):
            i_path = os.path.join(self.root_dir, i)

            if not os.path.isdir(i_path):
                continue

            try:
                game = Game(i_path)
                games.append(game)
            except FileNotFoundError:
                continue

            if self.ts < game.ts:
                self.ts = game.ts

        self.games = sorted(games, key=attrgetter('ts'), reverse=True)


    def __repr__(self):
        return f"<{self.__class__.__name__}> {self.name}"


class Slots():
    """
    Manager class for save directories containing states of data files.

    Represents a flat namespace of alphanumeric character names.

    slots contains all states as Profiles sorted by modification time.
    """

    def get_slot(self, slot_name):
        """
        Returns a Profile representing the save with the requested name.

        Accepts 'subdir.slot' syntax, falls back to default_subdir if omitted.
        """
        parts = slot_name.split('.')
        if len(parts) > 1:
            sd = parts[0]
            slot = parts[1]

        else:
            sd = self.default_subdir
            slot = slot_name

        for p in self.slots:
            if p.name == slot and p.group == sd:
                return p

        return None


    def __init__(self, base_dir, subdirs=['manual'], default_subdir='manual'):
        """
        Accepts a list of subdirs to construct its slots from.
        """
        self.name = '+'.join(subdirs)
        self.root_dir = os.path.expanduser(base_dir)

        self.subdirs = [os.path.join(self.root_dir, i) for i in subdirs]
        self.default_subdir = default_subdir

        slots = []
        for sd in self.subdirs:
            for i in os.listdir(sd):
                i_path = os.path.join(sd, i)

                try:
                    slots.append(Profile(i_path))
                except FileNotFoundError:
                    print("oops")
                    pass

        self.slots = sorted(slots, key=attrgetter('ts'), reverse=True)


    def __repr__(self):
        return f"<{self.__class__.__name__}> {self.name}"
