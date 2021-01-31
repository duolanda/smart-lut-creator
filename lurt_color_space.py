import colour
import numpy as np
from skimage.color import rgb2xyz, xyz2rgb, rgb2lab, lab2rgb, rgb2hsv, rgb2ycbcr,rgb2yuv

def vector_dot(m, v): 
    '''
    m 是变换矩阵，v 是图像矩阵（只有一个像素或整张图都可以）
    非常神奇，经过实际验证，其效果与逐像素去和变换矩阵相乘完全相同，速度还飞快
    '''
    return np.einsum('...ij,...j->...i', m, v)

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


def colorpy_mat():
    '''
    返回 srgb to xyz 矩阵
    '''
    # 注意，这里的是小写 x,y,z，ColorIO 是从 xyY 转成的大写 XYZ
    def xyz_color (x, y, z = None):
        '''Construct an xyz color.  If z is omitted, set it so that x+y+z = 1.0.'''
        if z == None:
            # choose z so that x+y+z = 1.0
            z = 1.0 - (x + y)
        rtn = np.array ([x, y, z])
        return rtn


    SGamut_Red   = xyz_color(0.73, 0.28)
    SGamut_Green = xyz_color(0.14, 0.855)
    SGamut_Blue  = xyz_color(0.1, -0.05)
    D65_White = xyz_color(0.95047, 1, 1.08883)  

    phosphor_red   = SGamut_Red   
    phosphor_green = SGamut_Green 
    phosphor_blue  = SGamut_Blue  
    white_point = D65_White 

    phosphor_matrix = np.column_stack ((phosphor_red, phosphor_green, phosphor_blue))
    # Determine intensities of each phosphor by solving:
    #     phosphor_matrix * intensity_vector = white_point
    intensities = np.linalg.solve (phosphor_matrix, white_point)
    # construct xyz_from_rgb matrix from the results
    specical_to_xyz_matrix = np.column_stack (
        (phosphor_red   * intensities [0],
         phosphor_green * intensities [1],
         phosphor_blue  * intensities [2]))

    return specical_to_xyz_matrix


sgamut_to_xyz_mat = colorpy_mat()
xyz_to_sgamut_mat = np.linalg.inv(sgamut_to_xyz_mat)


img_in = colour.read_image('test_img/s-log.tif')

# img_out = cs_convert('srgb', 'srgb', img_in, input_gamma=2.6, output_gamma=2.2)
img_out = vector_dot(sgamut_to_xyz_mat, img_in)
img_out = cs_convert('xyz', 'srgb', img_out)

colour.write_image(img_out, 'test_img/output2.png')



