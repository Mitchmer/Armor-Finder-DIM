import armor_sorting as armsort
import csv
import os
import json

from flask import Flask, request, jsonify, render_template
import io

app = Flask(__name__)

# TODO: archetypes and sets should be on a single rows when in mobile
# TODO: New tab for usage instructions

def process_csv(file_stream, params):
    # Replace this with your existing logic
    reader = csv.DictReader(io.StringIO(file_stream.decode("utf-8")))
    #rows = list(reader)
    # do your sorting/filtering here with sort_params
    armor_items = []
    #if os.path.exists(armsort.ARMOR_FILEPATH):
    #    with open(armsort.ARMOR_FILEPATH, newline='') as csvfile:
    #        reader = csv.DictReader(csvfile)

    #        for dict in reader:
    #            if ((int(dict.get("Tier")) > 0) and (dict.get("Rarity") == "Legendary")):
    #                armor_items.append(armsort.Armor(dict)) 

    for dict in reader:
        if ((int(dict.get("Tier")) > 0) and (dict.get("Rarity") == "Legendary")):
            armor_items.append(armsort.Armor(dict)) 
    buckets = armsort.sort_armor_into_sets(armor_items, params, False)
    max_buckets = armsort.sort_armor_into_sets(armor_items, params, True)
    set_output_string_ids = ""
    #with open(armsort.OUTPUT_FILEPATH, "w") as f:
    armor_count = 0
    for bucket in buckets:
        if bucket is not None:
            for armor in bucket.armor_list:
                #f.write(f"{'or' if armor_count > 0 else '('} id:{armor.id} ")
                set_output_string_ids = set_output_string_ids + f"{'or' if armor_count > 0 else '('} id:{armor.id} "
                armor_count += 1
        #f.write(")\n")
    set_output_string_ids += ") \n"
    
    overall_output_string_ids = ""
    armor_count = 0
    for bucket in max_buckets:
        if bucket is not None:
            for armor in bucket.armor_list:
                #f.write(f"{'or' if armor_count > 0 else '('} id:{armor.id} ")
                overall_output_string_ids = overall_output_string_ids + f"{'or' if armor_count > 0 else '('} id:{armor.id} "
                armor_count += 1
        #f.write(")\n")
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
    tier = request.form.get("tier")  # "1".."5" or None
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

    # your processing...
    set_output, overall_output = process_csv(file.read(), params)
    return jsonify({"resultTop": set_output, "resultBottom": overall_output})


    #return jsonify({"result": output})


#def main():
#    process_file()
    

if __name__ == "__main__":
    app.run(debug=True)
    #main()        


