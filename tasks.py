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

from invoke import Collection, task

from spdiu import util
from spdiu.model import Slots, Profile
from spdiu.collections import cheat


# Default SPDIU configuration. Override values in invoke.yaml.
ns = Collection()
ns.configure({
    'spdiu': {
        # Game binaries
        'game_dir': os.path.dirname(os.path.realpath(__file__)),
        'game_cmd': 'bin/Shattered Pixel Dungeon',
        'game_ns': 'com.shatteredpixel.shatteredpixeldungeon',

        # Game data
        'data_dir': '~/.local/share/.shatteredpixel',
        'active_save': 'shattered-pixel-dungeon',

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
        util.replace(src, dest)

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
    if not util.exists(os.path.join(data_dir, cfg.active_save)):
        print('Aborting! There seems to be no active data folder.')
        return

    s = Slots(cfg.work_dir)
    for p in s.slots:
        util.remove(p.root_dir)

    print(f"{cfg.i_clean} {len(s.slots)} saved states deleted.")


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

    if util.exists(dest):
        util.replace(dest, bak)
        print(f"Previous save preserved as {cfg.i_bak} {cfg.backup_slot}.{slot}")

    try:
        util.replace(src, dest)
    except FileNotFoundError:
        print("No game data found to save!")

    print(f"State saved! {cfg.disc_b} {slot}")


@task
def load(c, last=False, slot=None, game=None):
    """
    Loads a save. -s [slot], -l for last save, -g [game] to only load a game.

    The --game [game name] flag allows loading only a specific game,
    while leaving the player profile untouched (i.e. keeping unlocks).

    Loading will save a backup of the active save in the backup slot,
    unless the backup slot itself is being loaded.
    """

    cfg = c.config.spdiu
    s = Slots(cfg.work_dir)

    # determine the profile slot from the arguments
    if slot == None:
        slot = cfg.default_slot

    if last:
        if not s.slots:
            print("No saves found. Make some with 'inv save [-s slot name]'")
            return

        slot = s.slots[0].name


    # Get the instance of the profile to load, build the destination path
    p = s.get_slot(slot)
    ap_path = os.path.join(cfg.data_dir, cfg.active_save)

    if not p:
        print(f"Invalid slot name: {slot}. 'inv ls' to list existing slots.")


    # Load the requested profile and exit
    if game == None:
        if p.name != cfg.backup_slot:
            backup(c)

        util.replace(p.root_dir, ap_path)

        print(f"State loaded! {cfg.disc_a} {slot}")
        return


    # Get the instance of the requested game, build the destination path.
    g = p.get_game(game)
    agp = os.path.join(ap.root_dir, game)

    if not g:
        print('Game not found in slot.')
        print(f"'inv show -s {slot}' to list existing games.")
        return

    if  p.name != cfg.backup_slot:
        backup(c)

    util.replace(g.root_dir, agp)
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

    print('Active SPDIU configuration:')
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
        s_dir = os.path.join(cfg.data_dir, cfg.active_save)
        print(f"Showing {cfg.disc_a} Active game data")

    else:
        s_dir = os.path.join(cfg.work_dir, slot)
        print(f"Showing details for slot {cfg.disc_b} {slot}")


    p = Profile(s_dir)
    print(f"\nProfile information:")


    # Settings
    settings = p.get_settings()
    print(f"{cfg.bullet_b}{len(settings)} options set.")


    # Badges
    badges = p.get_dat('badges.dat')
    if badges:
        print(f"{cfg.bullet_b}{len(badges['badges'])} badges and related unlocks.")

    # Bones
    bones = p.get_dat('bones.dat')
    if bones:
        if 'hero_class' not in bones:
            print(f"{cfg.bullet_b}No character bones are set to spawn.")

        else:
            hero = bones['hero_class']
            lvl = bones['level']
            br = bones['branch']

            print(f"{cfg.bullet_a}{hero} bones at level {lvl}, branch {br}.")

    # Journal
    journal = p.get_dat('journal.dat')
    if journal:
        # NOTE: Entries appear in the file only after they've been unlocked,
        #       So total numbers are not represented in the save.

        # bestiary_classes <list> [class name] bestiary class index
        # bestiary_seen <list> [all True] bestiary seen status
        # bestiary_encounters <list> [int] bestiary encounter count

        b_seen = len(journal['bestiary_seen'])
        print(f"{cfg.bullet_b}Bestiary: {b_seen} mobs seen.")

        # catalog_uses <list> 297 values.
        # catalog_seen <list> 297 values.
        # catalog_classes <list> 297 values.

        c_seen = len(journal['catalog_seen'])
        print(f"{cfg.bullet_b}Catalog: {c_seen} items seen.")

        # documents <dict>
        # {<str> CATEGORY: {<str> note name: <int> 1 unread or 2 read }}.
        doc_count = 0
        for k, v in journal['documents'].items():
            doc_count += len(v)

        print(f"{cfg.bullet_b}{doc_count} tutorials and notes discovered.")

    # Rankings
    ranks = p.get_dat('rankings.dat')
    if ranks:
        # won <int>: number of wins
        won = int(ranks['won'])
        # total <int>: total games played
        total = int(ranks['total'])

        print(f"{cfg.bullet_a}{won} games won out of {total} played.")

        # records <list> [dict Rankings$Record]
        # latest <int> index of latest game in 'records'

        # assertion: if latest is unset there's no records
        if 'latest' not in ranks:
            return

        print(f"{cfg.bullet_a}{len(ranks['records'])} stored ranking records.")

        records = ranks['records']
        latest = ranks['records'][int(ranks['latest'])]

        print(f"{cfg.bullet_b}Latest run:")
        print("    ", end="")

        _summarize_record(latest)

        # latest_daily <dict Rankings$Record>
        # daily_history_dates <list> [int secs since epoch]
        # daily_history_scores <list> [int score]

        # assertion: no daily has ever been played
        if 'latest_daily' not in ranks:
            return

        print(f"{cfg.bullet_b}Latest daily:")
        print("    ", end="")

        _summarize_record(ranks['latest_daily'])


    print(f"\n{cfg.i_game} {len(p.games)} games found:")

    for g in reversed(p.games):
        bullet = cfg.bullet_a if g == p.games[0] else cfg.bullet_b
        time = strftime(cfg.time_format, g.ts)
        print(f"{bullet} {time} {cfg.i_game} {g.name}")


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
    ap = Profile(os.path.join(cfg.data_dir, cfg.active_save))
    s = Slots(cfg.work_dir)

    # active save vars
    a_bullet = cfg.bullet_a
    a_disc = cfg.disc_a

    # Calculate latest save
    if s.slots:
        latest = s.slots[0]

        # adjust the active save display
        if ap.ts <= latest.ts:
            a_bullet = cfg.bullet_b
            a_disc = cfg.disc_b


    print(f"Displaying {len(s.slots)} save slots, oldest to newest:")
    for slot in reversed(s.slots):

        bullet = cfg.bullet_a if slot == latest else cfg.bullet_b

        if slot.name.split(".")[0] == cfg.backup_slot:
            disc = cfg.i_bak
        elif slot == latest and ap.ts <= latest.ts:
            disc = cfg.disc_a
        else:
            disc = cfg.disc_b

        time = strftime(cfg.time_format, slot.ts)
        print(f"{bullet}{time} {disc} {slot.name}")


    print(f"\nActive slot:")

    print(a_bullet + strftime(cfg.time_format, ap.ts) + f" {a_disc} {cfg.active_save}")


# Adding tasks to namespace
ns.add_task(info)

ns.add_task(save)
ns.add_task(load)

ns.add_task(ls)
ns.add_task(show)

ns.add_task(backup)
ns.add_task(clean)

ns.add_collection(cheat)


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
