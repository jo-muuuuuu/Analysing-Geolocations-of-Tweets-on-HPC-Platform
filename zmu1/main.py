import ijson
import argparse
import time
import os.path
import numpy as np
import pandas as pd
import util
from collections import defaultdict
from mpi4py import MPI


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
    start_time = time.time()

    # MPI Initialization
    comm = MPI.COMM_WORLD
    comm_rank = comm.Get_rank()
    comm_size = comm.Get_size()

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
            r = index % comm_size
            if r == comm_rank:
                process_data(twitter_data_point, code_by_places, id_places_dict, ambiguous_locations)
        
        author_list = list(id_places_dict.keys())
        author_by_gcc_arr = np.array([a for a in id_places_dict.values()])

        # MPI MERGE
        # Get all dataframes and then concatenate them, e.g.
        # df_sum_al = pd.concat([df_1, df_2, ...]).groupby("Authors:").sum()
        if comm_rank == 0:
            gathered_data = [author_by_gcc_arr]

            for i in range(1, comm_size):
                data = comm.recv(source=i)
                author_list.extend(comm.recv(source=i))

                gathered_data.append(data)

            final_data = np.concatenate(gathered_data, axis=0)

        else:
            comm.send(author_by_gcc_arr, dest=0)
            comm.send(author_list, dest=0)

        if comm_rank == 0:
            author_by_gcc_df = pd.DataFrame(final_data, index=pd.Index(author_list, name="Authors:"),
                                        columns=pd.Index(util.GCC_DICT.values(), name='GGC:'))
            
            author_by_gcc_df = author_by_gcc_df.groupby(level=0).sum()

            print("--- Time to Process Data: %.3f seconds ---" % (time.time() - start_time))

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

    
