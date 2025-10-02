import duckdb as ddb
from flask import request
import duckdb, pandas as pd
import armor_sorting as armsort

import io
ARCHETYPE = 'Gunner'
TERTIARY_STAT = 1943323491
ARMOR_STAT_HASHES = {
    392767087 : "Health",
    4244567218 : "Melee",
    1735777505 : "Grenade",
    144602215 : "Super",
    1943323491 : "Class",
    2996146975 : "Weapons"
}
TIER = 3
SET_NAME = "Techsec"


def build_query(database, params):
    # we start with the classes
    # for each class in params
    #print("Sorting parameters:")
    #print(params.classes)
    #print(params.archetypes)
    #print(params.sets)
    #print(params.minimum_tier)
    max_set_armor_ids = []
    max_overall_armor_ids = []
    for equippable_class in params.classes:
        for set in params.sets:
            for archetype in params.archetypes:
                for tertiary in armsort.ARMOR_ARCHETYPES_TERTIARY_STATS.get(archetype):
                    found_set_tier_5 = False
                    found_overall_tier_5 = False

                    for tuning, hash in armsort.ARMOR_STAT_HASHES.items():
                        overall_query_string = ("""
                            SELECT Name, Id, Tier, Type,  Rarity, Equippable, Archetype, "Tertiary Stat", "Tuning Stat", "Total (Base)",  FROM 'upload'
                            WHERE "Tertiary Stat" IS NOT NULL and Rarity != 'Exotic'
                        """)
                        overall_query_string += f""" 
                            and Tier >= \'{params.minimum_tier}\' 
                            and Equippable = \'{equippable_class}\'
                            and Archetype = \'{archetype}\'
                            and "Tertiary Stat" = \'{tertiary}\'
                            and "Tuning Stat" = \'{hash}\'
                        """
                        relation = database.execute(overall_query_string).df()
                        result = database.execute("""
                            SELECT Id
                            FROM relation r
                            WHERE "Total (Base)" = (
                                SELECT Max("Total (Base)")
                                FROM relation
                                WHERE Type = r.Type
                            )
                        """).fetchall()
                        overall_armor_ids = [("id:" + item[0].strip('"')) for item in result]
                        max_overall_armor_ids.extend(overall_armor_ids)

                        set_query_string = overall_query_string + f" and Name LIKE \'{set}%\'"
                        relation = database.execute(set_query_string).df()
                        result = database.execute("""
                            SELECT Id
                            FROM relation r
                            WHERE "Total (Base)" = (
                                SELECT Max("Total (Base)")
                                FROM relation
                                WHERE Type = r.Type
                            )
                        """).fetchall()
                        set_armor_ids = [("id:" + item[0].strip('"')) for item in result]
                        max_set_armor_ids.extend(set_armor_ids)
                        if (len(overall_armor_ids) > 0):
                            found_overall_tier_5 = True
                        if (len(set_armor_ids) > 0):
                            found_set_tier_5 = True

                    # TODO: currently pulls a duplicate sub-Tier 5 armor if a Tier 5 piece is found for any particular slot
                    overall_query_string = ("""
                            SELECT Name, Id, Tier, Type,  Rarity, Equippable, Archetype, "Tertiary Stat", "Tuning Stat", "Total (Base)",  FROM 'upload'
                            WHERE "Tertiary Stat" IS NOT NULL and Rarity != 'Exotic'
                        """)
                    overall_query_string += f""" 
                        and Tier >= \'{params.minimum_tier}\' 
                        and Equippable = \'{equippable_class}\'
                        and Archetype = \'{archetype}\'
                        and "Tertiary Stat" = \'{tertiary}\'
                        and "Tuning Stat" IS NULL
                    """
                    
                    relation = database.execute(overall_query_string).df()
                    result = database.execute("""
                        SELECT Id
                        FROM relation r
                        WHERE "Total (Base)" = (
                            SELECT Max("Total (Base)")
                            FROM relation
                            WHERE Type = r.Type
                        )
                    """).fetchall()
                    armor_ids = [("id:" + item[0].strip('"')) for item in result]
                    max_overall_armor_ids.extend(armor_ids)

                    set_query_string = overall_query_string + f" and Name LIKE \'{set}%\'"
                    relation = database.execute(set_query_string).df()
                    result = database.execute("""
                        SELECT Id
                        FROM relation r
                        WHERE "Total (Base)" = (
                            SELECT Max("Total (Base)")
                            FROM relation
                            WHERE Type = r.Type
                        )
                    """).fetchall()
                    armor_ids = [("id:" + item[0].strip('"')) for item in result]
                    max_set_armor_ids.extend(armor_ids)

    max_overall_output = "("
    for i, id in enumerate(max_overall_armor_ids):
        max_overall_output += id
        if i < (len(max_overall_armor_ids) - 1):
            max_overall_output += " or "
    max_overall_output += ")"
    #print(max_overall_output)
    
    max_set_output = "("
    for i, id in enumerate(max_set_armor_ids):
        max_set_output += id
        if i < (len(max_set_armor_ids) - 1):
            max_set_output += " or "
    max_set_output += ")"
    #print(max_set_output)
    return max_set_output, max_overall_output


def read_inventory_from_file(file):
    database = duckdb.connect("data.duckdb")
    file.stream.seek(0)
    df = pd.read_csv(file.stream)
    database.register("upload", df)
    return database
