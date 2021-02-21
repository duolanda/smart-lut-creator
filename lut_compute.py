import os
import json
import math
from PIL import Image
import numpy as np

from lut import LutM
from lut import LUT
from constants import HALD_FILENAME, LUT_CUBE_FILENAME, LUT_JSON_FILENAME, LUT_PNG_FILENAME



def compute_lut(hald_path, lut_size, out_path, name=None):
    """
    读取改变后的 HALD，计算 LUT，并保存为多种格式的文件。
    type 是三维向量，分别代表生成 json、cube、png。
    """

    if name == None:
        name = str(lut_size)

    lut = LutM(lut_size)

    image = Image.open(os.path.join(hald_path,HALD_FILENAME.format(name)))
    colors = []
    pixels = image.getdata()
    for pixel in pixels:
        r = pixel[0]/255
        g = pixel[1]/255
        b = pixel[2]/255
        color = (r,g,b)
        colors.append(color)
    out_lut = LUT.FromCompute(lut_size, colors)
    out_lut.ToCubeFile(out_path)

    return (lut)

def compute_lut_np(hald_img_pixel, lut_size, name=None):
    """
    与 compute_lut 的区别在于不再读写文件，而是直接处理内存中的 numpy 矩阵
    """

    if name == None:
        name = str(lut_size)

    lut = LutM(lut_size)

    colors = []
    pixels = hald_img_pixel.reshape(lut_size**3, 3) #(w*h, 3) 的图片矩阵
    for pixel in pixels:
        r = pixel[0]
        g = pixel[1]
        b = pixel[2]
        color = (r,g,b)
        colors.append(color)
    out_lut = LUT.FromCompute(lut_size, colors)
    return out_lut

if __name__ == '__main__':
    path = ''
    lut_size = 36
    out_path = 'test_lut/smart_cube.cube'
    compute_lut(path, lut_size, out_path)