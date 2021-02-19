from PIL import Image, ImageFilter, ImageMath

from itertools import chain

import numpy as np

from lut import LUT
from lut_IO import lut_to_numpy



def load_lut(lut, target_mode=None, cls=ImageFilter.Color3DLUT):
    """Loads 3D lookup table from .cube file format.

    :param lines: Filename or iterable list of strings with file content.
    :param target_mode: Image mode which should be after color transformation.
                        The default is None, which means mode doesn't change.
    :param cls: A class which handles the parsed file.
                Default is ``ImageFilter.Color3DLUT``.
    """
    # name, size = None, None
    # channels = 3
    # file = None

    # file = lines = open(lines, 'rt')

    # try:
    #     iterator = iter(lines)

    #     for i, line in enumerate(iterator, 1):
    #         line = line.strip()
    #         if line.startswith('TITLE "'):
    #             name = line.split('"')[1]
    #             continue
    #         if line.startswith('LUT_3D_SIZE '):
    #             size = [int(x) for x in line.split()[1:]]
    #             if len(size) == 1:
    #                 size = size[0]
    #             continue
    #         if line.startswith('CHANNELS '):
    #             channels = int(line.split()[1])
    #         if line.startswith('LUT_1D_SIZE '):
    #             raise ValueError("1D LUT cube files aren't supported")

    #         try:
    #             float(line.partition(' ')[0])
    #         except ValueError:
    #             pass
    #         else:
    #             # Data starts
    #             break

    #     if size is None:
    #         raise ValueError('No size found in the file')

    #     table = []
    #     for i, line in enumerate(chain([line], iterator), i):
    #         line = line.strip()
    #         if not line or line.startswith('#'):
    #             continue
    #         try:
    #             pixel = [float(x) for x in line.split()]
    #         except ValueError:
    #             raise ValueError("Not a number on line {}".format(i))
    #         if len(pixel) != channels:
    #             raise ValueError(
    #                 "Wrong number of colors on line {}".format(i))
    #         table.extend(pixel)
    # finally:
    #     if file is not None:
    #         file.close()

    size = lut.cubeSize
    name = lut.name
    channels = 3

    table = lut_to_numpy(lut, True) #用“bgr”
    table = table.flatten()

    instance = cls(size, table, channels=channels,
                   target_mode=target_mode, _copy_table=False) #table是size*size*size*3的list
    if name is not None:
        instance.name = name
    return instance

def apply_lut(lut_file, img_file):
    lut = LUT.FromCubeFile(lut_file)
    lut = load_lut(lut)

    img = Image.open(img_file)
    img.filter(lut).save('PILTest.bmp')
        

def apply_lut_np(lut, img):
    lut = load_lut(lut)
    img = Image.fromarray(np.uint8(img*255))
    return np.array(img.filter(lut))


if __name__ == '__main__':
    lut_file = 'test_lut/ARRI_LogC2Video_Classic709_davinci3d_33.cube'
    img_file = 'test_img/Alexa.bmp'
    apply_lut(lut_file, img_file, True)
