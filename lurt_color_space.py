import colour
import numpy as np
import colorio
from skimage.color import rgb2xyz, xyz2rgb, rgb2lab, lab2rgb, rgb2hsv, rgb2ycbcr,rgb2yuv
from skimage import data, io

def vector_dot(m, v): 
    '''
    m 是变换矩阵，v 是图像矩阵（只有一个像素或整张图都可以）
    非常神奇，经过实际验证，其效果与逐像素去和变换矩阵相乘完全相同，速度还飞快
    '''
    return np.einsum('...ij,...j->...i', m, v)

srgb_trans = colorio.SrgbLinear()

img_in = colour.read_image('test_img/fruits.tif')
# img_in = io.imread('test_img/fruits.tif')

# img_in = img_in ** (1/2.2)

# for i in range(len(img_in)):
#     if(i%100 == 0):
#         print(i/len(img_in)*100)
#     for j in range(len(img_in[i])):
#         img_in[i][j] = srgb_trans.to_xyz100(img_in[i][j])


# img_out = colour.XYZ_to_Lab(colour.sRGB_to_XYZ(img_in))
# img_out = colour.RGB_to_HSV(img_in)
# img_out = colour.RGB_to_YCbCr(img_in)

# img_out = rgb2xyz(img_in)

# img_out = img_out ** 2.2
# colour.write_image(img_out, 'test_img/output.png')

io.imsave('test_img/output.png', img_out)



