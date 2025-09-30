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


def build_query(database, is_overall, params):
    # we start with the classes
    # for each class in params
    print("build_query stub")


def read_inventory_from_file(file, params):
    database = duckdb.connect("data.duckdb")

    file.stream.seek(0)
    df = pd.read_csv(file.stream)

    database.register("upload", df)
    # output = database.execute("""
    #     PUT STUFF HERE
    # """).df()

    print("Sorting parameters:")
    print(file)
    print("Hello!")
    # print(io.StringIO(file.decode("utf-8")))
    # ddb.read_csv()
    # ddb.read_csv(io.StringIO(file.decode("utf-8")))
    #if ()

    # relation = ddb.sql(f"""
    #         SELECT Name, Id, Tier, Type,  Rarity, Equippable, Archetype, "Tertiary Stat", "Tuning Stat", "Total (Base)",  FROM 'destiny-armor.csv'
    #         WHERE "Tertiary Stat" IS NOT NULL and Rarity != 'Exotic' and Tier >= \'{TIER}\'
    #             and Equippable = 'Titan'
    #             and (Archetype = \'{ARCHETYPE}\' or Archetype = 'Paragon') 
    #             and "Tertiary Stat" = \'{144602215}\' 
    #             and Name LIKE \'{SET_NAME}%\'
    #         """)
    # #                 
    # #  must run max query for each tertiary "bucket"
    # result = ddb.sql("""
    #         SELECT Id
    #         FROM relation r
    #         WHERE "Total (Base)" = (
    #             SELECT Max("Total (Base)")
    #             FROM relation
    #             WHERE Type = r.Type
    #         )
    #         """
    #                  # maybe under this WHERE is where to put filters?
    # ).fetchall()
    # armor_ids = [("id:" + item[0].strip('"')) for item in result]
    # output = "("
    # for i, id in enumerate(armor_ids):
    #     output += id
    #     if i < (len(armor_ids) - 1):
    #         output += " or "
    # output += ")"
    # print(output)

# build class query
    # build archetype query
        # build tertiary query
            # if is_overall_query = False:
                # build set query
                # fetch
            # else:
                # fetch