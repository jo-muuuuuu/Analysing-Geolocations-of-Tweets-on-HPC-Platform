import json
import os.path
import re
import numpy as np
from collections import defaultdict

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


def get_code_by_places(sal):
    code_by_place_dict = {}

    for (place, value) in sal.items():
        code = value.get("gcc")

        # commented out because considering this scenario:
        # picton A -> 1gsyd, picton B -> 1rnsw
        # if the twitter location only says 'picton' and we filter out the rural gcc, i.e. 1rnsw, we won't be able to know there is another choice that may cause ambiguity.
        # This hence lead to overconfidence in the logic and results in 1gsyd, where we in fact can't really say for sure
        # gcc_found = re.search("\dg\w{3}|8acte", code)

        # if gcc_found:
        code_by_place_dict[place] = code

    return code_by_place_dict


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

def top_id_places(twitter, code_by_places):
    id_places_dict = {}

    for j in range(len(twitter)):
        cur_author_id = twitter[j]['data'].get("author_id")

        if cur_author_id not in id_places_dict.keys():
            id_places_dict.update({cur_author_id: {}})

        includes_data = twitter[j]['includes'].get("places")[0]
        place_name = includes_data.get("full_name").lower()

        index = get_index(place_name)

        for k in range(len(place_code_lst[index])):
            for (key, value) in place_code_lst[index][k].items():
                temp_name = key
                temp_code = value

            if place_name.find(temp_name) != -1:
                cur = id_places_dict.get(cur_author_id)
                if temp_code in cur.keys():
                    temp = cur.get(temp_code) + 1
                    cur.update({temp_code: temp})
                else:
                    cur.update({temp_code: 1})

    id_places_sorted = sorted(id_places_dict.items(), key=lambda x: len(x[1]), reverse=True)

    # for l in range(10):
    #     print(id_places_sorted[l])

    print(id_places_sorted)

    # print(id_places_dict)

    # No Twitter user tweet in more than 1 place in twitter-data-small.json
    # for (key, value) in id_places_dict.items():
    #     if len(value) > 1:
    #         print("Found")


if __name__ == '__main__':
    # with open(os.path.dirname(__file__) + '/../test_3.json', 'r', encoding='UTF-8') as twitter_file:
    with open(os.path.dirname(__file__) + '/twitter-data-small.json', 'r', encoding='UTF-8') as twitter_file:
        twitter = json.load(twitter_file)

    sal_file = open('sal.json')
    sal = json.load(sal_file)

    code_by_places = get_code_by_places(sal)
    # print(place_code_lst)

    # Top 10 Author IDs
    # top_ten_id(twitter)
    # print("\n-------------------------------------------\n")

    # Places with the most twitters
    # top_places(twitter, place_code_lst)
    # print("\n-------------------------------------------\n")

    # IDs with the most places
    top_id_places(twitter, place_code_lst)
