import os
from PIL import Image, ImageDraw
from lut import Lut
import math


META_FILENAME = '{}_metadata.json'
HALD_FILENAME = 'HALD_{}.png'
LUT_JSON_FILENAME = '{}.json'
LUT_CUBE_FILENAME = '{}.cube'
LUT_PNG_FILENAME = '{}.png'

def generate_HALD(lut_size, output_path,image_size = None, name = None):
    """
    生成色彩图
    """
    if image_size == None:
        image_size =  math.ceil((lut_size ** 3) ** 0.5)
    if name == None:
        name = str(lut_size)

    lut = Lut(lut_size, image_size)
    colors = lut.generate_colors()
    image = Image.new('RGB', (lut.image_size, lut.image_size), (0, 0, 0))
    draw = ImageDraw.Draw(image)

    lookup_table = list(range(lut.swatch_count))

    for i, color in enumerate(colors):
        draw.rectangle(lut.cell_bounds(lookup_table[i]), fill=tuple(color))

    image.save(os.path.join(output_path,HALD_FILENAME.format(name)), "PNG")
    return None


if __name__ == '__main__':
    lut_size = 64
    data_dir = ''
    # image_size = 512
    # name = 'lut'
    generate_HALD(lut_size, data_dir)