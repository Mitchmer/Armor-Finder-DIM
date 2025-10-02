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
    "Iron Beryllium",
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
        self.sets = dict.get("sets")
        self.archetypes = dict.get("archetypes") if dict.get("archetypes") is not None else ARMOR_ARCHETYPES.keys()
        self.minimum_tier = dict.get("minimum_tier")
        self.classes = dict.get("classes") if dict.get("classes") is not None else EQUIPPABLE_CLASSES


class Armor:
    def __init__(self, dict):
        self.name = dict.get("Name")
        self.id = int(dict.get("Id").strip('"'))
        self.equippable_class = dict.get("Equippable")
        self.slot = dict.get("Type") 
        self.tier = int(dict.get("Tier").strip('"'))
        self.season = int(dict.get("Season").strip('"'))
        self.stats = {
            "Health" : int(dict.get("Health (Base)").strip('"')),
            "Melee" : int(dict.get("Melee (Base)").strip('"')),
            "Grenade" : int(dict.get("Grenade (Base)").strip('"')),
            "Super" : int(dict.get("Super (Base)").strip('"')),
            "Class" : int(dict.get("Class (Base)").strip('"')),
            "Weapons" : int(dict.get("Weapons (Base)").strip('"')),
            "Total" : int(dict.get("Total (Base)").strip('"'))
        }
        # strip set name from armor name
        temp_set_list = dict.get("Name").split(' ')
        temp_set_list_removed = temp_set_list.pop()
        delimiter = " "
        self.set = delimiter.join(temp_set_list).strip()

        self.archetype = dict.get("Archetype")
        self.primary_stat = ARMOR_ARCHETYPES.get(self.archetype)[0]
        self.secondary_stat = ARMOR_ARCHETYPES.get(self.archetype)[1]
        self.tertiary_stat = ARMOR_STAT_HASHES.get(int(dict.get("Tertiary Stat")))
        
        if (dict.get("Tuning Stat") is not None and (dict.get("Tuning Stat") != "") and (dict.get("Tuning Stat") != '')):
            self.tuning_stat = ARMOR_STAT_HASHES.get(int(dict.get("Tuning Stat")))
        else:
            self.tuning_stat = None


class Armor_Bucket:
    def __init__(self, armor_list, set, archetype, tertiary_stat, tuning_stat, equippable_class):
        self.set = set
        self.archetype = archetype
        self.tertiary_stat = tertiary_stat
        self.armor_list = armor_list
        self.equippable_class = equippable_class
        self.tuning_stat = tuning_stat


def sort_armor_into_sets(armor_items, params, is_finding_overall_max_buckets):
    buckets = []
    
    if (is_finding_overall_max_buckets is False) and (len(params.sets) > 0):
        sorted_armor_dict = {}
        for set in params.sets:
            sorted_armor_dict.update({ set : []})
        for armor_item in armor_items:
            # check if the armor piece is in the set list AND archetype list
            if (armor_item.set in params.sets) and (armor_item.archetype in (params.archetypes if (params.archetypes is not None) and (len(params.archetypes) != 0) else list(ARMOR_ARCHETYPES.keys()))) and (armor_item.tier >= params.minimum_tier):
                sorted_armor_dict.get(armor_item.set).append(armor_item)
            #now that they're sorted into lists, i need to, for each set
            # sort them into archetypes
        #if params.classes is not None:
        #    if (params.classes)
        for set in sorted_armor_dict.keys():
            returned_buckets = sort_set_into_archetypes(sorted_armor_dict.get(set), params.archetypes if (params.archetypes is not None) and (len(params.archetypes) != 0) else list(ARMOR_ARCHETYPES.keys()), set, is_finding_overall_max_buckets, params.classes if (params.classes is not None) and (len(params.classes) != 0) else EQUIPPABLE_CLASSES)
            buckets.extend(returned_buckets)
    else:
        sorted_armor_list = []
        for armor_item in armor_items:
            # check if the armor piece is in the set list AND archetype list
            if (armor_item.archetype in (params.archetypes if (params.archetypes is not None) and (len(params.archetypes) != 0) else list(ARMOR_ARCHETYPES.keys()))) and (armor_item.tier >= params.minimum_tier):
                sorted_armor_list.append(armor_item)
            #now that they're stored in a list, i need to sort them into archetypes
        returned_buckets = sort_set_into_archetypes(sorted_armor_list, params.archetypes if (params.archetypes is not None) and (len(params.archetypes) != 0) else list(ARMOR_ARCHETYPES.keys()), "None", is_finding_overall_max_buckets, params.classes if (params.classes is not None) and (len(params.classes) != 0) else EQUIPPABLE_CLASSES)
        buckets.extend(returned_buckets) 
    return buckets


def sort_set_into_archetypes(armor_items, wanted_archetypes, set, is_finding_overall_max_buckets, equippable_classes):
    #we're just dealing with one set at a time
    # all of the armor pieces in the list are of the same set
    buckets = []
    sorted_armor_dict = {}
    # for each archetype, create a bucket to store the related armor pieces
    for archetype in wanted_archetypes:
        sorted_armor_dict.update({ archetype : []})
    # for each armor piece, add it to the related archetype bucket
    for armor in armor_items:
        sorted_armor_dict.get(armor.archetype).append(armor)
    # for each archetype bucket, pass its armor items to be sorted into tertiary buckets
    for archetype, items in sorted_armor_dict.items():
        returned_buckets = sort_archetype_into_tertiary_buckets(items, set, archetype, is_finding_overall_max_buckets, equippable_classes)
        buckets.extend(returned_buckets)
    
    return buckets


def sort_archetype_into_tertiary_buckets(armor_items, set, archetype, is_finding_overall_max_buckets, equippable_classes):
    # here, we are only dealing with a single archetype by now.
    # we just need to sort the remaining armor pieces into buckets where 
    # they share the same "tertiary" stat.
    tertiary_stats = ARMOR_ARCHETYPES_TERTIARY_STATS.get(archetype)

    buckets = []

    sorted_armor_dict = {}

    # for each tertiary stat, create a bucket to hold its resepective armors
    for stat in tertiary_stats:
        sorted_armor_dict.update({ stat : [] })
    # for each armor piece, put it in its related tertiary stat bucket
    for armor in armor_items:
        sorted_armor_dict.get(armor.tertiary_stat).append(armor)

    # now we need to pull the ids of the highest stat pieces for each tertiary stat bucket

    # if an armor is tier 5,
    # we need 2 separate paths, both of which add to the same pool.
    # if it's tier 5, we need to sort out the best armor pieces.
    # if it's not, we can go straight to getting the best stats.

    for stat in sorted_armor_dict.keys():
        returned_buckets = sort_tertiary_stats_into_tuning_stat_buckets(sorted_armor_dict.get(stat), set, archetype, stat, equippable_classes, is_finding_overall_max_buckets)
        buckets.extend(returned_buckets)

    
    return buckets


def sort_tertiary_stats_into_tuning_stat_buckets(armor_items, set, archetype, tertiary_stat, equippable_classes, is_finding_overall_max_buckets):
    tier_5_list = []
    low_tier_list = []
    buckets = []
    
    sorted_armor_dict = {}
    for tuning_stat in STAT_LIST:
        sorted_armor_dict.update({ tuning_stat : [] })
    for armor in armor_items:
        # if it's tier 5, but it in the tier 5 list
        # otherwise, put it in the low_tier list
        if armor.tuning_stat is not None:
            tier_5_list.append(armor)
        else:
            low_tier_list.append(armor)
    
    for equippable_class in equippable_classes:
        # for the tier 5 items, now we can sort through the best stats.
        for armor in tier_5_list:
            sorted_armor_dict.get(armor.tuning_stat).append(armor)
            for tuning_stat in sorted_armor_dict.keys():
                if (len(sorted_armor_dict.get(tuning_stat)) > 0):
                    found_bucket = find_max_stat_armor_ids_for_equippable_class(sorted_armor_dict.get(tuning_stat), set, archetype, tertiary_stat, equippable_class, is_finding_overall_max_buckets, tuning_stat)
                    buckets.append(found_bucket)
        #for armor in low_tier_list:
        found_bucket = find_max_stat_armor_ids_for_equippable_class(low_tier_list, set, archetype, tertiary_stat, equippable_class, is_finding_overall_max_buckets, None)
        if found_bucket is not None:
            buckets.append(found_bucket)

    return buckets
        # for the lower tiers, we need to separately sort so tier 5s do not get double-filtered.
#        for armor in low_tier_list:
#            found_bucket = find_max_stat_armor_ids_for_equippable_class()


def find_max_stat_armor_ids_for_equippable_class(armor_items, set, archetype, stat, equippable_class, is_finding_overall_max_buckets, tuning_stat):

    ########################################
    ## PASS 1 : FIND MAX VALUES
    ########################################

    max_stat_helmet = 0
    max_stat_gauntlets = 0
    max_stat_chest = 0
    max_stat_legs = 0
    max_stat_class_item = 0
    pre_max_value_armor_list = []

    for armor in armor_items:
        if (armor.equippable_class == equippable_class):
            # if helmet
            if (armor.slot == "Helmet"):
                if armor.stats.get("Total") >= max_stat_helmet:
                    max_stat_helmet = armor.stats.get("Total")
                    pre_max_value_armor_list.append(armor)
            # if gauntlets
            elif (armor.slot == "Gauntlets"):
                if armor.stats.get("Total") >= max_stat_gauntlets:
                    max_stat_gauntlets = armor.stats.get("Total")
                    pre_max_value_armor_list.append(armor)
            # if chest
            elif (armor.slot == "Chest Armor"):
                if armor.stats.get("Total") >= max_stat_chest:
                    max_stat_chest = armor.stats.get("Total")
                    pre_max_value_armor_list.append(armor)
            # if legs
            elif (armor.slot == "Leg Armor"):
                if armor.stats.get("Total") >= max_stat_legs:
                    max_stat_legs = armor.stats.get("Total")
                    pre_max_value_armor_list.append(armor)
            # if class item
            elif armor.slot in CLASS_ITEM_LIST:
                if armor.stats.get("Total") >= max_stat_class_item:
                    max_stat_class_item = armor.stats.get("Total")
                    pre_max_value_armor_list.append(armor)
            else:
                print("Armor type not found")

    ########################################
    ## PASS 2: FIND ALL MAX VALUES
    ########################################
    max_helmet_list = []
    max_gauntlets_list = []
    max_chest_list = []
    max_legs_list = []
    max_class_item_list = []
    for armor in pre_max_value_armor_list:
        if (armor.slot == "Helmet"):
            if (armor.stats.get("Total") == max_stat_helmet):
                max_helmet_list.append(armor)
        elif (armor.slot == "Gauntlets"):
            if (armor.stats.get("Total") == max_stat_gauntlets):
                max_gauntlets_list.append(armor)
        elif (armor.slot == "Chest Armor"):
            if (armor.stats.get("Total") == max_stat_chest):
                max_chest_list.append(armor)
        elif (armor.slot == "Leg Armor"):
            if (armor.stats.get("Total") == max_stat_legs):
                max_legs_list.append(armor)
        elif (armor.slot in CLASS_ITEM_LIST):
            if (armor.stats.get("Total") == max_stat_class_item):
                max_class_item_list.append(armor)

    # combine all lists together
    max_armor_list = max_helmet_list + max_gauntlets_list + max_chest_list + max_legs_list + max_class_item_list
   
    if len(max_armor_list) != 0:
        if is_finding_overall_max_buckets is False:
            return Armor_Bucket(max_armor_list, set, archetype, stat, tuning_stat, equippable_class)
        else:
            return Armor_Bucket(max_armor_list, "None", archetype, stat, tuning_stat, equippable_class)
