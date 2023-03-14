import json
import os
import re


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
            return place_dict[place_first_part]
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
                    return None
                elif len(refined_matched_places) > 1 and len(set(place_dict[place] for place in refined_matched_places) > 1):
                    return None
                elif is_gcc(place_dict[refined_matched_places[0]]):
                    return place_dict[refined_matched_places[0]]
    return None

def is_gcc(code):
    if re.search("\dg\w{3}|8acte", code):
        return True
    return False

def get_top_gcc_by_num_of_tweet(author_by_gcc_df, n=8):
    gcc_tweet_sum = author_by_gcc_df.sum()
    gcc_tweet_sum_sorted = gcc_tweet_sum.sort_values(ascending=False).head(n)

    print(gcc_tweet_sum_sorted)
    return gcc_tweet_sum_sorted

def get_top_author_by_num_of_tweet(author_by_gcc_df, n=10):
    author_tweet_sum = author_by_gcc_df.T.sum()
    author_tweet_sum_sorted = author_tweet_sum.sort_values(ascending=False).head(n)

    print(author_tweet_sum_sorted)
    return author_tweet_sum_sorted