import colour
import numpy as np
from skimage.color import rgb2xyz, xyz2rgb, rgb2lab, lab2rgb, rgb2hsv, rgb2ycbcr,rgb2yuv

def vector_dot(m, v): 
    '''
    m 是变换矩阵，v 是图像矩阵（只有一个像素或整张图都可以）
    非常神奇，经过实际验证，其效果与逐像素去和变换矩阵相乘完全相同，速度还飞快
    '''
    return np.einsum('...ij,...j->...i', m, v)

def xyy_to_xyz100(xyy):
    x, y, Y = xyy
    return np.array([Y / y * x, Y, Y / y * (1 - x - y)]) * 100

def cs_convert(input_cs, out_cs, img, input_gamma = 1.0, output_gamma = 1.0):
    '''
    支持色彩空间：srgb, xyz, lab, hsv, ycbcr
    '''
    img = img**input_gamma

    if input_cs == 'srgb' and out_cs == 'xyz':
        img_out = colour.sRGB_to_XYZ(img)
    elif input_cs == 'xyz' and out_cs == 'srgb':
        img_out = colour.XYZ_to_sRGB(img)

    elif input_cs == 'srgb' and out_cs == 'lab':
        img_out = colour.XYZ_to_Lab(colour.sRGB_to_XYZ(img))
    elif input_cs == 'lab' and out_cs == 'srgb':
        img_out = colour.XYZ_to_sRGB(colour.Lab_to_XYZ(img))

    elif input_cs == 'srgb' and out_cs == 'hsv':
        img_out = colour.RGB_to_HSV(img)
    elif input_cs == 'hsv' and out_cs == 'srgb':
        img_out = colour.HSV_to_RGB(img)

    elif input_cs == 'srgb' and out_cs == 'ycbcr':
        img_out = colour.RGB_to_YCbCr(img)
    elif input_cs == 'ycbcr' and out_cs == 'srgb':
        img_out = colour.YCbCr_to_RGB(img)

    elif input_cs == 'srgb' and out_cs == 'srgb':
        img_out = img

    img_out = img_out**(1/output_gamma)

    return img_out

class MySrgb:
    def __init__(self):
        srgb_primaries_xyy = np.array([[0.64, 0.33, 0.212656], [0.30, 0.60, 0.715158], [0.15, 0.06, 0.072186]])
        srgb_primaries_xyz = xyy_to_xyz100(srgb_primaries_xyy.T)
        D65 = np.array([95.047, 100, 108.883]) #cie1931

        wp_correction = D65/np.sum(srgb_primaries_xyz, axis=1)
        self.mat = srgb_primaries_xyz * wp_correction
        self.mat /= 100

    def xyz_to_srgb(self, xyz):
        # return np.linalg.solve(self.mat, xyz / 100)
        self.mat = np.linalg.inv(self.mat)
        return np.dot(self.mat, xyz)

    def srgb_to_xyz(self, srgb):
        return 100*np.dot(self.mat, srgb)


trans = MySrgb()
print(trans.xyz_to_srgb(np.array([0.95047, 1.00000, 1.08883])))

# # img_in = colour.read_image('test_img/fruits.tif')
# img_in = colour.read_image('test_img/output.png')

# img_out = cs_convert('srgb', 'srgb', img_in, input_gamma=2.6, output_gamma=2.2)

# colour.write_image(img_out, 'test_img/output2.png')



