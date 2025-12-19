#!/usr/bin/env python
# Copyright (C) 2025 Tasos Alvas <tasos.alvas@qwertyuiopia.com>
# SPDX-License-Identifier: AGPL-3.0-or-later
"""
SPDIU Display task collection.

Tasks that query and display game data.

By convention, where applicable:
-s, --slot is used to load a save slot by name
-g, --game to pick a specific game in a slot
"""

import os
from time import strftime

from invoke import Collection, task

from ..model import Profile


ns = Collection("view")


def _recurse_dump(c, dump, title, breadcrumb=[], silent=False):
    """
    Explore a dat file, printing merrily along the way.

    Accepts any data type, will recurse into lists and dicts.

    It returns a flat list of tuples for every value in the structure:
    (breadcrumb: list, title: str, d_type: str, game_class: str, summary: str)

    By default, it pretty prints the values. silent=True to just get the list.
    """
    cfg = c.config.spdiu
    ns = cfg.game_ns

    d_breadcrumb = '.'.join(breadcrumb)
    d_type = type(dump).__name__
    d_title = f"{title} <{d_type}>"
    d_icon = cfg[f"i_{d_type}"]


    game_class = ""

    if d_type == 'dict' and '__className' in dump:
        game_class = dump['__className'][len(ns)+1:]
        summary = f"{cfg.i_game} {game_class}, {len(dump)} values"


    elif d_type == 'str' and ns in dump:
        game_class = dump[len(ns)+1:]
        summary = f"{cfg.i_game} {game_class}"


    elif d_type in ('list', 'dict'):
        summary = f"{len(dump)} values"


    else:
        summary = f"{str(dump)}"


    results = [(breadcrumb, title, d_type, game_class, summary)]

    if not silent:
        lpad = "  " * len(breadcrumb)
        newline = '\n' if d_type in ('list', 'dict') and len(dump) > 0 else ''
        print(newline + lpad + f"{d_breadcrumb} {d_title} {d_icon}: {summary}")

    breadcrumb_next = breadcrumb + [title]


    # Got our line, now to dig deeper
    if d_type == 'dict':

        for k, v in dump.items():
            results += _recurse_dump(c, v, k, breadcrumb_next, silent)


    elif d_type == 'list':

        for idv, v in enumerate(dump):
            idv_title = f"[{str(idv)}]"
            results += _recurse_dump(c, v, idv_title, breadcrumb_next, silent)


    return results


# Object summaries
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


@task
def show(c, slot=None, active=False):
    """
    Displays details for a save slot. -s [slot] or -a for the active data.
    """
    cfg = c.config.spdiu
    if slot is None:
        slot = cfg.default_slot

    if active:
        s_dir = os.path.join(cfg.data_dir, cfg.active_save)
        print(f"Showing {cfg.disc_a} Active game data")

    else:
        s_dir = os.path.join(cfg.work_dir, slot)
        print(f"Showing details for slot {cfg.disc_b} {slot}")


    p = Profile(s_dir)
    print("\nProfile information:")


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


ns.add_task(show)
