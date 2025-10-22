import numpy as np
import pandas as pd
import re

ARMOR_FILEPATH = "destiny-armor.csv"
OUTPUT_FILEPATH = "destiny-finder-DIM-output.txt"

#TODO: Create "duplicate" output

ARMOR_ARCHETYPES = {
    "Brawler" : ["Melee", "Health"],
    "Bulwark" : ["Health", "Class"],
    "Grenadier" : ["Grenade", "Super"],
    "Gunner" : ["Weapons", "Grenade"],
    "Paragon" : ["Super", "Melee"],
    "Specialist" : ["Class", "Weapons"]
}

ARMOR_SETS = {
    "AION Adapter",
    "AION Renewal",
    "Bushido",
    "Collective Psyche",
    "Disaster Corps",
    "Iron Panoply",
    "Last Disciple",
    "Lustrous",
    "Smoke Jumper",
    "Techsec",
    "Twofold Crown",
    "Wayward Psyche"
}

STAT_LIST = [
    "Health",
    "Melee",
    "Grenade",
    "Super",
    "Class",
    "Weapons"
]

ARMOR_STAT_HASHES = {
    "Health" : 392767087,
    "Melee" : 4244567218,
    "Grenade" : 1735777505,
    "Super" : 144602215,
    "Class" : 1943323491,
    "Weapons" : 2996146975
}

EXCLUDED_NAMES = [
    "Masquerader"
]

temp_archetype_tertiaries = {}
temp_tertiary = []
for archetype, stats in ARMOR_ARCHETYPES.items():
    temp_archetype_tertiaries.update({ archetype : [] })
    for stat, hash in ARMOR_STAT_HASHES.items():
        if stat not in stats:
            temp_archetype_tertiaries.get(archetype).append(hash)
ARMOR_ARCHETYPES_TERTIARY_STATS = temp_archetype_tertiaries

CLASS_ITEM_LIST = [
    "Titan Mark",
    "Hunter Cloak",
    "Warlock Bond"
]

EQUIPPABLE_CLASSES = [
    "Titan",
    "Hunter",
    "Warlock"
]

class SortingParameters:
    def __init__(self, dict):
        self.sets = np.array(dict.get("sets"), dtype=str)
        self.archetypes = np.array(dict.get("archetypes") if dict.get("archetypes") is not None else ARMOR_ARCHETYPES.keys(), dtype=str)
        self.minimum_tier = dict.get("minimum_tier")
        self.classes = dict.get("classes") if dict.get("classes") is not None else EQUIPPABLE_CLASSES


def exclude_names_from_inventory(names, inventory):
    pattern = "|".join(map(re.escape, names))
    mask = inventory['Name'].str.contains(pattern, case=False, na=False, regex=True)
    return inventory[~mask]


def get_max_ids(inventory, groups, params):
    inventory = exclude_names_from_inventory(EXCLUDED_NAMES, inventory)

    inventory_archetypes = inventory['Archetype'].astype("string").to_numpy(dtype=str)
    mask = np.logical_or.reduce([np.char.find(inventory_archetypes, a) >= 0 for a in params.archetypes])
    inventory = inventory[mask]

    tertiary_inventory = inventory[
        (inventory['Tertiary Stat'].notna()) & (inventory['Rarity'] != 'Exotic') & (inventory['Tier'] >= params.minimum_tier)
    ]

    max_total_groupby = tertiary_inventory.groupby(groups, dropna=False)
    mask = max_total_groupby.obj['Total (Base)'].eq(max_total_groupby['Total (Base)'].transform('max'))
    max_total_group = max_total_groupby.obj[mask]
    ids_list = max_total_group.get('Id').to_numpy()

    ids_string = ""
    for id in ids_list:
        ids_string += 'id:' + id + ' or '
    
    slice_len = len(' or ')
    return ids_string[:-slice_len]
