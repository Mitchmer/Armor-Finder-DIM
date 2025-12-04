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
    "Wayward Psyche",
    "Sage Protector",
    "Shrewd Survivor",
    "Thriving Survivor",
    "Ferropotent",
    "Swordmaster",
    "New Demotic"
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


def find_duplicates(inventory, groups):
    # group by the selected columns (i.e. Archetype, Tertiary Stat, Tuning Stat) and count number of occurrences
    grouped_inventory = inventory.groupby(groups, dropna=False).count()
    # find all combinations with more than one instance
    grouped_inventory = grouped_inventory[grouped_inventory.get('Total (Base)') > 1]
    # create a masking column to filter the main inventory with
    grouped_inventory = grouped_inventory.reset_index().get(groups).assign(Duplicate= True)
    # merge the duplicates found mask with main inventory
    inventory_with_dupes = inventory.merge(grouped_inventory, on=groups, how='left')
    # filter all non-duplicates
    dupes = inventory_with_dupes[inventory_with_dupes.get('Duplicate') == True]
    # return the id's of all duplicates
    return dupes.get('Id')


def get_max_ids(inventory, groups, params):
    inventory = exclude_names_from_inventory(EXCLUDED_NAMES, inventory)

    inventory_archetypes = inventory['Archetype'].astype("string").to_numpy(dtype=str)
    mask = np.logical_or.reduce([np.char.find(inventory_archetypes, a) >= 0 for a in params.archetypes])
    inventory = inventory[mask]

    tertiary_inventory = inventory[
        (inventory['Tertiary Stat'].notna()) & (inventory['Rarity'] != 'Exotic') & (inventory['Tier'] >= params.minimum_tier)
    ]

    # create a separate inventory for tier >= 5
    high_tier_inventory = tertiary_inventory[tertiary_inventory['Tier'] >= 5]
    high_max_total_groupby = high_tier_inventory.groupby(groups, dropna=False)
    high_mask = high_max_total_groupby.obj['Total (Base)'].eq(high_max_total_groupby['Total (Base)'].transform('max'))
    high_max_total_group = high_max_total_groupby.obj[high_mask]
    
    # if the tier is <5 create a separate inventory for tiers less than 5
    low_tier_inventory = pd.DataFrame()
    if params.minimum_tier < 5:
        low_tier_inventory = tertiary_inventory[tertiary_inventory['Tier'] < 5]
        low_max_total_groupby = low_tier_inventory.groupby(groups, dropna=False)
        low_mask = low_max_total_groupby.obj['Total (Base)'].eq(low_max_total_groupby['Total (Base)'].transform('max'))
        low_max_total_group = low_max_total_groupby.obj[low_mask]
    
        compare_mask = high_max_total_group.get(groups[:-1]).drop_duplicates()
        compare_mask['remove'] = 1
        #display(compare_mask)
        low_max_dupes = low_max_total_group.merge(compare_mask, on=groups[:-1], how='left')
        low_max_dupes = low_max_dupes[low_max_dupes['remove'] != 1].drop(columns='remove')
    
        high_max_total_group = pd.concat([low_max_dupes, high_max_total_group], ignore_index=True)

    # make a copy of the max-stat inventory to query for duplicates
    total_max_pieces = high_max_total_group.copy()

    # grab all id's of max armor pieces
    ids_list = total_max_pieces.get('Id').to_numpy()
    
    # get ids of all duplicates
    dupe_ids_list = find_duplicates(high_max_total_group, groups)

    ids_string = ""
    for id in ids_list:
        ids_string += 'id:' + id + ' or '

    dupe_ids_string = ""
    for id in dupe_ids_list:
        dupe_ids_string += 'id:' + id + ' or '
    
    slice_len = len(' or ')
    return ids_string[:-slice_len], dupe_ids_string[:-slice_len]