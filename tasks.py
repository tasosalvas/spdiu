#!/usr/bin/env python
# Copyright (C) 2025 Tasos Alvas <tasos.alvas@qwertyuiopia.com>
# SPDX-License-Identifier: AGPL-3.0-or-later
"""
Shattered Pixel Dungeon Invoke Utility.

Manages save slots for the game.

Usage:
'inv info' for general documentation
'inv -l' for a list of tasks
'inv -h [task]' for a task's full docstring.
"""

import os

from time import strftime
from operator import itemgetter

from invoke import Collection, task

import spdiu


# Default (Collection level) configuration. Override values in invoke.yaml.
ns = Collection()
ns.configure({
    'spdiu': {
        # Game binaries
        'game_dir': os.path.dirname(os.path.realpath(__file__)),
        'game_cmd': 'bin/Shattered Pixel Dungeon',

        # Game data
        'data_dir': '~/.local/share/.shatteredpixel',
        'active_save': 'shattered-pixel-dungeon',

        'data_files': (
            'settings.xml',
            'badges.dat',
            'bones.dat',
            'journal.dat',
            'rankings.dat',
        ),

        # SPDIU config
        'work_dir': '~/.local/share/.shatteredpixel/saves',
        'default_slot': 'default',
        'backup_slot': 'bak',

        # Fancy decorations
        'time_format': '🗓️ %Y %b %d 🕰️ %H:%M:%S',

        'bullet_a': ' ||> ',
        'bullet_b': '  |> ',

        'disc_a': '📀',
        'disc_b': '💿',

        'i_bak': '💾',
        'i_game': '🕹️',
        'i_data': '🗂️',
        'i_clean': '🧹',
    }
})


# Helper functions, no context
def _get_games(save_dir):
    """
    Returns a list of game tuples: (path, last mod, game) for a data dir.

    Takes an absolute directory name, and returns the names of any folders in it
    that contain a 'game.dat'.
    """
    games = []

    for i in os.listdir(save_dir):
        i_path = os.path.join(save_dir, i)

        id_file = os.path.join(save_dir, i, 'game.dat')  # Used to detect a game
        if os.path.isdir(i_path) and os.path.isfile(id_file):
            games.append((i_path, spdiu.get_ts(i_path), i))

    return games


def _summarize_record(record):
    """
    Prints a brief summary of a rankings record.

    Accepts a dict of serialized data from a
    com.shatteredpixel.shatteredpixeldungeon.Rankings$Record.

    Only looks for 'Rankings$Record' to enable fork compatibility.
    """

    # __className <str>: Java class for ranking records
    if record['__className'].split('.')[-1] != 'Rankings$Record':
        return

    # date <str> 'YY-MM-DD' completion date
    # win <bool>
    # ascending <bool>
    # depth <int>

    # class <str> Hero class
    # level <int> Hero level
    # cause <str> Cause of death, items.Amulet on win or ascension
    # score <int> Run score

    title_line = f"{record['date']}  "
    title_line += f"l{record['level']:<2} {record['class']:<10}"
    title_line += f"{record['score']:>9,}  "

    if record['win'] and record['ascending']:
        title_line += 'Ascended with the Amulet.'
    elif record['win']:
        title_line += 'Obtained the Amulet.'
    else:
        title_line += f"Died by {record['cause'].split('.')[-1]} "
        title_line += f"on depth {record['depth']}."

    # tier <int> 1 to 6, depending on dungeon region progress

    # daily <bool>
    # custom_seed <str> empty on random seed runs

    # version <str> Game version used for the run
    # gameID <str> some hashed identifier?

    # gameData <dict>

    print(title_line)


# Helper functions, need context
def _get_slot(c, slot):
    """
    Returns a slot tuple: (path, last modification, slot name) from a name.
    """
    slot_path = os.path.join(os.path.expanduser(c.config.spdiu.work_dir), slot)

    return (
        slot_path,
        spdiu.get_ts(slot_path),
        slot,
    )


def _get_slots(c):
    """
    Returns all save slots as tuples:
    """
    cfg = c.config.spdiu

    try:
        folders = os.listdir(os.path.expanduser(cfg.work_dir))
    except FileNotFoundError:
        folders = ()

    slots = []
    for i in folders:
        slot = _get_slot(c, i)
        if slot:
            slots.append(slot)

    return slots


def _get_profile(c, dir_name):
    """
    Gets the contents of all the dat files in a save slot.
    """
    cfg = c.config.spdiu
    profile = {}

    for fn in cfg.data_files:
        f_path = os.path.join(dir_name, fn)

        f_parts = fn.split('.')
        f_ext = f_parts[1].lower() if len(f_parts) > 1 else ""

        if f_ext == "dat":
            profile[fn] = spdiu.read_dat(f_path)

        elif f_ext == "xml":
            profile[fn] = spdiu.read_xml(f_path)

    return profile


# File manipulation Tasks
@task
def backup(c):
    """
    Creates a backup of the active data.

    Automatically called by load and clean.
    """
    cfg = c.config.spdiu
    src = os.path.join(cfg.data_dir, cfg.active_save)
    dest = os.path.join(cfg.work_dir, cfg.backup_slot)

    try:
        spdiu.replace(src, dest)

    except FileNotFoundError:
        print('Aborting! There seems to be no active data folder.')
        return

    print(f"Active state backup created! {cfg.i_bak} {cfg.backup_slot}")


@task(post=[backup])
def clean(c):
    """
    Removes all saved states, leaves a backup of the active data folder.
    """
    cfg = c.config.spdiu
    if not spdiu.exists(os.path.join(data_dir, cfg.active_save)):
        print('Aborting! There seems to be no active data folder.')
        return

    slots = _get_slots(c)
    for (fn, mtime, slot) in slots:
        spdiu.remove(fn)

    print(f"{cfg.i_clean} {len(slots)} saved states deleted.")


@task
def save(c, slot=None):
    """
    Saves a copy of the current savegame folder. -s [slot] to name a slot.

    Slot names can only be alphanumeric characters.

    When saving over an existing slot, a backup of the previous state is kept
    as bak.[slot name].

    Saves are kept in the game's data folder, with their slot as an extension.
    """
    cfg = c.config.spdiu

    if slot == None:
        slot = cfg.default_slot

    if slot and not slot.isalnum():
        print("Aborting! Names can only contain alphanumeric characters.")
        return

    src = os.path.join(cfg.data_dir, cfg.active_save)
    dest = os.path.join(cfg.work_dir, slot)
    bak = os.path.join(cfg.work_dir, f"{cfg.backup_slot}.{slot}")

    if spdiu.exists(dest):
        spdiu.replace(dest, bak)
        print(f"Previous save preserved as {cfg.i_bak} {cfg.backup_slot}.{slot}")

    try:
        spdiu.replace(src, dest)
    except FileNotFoundError:
        print("No game data found to save!")

    print(f"State saved! {cfg.disc_b} {slot}")


@task
def load(c, slot=None, last=False, game=None):
    """
    Loads a save. -s [slot], -l for last save, -g [game] to only load a game.

    The --game [game name] flag allows loading only a specific game,
    while leaving the player profile untouched (i.e. keeping unlocks).

    Loading will save a backup of the active save in the backup slot,
    unless the backup slot itself is being loaded.
    """
    cfg = c.config.spdiu

    if slot == None:
        slot = cfg.default_slot

    if last:
        slots = sorted(_get_slots(c), key=itemgetter(1), reverse=True)

        if not slots:
            print("No saves found. Make some with 'inv save [-n name]'")
            return

        slot = slots[0][2]


    src_slot = os.path.join(cfg.work_dir, slot)
    dest_slot = os.path.join(cfg.data_dir, cfg.active_save)

    if not spdiu.exists(src_slot):
        print("Invalid slot name. 'inv ls' to list existing slots.")
        return


    if game == None:
        if slot != cfg.backup_slot:
            backup(c)

        spdiu.replace(src_slot, dest_slot)

        print(f"State loaded! {cfg.disc_a} {slot}")
        return


    src_game = os.path.join(src_slot, game)
    dest_game = os.path.join(dest_slot, game)

    if not spdiu.exists(src_game):
        print('Game not found in slot.')
        print(f"'inv show -s {slot}' to list existing games.")
        return

    if slot != cfg.backup_slot:
        backup(c)

    spdiu.replace(src_game, dest_game)
    print(f"Game loaded! {cfg.disc_a} {slot} {cfg.i_game} {game}")


# Informational tasks
@task
def info(c, config=False):
    """
    Usage and documentation. -c to display active SPDIU configuration.

    It prints the tasks file docstring.
    """
    cfg = c.config.spdiu

    print(__doc__)

    if not config:
        print("'inv info -c' to display active SPDIU configuration.")
        return

    print('Active configuration:')
    for k, v in cfg.items():
        print(f"{k}: {v}")


@task
def show(c, slot=None, active=False):
    """
    Displays details for a save slot. -s [slot] or -a for the active data.
    """
    cfg = c.config.spdiu
    if slot == None:
        slot = cfg.default_slot

    if active:
        s_dir = os.path.join(os.path.expanduser(cfg.data_dir), cfg.active_save)
        s_mtime = spdiu.get_ts(s_dir)
        print(f"Showing {cfg.disc_a} Active game data")

    else:
        print(f"Showing details for slot {cfg.disc_b} {slot}")
        s_dir, s_mtime, s_name = _get_slot(c, slot)


    profile = _get_profile(c, s_dir)
    print(f"\nProfile information:")

    for fn, v in profile.items():

        print(f"{cfg.i_data} {fn}")

        if fn == 'settings.xml':
            print(f"{cfg.bullet_b}{len(v)} options set.")


        elif fn == 'badges.dat':
            badges = v['badges']

            print(f"{cfg.bullet_b}{len(badges)} badges and related unlocks.")


        elif fn == 'bones.dat':

            if 'hero_class' not in v:
                print(f"{cfg.bullet_b}No character bones are set to spawn.")

            else:
                hero = v['hero_class']
                lvl = v['level']
                br = v['branch']

                print(f"{cfg.bullet_a}{hero} bones at level {lvl}, branch {br}.")


        elif fn == 'journal.dat':
            # NOTE: Entries appear in the file only after they've been unlocked,
            #       So total numbers are not represented in the save.

            # bestiary_classes <list> [class name] bestiary class index
            # bestiary_seen <list> [all True] bestiary seen status
            # bestiary_encounters <list> [int] bestiary encounter count

            b_seen = len(v['bestiary_seen'])
            print(f"{cfg.bullet_b}Bestiary: {b_seen} mobs seen.")

            # catalog_uses <list> 297 values.
            # catalog_seen <list> 297 values.
            # catalog_classes <list> 297 values.

            c_seen = len(v['catalog_seen'])
            print(f"{cfg.bullet_b}Catalog: {c_seen} items seen.")

            # documents <dict>
            # {<str> CATEGORY: {<str> note name: <int> 1 unread or 2 read }}.
            doc_count = 0
            for k, v in v["documents"].items():
                doc_count += len(v)

            print(f"{cfg.bullet_b}{doc_count} tutorials and notes discovered.")


        elif fn == 'rankings.dat':

            # won <int>: number of wins
            won = int(v['won'])
            # total <int>: total games played
            total = int(v['total'])

            print(f"{cfg.bullet_a}{won} games won out of {total} played.")

            # records <list> [dict Rankings$Record]
            # latest <int> index of latest game in 'records'

            # assertion: if latest is unset there's no records
            if 'latest' not in v:
                return

            print(f"{cfg.bullet_a}{len(v['records'])} stored ranking records.")

            records = v['records']
            latest = v['records'][int(v['latest'])]

            print(f"{cfg.bullet_b}Latest run:")
            print("    ", end="")
            _summarize_record(latest)

            # latest_daily <dict Rankings$Record>
            # daily_history_dates <list> [int secs since epoch]
            # daily_history_scores <list> [int score]

            # assertion: no daily has ever been played
            if 'latest_daily' not in v:
                return

            print(f"{cfg.bullet_b}Latest daily:")
            print("    ", end="")
            _summarize_record(v['latest_daily'])


    games = sorted(_get_games(s_dir), key=itemgetter(1), reverse=True)
    print(f"\n{cfg.i_game} {len(games)} games found:")
    for fn, mtime, game in games:

        if fn == games[0][0]:
            bullet = cfg.bullet_a
        else:
            bullet = cfg.bullet_b

        time = strftime(cfg.time_format, mtime)

        print(f"{bullet} {time} {cfg.i_game} {game}")


@task
def ls(c):
    """
    Lists all saved states chronologically.

    The disc icon signifies the latest data folder between all states.

    The bullet indicator signifies whether the active state is latest,
    but also displays the latest save slot, even if the active one is newer.

    The slots are sorted by time, so the latest one is always last.
    """
    cfg = c.config.spdiu
    slots = sorted(_get_slots(c), key=itemgetter(1))

    # active save vars
    a_ts = spdiu.get_ts(os.path.join(cfg.data_dir, cfg.active_save))
    a_bullet = cfg.bullet_a
    a_disc = cfg.disc_a

    # Calculate latest save
    if slots:
        latest = slots[-1]

        # adjust the active save display
        if a_ts <= latest[1]:
            a_bullet = cfg.bullet_b
            a_disc = cfg.disc_b


    print(f"Displaying {len(slots)} save slots, oldest to newest:")
    for (fn, mtime, slot) in slots:

        bullet = cfg.bullet_a if slot == latest[2] else cfg.bullet_b

        if slot.split(".")[0] == cfg.backup_slot:
            disc = cfg.i_bak
        elif slot == latest[2] and a_ts <= latest[1]:
            disc = cfg.disc_a
        else:
            disc = cfg.disc_b

        time = strftime(cfg.time_format, mtime)
        print(f"{bullet}{time} {disc} {slot}")


    print(f"\nActive slot:")

    print(a_bullet + strftime(cfg.time_format, a_ts) + f" {a_disc} {cfg.active_save}")


# Adding tasks to namespace
ns.add_task(save)
ns.add_task(load)

ns.add_task(ls)
ns.add_task(show)

ns.add_task(backup)
ns.add_task(clean)
ns.add_task(info)


# Conditionally import local project tasks
try:
    import local_tasks

    if 'ns' in dir(local_tasks):
        ns.add_collection(local_tasks.ns)

    else:
        if 'collection_name' in dir(local_tasks):
            col_name = local_tasks.collection_name
        else:
            col_name = 'u'

        ns.add_collection(Collection.from_module(local_tasks, col_name))

except ModuleNotFoundError:
    pass
