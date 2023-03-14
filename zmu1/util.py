import json
import os

def process_location_file(location_path):
    with open(os.path.dirname(__file__) + location_path, 'r', encoding='UTF-8') as location_file:
        sal = json.load(location_file)

    return get_code_by_places(sal)

def get_code_by_places(sal):
    code_by_place_dict = {}

    for (place, value) in sal.items():
        code = value.get("gcc")

        code_by_place_dict[place] = code

    return code_by_place_dict