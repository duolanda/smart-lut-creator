import os
import json
import math
from PIL import Image

from lut import LutM
from lut import LUT
from constants import HALD_FILENAME, LUT_CUBE_FILENAME, LUT_JSON_FILENAME, LUT_PNG_FILENAME



def compute_lut(path, lut_size, name=None):
    """
    读取改变后的 HALD，计算 LUT，并保存为多种格式的文件。
    type 是三维向量，分别代表生成 json、cube、png。
    """

    if name == None:
        name = str(lut_size)

    lut = LutM(lut_size)

    image = Image.open(os.path.join(path,HALD_FILENAME.format(name)))
    colors = []
    pixels = image.getdata()
    for pixel in pixels:
        r = pixel[0]
        g = pixel[1]
        b = pixel[2]
        color = (r,g,b)
        colors.append(color)
    out_lut = LUT.FromCompute(lut_size, colors)
    out_lut.ToCubeFile('test_lut/smart_cube.cube')

    return (lut)


if __name__ == '__main__':
    path = ''
    lut_size = 36
    compute_lut(path, lut_size)