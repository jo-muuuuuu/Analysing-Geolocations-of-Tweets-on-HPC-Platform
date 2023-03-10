import json

if __name__ == '__main__':
    twitter_file = open('twitter-data-small.json')
    twitter = json.load(twitter_file)

    sal_file = open('sal.json')
    sal = json.load(sal_file)

    # print(type(sal)) # Type: Dict
    # print(type(twitter[0]['data']))   # Type : Dict
    # print(type(twitter))      # Type:List

    place_code_dict = {}

    for (key, value) in sal.items():
        place_code_dict.update({key: value.get("gcc")})

    # print(sorted(set(place_code_dict.values())))
    # print(len(set(place_code_dict.values())))

    place_code_lst = [[] for i in range(7)]

    for (key, value) in sal.items():
        code = value.get("gcc")

        if code[1] == 'g':
            index = int(value.get("ste"))
            place_code_lst[index - 1].append({key: code})

    for i in range(7):
        print(place_code_lst[i])
