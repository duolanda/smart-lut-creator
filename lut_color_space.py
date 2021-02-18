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

def srgb(img, to_linear):
    if to_linear:
        choicelist = [img / 12.92, ((img + 0.055) / 1.055) ** 2.4]
        img = np.select([img <= 0.04045, True], choicelist) #其实就是对满足条件的执行 choicelist 里的第一个计算，不满足的执行第二个
    else:
        choicelist = [img * 12.92, (img ** (1 / 2.4)) * 1.055 - 0.055]
        img = np.select([img <= 0.0031308, True], choicelist)
    return img

def rec709(img, to_linear):
    if to_linear:
        choicelist = [img / 4.5, ((img + 0.099) / 1.099) ** (1/0.45)]
        img = np.select([img <= 0.081, True], choicelist)
    else:
        choicelist = [img * 4.5, (img ** (0.45)) * 1.099 - 0.099]
        img = np.select([img <= 0.018, True], choicelist)
    return img

def slog3(img, to_linear):
    if to_linear:
        choicelist = [(10**((img*1023-420)/261.5))*(0.18+0.01)-0.01, 
                    (img*1023-95)*0.01125/(171.2102946929-95)]
        img = np.select([img >= 171.2102946929 / 1023, True], choicelist)
    else:
        choicelist = [(420+math.log10((img+0.01)/(0.18+0.01))*261.5)/1023, 
                    (img*(171.2102946929-95)/0.01125+95)/1023]
        img = np.select([img >= 0.01125, True], choicelist)
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
        choicelist = [(10**((img-d)/c)-b)/a, 
                    (img-f)/e]
        img = np.select([img > e*cut+f, True], choicelist)
    else:
        choicelist = [c*math.log10(a*img+b)+d, 
                    e*img[i][j][k]+f]
        img = np.select([img > cut, True], choicelist)
    return img

def cs_convert(input_cs, out_cs, img, input_gamma = 1.0, output_gamma = 1.0, clip=True):
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

    if clip:
        img_out[img_out>1] = 1
        img_out[img_out<0] = 0

    return img_out

def gamut_convert(in_gamut, out_gamut, img, norm=True, in_wp='D65', out_wp='D65'):
    '''
    色域转换函数，
    - in_gamut 和 out_gamut 为字符串
    '''
    #存储不同色域 RGB 的 xy 坐标值的字典
    gxydict = {
        #sRGB
        'srgb': [[0.64, 0.33], [0.3, 0.6], [0.15, 0.06]],
        #Sony S-Gamut/S-Gamut3
        'sgamut': [[0.73, 0.28], [0.14, 0.855], [0.1, -0.05]], # 这里的是小写 x,y 顺序为 RGB
        #Sony S-Gamut.Cine
        'sgamutcine': [[0.766, 0.275], [0.225, 0.8], [0.089, -0.087]],
        #ALEXA Wide Gamut RGB
        'alexawg':[[0.6840, 0.3130], [0.2210, 0.8480], [0.0861, -0.1020]],
    }

    #cie 1931
    wpdict = {
        'D65':[0.95047, 1, 1.08883],
        'A':[1.0985, 1, 0.35585],
        'C':[0.98074, 1, 1.18232],
        'D50':[0.96422, 1, 0.82521],
        'D55':[0.95682, 1, 0.92149],
        'D75':[0.94972, 1, 1.22638],
    }

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
        

    if in_gamut == out_gamut and in_wp == out_wp:
        return img
    else:
        mat = colorpy_mat(gxydict[in_gamut], wpdict[in_wp])
        img = vector_dot(mat, img)
        mat = np.linalg.inv(colorpy_mat(gxydict[out_gamut], wpdict[out_wp]))
        img = vector_dot(mat, img)


    if norm:
        img = img/np.max(img)
        img[img<0] = 0
    
    return img

def gamma_convert(img, input_gamma = 2.2, output_gamma = 2.2, clip=True):
    # 导入进来的图像默认根据推测是rec709，而不是linear，而所有变换公式都是针对linear的，所以如果不输入gamma就给2.2，但需要注意，rec709并非就是2.2，这里只是为了节省时间做的近似，肉眼不怎么看得出来差异
    if input_gamma == output_gamma:
        return img

    if input_gamma == 'slog3':
        img = slog3(img, to_linear = True)
    elif input_gamma == 'logc':
        img = logc(img, to_linear = True)
    elif input_gamma == 'srgb':
        img = srgb(img, to_linear = True)
    elif input_gamma == 'rec709':
        img = rec709(img, to_linear = True)
    else:
        img = img ** input_gamma

    if output_gamma == 'slog3':
        img = slog3(img, to_linear = False)
    elif output_gamma == 'logc':
        img = logc(img, to_linear = False)
    elif output_gamma == 'srgb':
        img = srgb(img, to_linear = False)
    elif output_gamma == 'rec709':
        img = rec709(img, to_linear = False)
    else:
        img = img ** (1/output_gamma)

    if clip:
        np.clip(img, 0, 1)

    return img


if __name__ == '__main__': #如果不用这个，导包的时候下面的语句也会执行
    # img_in = colour.read_image('test_img/lena_std.tif')
    # img_in = colour.read_image('test_img/fruits.tif')
    img_in = colour.read_image('test_img/Alexa.jpg')
    # img_in = colour.read_image('test_img/s-log.tif')
    # img_in = colour.read_image('HALD_36.png')


    # img_out = cs_convert('srgb', 'srgb', img_in, input_gamma=2.6, output_gamma=2.2)

    # img_out = gamut_convert('sgamut', 'srgb', img_in)
    # img_out = gamma_convert(img_out, 'rec709', 1) #完成色域转换必须调 gamma

    # img_out = gamma_convert(img_in, input_gamma='rec709', output_gamma='slog3')
    # img_out = gamma_convert(img_in, input_gamma='slog3', output_gamma='rec709', clip=False)

    img_out = gamut_convert('alexawg', 'srgb', img_in)
    img_out = gamma_convert(img_out, 'srgb', 'rec709')

    # img_out = gamma_convert(img_in, input_gamma='logc', output_gamma='rec709')

    # img_out = gamma_convert(img_in, input_gamma='srgb', output_gamma='rec709')

    # img_out = gamut_convert('srgb', 'srgb', img_in, True, 'D65', 'D50')
    # img_out = gamma_convert(img_out, 1, 'rec709')


    colour.write_image(img_out, 'test_img/output.png')



