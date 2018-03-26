import urllib.request
import os

POKE_URL = "https://assets.pokemon.com/assets/cms2/img/pokedex/detail/"
POKE_SAVE = "./poke_save/"

if not os.path.exists(POKE_SAVE):
    os.mkdir(POKE_SAVE)

for i in range(1, 807):
    fmtI = str(i).zfill(3)
    path = fmtI + ".png"
    print(path)
    urllib.request.urlretrieve(POKE_URL + path, POKE_SAVE + path)
