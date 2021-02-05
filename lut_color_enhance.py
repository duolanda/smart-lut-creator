from math import sin

import colour
import numpy 


def _rgb_to_yuv(r, g, b):
    y = (0.299 * r) + (0.587 * g) + (0.114 * b)
    u = (1.0 / 1.772) * (b - y)
    v = (1.0 / 1.402) * (r - y)
    return y, u, v


def _yuv_to_rgb(y, u, v):
    r = 1.402 * v + y
    g = (y - (0.299 * 1.402 / 0.587) * v - (0.114 * 1.772 / 0.587) * u)
    b = 1.772 * u + y
    return r, g, b


def rgb_color_enhance(source,
                      brightness=0, exposure=0, contrast=0, warmth=0,
                      saturation=0, vibrance=0):

    if brightness:
        if not -1.0 <= brightness <= 1.0:
            raise ValueError("Brightness should be from -1.0 to 1.0")

    if exposure:
        if not -5.0 <= exposure <= 5.0:
            raise ValueError("Exposure should be from -5.0 to 5.0")
        exposure = 2**exposure

    if contrast:
        if not -1.0 <= contrast <= 5.0 :
            raise ValueError("Contrast should be from -1.0 to 5.0")
        contrast = contrast + 1

    if warmth:
        if warmth < 0:
            warmth = (warmth * -0.0588, warmth * -0.1569, warmth * 0.1255)
        else:
            warmth = (warmth * 0.1765, warmth * -0.1255, warmth * 0.0902)

    if saturation:
        if not -1.0 <= saturation <= 5.0:
            raise ValueError("Saturation should be from -1.0 to 5.0")

    if vibrance:
        if not -1.0 <= vibrance <= 5.0:
            raise ValueError("Vibrance should be from -1.0 to 1.0")
        vibrance = vibrance * 2

    output = source.copy() #直接改 source 的话会把 img_in 也改掉
    r = output[:,:,0]
    g = output[:,:,1]
    b = output[:,:,2]

    if contrast:
        r = (r - 0.5) * contrast + 0.5
        g = (g - 0.5) * contrast + 0.5
        b = (b - 0.5) * contrast + 0.5

    if saturation:
        avg_v = r * 0.2126 + g * 0.7152 + b * 0.0722
        r += (r - avg_v) * saturation
        g += (g - avg_v) * saturation
        b += (b - avg_v) * saturation

    if vibrance:
        max_v = numpy.maximum.reduce([r, g, b])
        avg_v = r * 0.2126 + g * 0.7152 + b * 0.0722
        r += (r - max_v) * (max_v - avg_v) * vibrance
        g += (g - max_v) * (max_v - avg_v) * vibrance
        b += (b - max_v) * (max_v - avg_v) * vibrance

    if exposure:
        r = 1.0 - (1.0 - r).clip(0) ** exposure
        g = 1.0 - (1.0 - g).clip(0) ** exposure
        b = 1.0 - (1.0 - b).clip(0) ** exposure

    if brightness:
        r += brightness
        g += brightness
        b += brightness

    if warmth:
        y, u, v = _rgb_to_yuv(r, g, b)
        scale = numpy.sin(y * 3.14159)
        y += scale * warmth[0]
        u += scale * warmth[1]
        v += scale * warmth[2]
        r, g, b = _yuv_to_rgb(y, u, v)

    output[:,:,0], output[:,:,1], output[:,:,2] = r, g, b
    output = output.clip(0,1)
    return output

if __name__ == '__main__': 
    img_in = colour.read_image('test_img/fruits.tif')

    img_out = rgb_color_enhance(img_in, brightness = 0.5) #-1~1
    colour.write_image(img_out, 'test_img/ce-brightness.png')

    img_out = rgb_color_enhance(img_in, exposure = 2.0) #-5~5
    colour.write_image(img_out, 'test_img/ce-exposure.png')

    img_out = rgb_color_enhance(img_in, warmth = 0.5) #-1~1
    colour.write_image(img_out, 'test_img/ce-warmth.png')

    img_out = rgb_color_enhance(img_in, contrast = 3.0) #-1~5
    colour.write_image(img_out, 'test_img/ce-contrast.png')

    img_out = rgb_color_enhance(img_in, saturation = 3.0) #-1~5
    colour.write_image(img_out, 'test_img/ce-saturation.png')

    img_out = rgb_color_enhance(img_in, vibrance = 0.5) #-1~1
    colour.write_image(img_out, 'test_img/ce-vibrance.png')
