# Loads all images and creates csv with parameteres
import requests
import json

response = requests.get("https://omgvamp-hearthstone-v1.p.mashape.com/cards/types/Minion?collectible=1",
                        headers={
                            "X-Mashape-Key": "Zsl54BcBsfmsh1nWboEz2atobEsVp1T5pKyjsnIRevAABJcE9c"
                        }
                        )

body = response.content
json_result = json.loads(body.decode("utf-8"))


def rarity_to_array(str_in):
    if str_in == "Free":
        return [1, 0, 0, 0, 0]
    if str_in == "Common":
        return [0, 1, 0, 0, 0]
    if str_in == "Rare":
        return [0, 0, 1, 0, 0]
    if str_in == "Epic":
        return [0, 0, 0, 1, 0]
    if str_in == "Legendary":
        return [0, 0, 0, 0, 1]


def class_to_array(item_in):
    class_str = ""
    try:
        class_str = item_in['playerClass']
    except Exception:
        pass
    if class_str == "":
        try:
            class_str = item_in['faction']
        except Exception:
            pass
    class_map = {'Neutral': [1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                 'Druid':   [0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
                 'Hunter':  [0, 0, 1, 0, 0, 0, 0, 0, 0, 0],
                 'Mage':    [0, 0, 0, 1, 0, 0, 0, 0, 0, 0],
                 'Paladin': [0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
                 'Priest':  [0, 0, 0, 0, 0, 1, 0, 0, 0, 0],
                 'Rogue':   [0, 0, 0, 0, 0, 0, 1, 0, 0, 0],
                 'Shaman':  [0, 0, 0, 0, 0, 0, 0, 1, 0, 0],
                 'Warlock': [0, 0, 0, 0, 0, 0, 0, 0, 1, 0],
                 'Warrior': [0, 0, 0, 0, 0, 0, 0, 0, 0, 1], }
    if class_map.get(class_str) is None:
        print(item)
        print(item_in['playerClass'])
    return class_map.get(class_str)

import os
card_folder = './cards/'
feature_folder = './features/'
if not os.path.exists(card_folder):
    os.makedirs(card_folder)
if not os.path.exists(feature_folder):
    os.makedirs(feature_folder)

import urllib.request

for item in json_result:
    print(item['name'])
    name = item['name'].replace(':','')
    print(rarity_to_array(item['rarity']))
    print(class_to_array(item))
    str_features = rarity_to_array(item['rarity']) + class_to_array(item)
    text_file = open(feature_folder + name + ".txt", "w")
    text_file.write(str(str_features)[1:-1])
    print(str(str_features)[1:-1])
    text_file.close()
    url = item['img']
    urllib.request.urlretrieve(url, card_folder + name + ".png")

#print(body.decode("utf-8"))
print(response.elapsed)