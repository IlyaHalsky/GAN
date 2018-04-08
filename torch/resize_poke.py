import os
import cv2
from PIL import Image
from PIL import ImageMath

src = "./poke_save"  # pokeRGB_black
dst = "./resize_black/"  # resized

if not os.path.exists(dst):
    os.mkdir(dst)

for each in os.listdir(src):
    im = Image.open(os.path.join(src, each)).convert('RGBA')
    fff = Image.new('RGBA', im.size, (256,) * 4)
    out = Image.composite(im, fff, im)
    out.convert('RGB').resize((128, 128), Image.ANTIALIAS).save(dst + each.split('.')[0] + ".jpg", "JPEG")
