import armor_sorting as armsort
import database_sorting as dbsort
import csv
import os
import json
from dotenv import load_dotenv
load_dotenv()

from flask import Flask, request, jsonify, render_template
import io

app = Flask(__name__)

app.config["MAX_CONTENT_LENGTH"] = 600 * 1024 # 600kb hard cap

# TODO: New tab for usage instructions

def process_csv(file, params):
    # reader = csv.DictReader(io.StringIO(file.decode("utf-8")))
    # armor_items = []
    database = dbsort.read_inventory_from_file(file)
    query = ""
    query_string = dbsort.build_query(database, params, query, "intial")
    # for dict in reader:
    #     if ((int(dict.get("Tier")) > 0) and (dict.get("Rarity") == "Legendary")):
    #         armor_items.append(armsort.Armor(dict)) 
    # buckets = armsort.sort_armor_into_sets(armor_items, params, False)
    # max_buckets = armsort.sort_armor_into_sets(armor_items, params, True)
    # set_output_string_ids = ""
    armor_count = 0
    # for bucket in buckets:
    #     if bucket is not None:
    #         for armor in bucket.armor_list:
    #             set_output_string_ids = set_output_string_ids + f"{'or' if armor_count > 0 else '('} id:{armor.id} "
    #             armor_count += 1
    if armor_count != 0:
        set_output_string_ids += ") \n"
    else:
        set_output_string_ids = "No armor found with selected filters"

    overall_output_string_ids = ""
    # armor_count = 0
    # for bucket in max_buckets:
    #     if bucket is not None:
    #         for armor in bucket.armor_list:
    #             overall_output_string_ids = overall_output_string_ids + f"{'or' if armor_count > 0 else '('} id:{armor.id} "
    #             armor_count += 1
    # if armor_count != 0:
    #     overall_output_string_ids += ")\n"
    # else:
    #     overall_output_string_ids += "No armor found with chosen archetype(s)"

    return set_output_string_ids, overall_output_string_ids


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/process', methods=['POST'])
def process_file():
    file = request.files['file']
    classes = json.loads(request.form.get('class', '[]'))
    archetypes = json.loads(request.form.get('archetype', '[]'))
    sets = json.loads(request.form.get('set', '[]'))
    tier = request.form.get("tier")
    tier_val = int(tier) if tier is not None else 1
    params = armsort.SortingParameters(
        {
            "sets" : sets,
            "archetypes" : archetypes,
            "minimum_tier" : tier_val,
            "classes" : classes
        }
    )

    set_output, overall_output = process_csv(file, params)
    return jsonify({"resultTop": set_output, "resultBottom": overall_output})


if __name__ == "__main__":
    import os
    debug = os.getenv("FLASK_DEBUG", "0") == "1" or os.getenv("DEBUG", "0") == "1"
    port = int(os.getenv("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=debug, use_reloader=debug)
     


