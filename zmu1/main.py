import ijson
import argparse
import time
import os.path
import numpy as np
import pandas as pd
import util
from collections import defaultdict


# def top_ten_id(twitter):
#     author_id_dict = {}
#
#     for i in range(len(twitter)):
#         cur_author_id = twitter[i]['data'].get("author_id")
#
#         if cur_author_id in author_id_dict:
#             temp = author_id_dict.get(cur_author_id) + 1
#             author_id_dict.update({cur_author_id: temp})
#         else:
#             author_id_dict.update({cur_author_id: 1})
#
#     # print(twitter_dict)
#     id_dict_sorted = sorted(author_id_dict.items(), key=lambda x: x[1], reverse=True)
#
#     for j in range(10):
#         print(id_dict_sorted[j])


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


def update_dict(id_places_dict, cur_author_id, code):
    """
    Increment the count of twitters from a single author
    :param id_places_dict: The dict contains the counts of twitters posted in different places from one author
    :param cur_author_id: The twitter ID of the author
    :param code: gcc code
    """

    cur_list = id_places_dict.get(cur_author_id)
    index = int(code[:1]) - 1
    cur_list[index] = cur_list[index] + 1
    # if code in cur.keys():
    #     temp = cur.get(code) + 1
    #     cur.update({code: temp})
    # else:
    #     cur.update({code: 1})


def process_data(twitter_data_point, code_by_places, id_places_dict, ambiguous_locations: set):
    """
    Process a single twitter data
    :param twitter_data_point: Json data containing all the information of a twitter
    :param code_by_places: Dict (Key: Place name, Value: gcc code)
    :param id_places_dict: The dict contains the counts of twitters posted in different places from one author
    :param ambiguous_locations: Dict (key: Ambiguous place name, Value: count)
    """

    cur_author_id = twitter_data_point['data'].get("author_id")

    if cur_author_id not in id_places_dict.keys():
        id_places_dict[cur_author_id] = [0] * 8

    t_place_name = twitter_data_point['includes'].get("places")[0].get("full_name").lower()

    code = util.get_gcc_code(t_place_name, code_by_places, ambiguous_locations)
    if code:
        update_dict(id_places_dict, cur_author_id, code)
            

def main(data_path, location_path):
    """
    The driver function to run the program
    :param data_path: The directory path of the place information file (Abbreviations)
    :param location_path: The directory path of the twitter file to be processed
    """

    # Get gcc code by locations. data looks like: [{"abb": "1gsyd"}, ...]
    code_by_places = util.process_location_file(location_path)

    id_places_dict = {}
    ambiguous_locations = defaultdict(int)  # Avoid key error, and assign value 0 to keys not defined

    # with open(os.path.dirname(__file__) + '/../test_3.json', 'r', encoding='UTF-8') as twitter_file:
    with open(os.path.dirname(__file__) + data_path, 'r', encoding='UTF-8') as twitter_file:
        twitter = ijson.items(twitter_file, 'item')

        # MPI PROCESS
        # TODO: implement MPI logic
        # We can get the index of the current json data point   - index
        # we have the rank of the current processor   -  comm_rank
        # we have the number of processors   -    comm_size
        # if the remainder r, where r = index % comm_size, is equal to the comm_rank,
        # the current process should process it, otherwise, ignore it.

        for index, twitter_data_point in enumerate(twitter):
            process_data(twitter_data_point, code_by_places, id_places_dict, ambiguous_locations)
        
        author_list = id_places_dict.keys()
        # print(author_list, "\n")
        author_by_gcc_arr = np.array([a for a in id_places_dict.values()])
        # print(author_by_gcc_arr, "\n")
        author_by_gcc_df = pd.DataFrame(author_by_gcc_arr, index=pd.Index(author_list, name="Authors:"),
                                        columns=pd.Index(util.GCC_DICT.values(), name='GGC:'))
        # print(author_by_gcc_df, "\n")

        # MPI MERGE
        # Get all dataframes and then concatenate them, e.g.
        # df_sum_al = pd.concat([df_1, df_2, ...]).groupby("Authors:").sum()


        # OUTPUT
        # Return GCC by the number of tweets in descending order
        print("==== GCCs by the number of tweets in descending order ====")
        util.get_top_gcc_by_num_of_tweet(author_by_gcc_df)

        print("==== Authors by the number of tweets in descending order ====")
        util.get_top_author_by_num_of_tweet(author_by_gcc_df)

        print("==== Top Authors by the number of Locations ====")
        util.get_top_author_by_num_of_gcc(author_by_gcc_df)

        print("==== Top 10 Ambiguous Locations ====")
        util.print_top_n_in_dict(ambiguous_locations)


if __name__ == '__main__':
    # USAGE: python main.py --location /../sal.json --data /../twitter-data-small.json

    parser = argparse.ArgumentParser(description='Processing Twitter data focusing on the geolocation attribute')
    # Pass in the location file path
    parser.add_argument('--location', type=str, help='File path to the location file. e.g. sal.json')
    # Pass in the twitter data file path
    parser.add_argument('--data', type=str, help='File path to the twitter data file')
    args = parser.parse_args()

    location_path = args.location
    data_path = args.data

    start_time = time.time()
    main(data_path, location_path)
    print("--- %.3f seconds ---" % (time.time() - start_time))

    
