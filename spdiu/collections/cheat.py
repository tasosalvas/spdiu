#!/usr/bin/env python
# Copyright (C) 2025 Tasos Alvas <tasos.alvas@qwertyuiopia.com>
# SPDX-License-Identifier: AGPL-3.0-or-later
"""
SPDIU Cheat task collection.

These tasks all work on the active game data. Make a save before using them.

Tasks that act on a game accept the -g --game_name flag. It defaults to 'game1'.
"""

import os
from invoke import task, Collection

from .. import util
from ..model import Profile, Item


ns = Collection('cheat')


@task
def gold(c, game_name='game1', number='10000'):
    """
    Set your Gold! -n --number [amount]
    """
    cfg = c.config.spdiu
    a_slot = os.path.join(cfg.data_dir, cfg.active_save)
    ap = Profile(a_slot)

    g = ap.get_game(game_name)
    gd = g.get_dat('game.dat')

    print(f"Previous Gold: {gd['gold']}")

    gd['gold'] = int(number)
    g.set_dat('game.dat', gd)

    print(f"{cfg.i_data} Gold set to {number}!")


@task
def energy(c, game_name='game1', number='1000'):
    """
    Set your Alchemical Energy! -n --number [amount]
    """
    cfg = c.config.spdiu
    ap = Profile(os.path.join(cfg.data_dir, cfg.active_save))

    g = ap.get_game(game_name)
    gd = g.get_dat('game.dat')

    print(f"Previous Alchemical Energy: {gd['energy']}")

    gd['energy'] = int(number)
    g.set_dat('game.dat', gd)

    print(f"{cfg.i_data} Alchemical Energy set to {number}!")


@task
def bones(c, package="", hero=""):
    """
    Sets your bones. 'inv -h cheat.bones' for options.

    -p, --package to pick your package, or you'll just get food.

    plate: Your one and only armor
    blade: Be one with the shadows
    wealth: Yog can wait
    reroll: Make your own seed
    regrowth: Stardew Pixel Dungeon
    zip: Walls are just a suggestion


    -h, --hero to pick, or a hero that fits your package will be assigned.

    i.e. WARRIOR, MAGE, ROGUE, HUNTRESS, DUELIST, CLERIC
    Classes are uppercase in game files, but you can enter them lowercase here.

    Read through the task code, it's easy to adapt in your own local task.
    """

    cfg = c.config.spdiu
    active_slot = os.path.join(cfg.data_dir, cfg.active_save)
    p = Profile(active_slot)


    namespace = '.'.join((cfg.game_ns, 'items'))

    if package == 'plate':
        hero_class = 'WARRIOR'
        item = 'armor.PlateArmor'

        # no auguments in bones :(
        # aug = 'armor.glyphs.Thorns'

        i = Item({
            '__className': '.'.join((namespace, item)),
            'level': 3,
            'mastery_potion_bonus': True,
        })


    elif package == 'blade':
        hero_class = 'DUELIST'
        item = 'weapon.melee.AssassinsBlade'
        i = Item({
            '__className': '.'.join((namespace, item)),
            'level': 3,
            'mastery_potion_bonus': True,
        })


    elif package == 'wealth':
        hero_class = 'ROGUE'
        item = 'rings.RingOfWealth'
        i = Item({
            '__className': '.'.join((namespace, item)),
            'level': 3,
        })


    elif package == 'reroll':
        hero_class = 'CLERIC'
        item = 'scrolls.ScrollOfTransmutation'
        i = Item({
            '__className': '.'.join((namespace, item)),
            'quantity': 6,
        })


    elif package == 'regrowth':
        hero_class = 'HUNTRESS'
        item = 'wands.WandOfRegrowth'
        i = Item({
            '__className': '.'.join((namespace, item)),
            'level': 3,
        })


    elif package == 'zip':
        hero_class = 'ROGUE'
        item = 'artifacts.EtherealChains'
        i = Item({
            '__className': '.'.join((namespace, item)),
        })


    else:
        hero_class = 'MAGE'
        item = 'food.Berry'
        #item = 'food.Food'
        i = Item({
            '__className': '.'.join((namespace, item)),
            'quantity': 12,
        })


    if hero:
        hero_class = hero.upper()


    bones = {
        'item': i.item,
        'hero_class': hero_class,
        'level': 1,
        'branch': 0,
    }

    p.set_dat('bones.dat', bones)
    print('A Small Package of Value Will Come to You, Shortly')


@task
def consumables(c, game_name='game1'):
    """
    Returns all consumable identities. -g --game [game_name] to pick a game.

    Bullet indicators show whether a consumable is known or not.
    """
    cfg = c.config.spdiu
    a_slot = os.path.join(cfg.data_dir, cfg.active_save)

    p = Profile(a_slot)
    g = p.get_game(game_name)
    gd = g.get_dat('game.dat')

    labels = {k: v for k, v in gd.items() if '_label' in k}

    potions = {k: v for k, v in labels.items() if 'PotionOf' in k}
    rings = {k: v for k, v in labels.items() if 'RingOf' in k}
    scrolls = {k: v for k, v in labels.items() if 'ScrollOf' in k}

    print(f" {cfg.i_data} Potions")
    for k, v in potions.items():
        iclass = k.split('_')[0]
        known = gd[iclass + '_known']
        name = iclass[len('PotionOf'):]
        bullet = cfg.bullet_a if known else cfg.bullet_b

        print(f"{bullet}{name}: {v}")

    print(f"\n {cfg.i_data} Rings")
    for k, v in rings.items():
        iclass = k.split('_')[0]
        known = gd[iclass + '_known']
        name = iclass[len('RingOf'):]
        bullet = cfg.bullet_a if known else cfg.bullet_b

        print(f"{bullet}{name}: {v}")

    print(f"\n {cfg.i_data} Scrolls")
    for k, v in scrolls.items():

        iclass = k.split('_')[0]
        known = gd[iclass + '_known']
        name = iclass[len('ScrollOf'):]
        bullet = cfg.bullet_a if known else cfg.bullet_b

        print(f"{bullet}{name}: {v}")


ns.add_task(gold)
ns.add_task(energy)
ns.add_task(bones)
ns.add_task(consumables)
