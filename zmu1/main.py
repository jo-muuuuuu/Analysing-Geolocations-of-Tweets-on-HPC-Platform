import json


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


def get_place_code(sal):
    place_code_lst = [[] for i in range(7)]

    for (key, value) in sal.items():
        code = value.get("gcc")

        if code[1] == 'g':
            index = int(value.get("ste"))
            place_code_lst[index - 1].append({key: code})

    # for i in range(7):
    #     print(place_code_lst[i])
    #     print("\n")

    return place_code_lst


def get_index(place_name):
    if "sydney" in place_name or "new south wales" in place_name:
        index = 0
    elif "melbourne" in place_name or "victoria" in place_name:
        index = 1
    elif "brisbane" in place_name or "queensland" in place_name:
        index = 2
    elif "adelaide" in place_name or "south australia" in place_name:
        index = 3
    elif "perth" in place_name or "west australia" in place_name:
        index = 4
    elif "hobart" in place_name or "tasmania" in place_name:
        index = 5
    elif "darwin" in place_name or "northern territory" in place_name:
        index = 6
    else:
        index = -1

    # print(place_name)
    # print(index)
    return index


def top_places(twitter, place_code_lst):
    place_code_dict = {}

    for j in range(len(twitter)):
        includes_data = twitter[j]['includes'].get("places")[0]
        place_name = includes_data.get("full_name").lower()

        index = get_index(place_name)
        if index < 0:
            continue

        for k in range(len(place_code_lst[index])):
            for (key, value) in place_code_lst[index][k].items():
                temp_name = key
                temp_code = value

            if place_name.find(temp_name) != -1:
                if temp_code in place_code_dict.keys():
                    temp = place_code_dict.get(temp_code) + 1
                    place_code_dict.update({temp_code: temp})
                else:
                    place_code_dict.update({temp_code: 1})

    # print(place_code_dict)
    name_dict_sorted = sorted(place_code_dict.items(), key=lambda x: x[1], reverse=True)

    for l in range(7):
        print(name_dict_sorted[l])


def top_id_places(twitter, place_code_lst):
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
    twitter_file = open('twitter-data-small.json')
    # twitter_file = open('test_1.json')
    twitter = json.load(twitter_file)

    sal_file = open('sal.json')
    sal = json.load(sal_file)

    place_code_lst = get_place_code(sal)
    # print(place_code_lst)

    # Top 10 Author IDs
    # top_ten_id(twitter)
    # print("\n-------------------------------------------\n")

    # Places with the most twitters
    # top_places(twitter, place_code_lst)
    # print("\n-------------------------------------------\n")

    # IDs with the most places
    top_id_places(twitter, place_code_lst)
