import numpy as np

from lut import LutM
from lut import LUT

HALD_FILENAME = 'HALD_{}.png'

def compute_lut_np(hald_img_pixel, lut_size, name=None):
    """
    读取改变后的 HALD，计算出 LUT，并返回 numpy 矩阵
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
    out_lut = LUT.from_compute(lut_size, colors, name)
    return out_lut

  