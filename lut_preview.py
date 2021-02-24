from PIL import Image, ImageFilter, ImageMath

from itertools import chain

import numpy as np

from lut import LUT
import lut_IO


def load_lut(lut, target_mode=None, cls=ImageFilter.Color3DLUT):
    """Loads 3D lookup table from .cube file format.

    :param lines: Filename or iterable list of strings with file content.
    :param target_mode: Image mode which should be after color transformation.
                        The default is None, which means mode doesn't change.
    :param cls: A class which handles the parsed file.
                Default is ``ImageFilter.Color3DLUT``.
    """

    size = lut.cubeSize
    name = lut.name
    channels = 3

    table = lut.lattice_np #用“bgr”
    table = table.flatten()

    instance = cls(size, table, channels=channels,
                   target_mode=target_mode, _copy_table=False) #table是size*size*size*3的list
    if name is not None:
        instance.name = name
    return instance

def apply_lut(lut_file, img_file):
    lut = lut_IO.FromCubeFile(lut_file)
    lut = load_lut(lut)

    img = Image.open(img_file)
    img.filter(lut).save('PILTest.bmp')
        

def apply_lut_np(lut, img):
    lut = load_lut(lut)
    img = Image.fromarray(np.uint8(img*255))
    return np.array(img.filter(lut))


if __name__ == '__main__':
    # lut_file = 'test_lut/ARRI_LogC2Video_Classic709_davinci3d_33.cube'
    # img_file = 'test_img/Alexa.bmp'
    # apply_lut(lut_file, img_file)

    lut_file = 'gen_img/srgb to sgmaut lattice.cube'
    img_file = 'test_img/fruits.tif '
    apply_lut(lut_file, img_file)
