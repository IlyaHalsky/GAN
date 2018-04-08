import imageio
import glob
import os

search_dir = "./newPokemon"
files = glob.glob(search_dir+"/*")
files.sort(key=os.path.getmtime)
filenames = files
images = []

for filename in filenames:
    print(filename)
    images.append(imageio.imread(filename))
imageio.mimsave('evolution.gif', images)