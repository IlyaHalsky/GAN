import os
import cv2
from PIL import Image
from PIL import ImageMath

src = "./final"  # pokeRGB_black
dst = "./final_resize/"  # resized

if not os.path.exists(dst):
    os.mkdir(dst)

orig_size = (307, 456)

for each in os.listdir(src):
    print(each)
    if each != 'Thumbs.db':
        im = Image.open(os.path.join(src, each))
        im_size = im.size
        new_size = (int(im_size[0] * 307 / 456), im_size[1])
        im.resize(new_size, Image.ANTIALIAS).save(dst + each.split('.')[0] + ".jpg", "JPEG")
