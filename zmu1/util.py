import json
import os
import re

AMBIGUOUS_REASON = "AMBIGUOUS"

STATE_ABB_DICT = {
    "new south wales": "nsw",
    "victoria": "vic",
    "queensland": "qld",
    "south australia": "sa",
    "western australia": "wa",
    "tasmania": "tas",
    "northern territory": "nt"
}

GCC_DICT = {"sydney": "1gsyd", "melbourne": "2gmel", "brisbane": "3gbri", "adelaide": "4gade", "perth": "5gper",
            "hobart": "6ghob", "darwin": "7gdar", "canberra": "8acte"}


def process_location_file(location_path):
    """
    Open sal.json and pass it to the next function to get gcc codes
    :param location_path: sal.json, which contains the gcc codes
    :return: Another function that extracts the gcc code
    """

    with open(os.path.dirname(__file__) + location_path, 'r', encoding='UTF-8') as location_file:
        sal = json.load(location_file)

    return get_code_by_places(sal)


def get_code_by_places(sal):
    """
    Extract all the gcc codes and save into a dict
    :param sal: place information in json format
    :return: gcc code (type: dict)
    """
    code_by_place_dict = {}

    for (place, value) in sal.items():
        code = value.get("gcc")

        code_by_place_dict[place] = code

    return code_by_place_dict


def get_gcc_code(t_place, place_dict: dict, ambiguous_locations: dict):
    """
    Get the gcc code of the place, and update the counts of ambiguous locations
    :param t_place: Temp place name
    :param place_dict: Dict (key: place name, Value: gcc code)
    :param ambiguous_locations: Dict (key: Ambiguous place name, Value: count)
    :return: gcc code or None
    """

    # if the location is in two parts
    if t_place.find(",") != -1:
        t_place_first, t_place_second = t_place.split(",", 1)
        # All locations that end with Australia are ambiguous. e.g. Victoria, Australia;  South Australia, Australia
        if t_place_second == "australia":
            ambiguous_locations[t_place] += 1
            return None

        if t_place_first in GCC_DICT.keys():
            return GCC_DICT[t_place_first]
        else:
            returns = check_against_places(t_place_first, place_dict, t_place_second)
            return handle_location_check_returns(t_place, ambiguous_locations, returns)
    # if the location is a single word
    else:
        # If it's Australia or States, return None, as they are ambiguous
        if t_place == "australia" or t_place in STATE_ABB_DICT.keys():
            ambiguous_locations[t_place] += 1
            return None

        returns = check_against_places(t_place, place_dict)
        return handle_location_check_returns(t_place, ambiguous_locations, returns)


def check_against_places(place_first_part, place_dict, place_second_part=None):
    """
    Check whether the place name is ambiguous, 
    if not, return the gcc code,
    if yes, return None (for the gcc code) and the reason why it is ambiguous
    :param place_first_part: The first part (before comma) of the temp place name
    :param place_dict: Dict (key: place name, Value: gcc code)
    :param place_second_part: The second part (after comma) of the temp place name, default value set to None
    :return: gcc code or None, and the reason (if not ambiguous, the reason is omitted)
    """

    # Get all places that contains the current location - O(n)
    places_matched = [place for place in place_dict.keys() if place_first_part in place]
    if len(places_matched) == 1:
        code = place_dict[places_matched[0]]
        if is_gcc(code):
            return code,

    # if there are multiple results found
    elif len(places_matched) > 1:
        # if there is an exact match
        if place_first_part in places_matched:
            return place_dict[place_first_part],

        # get all returned gcc in a set
        gcc_variances = set(place_dict[place] for place in places_matched)
        # if we only have one kind of gcc code, then it's the one
        if len(gcc_variances) == 1:
            if is_gcc(list(gcc_variances)[0]):
                return list(gcc_variances)[0],
            else:
                return None, "NOT_A_GCC"

        elif len(gcc_variances) > 1:
            state_abb = STATE_ABB_DICT.get(place_second_part.strip())
            if state_abb:
                # Try to find a specific match with state info
                specific_refined_matched_places = [place for place in places_matched if
                                          re.search(f"{place_first_part} \({state_abb}\.?\).*", place)]
                if len(specific_refined_matched_places) == 1:
                        if is_gcc(place_dict[specific_refined_matched_places[0]]):
                            return place_dict[specific_refined_matched_places[0]],
                        else:
                            return None, "NOT_A_GCC"

                # Try to do a fuzzy match with state info
                fuzzy_refined_matched_places = [place for place in places_matched if
                                          re.search(f".*{place_first_part}.*{state_abb}\.?.*", place)]
                # Find place names include state abbreviations in brackets, like white rock (cairns - qld).

                if len(fuzzy_refined_matched_places) == 0:
                    return None, f"{AMBIGUOUS_REASON}: Multiple Matches Found, But None Matched After State Info Applied"

                elif len(fuzzy_refined_matched_places) > 1 and \
                        len(set(place_dict[place] for place in fuzzy_refined_matched_places)) > 1:
                    return None, f"{AMBIGUOUS_REASON}: Multiple Matches Found After State Info Applied"

                # REPORT: If the only refined match can't match the location with a GCC,
                # we don't consider it as AMBIGUOUS
                # e.g. 'gold coast, queensland' is not ambiguous, as all entries found in sal.json are not within a GCC.
                elif is_gcc(place_dict[fuzzy_refined_matched_places[0]]):
                    return place_dict[fuzzy_refined_matched_places[0]],
    else:
        return None, "NO_MATCH_FOUND"

    return None, "NOT_A_GCC"


def is_gcc(code):
    """
    Use regular expressions to identify whether the gcc code belongs to a greater city
    :param code: gcc code
    :return: true/false (is a greater city or not)
    """

    if re.search("\dg\w{3}|8acte", code):
        # "\d" - Digits, 'g' - Character 'g',
        # "\w" - Word Characters, "{3}" - Exactly 3 word characters.
        # Or "8acte"
        return True
    return False


def handle_location_check_returns(t_place, ambiguous_locations: dict, returns):
    """
    Handle the returns.
    If the location is ambiguous, update the count in the dict.
    If not, return the gcc code.
    :param t_place: Temp place name
    :param ambiguous_locations: Dict (key: place name, Value: count)
    :param returns: Return values (First value: Place code or None, Second Value: Omitted or Reason)
    :return: If not ambiguous, return gcc code. If ambiguous, return None.
    """

    if len(returns) == 1:
        return returns[0]
    else:
        if AMBIGUOUS_REASON in returns[1]:
            ambiguous_locations[t_place] += 1
        return None


def get_top_gcc_by_num_of_tweet(author_by_gcc_df, n=8):
    """
    Get a list of GCC codes with most numbers of twitters
    :param author_by_gcc_df: Dataframe of twitter counts
    :param n: Number of GCCs
    :return: Sorted list
    """

    gcc_tweet_sum = author_by_gcc_df.sum()
    gcc_tweet_sum_sorted = gcc_tweet_sum.sort_values(ascending=False).head(n)

    print(gcc_tweet_sum_sorted)
    return gcc_tweet_sum_sorted


def get_top_author_by_num_of_tweet(author_by_gcc_df, n=10):
    """
    Get a list of Authors with most numbers of twitters
    :param author_by_gcc_df: Dataframe of twitter counts
    :param n: Number of authors
    :return: Sorted List
    """

    author_tweet_sum = author_by_gcc_df.T.sum()  # Transpose rows and columns
    author_tweet_sum_sorted = author_tweet_sum.sort_values(ascending=False).head(n)

    print(author_tweet_sum_sorted)
    return author_tweet_sum_sorted


def get_top_author_by_num_of_gcc(author_by_gcc_df, n=10):
    """
    Get a list of Authors with most numbers of GCCs
    :param author_by_gcc_df: Dataframe of twitter counts
    :param n: Number of authors
    :return: Sorted List
    """
    author_gcc_sum = author_by_gcc_df

    gcc_counts = (author_gcc_sum > 0).sum(axis=1)
    author_gcc_sum['GCC_Count'] = gcc_counts

    twitter_counts = author_by_gcc_df.T.sum()
    author_gcc_sum['Twitter_Count'] = twitter_counts

    author_gcc_sum_sorted = author_gcc_sum.sort_values(by=['GCC_Count', 'Twitter_Count'],
                                                       ascending=[False, False]).head(n)

    print(author_gcc_sum_sorted)
    return author_gcc_sum_sorted


def print_top_n_in_dict(output_dic: dict, n: int = 10, desc: bool = True):
    """
    Print top n in the dict
    :param output_dic: Dict to output
    :param n: Number of output rows, default value set to 10
    :param desc: Desc/Asc Order
    """

    sorted_dict = sorted(output_dic.items(), key=lambda x: x[1], reverse=desc)
    n_dict = len(output_dic)
    n = n if n <= n_dict else n_dict
    for i in range(n):
        print(sorted_dict[i])
