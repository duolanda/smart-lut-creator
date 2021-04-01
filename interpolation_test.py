from lut_IO import FromCubeFile
from colour import read_image, write_image
import numpy as np
import math
import time

def clamp(value, min, max):
	if min > max:
		raise NameError("Invalid Clamp Values")
	if value < min:
		return min
	if value > max:
		return max
	return value

def nearst_interpolation_np(lut, r, g, b):
    r,b = b,r

    l = lut.lattice_np
    r = np.round(r).astype(np.uint8)
    g = np.round(g).astype(np.uint8)
    b = np.round(b).astype(np.uint8)
    output = l[r,g,b]
    return output

def trilinear_interpolation(lut, r, g, b):
    '''
    三线性插值，但是有的地方会有黑点，经证实不是 numpy 的问题，原因不明
    '''

    r,b = b,r #因为 lattie_np 其实是按bgr来的，不交换的话会错

    size = lut.size

    r0 = np.clip(np.floor(r).astype(np.uint8), 0, size-1)
    r1 = np.clip(r0+1, 0, size-1)

    g0 = np.clip(np.floor(g).astype(np.uint8), 0, size-1)
    g1 = np.clip(g0+1, 0, size-1)

    b0 = np.clip(np.floor(b).astype(np.uint8), 0, size-1)
    b1 = np.clip(b0+1, 0, size-1)

    l = lut.lattice_np

    fr = (r-r0)/(r1-r0)
    fg = (g-g0)/(g1-g0)
    fb = (b-b0)/(b1-b0)

    fr[np.isnan(fr)]=1 #r = size-1 时会出现 0/0 得 nan，这些应该为 1
    fg[np.isnan(fg)]=1
    fb[np.isnan(fb)]=1


    fr = fr[:,:,np.newaxis] #增加一个维度，方便广播
    fg = fg[:,:,np.newaxis] 
    fb = fb[:,:,np.newaxis] 


    C000 = l[r0, g0, b0]
    C010 = l[r0, g1, b0]
    C100 = l[r1, g0, b0]
    C001 = l[r0, g0, b1]
    C110 = l[r1, g1, b0]
    C111 = l[r1, g1, b1]
    C101 = l[r1, g0, b1]
    C011 = l[r0, g1, b1]

    C00  = (1-fr)*C000 + fr*C100
    C10  = (1-fr)*C010 + fr*C110
    C01  = (1-fr)*C001 + fr*C101
    C11  = (1-fr)*C011 + fr*C111

    C0 = (1-fg)*C00 + fg*C10
    C1 = (1-fg)*C01 + fg*C11

    output = (1-fb)*C0 + fb*C1

    return output


def tetrahedral_interpolation(lut, r, g, b):
    '''
    四面体插值
    r,g,b 是要插值的晶格点，不是具体的颜色值，一般是个浮点数
    '''
    r,b = b,r #因为 lattie_np 其实是按bgr来的，不交换的话会错

    size = lut.size

    l = lut.lattice_np
    r0 = clamp(int(math.floor(r)), 0, size-1)
    r1 = clamp(r0+1, 0, size-1)

    g0 = clamp(int(math.floor(g)), 0, size-1)
    g1 = clamp(g0+1, 0, size-1)

    b0 = clamp(int(math.floor(b)), 0, size-1)
    b1 = clamp(b0+1, 0, size-1)

    fr = (r-r0)/(r1-r0)
    fg = (g-g0)/(g1-g0)
    fb = (b-b0)/(b1-b0)

    if fr > fg:
        if fg > fb: #\ 用来续行（Python不能无故换行）
            output = (1-fr)  * l[r0][g0][b0] \
                    +(fr-fg) * l[r1][g0][b0] \
                    +(fg-fb) * l[r1][g1][b0] \
                    +(fb)    * l[r1][g1][b1]
        elif fr > fb:
            output = (1-fr)  * l[r0][g0][b0] \
                    +(fr-fb) * l[r1][g0][b0] \
                    +(fb-fg) * l[r1][g0][b1] \
                    +(fg)    * l[r1][g1][b1]
        else:
            output = (1-fb)  * l[r0][g0][b0] \
                    +(fb-fr) * l[r0][g0][b1] \
                    +(fr-fg) * l[r1][g0][b1] \
                    +(fg)    * l[r1][g1][b1]
    else:
        if fb > fg: 
            output = (1-fb)  * l[r0][g0][b0] \
                    +(fb-fg) * l[r0][g0][b1] \
                    +(fg-fr) * l[r0][g1][b1] \
                    +(fr)    * l[r1][g1][b1]
        elif fb > fr:
            output = (1-fg)  * l[r0][g0][b0] \
                    +(fg-fb) * l[r0][g1][b0] \
                    +(fb-fr) * l[r0][g1][b1] \
                    +(fr)    * l[r1][g1][b1]
        else:
            output = (1-fg)  * l[r0][g0][b0] \
                    +(fg-fr) * l[r0][g1][b0] \
                    +(fr-fb) * l[r1][g1][b0] \
                    +(fb)    * l[r1][g1][b1]
    return output

def tetrahedral_interpolation_np(lut, r, g, b):
    '''
    四面体插值
    r,g,b 是要插值的晶格点，不是具体的颜色值，一般是个浮点数
    '''
    r,b = b,r #因为 lattie_np 其实是按bgr来的，不交换的话会错

    size = lut.size

    l = lut.lattice_np

    r0 = np.clip(np.floor(r).astype(np.uint8), 0, size-1)
    r1 = np.clip(r0+1, 0, size-1)

    g0 = np.clip(np.floor(g).astype(np.uint8), 0, size-1)
    g1 = np.clip(g0+1, 0, size-1)

    b0 = np.clip(np.floor(b).astype(np.uint8), 0, size-1)
    b1 = np.clip(b0+1, 0, size-1)

    fr = (r-r0)/(r1-r0)
    fg = (g-g0)/(g1-g0)
    fb = (b-b0)/(b1-b0)

    fr[np.isnan(fr)]=1 
    fg[np.isnan(fg)]=1
    fb[np.isnan(fb)]=1

    fr = fr[:,:,np.newaxis] 
    fg = fg[:,:,np.newaxis] 
    fb = fb[:,:,np.newaxis] 

    output = np.select([
        np.logical_and(fr > fg, fg > fb),
        np.logical_and(fr > fg, fr > fb),
        np.logical_and(fr > fg, np.logical_and(fg <= fb, fr <= fb)),
        np.logical_and(fr <= fg, fb > fg),
        np.logical_and(fr <= fg, fb > fr),
        np.logical_and(fr <= fg, np.logical_and(fb <= fg, fb <= fr)),
    ], [
        (1-fr)*l[r0,g0,b0] + (fr-fg)*l[r1,g0,b0] + (fg-fb)*l[r1,g1,b0] + (fb)*l[r1,g1,b1],
        (1-fr)*l[r0,g0,b0] + (fr-fb)*l[r1,g0,b0] + (fb-fg)*l[r1,g0,b1] + (fg)*l[r1,g1,b1],
        (1-fb)*l[r0,g0,b0] + (fb-fr)*l[r0,g0,b1] + (fr-fg)*l[r1,g0,b1] + (fg)*l[r1,g1,b1],
        (1-fb)*l[r0,g0,b0] + (fb-fg)*l[r0,g0,b1] + (fg-fr)*l[r0,g1,b1] + (fr)*l[r1,g1,b1],
        (1-fg)*l[r0,g0,b0] + (fg-fb)*l[r0,g1,b0] + (fb-fr)*l[r0,g1,b1] + (fr)*l[r1,g1,b1],
        (1-fg)*l[r0,g0,b0] + (fg-fr)*l[r0,g1,b0] + (fr-fb)*l[r1,g1,b0] + (fb)*l[r1,g1,b1],
    ])
    
    return output


def apply_lut(lut, img, method):
    '''
    使用不同的插值方法将 lut 应用到图片上
    - near：最近邻
    - tri：三线性插值
    - tet：四面体插值
    '''
    size = lut.size

    r,g,b = img[:,:,0], img[:,:,1], img[:,:,2]
    r = r * (size-1) 
    g = g * (size-1) 
    b = b * (size-1) 

    if method == 'tri':
        img = trilinear_interpolation(lut,r,g,b)
    elif method == 'tet':
        img = tetrahedral_interpolation_np(lut,r,g,b)
    elif method == 'near':
        img = nearst_interpolation_np(lut,r,g,b)


    write_image(img, 'new.png')




img = read_image('test_img/s-log.tif')
lut = FromCubeFile('test_lut/From_SLog2SGumut_To_LC-709_.cube')
# output = tetrahedral_interpolation(lut, 1.2, 1.5, 1.7)
# print(output)
# output2 = trilinear_interpolation(lut, 1.2, 1.5, 1.7)
# print(output2)
# output3 = nearst_interpolation(lut, 1.2, 1.5, 1.7)
# print(output3)

old = time.perf_counter()
apply_lut(lut, img, 'tet')
print(time.perf_counter()-old)