#!/usr/bin/env python
# Copyright (C) 2025 Tasos Alvas <tasos.alvas@qwertyuiopia.com>
# SPDX-License-Identifier: AGPL-3.0-or-later
"""Classes that represent SPD game entities."""


class Item:
    """An inventory item with an initialized dict."""

    def __init__(self, itemdict={}):
        """Construct a valid item dict, then overload its values with itemdict."""
        self.item = {
            "cursedKnown": True,
            "quantity": 1,
            "levelKnown": False,
            "cursed": False,
            "level": 0,
            "uses_left_to_id": 10,
            "__className": "com.shatteredpixel.shatteredpixeldungeon.items.armor.LeatherArmor",
            "kept_lost": False,
            "curse_infusion_bonus": False,
            "augment": "NONE",
            "glyph_hardened": False,
            "mastery_potion_bonus": False,
            "available_uses": 5,
        }

        for k, v in itemdict.items():
            self.item[k] = v
