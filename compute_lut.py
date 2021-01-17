import os
import json
import math
from PIL import Image

from lut import Lut
from constants import HALD_FILENAME, LUT_CUBE_FILENAME, LUT_JSON_FILENAME, LUT_PNG_FILENAME



def compute_lut(path, lut_size, gen_format, name=None):
    """
    读取改变后的 HALD，计算 LUT，并保存为多种格式的文件。
    type 是三维向量，分别代表生成 json、cube、png。
    """

    if name == None:
        name = str(lut_size)

    lut = Lut(lut_size)

    image = Image.open(os.path.join(path,HALD_FILENAME.format(name)))
    colors = []
    pixels = image.getdata()
    for pixel in pixels:
        r = pixel[0]
        g = pixel[1]
        b = pixel[2]
        color = (r,g,b)
        colors.append(color)

    if gen_format[0]:
        save_lut_json(path, name, lut, colors)
    if gen_format[1]:
        save_lut_cube(path, name, lut, colors)
    if gen_format[2]:
        save_lut_png(path, name, lut, colors)

    return (lut)


def cube_row(color):
    """
    Format color tuple as string for a CUBE file line
    """
    return ' '.join(map(lambda x: str(x/255), color))


def save_lut_json(path, name, lut, colors):
    """
    Save LUT data as JSON, for general programmatic use.
    """
    with open(os.path.join(path,LUT_JSON_FILENAME.format(name)),'w') as f:
        f.write(json.dumps({
                'name': name,
                'lut_size': lut.size,
                'samples': list(map(lambda x: list(map(lambda y: y/255, x)), colors))
                }))


def save_lut_cube(path, name, lut, colors):
    """
    Save LUT data as Adobe Cube, for use in Photoshop, Premiere, etc.
    Adobe Cube Spec: http://wwwimage.adobe.com/content/dam/Adobe/en/products/speedgrade/cc/pdfs/cube-lut-specification-1.0.pdf
    """
    cube = 'LUT_3D_SIZE {}\n'.format(lut.size) + '\n'.join(map(cube_row, colors))
    with open(os.path.join(path,LUT_CUBE_FILENAME.format(name)),'w') as f:
        f.write(cube)


def save_lut_png(path, name, lut, colors):
    """
    Save LUT data as pseudo-3D texture, for use in OpenGL shaders.
    """
    im = Image.new('RGB', (pow(lut.size,2), lut.size), (0, 0, 0))
    for i,color in enumerate(colors):
        column, row, z = lut.lattice_coords(i)
        im.putpixel((z*lut.size+column,row), color)
    im.save(os.path.join(path, LUT_PNG_FILENAME.format(name)),'PNG')

if __name__ == '__main__':
    path = ''
    lut_size = 64
    gen_format = [False, True, False]
    compute_lut(path, lut_size, gen_format)