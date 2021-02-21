import os
from PIL import Image, ImageDraw
from lut import LutM
import math
import numpy as np
from constants import HALD_FILENAME

'''
faymontage/lut-maker: Generate 3D color LUTs in Adobe Cube and Pseudo-3D texture format
https://github.com/faymontage/lut-maker
'''

HALD_FILENAME = 'HALD_{}.png'
LUT_CUBE_FILENAME = '{}.cube'
LUT_PNG_FILENAME = '{}.png'

def generate_HALD(lut_size, output_path, name = None):
    """
    生成色彩图
    """
    if name == None:
        name = str(lut_size)

    lut = LutM(lut_size)
    colors = lut.generate_colors()
    image = Image.new('RGB', (lut.image_size, lut.image_size), (0, 0, 0))
    draw = ImageDraw.Draw(image)

    lookup_table = list(range(lut.swatch_count))

    for i, color in enumerate(colors):
        draw.rectangle(lut.cell_bounds(lookup_table[i]), fill=tuple(color))

    image.save(os.path.join(output_path,HALD_FILENAME.format(name)), "PNG")
    return None


def generate_HALD_np(lut_size):
    """
    生成色彩图，直接返回 numpy 格式的图片
    """

    lut = LutM(lut_size)
    colors = lut.generate_colors()
    image = Image.new('RGB', (lut.image_size, lut.image_size), (0, 0, 0))
    draw = ImageDraw.Draw(image)

    lookup_table = list(range(lut.swatch_count))

    for i, color in enumerate(colors):
        draw.rectangle(lut.cell_bounds(lookup_table[i]), fill=tuple(color))

    hald_img = np.float64(np.array(image.getdata())/255)
    hald_img = hald_img.reshape(image.height, image.width, 3)
    return hald_img

if __name__ == '__main__':
    lut_size = 36
    data_dir = ''
    # image_size = 512
    # name = 'lut'
    generate_HALD(lut_size, data_dir)
