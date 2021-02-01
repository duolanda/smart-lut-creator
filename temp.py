from PIL import Image, ImageFilter, ImageMath

from itertools import chain

try:
    import numpy
except ImportError:  # pragma: no cover
    numpy = None


def load_cube_file(lines, target_mode=None, cls=ImageFilter.Color3DLUT):
    """Loads 3D lookup table from .cube file format.

    :param lines: Filename or iterable list of strings with file content.
    :param target_mode: Image mode which should be after color transformation.
                        The default is None, which means mode doesn't change.
    :param cls: A class which handles the parsed file.
                Default is ``ImageFilter.Color3DLUT``.
    """
    name, size = None, None
    channels = 3
    file = None

    file = lines = open(lines, 'rt')

    try:
        iterator = iter(lines)

        for i, line in enumerate(iterator, 1):
            line = line.strip()
            if line.startswith('TITLE "'):
                name = line.split('"')[1]
                continue
            if line.startswith('LUT_3D_SIZE '):
                size = [int(x) for x in line.split()[1:]]
                if len(size) == 1:
                    size = size[0]
                continue
            if line.startswith('CHANNELS '):
                channels = int(line.split()[1])
            if line.startswith('LUT_1D_SIZE '):
                raise ValueError("1D LUT cube files aren't supported")

            try:
                float(line.partition(' ')[0])
            except ValueError:
                pass
            else:
                # Data starts
                break

        if size is None:
            raise ValueError('No size found in the file')

        table = []
        for i, line in enumerate(chain([line], iterator), i):
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            try:
                pixel = [float(x) for x in line.split()]
            except ValueError:
                raise ValueError("Not a number on line {}".format(i))
            if len(pixel) != channels:
                raise ValueError(
                    "Wrong number of colors on line {}".format(i))
            table.extend(pixel)
    finally:
        if file is not None:
            file.close()

    instance = cls(size, table, channels=channels,
                   target_mode=target_mode, _copy_table=False)
    if name is not None:
        instance.name = name
    return instance

if __name__ == '__main__':
    # lut = load_cube_file('gen_lut/srgb to xyz.cube')
    # im = Image.open('test_img/fruits.tif')
    # im.filter(lut).save('gen_img/srgb to xyz.jpg')

    # lut = load_cube_file('gen_lut/srgb to lab.cube')
    # im = Image.open('test_img/fruits.tif')
    # im.filter(lut).save('gen_img/srgb to lab.jpg')

    # lut = load_cube_file('gen_lut/srgb to hsv.cube')
    # im = Image.open('test_img/fruits.tif')
    # im.filter(lut).save('gen_img/srgb to hsv.jpg')

    # lut = load_cube_file('gen_lut/srgb to ycbcr.cube')
    # im = Image.open('test_img/fruits.tif')
    # im.filter(lut).save('gen_img/srgb to ycbcr.jpg')

    # lut = load_cube_file('gen_lut/xyz to srgb.cube')
    # im = Image.open('test_img/output-xyz-colour.png')
    # im.filter(lut).save('gen_img/xyz to srgb.jpg')

    # lut = load_cube_file('gen_lut/gamma 2.6 to 2.2.cube')
    # im = Image.open('test_img/fruits.tif')
    # im.filter(lut).save('gen_img/gamma 2.6 to 2.2.jpg')

    
    # lut = load_cube_file('gen_lut/sgamut to srgb.cube')
    # im = Image.open('test_img/s-log.tif')
    # im.filter(lut).save('gen_img/sgamut to srgb.jpg')

    # lut = load_cube_file('gen_lut/alexawg to srgb.cube')
    # im = Image.open('test_img/Alexa.bmp')
    # im.filter(lut).save('gen_img/alexawg to srgb.jpg')


    lut = load_cube_file('gen_lut/slog3 to rec709.cube')
    im = Image.open('test_img/s-log.tif')
    im.filter(lut).save('gen_img/slog3 to rec709.jpg')

    # lut = load_cube_file('gen_lut/logc to rec709.cube')
    # im = Image.open('test_img/Alexa.bmp')
    # im.filter(lut).save('gen_img/logc to rec709.jpg')

    # lut = load_cube_file('gen_lut/rec709 to srgb.cube')
    # im = Image.open('test_img/fruits.tif')
    # im.filter(lut).save('gen_img/rec709 to srgb.jpg')

    # lut = load_cube_file('test_lut/slog3 to 709 lutcalc.cube')
    # im = Image.open('test_img/s-log.tif')
    # im.filter(lut).save('gen_img/slog3 to 709 lutcalc.jpg')