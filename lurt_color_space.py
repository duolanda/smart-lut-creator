import colour
from colormath.color_conversions import convert_color
from colormath.color_objects import (
    sRGBColor,
    XYZColor,
)
import numpy as np

img_in = colour.read_image('test_img/smpte_digital_leader_4k_24fps_2d_ar185_xyz16.tif')


for i in range(len(img_in)):
    for pixel in img_in[i]:
        xyz = XYZColor(pixel[0], pixel[1], pixel[2])
        srgb = convert_color(xyz, sRGBColor)
        pixel = np.asarray([srgb.rgb_r, srgb.rgb_g, srgb.rgb_b])

# img_out = colour.XYZ_to_sRGB(img_in)
img_out = img_in
colour.write_image(img_out, 'output.tif')