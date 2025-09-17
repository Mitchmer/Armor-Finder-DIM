ARMOR_FILEPATH = "destiny-armor.csv"
OUTPUT_FILEPATH = "destiny-finder-DIM-output.txt"

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

temp_archetype_tertiaries = {}
temp_tertiary = []
for archetype, stats in ARMOR_ARCHETYPES.items():
    temp_archetype_tertiaries.update({ archetype : [] })
    for stat in STAT_LIST:
        if stat not in stats:
            temp_archetype_tertiaries.get(archetype).append(stat)
ARMOR_ARCHETYPES_TERTIARY_STATS = temp_archetype_tertiaries

ARMOR_STAT_HASHES = {
    392767087 : "Health",
    4244567218 : "Melee",
    1735777505 : "Grenade",
    144602215 : "Super",
    1943323491 : "Class",
    2996146975 : "Weapons"
}

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

#TODO : check against no sets selected

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
        #primary_value = 0
        #secondary_value = 0
        #tertiary_value = 0
        #for key, value in self.stats.items():
        #    if (key != "Total"):
        #        if value > primary_value:
        #            self.tertiary_stat, tertiary_value = self.secondary_stat, secondary_value
        #            self.secondary_stat, secondary_value = self.primary_stat, primary_value
        #            self.primary_stat, primary_value = key, value
        #        elif value > secondary_value:
        #            self.tertiary_stat, tertiary_value = self.secondary_stat, secondary_value
        #            self.secondary_stat, secondary_value = key, value
        #        elif value > tertiary_value:
        #            self.tertiary_stat, tertiary_value = key, value

        #archetype_pair = [self.primary_stat, self.secondary_stat]
        #for archetype, stats_pair in ARMOR_ARCHETYPES.items():
        #    if archetype_pair == stats_pair:
        #        self.archetype = archetype


class Armor_Bucket:
    def __init__(self, armor_list, set, archetype, tertiary_stat, equippable_class):
        self.set = set
        self.archetype = archetype
        self.tertiary_stat = tertiary_stat
        self.armor_list = armor_list
        self.equippable_class = equippable_class


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
    for archetype in wanted_archetypes:
        sorted_armor_dict.update({ archetype : []})
    for armor in armor_items:
        sorted_armor_dict.get(armor.archetype).append(armor)
    for archetype in sorted_armor_dict.keys():
        returned_buckets = sort_archetype_into_tertiary_buckets(sorted_armor_dict.get(archetype), set, archetype, is_finding_overall_max_buckets, equippable_classes)
        buckets.extend(returned_buckets)
    
    return buckets


def sort_archetype_into_tertiary_buckets(armor_items, set, archetype, is_finding_overall_max_buckets, equippable_classes):
    # here, we are only dealing with a single archetype by now.
    # we just need to sort the remaining armor pieces into buckets where 
    # they share the same "tertiary" stat.
    tertiary_stats = ARMOR_ARCHETYPES_TERTIARY_STATS.get(archetype)

    sorted_armor_dict = {}
    for stat in tertiary_stats:
        sorted_armor_dict.update({ stat : [] })
    for armor in armor_items:
        sorted_armor_dict.get(armor.tertiary_stat).append(armor)

    # now we need to pull the ids of the highest stat pieces for each tertiary
    # stat bucket

        # TODO: If tuning slot, we need one more step.

    buckets = []
    for stat in sorted_armor_dict.keys():
        for equippable_class in equippable_classes:
            found_bucket = find_max_tertiary_stat_armor_ids_for_equippable_class(sorted_armor_dict.get(stat), set, archetype, stat, equippable_class, is_finding_overall_max_buckets)
            buckets.append(found_bucket)
    
    return buckets


def find_max_tertiary_stat_armor_ids_for_equippable_class(armor_items, set, archetype, stat, equippable_class, is_finding_overall_max_buckets):

    # need to check if equal total, then check primary. if primary equal, then check secondary. if secondary equal, check tertiary.
    # if tertiary equal, then leave it alone

    ########################################
    ## PASS 1 : FIND MAX VALUES
    ########################################
    # TODO: pass "found" armor pieces to new
    #   list for later efficiency
    #   Not super imperative for only a
    #   couple hundred items at most.
    max_stat_helmet = 0
    max_stat_gauntlets = 0
    max_stat_chest = 0
    max_stat_legs = 0
    max_stat_class_item = 0

    for armor in armor_items:
        # if helmet
        if (armor.slot == "Helmet"):
            if armor.stats.get("Total") > max_stat_helmet:
                max_stat_helmet = armor.stats.get("Total")
        # if gauntlets
        elif (armor.slot == "Gauntlets"):
            if armor.stats.get("Total") > max_stat_gauntlets:
                max_stat_gauntlets = armor.stats.get("Total")
        # if chest
        elif (armor.slot == "Chest Armor"):
            if armor.stats.get("Total") > max_stat_chest:
                max_stat_chest = armor.stats.get("Total")
        # if legs
        elif (armor.slot == "Leg Armor"):
            if armor.stats.get("Total") > max_stat_legs:
                max_stat_legs = armor.stats.get("Total")
        # if class item
        elif armor.slot in CLASS_ITEM_LIST:
            if armor.stats.get("Total") > max_stat_class_item:
                max_stat_class_item = armor.stats.get("Total")
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
    for armor in armor_items:
        if (armor.slot == "Helmet"):
            if (armor.stats.get("Total") == max_stat_helmet):
                max_helmet_list.append(armor)
        elif (armor.slot == "Guantlets"):
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

    #for armor_item in armor_items:
    #    if (armor_item.equippable_class == equippable_class):
    #        #print(armor_item.name)
    #        if (armor_item.slot == "Helmet"):
    #            # if the total is greater than
    #            if max_stat_helmet == None or armor_item.stats.get("Total") > max_stat_helmet.stats.get("Total"):
    #                max_stat_helmet = armor_item
    #            elif armor_item.stats.get("Total") == max_stat_helmet.stats.get("Total"):
    #                #we have a tie, we need to break it. check primary
    #                if armor_item.stats.get(armor_item.primary_stat) > max_stat_helmet.stats.get(max_stat_helmet.primary_stat):
    #                    max_stat_helmet = armor_item
    #                elif armor_item.stats.get(armor_item.primary_stat) == max_stat_helmet.stats.get(max_stat_helmet.primary_stat):
    #                    #we have a tie, we need to break it. check secondary
    #                    if armor_item.stats.get(armor_item.secondary_stat) > max_stat_helmet.stats.get(max_stat_helmet.secondary_stat):
    #                        max_stat_helmet = armor_item
    #                    elif armor_item.stats.get(armor_item.secondary_stat) == max_stat_helmet.stats.get(max_stat_helmet.secondary_stat):
    #                        #we have a tie, we need to break it. check tertiary
    #                        if armor_item.stats.get(armor_item.tertiary_stat) > max_stat_helmet.stats.get(max_stat_helmet.tertiary_stat):
    #                            max_stat_helmet = armor_item
    #            #print("Found helmet")
    #        elif (armor_item.slot == "Gauntlets"):
    #            if max_stat_gauntlets == None or armor_item.stats.get("Total") > max_stat_gauntlets.stats.get("Total"):
    #                max_stat_gauntlets = armor_item
    #            elif armor_item.stats.get("Total") == max_stat_gauntlets.stats.get("Total"):
    #                #we have a tie, we need to break it. check primary
    #                if armor_item.stats.get(armor_item.primary_stat) > max_stat_gauntlets.stats.get(max_stat_gauntlets.primary_stat):
    #                    max_stat_gauntlets = armor_item
    #                elif armor_item.stats.get(armor_item.primary_stat) == max_stat_gauntlets.stats.get(max_stat_gauntlets.primary_stat):
    #                    #we have a tie, we need to break it. check secondary
    #                    if armor_item.stats.get(armor_item.secondary_stat) > max_stat_gauntlets.stats.get(max_stat_gauntlets.secondary_stat):
    #                        max_stat_gauntlets = armor_item
    #                    elif armor_item.stats.get(armor_item.secondary_stat) == max_stat_gauntlets.stats.get(max_stat_gauntlets.secondary_stat):
    #                        #we have a tie, we need to break it. check tertiary
    #                        if armor_item.stats.get(armor_item.tertiary_stat) > max_stat_gauntlets.stats.get(max_stat_gauntlets.tertiary_stat):
    #                            max_stat_gauntlets = armor_item
    #            #print("Found helmet")
    #        elif (armor_item.slot == "Chest Armor"):
    #            if max_stat_chest == None or armor_item.stats.get("Total") > max_stat_chest.stats.get("Total"):
    #                max_stat_chest = armor_item
    #            elif armor_item.stats.get("Total") == max_stat_chest.stats.get("Total"):
    #                #we have a tie, we need to break it. check primary
    #                if armor_item.stats.get(armor_item.primary_stat) > max_stat_chest.stats.get(max_stat_chest.primary_stat):
    #                    max_stat_chest = armor_item
    #                elif armor_item.stats.get(armor_item.primary_stat) == max_stat_chest.stats.get(max_stat_chest.primary_stat):
    #                    #we have a tie, we need to break it. check secondary
    #                    if armor_item.stats.get(armor_item.secondary_stat) > max_stat_chest.stats.get(max_stat_chest.secondary_stat):
    #                        max_stat_chest = armor_item
    #                    elif armor_item.stats.get(armor_item.secondary_stat) == max_stat_chest.stats.get(max_stat_chest.secondary_stat):
    #                        #we have a tie, we need to break it. check tertiary
    #                        if armor_item.stats.get(armor_item.tertiary_stat) > max_stat_chest.stats.get(max_stat_chest.tertiary_stat):
    #                            max_stat_chest = armor_item
    #            #print("Found chest armor")
    #        elif (armor_item.slot == "Leg Armor"):
    #            if max_stat_legs == None or armor_item.stats.get("Total") > max_stat_legs.stats.get("Total"):
    #                max_stat_legs = armor_item
    #            elif armor_item.stats.get("Total") == max_stat_legs.stats.get("Total"):
    #                #we have a tie, we need to break it. check primary
    #                if armor_item.stats.get(armor_item.primary_stat) > max_stat_legs.stats.get(max_stat_legs.primary_stat):
    #                    max_stat_legs = armor_item
    #                elif armor_item.stats.get(armor_item.primary_stat) == max_stat_legs.stats.get(max_stat_legs.primary_stat):
    #                    #we have a tie, we need to break it. check secondary
    #                    if armor_item.stats.get(armor_item.secondary_stat) > max_stat_legs.stats.get(max_stat_legs.secondary_stat):
    #                        max_stat_legs = armor_item
    #                    elif armor_item.stats.get(armor_item.secondary_stat) == max_stat_legs.stats.get(max_stat_legs.secondary_stat):
    #                        #we have a tie, we need to break it. check tertiary
    #                        if armor_item.stats.get(armor_item.tertiary_stat) > max_stat_legs.stats.get(max_stat_legs.tertiary_stat):
    #                            max_stat_legs = armor_item
    #            #print("Found leg armor")
    #        elif armor_item.slot in CLASS_ITEM_LIST:
    #            if max_stat_class_item == None or armor_item.stats.get("Total") > max_stat_class_item.stats.get("Total"):
    #                max_stat_class_item = armor_item
    #            elif armor_item.stats.get("Total") == max_stat_class_item.stats.get("Total"):
    #                #we have a tie, we need to break it. check primary
    #                if armor_item.stats.get(armor_item.primary_stat) > max_stat_class_item.stats.get(max_stat_class_item.primary_stat):
    #                    max_stat_class_item = armor_item
    #                elif armor_item.stats.get(armor_item.primary_stat) == max_stat_class_item.stats.get(max_stat_class_item.primary_stat):
    #                    #we have a tie, we need to break it. check secondary
    #                    if armor_item.stats.get(armor_item.secondary_stat) > max_stat_class_item.stats.get(max_stat_class_item.secondary_stat):
    #                        max_stat_class_item = armor_item
    #                    elif armor_item.stats.get(armor_item.secondary_stat) == max_stat_class_item.stats.get(max_stat_class_item.secondary_stat):
    #                        #we have a tie, we need to break it. check tertiary
    #                        if armor_item.stats.get(armor_item.tertiary_stat) > max_stat_class_item.stats.get(max_stat_class_item.tertiary_stat):
    #                            max_stat_class_item = armor_item
    #            #print("Found class item")
    #        else:
    #            print("Error: armor slot not found")

    #if max_stat_helmet is not None:
    #    #print("or id:" + str(max_stat_helmet.id) + " ")
    #    max_armor_list.append(max_stat_helmet)
    #if max_stat_gauntlets is not None:
    #    #print(" or id:" + str(max_stat_gauntlets.id) + " ")
    #    max_armor_list.append(max_stat_gauntlets)
    #if max_stat_chest is not None:
    #    #print(" or id:" + str(max_stat_chest.id) + " ")
    #    max_armor_list.append(max_stat_chest)
    #if max_stat_legs is not None:
    #    #print(" or id:" + str(max_stat_legs.id) + " ")
    #    max_armor_list.append(max_stat_legs)
    #if max_stat_class_item is not None:
    #    #print(" or id:" + str(max_stat_class_item.id) + " ")
    #    max_armor_list.append(max_stat_class_item)
   
    if len(max_armor_list) != 0:
        if is_finding_overall_max_buckets is False:
            return Armor_Bucket(max_armor_list, set, archetype, stat, equippable_class)
        else:
            return Armor_Bucket(max_armor_list, "None", archetype, stat, equippable_class)
