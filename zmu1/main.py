import ijson
import json
import argparse
import os.path
import re
import numpy as np
import util

STATE_ABB_DICT = {
    "new south wales": "nsw",
    "victoria": "vic",
    "queensland": "qld",
    "south australia": "sau",
    "western australia": "wau",
    "tasmania": "tas",
    "northern territory":"nte"
}

GCC_DICT = { "sydney":"1gsyd", "melbourne": "2gmel","brisbane":"3gbri", "adelaide":"4gade", "perth":"5gper", "hobart":"6ghob","darwin":"7gdar", "canberra":"8acte"}

def top_ten_id(twitter):
    author_id_dict = {}

    for i in range(len(twitter)):
        cur_author_id = twitter[i]['data'].get("author_id")

        if cur_author_id in author_id_dict:
            temp = author_id_dict.get(cur_author_id) + 1
            author_id_dict.update({cur_author_id: temp})
        else:
            author_id_dict.update({cur_author_id: 1})

    # print(twitter_dict)
    id_dict_sorted = sorted(author_id_dict.items(), key=lambda x: x[1], reverse=True)

    for j in range(10):
        print(id_dict_sorted[j])





# def top_places(twitter, place_code_lst):
#     place_code_dict = {}

#     for j in range(len(twitter)):
#         includes_data = twitter[j]['includes'].get("places")[0]
#         place_name = includes_data.get("full_name").lower()

#         index = get_index(place_name)
#         if index < 0:
#             continue

#         for k in range(len(place_code_lst[index])):
#             for (key, value) in place_code_lst[index][k].items():
#                 temp_name = key
#                 temp_code = value

#             if place_name.find(temp_name) != -1:
#                 if temp_code in place_code_dict.keys():
#                     temp = place_code_dict.get(temp_code) + 1
#                     place_code_dict.update({temp_code: temp})
#                 else:
#                     place_code_dict.update({temp_code: 1})

#     # print(place_code_dict)
#     name_dict_sorted = sorted(place_code_dict.items(), key=lambda x: x[1], reverse=True)

#     for l in range(7):
#         print(name_dict_sorted[l])


def get_gcc_code(t_place, place_dict:dict):
    # if the location is in two parts
    if t_place.find(",") != -1:
        t_place_first, t_place_second = t_place.split(",", 1)
        # All locations that end with Australia are ambiguous. e.g. Victoria, Australia;  South Australia, Australia
        if t_place_second == "australia":
            return None
        if t_place_first in GCC_DICT.keys():
            return GCC_DICT[t_place_first]
        else:
            return check_against_places(t_place_first, place_dict, t_place_second)
    # if the location is a single word
    else:
        # If it's Australia or States, return None, as they are ambiguous
        if t_place == "australia" or t_place in STATE_ABB_DICT.keys():
                return None
        return check_against_places(t_place, place_dict)
    
def check_against_places(place_first_part, place_dict, place_second_part=None):
    # Get all places that contains the current location - O(n)
    places_matched = [place for place in place_dict.keys() if place_first_part in place ]
    if len(places_matched) == 1:
        code = place_dict[places_matched[0]]
        if is_gcc(code):
            return code
    # if there are multiple results found
    elif len(places_matched) > 1:
        # if there is an exact match
        if place_first_part in places_matched:
            return place_dict[place_first_part],
        # get all returned gcc in a set
        gcc_variances = set(place_dict[place] for place in places_matched)
        # if we only have one kind of gcc code and it's one of the gcc
        if len(gcc_variances) == 1 and is_gcc(list(gcc_variances)[0]):
            return list(gcc_variances)[0]
        elif len(gcc_variances) > 1:
            state_abb = STATE_ABB_DICT.get(place_second_part.strip()) 
            if state_abb:
                refined_matched_places = [place for place in places_matched if re.search(f"{place_first_part}.*\({state_abb}\).*", place)]
                if len(refined_matched_places) == 0:
                    return None,
                elif len(refined_matched_places) > 1 and len(set(place_dict[place] for place in refined_matched_places) > 1):
                    return None
                elif is_gcc(place_dict[refined_matched_places[0]]):
                    return place_dict[refined_matched_places[0]]
    return None

def is_gcc(code):
    if re.search("\dg\w{3}|8acte", code):
        return True
    return False

def update_dict(id_places_dict, cur_author_id, code):
    cur = id_places_dict.get(cur_author_id)
    if code in cur.keys():
        temp = cur.get(code) + 1
        cur.update({code: temp})
    else:
        cur.update({code: 1})

def top_id_places(twitter_data_point, code_by_places, id_places_dict):
    cur_author_id = twitter_data_point['data'].get("author_id")

    if cur_author_id not in id_places_dict.keys():
        id_places_dict.update({cur_author_id: {}})

    t_place_name = twitter_data_point['includes'].get("places")[0].get("full_name").lower()

    code = get_gcc_code(t_place_name, code_by_places)
    if code:
        update_dict(id_places_dict, cur_author_id, code)
            


def main(data_path, location_path):
    # Get gcc code by locations. data looks like: [{"abb": "1gsyd"}, ...]
    code_by_places = util.process_location_file(location_path)

    id_places_dict = {}
    # with open(os.path.dirname(__file__) + '/../test_3.json', 'r', encoding='UTF-8') as twitter_file:
    with open(os.path.dirname(__file__) + data_path, 'r', encoding='UTF-8') as twitter_file:
        twitter = ijson.items(twitter_file, 'item')

        # TODO: implement MPI logic 
        # We can get the index of the current json data point   - index
        # we have the rank of the current processor   -  comm_rank
        # we have the number of processors   -    comm_size
        # if the remainder r, where r = index % comm_size, is equal to the comm_rank, the current process should process it, otherwise, ignore it.
        for index, twitter_data_point in enumerate(twitter):
            top_id_places(twitter_data_point, code_by_places, id_places_dict)

        id_places_sorted = sorted(id_places_dict.items(), key=lambda x: len(x[1]), reverse=True)

        print(id_places_sorted)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Processing Twitter data focusing on the geolocation attribute')
    # Pass in the location file path
    parser.add_argument('--location', type=str, help='File path to the location file. e.g. sal.json')
    # Pass in the twitter data file path
    parser.add_argument('--data', type=str, help='File path to the twitter data file')
    args = parser.parse_args()

    location_path = args.location
    data_path = args.data

    main(data_path, location_path)

    
