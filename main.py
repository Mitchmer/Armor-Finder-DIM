import armor_sorting as armsort
import csv
import os
import json
from dotenv import load_dotenv
load_dotenv()

from flask import Flask, request, jsonify, render_template
import io

app = Flask(__name__)

app.config["MAX_CONTENT_LENGTH"] = 600 * 1024 # 600kb hard cap

# IGNORE THIS FOR NOW
# TODO: Remove ")" from empty output strings.
# TODO: notify user when sorting didn't find anything.
# TODO: New tab for usage instructions
# END IGNORE

def process_csv(file_stream, params):
    reader = csv.DictReader(io.StringIO(file_stream.decode("utf-8")))
    armor_items = []

    for dict in reader:
        if ((int(dict.get("Tier")) > 0) and (dict.get("Rarity") == "Legendary")):
            armor_items.append(armsort.Armor(dict)) 
    buckets = armsort.sort_armor_into_sets(armor_items, params, False)
    max_buckets = armsort.sort_armor_into_sets(armor_items, params, True)
    set_output_string_ids = ""
    armor_count = 0
    for bucket in buckets:
        if bucket is not None:
            for armor in bucket.armor_list:
                set_output_string_ids = set_output_string_ids + f"{'or' if armor_count > 0 else '('} id:{armor.id} "
                armor_count += 1
    set_output_string_ids += ") \n"
    
    overall_output_string_ids = ""
    armor_count = 0
    for bucket in max_buckets:
        if bucket is not None:
            for armor in bucket.armor_list:
                overall_output_string_ids = overall_output_string_ids + f"{'or' if armor_count > 0 else '('} id:{armor.id} "
                armor_count += 1
    overall_output_string_ids += ")\n"

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
    print(params.sets)
    print(params.archetypes)
    print(params.minimum_tier)
    print(params.classes)

    set_output, overall_output = process_csv(file.read(), params)
    return jsonify({"resultTop": set_output, "resultBottom": overall_output})


if __name__ == "__main__":
    import os
    debug = os.getenv("FLASK_DEBUG", "0") == "1" or os.getenv("DEBUG", "0") == "1"
    port = int(os.getenv("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=debug, use_reloader=debug)
     


