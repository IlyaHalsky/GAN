import os
import cv2
from PIL import Image
from PIL import ImageMath

src = "./cards"  # pokeRGB_black
dst = "./resize_cards/"  # resized

if not os.path.exists(dst):
    os.mkdir(dst)

orig_size = size = (307, 456)
size = (307, 307)

for each in os.listdir(src):
    if each != 'Thumbs.db':
        im = Image.open(os.path.join(src, each)).convert('RGBA')
        fff = Image.new('RGBA', im.size, (256,) * 4)
        out = Image.composite(im, fff, im)
        out.convert('RGB').resize(size, Image.ANTIALIAS).save(dst + each.split('.')[0] + ".jpg", "JPEG")
