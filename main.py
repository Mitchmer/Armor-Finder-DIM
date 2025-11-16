import armor_sorting as armsort
import pandas as pd
import re
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
    pattern = r"(" + "|".join(map(re.escape, params.sets)) + r")"

    set_inventory = pd.read_csv(file, sep=',', header=0).get(['Name', 'Id', 'Type', 'Rarity', 'Tier', 'Equippable', 'Archetype', 'Tertiary Stat', 'Tuning Stat', 'Total (Base)'])
    overall_inventory = set_inventory.copy()
    groups = ['Type', 'Equippable', 'Archetype', 'Tertiary Stat', 'Tuning Stat']
    overall_ids_output, overall_dupes_ids_output = armsort.get_max_ids(overall_inventory, groups, params)

    groups.insert(0, 'Name')
    names = set_inventory['Name'].str.extract(pattern, expand=False)
    set_inventory.loc[:, 'Name'] = names
    set_inventory = set_inventory[set_inventory['Name'].notna()]
    set_ids_output, set_dupes_ids_output = armsort.get_max_ids(set_inventory, groups, params)
    
    return set_ids_output, set_dupes_ids_output, overall_ids_output, overall_dupes_ids_output


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

    set_output, set_dupes_output, overall_output, overall_dupes_output = process_csv(file, params)
    return jsonify({"resultTop": set_output, "resultTopDupes": set_dupes_output, "resultBottom": overall_output, "resultBottomDupes": overall_dupes_output})


if __name__ == "__main__":
    import os
    debug = os.getenv("FLASK_DEBUG", "0") == "1" or os.getenv("DEBUG", "0") == "1"
    port = int(os.getenv("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=debug, use_reloader=debug)
