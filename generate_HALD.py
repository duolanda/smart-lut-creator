from PIL import Image, ImageDraw
from lut import LutM
import numpy as np


'''
faymontage/lut-maker: Generate 3D color LUTs in Adobe Cube and Pseudo-3D texture format
https://github.com/faymontage/lut-maker
'''

HALD_FILENAME = 'HALD_{}.png'

def generate_HALD_np(lut_size):
    """
    生成色彩图，直接返回 numpy 格式的图片
    """

    lut = LutM(lut_size)
    colors = lut.generate_colors()
    image = np.zeros((1, lut.swatch_count, 3))

    for i in range(len(image[0])):
        image[0][i] = np.array(colors[i])

    hald_img = np.float64(image/255)
    return hald_img


    

