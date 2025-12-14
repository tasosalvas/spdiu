#!/usr/bin/env python
# Copyright (C) 2025 Tasos Alvas <tasos.alvas@qwertyuiopia.com>
# SPDX-License-Identifier: AGPL-3.0-or-later
"""
Classes that represent the user data of an SPD installation.
"""
import os

from . import util


class DataDir():
    """
    A directory of game data. Inherited by Profile and Game.

    It knows its last modification time and the .dat files it contains.
    """

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
        self.ts = util.get_ts(base_dir)

        self.dat_files = [
            i for i in os.listdir(self.root_dir)      \
            if os.path.splitext(i)[1] == '.dat'       \
        ]


class Game(DataDir):
    """
    An active game of SPD. A Profile can have multile Games.
    """

    def __init__(self, game_dir):
        super().__init__(game_dir)


    def __repr__(self):
        return f"<{self.__class__.__name__}> {self.name}"


class Profile(DataDir):
    """
    An SPD data folder. Includes settings, profile stats, and games.
    """

    def get_settings(self):
        """
        Returns the values from settings.xml as a dict.
        """
        try:
            return util.read_xml(os.path.join(self.root_dir, 'settings.xml'))

        except FileNotFoundError:
            return {}


    def _get_games(self):
        """
        Returns a list of Game objects for the Profile.
        """
        games = []
        for i in os.listdir(self.root_dir):
            i_path = os.path.join(self.root_dir, i)
            # Used to detect whether a folder is a game
            id_file = os.path.join(i_path, 'game.dat')

            if os.path.isdir(i_path) and os.path.isfile(id_file):
                games.append(Game(i_path))

        return games


    def __init__(self, base_dir):
        super().__init__(base_dir)
        self.games = self._get_games()


    def __repr__(self):
        return f"<{self.__class__.__name__}> {self.name}"

