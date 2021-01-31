import colour
import numpy as np
from skimage.color import rgb2xyz, xyz2rgb, rgb2lab, lab2rgb, rgb2hsv, rgb2ycbcr,rgb2yuv
import math

def vector_dot(m, v): 
    '''
    m 是变换矩阵，v 是图像矩阵（只有一个像素或整张图都可以）
    非常神奇，经过实际验证，其效果与逐像素去和变换矩阵相乘完全相同，速度还飞快
    '''
    return np.einsum('...ij,...j->...i', m, v)

def xyz_color (x, y, z = None):
    '''Construct an xyz color.  If z is omitted, set it so that x+y+z = 1.0.'''
    if z == None:
        # choose z so that x+y+z = 1.0
        z = 1.0 - (x + y)
    rtn = np.array ([x, y, z])
    return rtn

def slog3(img, to_linear):
    if to_linear:
        for i in range(len(img)):
            for j in range(len(img[i])):
                for k in range(3):
                    if img[i][j][k] >= 171.2102946929 / 1023:
                        img[i][j][k] = (10**((img[i][j][k]*1023-420)/261.5))*(0.18+0.01)-0.01
                    else:
                        img[i][j][k] = (img[i][j][k]*1023-95)*0.01125/(171.2102946929-95)
    else:
        for i in range(len(img)):
            for j in range(len(img[i])):
                for k in range(3):
                    if img[i][j][k] >= 0.01125:
                        img[i][j][k] = (420+math.log10((img[i][j][k]+0.01)/(0.18+0.01))*261.5)/1023
                    else:
                        img[i][j][k] = (img[i][j][k]*(171.2102946929-95)/0.01125+95)/1023
    return img

def logc(img, to_linear): 
    #取 EI = 800 时的值（曝光）
    cut = 0.010591 
    a = 5.555556 
    b = 0.052272 
    c = 0.247190 
    d = 0.385537 
    e = 5.367655 
    f = 0.092809 

    if to_linear:
        for i in range(len(img)):
            for j in range(len(img[i])):
                for k in range(3):
                    if img[i][j][k] > e*cut+f:
                        img[i][j][k] = (10**((img[i][j][k]-d)/c)-b)/a
                    else:
                        img[i][j][k] = (img[i][j][k]-f)/e
    else:
        for i in range(len(img)):
            for j in range(len(img[i])):
                for k in range(3):
                    if img[i][j][k] > cut:
                        img[i][j][k] = c*math.log10(a*img[i][j][k]+b)+d
                    else:
                        img[i][j][k] = e*img[i][j][k]+f
    return img

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

    elif input_cs == out_cs:
        img_out = img

    img_out = img_out**(1/output_gamma)

    return img_out

def gamut_convert(input_gamut, out_gamut, img, norm=True):
    #Sony S-Gamut/S-Gamut3
    sgamut_xy = [[0.73, 0.28], [0.14, 0.855], [0.1, -0.05]] # 这里的是小写 x,y 顺序为 RGB
    #Sony S-Gamut.Cine
    sgamutcine_xy = [[0.766, 0.275], [0.225, 0.8], [0.089, -0.087]] 
    #ALEXA Wide Gamut RGB
    alexawg_xy = [[0.6840, 0.3130], [0.2210, 0.8480], [0.0861, -0.1020]]

    #cie 1931
    w_D65 = [0.95047, 1, 1.08883]
    w_A = [109.850, 100, 35.585]
    w_C = [98.074, 100, 118.232]
    w_D50 = [96.422, 100, 82.521]
    w_D55 = [95.682, 100, 92.149]
    w_D65 = [95.047, 100, 108.883]
    w_D75 = [94.972, 100, 122.638]

    def colorpy_mat(xy, wp):
        '''
        返回指定色域到 XYZ 空间的矩阵
        '''
        #目前还缺少理论支撑
        #白点也没有分离出来（倒也没什么问题）
        #其实剩下的公式都可以直接去 lutcalc 找了，都不用白皮书

        xy = [xyz_color(xy[0][0], xy[0][1]), xyz_color(xy[1][0], xy[1][1]), xyz_color(xy[2][0], xy[2][1])]
        wp = xyz_color(wp[0], wp[1], wp[2])

        phosphor_red   = xy[0]
        phosphor_green = xy[1]
        phosphor_blue  = xy[2]  
        white_point = wp 

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

    if input_gamut == 'srgb' and out_gamut == 'sgamut': #srgb与rec.709色域相同，这里用srgb指代
        mat = np.linalg.inv(colorpy_mat(sgamut_xy, w_D65))
        img = cs_convert('srgb', 'xyz', img)
        img = vector_dot(mat, img)

    elif input_gamut == 'sgamut' and out_gamut == 'srgb':
        mat = colorpy_mat(sgamut_xy, w_D65)
        img = vector_dot(mat, img)
        img = cs_convert('xyz', 'srgb', img)

    elif input_gamut == 'srgb' and out_gamut == 'alexawg': #srgb与rec.709色域相同，这里用srgb指代
        mat = np.linalg.inv(colorpy_mat(alexawg_xy, w_D65))
        img = cs_convert('srgb', 'xyz', img)
        img = vector_dot(mat, img)

    elif input_gamut == 'alexawg' and out_gamut == 'srgb':
        mat = colorpy_mat(alexawg_xy, w_D65)
        img = vector_dot(mat, img)
        img = cs_convert('xyz', 'srgb', img)

    elif input_gamut == out_gamut:
        pass

    if norm:
        img = img/np.max(img)
        img[img<0] = 0
    
    return img

def gamma_convert(img, input_gamma = 1.0, output_gamma = 1.0, clip=True):
    #把 srgb 和 rec709 加上，就俩数的事
    if input_gamma == 'slog3':
        img = slog3(img, to_linear = True)
        img = img**(1/2.2) ##不加这个的话总是会太黑
    elif input_gamma == 'logc':
        img = logc(img, to_linear = True)
        img = img**(1/2.2)
    else:
        img = img ** input_gamma


    if output_gamma == 'slog3':
        img = img**2.2 ##不加这个的话总是会太白
        img = slog3(img, to_linear = False)
    elif output_gamma == 'loc':
        img = logc(img, to_linear = False)
    else:
        img = img ** (1/output_gamma)

    if clip:
        img[img>1] = 1
        img[img<0] = 0

    return img


img_in = colour.read_image('test_img/Alexa.jpg')
# img_in = colour.read_image('test_img/s-log.tif')


# img_out = cs_convert('srgb', 'srgb', img_in, input_gamma=2.6, output_gamma=2.2)

# img_out = gamut_convert('sgamut', 'srgb', img_in)
# img_out = gamma_convert(img_out, 2.2) #完成色域转换必须调 gamma

# img_out = gamma_convert(img_in, output_gamma='slog3')

# img_out = gamut_convert('alexawg', 'srgb', img_in)
# img_out = gamma_convert(img_out, 2.2)

img_out = gamma_convert(img_in, input_gamma='logc')

colour.write_image(img_out, 'test_img/output.png')



