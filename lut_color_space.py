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

def logx(a, b):
    '''
    换底公式，a 是底，b 是真数
    '''
    return np.log(b)/np.log(a)

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
        choicelist = [(420+np.log10((img+0.01)/(0.18+0.01))*261.5)/1023, 
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
        choicelist = [c*np.log10(a*img+b)+d, 
                    e*img+f]
        img = np.select([img > cut, True], choicelist)
    return img

def clog(img, to_linear):
    if to_linear:
        choicelist = [(10**((img - 0.1251224801564)/0.45310179472141) - 1)/10.1596, 
                    (img*1023-95)*0.01125/(171.2102946929-95)]
        img = np.select([img >= 0.00391002619746, True], choicelist)
    else:
        choicelist = [(0.45310179472141 * np.log10((img * 10.1596) + 1)/np.log(10)) + 0.1251224801564, #np.log 是 ln
                    (img + 0.0467265867)/0.3734467748]
        img = np.select([img >= -0.0452664, True], choicelist)
    return img

def vlog(img, to_linear):
    b = 0.00873
    c = 0.241514
    d = 0.598206
    if to_linear:
        choicelist = [10**((img-d)/c)-b, 
                    (img-0.125)/5.6]
        img = np.select([img >= 0.181, True], choicelist)
    else:
        choicelist = [c*np.log10(img+b)+d,
                    5.6*img+0.125]
        img = np.select([img >= 0.01, True], choicelist)
    return img

def flog(img, to_linear):
    a = 0.555556
    b = 0.009468
    c = 0.344676
    d = 0.790453
    e = 8.735631
    f = 0.092864
    if to_linear:
        choicelist = [(10**((img-d)/c))/a-b/a, 
                    (img-f)/e]
        img = np.select([img >= 0.100537775223865, True], choicelist)
    else:
        choicelist = [c*np.log10(a*img+b)+d,
                    e*img+f]
        img = np.select([img >= 0.00089, True], choicelist)
    return img

def redlog3g10(img, to_linear):
    a = 0.224282
    b = 155.975327
    c = 0.01
    g = 15.1927
    if to_linear:
        choicelist = [(10**(img/a)-1)/b, 
                    (img/g)-c]
        img = np.select([img >= 0, True], choicelist)
        img = img-c
    else:
        img = img+c
        choicelist = [a*np.log10((img*b)+1),
                    img*g]
        img = np.select([img >= 0, True], choicelist)
    return img

def other_log(img, to_linear, name):
    if name == "BMD Pocket Film":
        m = [ 0.195367159 / 0.9, -0.014273567 / 0.9, 0.36274758, 1.05345192 * 0.9, 10, 0.63659829, 0.027616437, 0.096214896, 0.004523664 * 0.9 ]
    elif name == "BMD Film":
        m = [ 0.261115778 * 0.9, -0.024248528 * 0.9, 0.367608577, 0.86786483 / 0.9, 10, 0.644065346, 0.03135747, 0.114002127, 0.005519226 / 0.9 ]
    elif name == "BMD Film 4K":
        m = [ 0.37237694 * 0.9, -0.034580801 * 0.9, 0.582240088, 2.617961052 / 0.9, 10, 0.461883884, 0.231964429, 0.10772883, 0.005534931 / 0.9 ]
    elif name == "BMD Film 4.6K":
        m = [ 0.195367159 / 0.9, -0.014273567 / 0.9, 0.36274758, 1.05345192 * 0.9, 10, 0.63659829, 0.027616437, 0.096214896, 0.004523664 * 0.9 ]
    # elif name == "GoPro Pro Tune":
    #     m = [ 0, 0, 876/1023, 53.39427221, 113, 64/1023, 1, 0, 0 ]
    else:
        raise("Not supported gamma")


    if to_linear:
        choicelist = [(10**((img - m[5])/m[2])-m[6])/m[3], 
                    m[0]*img+m[1]]
        img = np.select([img >= m[7], True], choicelist)
    else:
        choicelist = [(m[2]*logx(m[4], img*m[3]+m[6]))+m[5], 
                    (img-m[1])/m[0]]
        img = np.select([img >= m[8], True], choicelist)
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
        img = np.clip(img, 0, 1)

    return img_out

def gamut_convert(in_gamut, out_gamut, img, norm=True, clip=True, in_wp='D65', out_wp='D65'):
    '''
    色域和白点转换函数，
    - in_gamut 和 out_gamut 为字符串
    '''
    #存储不同色域 RGB 的 xy 坐标值的字典
    gxydict = {
        'sRGB': [[0.64, 0.33], [0.3, 0.6], [0.15, 0.06]],
        'Sony S-Gamut/S-Gamut3': [[0.73, 0.28], [0.14, 0.855], [0.1, -0.05]], # 这里的是小写 x,y 顺序为 RGB
        'Sony S-Gamut/S-Gamut3.Cine': [[0.766, 0.275], [0.225, 0.8], [0.089, -0.087]],
        'Arri Wide Gamut':[[0.6840, 0.3130], [0.2210, 0.8480], [0.0861, -0.1020]],
        'Canon Cinema Gamut':[[0.74, 0.27], [0.17, 1.14], [0.08, -0.10]],
        'Panasonic V-Gamut':[[0.730,0.280], [0.165,0.840], [0.100,-0.030]],
        'BMDFilm 4K(Legacy)':[[1.065485164,0.395870911], [0.369219642,0.778131628], [0.095906214,0.033373394]], #指定白点
        'Fuji F-Log Gamut':[[0.70800,0.29200], [0.17000,0.79700], [0.13100,0.04600]],
        'RedWideGamutRGB':[[0.780308,0.304253], [0.121595,1.493994], [0.095612,-0.084589]],
        'DJI D-Gamut':[[0.71,0.31], [0.21,0.88], [0.09,-0.08]],
        'GoPro ProTune Native':[[0.70419975,0.19595152], [0.33147178,0.98320117], [0.1037611,-0.04367584]], #d60
    }

    #cie 1931 分别是 XYZ，Y归一化为1
    wpdict = {
        'D65':[0.95047, 1, 1.08883],
        'A':[1.0985, 1, 0.35585],
        'C':[0.98074, 1, 1.18232],
        'D50':[0.96422, 1, 0.82521],
        'D55':[0.95682, 1, 0.92149],
        'D60':[0.9523, 1, 1.00856], #待验证
        'D75':[0.94972, 1, 1.22638],
        'BMDFilm 4K(Legacy)':[0.94960328, 1, 1.08308685],
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
        mat_i = colorpy_mat(gxydict[in_gamut], wpdict[in_wp])
        mat_o = np.linalg.inv(colorpy_mat(gxydict[out_gamut], wpdict[out_wp]))
        mat = np.dot(mat_o, mat_i)
        img = vector_dot(mat, img)


    if norm:
        img = img/np.max(img)
        img[img<0] = 0

    if clip:
        img = np.clip(img, 0, 1)

    
    return img

def gamma_convert(img, input_gamma = 2.2, output_gamma = 2.2, clip=True):
    '''
    Gamma 转换函数
    '''
    # 导入进来的图像默认根据推测是rec709，而不是linear，而所有变换公式都是针对linear的，所以如果不输入gamma就给2.2，但需要注意，rec709并非就是2.2，这里只是为了节省时间做的近似，肉眼不怎么看得出来差异
    if input_gamma == output_gamma:
        return img

    if input_gamma == 'Sony S-Log3':
        img = slog3(img, to_linear = True)
    elif input_gamma == 'Arri LogC EI 800':
        img = logc(img, to_linear = True)
    elif input_gamma == 'sRGB':
        img = srgb(img, to_linear = True)
    elif input_gamma == 'Rec.709':
        img = rec709(img, to_linear = True)
    elif input_gamma == 'Linear':
        img = img ** 1 
    elif input_gamma == 'Canon C-Log':
        img = clog(img, to_linear = True)
    elif input_gamma == 'Panasonic V-Log':
        img = vlog(img, to_linear = True)
    elif input_gamma == 'Fujifilm F-Log':
        img = flog(img, to_linear = True)
    elif input_gamma == 'BMD Pocket Film':
        img = other_log(img, to_linear = True, name='BMD Pocket Film')
    elif input_gamma == 'BMD Film':
        img = other_log(img, to_linear = True, name='BMD Film')
    elif input_gamma == 'BMD Film 4K':
        img = other_log(img, to_linear = True, name='BMD Film')
    elif input_gamma == 'BMD Film 4.6K':
        img = other_log(img, to_linear = True, name='BMD Film')
    # elif input_gamma == 'GoPro Protune':
    #     img = other_log(img, to_linear = True, name='GoPro Pro Tune')
    elif input_gamma == 'Red Log3G10':
        img = redlog3g10(img, to_linear = True)
        
    else:
        img = img ** input_gamma

    if output_gamma == 'Sony S-Log3':
        img = slog3(img, to_linear = False)
    elif output_gamma == 'Arri LogC EI 800':
        img = logc(img, to_linear = False)
    elif output_gamma == 'sRGB':
        img = srgb(img, to_linear = False)
    elif output_gamma == 'Rec.709':
        img = rec709(img, to_linear = False)
    elif output_gamma == 'Canon C-Log':
        img = clog(img, to_linear = False)
    elif output_gamma == 'Panasonic V-Log':
        img = vlog(img, to_linear = False)
    elif output_gamma == 'Fujifilm F-Log':
        img = flog(img, to_linear = False)
    elif output_gamma == 'Linear':
        img = img ** 1 
    elif output_gamma == 'BMD Pocket Film':
        img = other_log(img, to_linear = False, name='BMD Pocket Film')
    elif output_gamma == 'BMD Film':
        img = other_log(img, to_linear = False, name='BMD Film')
    elif output_gamma == 'BMD Film 4K':
        img = other_log(img, to_linear = False, name='BMD Film')
    elif output_gamma == 'BMD Film 4.6K':
        img = other_log(img, to_linear = False, name='BMD Film')
    # elif output_gamma == 'GoPro Protune':
    #     img = other_log(img, to_linear = False, name='GoPro Pro Tune')
    elif output_gamma == 'Red Log3G10':
        img = redlog3g10(img, to_linear = False)
    else:
        img = img ** (1/output_gamma)

    if clip:
        img = np.clip(img, 0, 1)

    return img





