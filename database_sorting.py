import duckdb as ddb
from flask import request
import duckdb, pandas as pd

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


def build_query(database, params, query_string, mode):
    # we start with the classes
    # for each class in params
    print("Sorting parameters:")
    print(params.classes)
    print(params.archetypes)
    print(params.sets)
    print(params.minimum_tier)
    overall_query_string = ""
    if (mode == "intial"):    
        query_string += ("""
            SELECT Name, Id, Tier, Type,  Rarity, Equippable, Archetype, "Tertiary Stat", "Tuning Stat", "Total (Base)",  FROM 'upload'
            WHERE "Tertiary Stat" IS NOT NULL and Rarity != 'Exotic'
        """)
        query_string += f" and Tier >= \'{params.minimum_tier}\' and ( "
        build_query(database, params, query_string, "class")
    elif (mode == "class"):
        for equippable_class in params.classes:
            build_query(database, params, query_string, "archetype")
    elif (mode == "archetype"):
        overall_query_string = query_string
        for archetype in params.archetypes:
            build_query(database, params, overall_query_string, "tertiary")
            build_query(database, params, query_string, "set")
    elif (mode == "set"):
        for set in params.sets:
            build_query(database, params, overall_query_string, "tertiary")
    elif (mode == "tertiary"):
        # build tertiary
        # return query string
        print("tertiary query stub")
    else:
        print("Tuning stub")

        

    relation = database.execute(f"""
            SELECT Name, Id, Tier, Type,  Rarity, Equippable, Archetype, "Tertiary Stat", "Tuning Stat", "Total (Base)",  FROM 'upload'
            WHERE "Tertiary Stat" IS NOT NULL and Rarity != 'Exotic' and Tier >= \'{TIER}\'
                and Equippable = 'Titan'
                and (Archetype = \'{ARCHETYPE}\' or Archetype = 'Paragon') 
                and "Tertiary Stat" = \'{144602215}\' 
                and Name LIKE \'{SET_NAME}%\'
            """).df()
    #                 
    #  must run max query for each tertiary "bucket"
    result = database.execute("""
            SELECT Id
            FROM relation r
            WHERE "Total (Base)" = (
                SELECT Max("Total (Base)")
                FROM relation
                WHERE Type = r.Type
            )
            """
                    # maybe under this WHERE is where to put filters?
    ).fetchall()
    armor_ids = [("id:" + item[0].strip('"')) for item in result]
    output = "("
    for i, id in enumerate(armor_ids):
        output += id
        if i < (len(armor_ids) - 1):
            output += " or "
    output += ")"
    print(output)

    # build class query
        # build archetype query
            # build tertiary query
                # if is_overall_query = False:
                    # build set query
                    # fetch
                # else:
                    # fetch


def read_inventory_from_file(file):
    database = duckdb.connect("data.duckdb")
    file.stream.seek(0)
    df = pd.read_csv(file.stream)
    database.register("upload", df)
    return database
