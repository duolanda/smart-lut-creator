import colour
import numpy as np

from lut import LUT
from lut import LutM
from lut_color_enhance import rgb_color_enhance
from lut_color_space import cs_convert, gamut_convert, gamma_convert
from lut_IO import FromCubeFile, FromNuke3DLFile, FromLustre3DLFile, ToCubeFile, ToNuke3DLFile, ToLustre3DLFile
from auto_cb import simplest_cb

def test_hald():
    def generate_HALD(lut_size, output_path, name = None):
        """
        生成色彩图
        """
        if name == None:
            name = str(lut_size)

        lut = LutM(lut_size)
        colors = lut.generate_colors()
        image = Image.new('RGB', (lut.image_size, lut.image_size), (0, 0, 0))
        draw = ImageDraw.Draw(image)

        lookup_table = list(range(lut.swatch_count))

        for i, color in enumerate(colors):
            draw.rectangle(lut.cell_bounds(lookup_table[i]), fill=tuple(color))

        image.save(os.path.join(output_path,HALD_FILENAME.format(name)), "PNG")
        return None
    lut_size = 36
    data_dir = ''
    # image_size = 512
    # name = 'lut'
    generate_HALD(lut_size, data_dir)


def test_hald_np(lut_size):
    """
    生成色彩图，并将返回的 numpy 图片存到本地以供测试
    """

    lut = LutM(lut_size)
    colors = lut.generate_colors()
    image = np.zeros((1, lut.swatch_count, 3))

    for i in range(len(image[0])):
        image[0][i] = np.array(colors[i])

    hald_img = np.float64(image/255)
    colour.write_image(hald_img, 'test_hald.png')
    return hald_img


def test_compute():
    def compute_lut(hald_path, lut_size, out_path, name=None):
        """
        读取改变后的 HALD，计算 LUT，并保存为多种格式的文件。
        """

        if name == None:
            name = str(lut_size)

        lut = LutM(lut_size)

        image = Image.open(os.path.join(hald_path,HALD_FILENAME.format(name)))
        colors = []
        pixels = image.getdata()
        for pixel in pixels:
            r = pixel[0]/255
            g = pixel[1]/255
            b = pixel[2]/255
            color = (r,g,b)
            colors.append(color)
        out_lut = LUT.FromCompute(lut_size, colors)
        ToCubeFile(out_lut, out_path)
        return (lut)

    path = ''
    lut_size = 33
    out_path = 'test_lut/smart_cube.cube'
    compute_lut(path, lut_size, out_path)


def test_preview():
    '''
    测试 LUT 预览模块
    '''
    def apply_lut(lut_file, img_file):
        lut = FromCubeFile(lut_file)
        lut = load_lut(lut)

        img = Image.open(img_file)
        img.filter(lut).save('PILTest.bmp')
    # lut_file = 'test_lut/ARRI_LogC2Video_Classic709_davinci3d_33.cube'
    # img_file = 'test_img/Alexa.bmp'
    # apply_lut(lut_file, img_file)

    lut_file = 'gen_img/srgb to sgmaut lattice.cube'
    img_file = 'test_img/fruits.tif '
    apply_lut(lut_file, img_file)


def test_ce():
    '''
    测试色彩增强模块
    '''

    img_in = colour.read_image('test_img/fruits.tif')

    # img_out = rgb_color_enhance(img_in, brightness = 0.5) #-1~1
    # colour.write_image(img_out, 'test_img/ce-brightness.png')

    # img_out = rgb_color_enhance(img_in, exposure = 2.0) #-5~5
    # colour.write_image(img_out, 'test_img/ce-exposure.png')

    # img_out = rgb_color_enhance(img_in, warmth = 0.8) #-1~1
    # colour.write_image(img_out, 'test_img/ce-warmth.png')

    # img_out = rgb_color_enhance(img_in, contrast = 2.0) #-1~5
    # colour.write_image(img_out, 'test_img/ce-contrast.png')

    # img_out = rgb_color_enhance(img_in, saturation = 3.0) #-1~5
    # colour.write_image(img_out, 'test_img/ce-saturation.png')

    # img_out = rgb_color_enhance(img_in, vibrance = 0.5) #-1~1
    # colour.write_image(img_out, 'test_img/ce-vibrance.png')

    # img_out = rgb_color_enhance(img_in, tint = 0.3) #-0.5~0.5
    # colour.write_image(img_out, 'test_img/ce-tint.png')


def test_cs():
    '''
    测试色彩空间转换模块
    '''
    img_in = colour.read_image('test_img/lena_std.tif')
    # img_in = colour.read_image('test_img/fruits.tif')
    # img_in = colour.read_image('test_img/Alexa.jpg')
    # img_in = colour.read_image('test_img/s-log.tif')
    # img_in = colour.read_image('HALD_36.png')


    # img_out = cs_convert('srgb', 'srgb', img_in, input_gamma=2.6, output_gamma=2.2)

    # img_out = gamut_convert('sgamut', 'srgb', img_in)
    # img_out = gamma_convert(img_out, 'rec709', 1) #完成色域转换必须调 gamma

    # img_out = gamma_convert(img_in, input_gamma='rec709', output_gamma='slog3')
    # img_out = gamma_convert(img_in, input_gamma='slog3', output_gamma='rec709', clip=False)

    # img_out = gamut_convert('alexawg', 'srgb', img_in)
    # img_out = gamma_convert(img_out, 'srgb', 'rec709')

    img_out = gamma_convert(img_in, input_gamma='Sony S-Log3', output_gamma='sRGB')

    # img_out = gamma_convert(img_in, input_gamma='srgb', output_gamma='rec709')

    # img_out = gamut_convert('srgb', 'srgb', img_in, True, 'D65', 'D50')
    # img_out = gamma_convert(img_out, 'rec709', 'srgb')


    colour.write_image(img_out, 'test_img/output.png')


def test_editor():
    '''
    测试 LUT 编辑模块
    '''
    # in_lut = FromCubeFile('test_lut/Lattice_33.cube')
    # out_lut = in_lut.Resize(24) #经测试，不管是放大还是缩小，结果都与 lattice 完全一致
    # ToCubeFile(out_lut, 'test_lut/smart_33 to 24.cube')


    # lut1 = FromCubeFile('test_lut/lut1_exposure_1.5.cube')
    # lut2 = FromCubeFile('test_lut/lut2_saturation_1.5.cube')
    # out_lut = lut1.CombineWithLUT(lut2)
    # ToCubeFile(out_lut, 'test_lut/lut3_combine.cube')


    in_lut = FromCubeFile('test_lut/lattice_33.cube')
    out_lut = in_lut.Reverse() 
    ToCubeFile(out_lut, 'test_lut/lut3_33_reverse.cube')

def test_auto_cb():
    '''
    测试自动色彩均衡模块
    '''
    img = cv2.imread('test_img/alexa.jpg') #0~255
    out = simplest_cb(img, 1)
    cv2.imshow("before", img)
    cv2.imshow("after", out)
    cv2.waitKey(0)

def test_custom_wb():
    xy = colour.CCT_to_xy(5500)
    xyz = colour.xy_to_XYZ(xy)
    rgb = colour.XYZ_to_sRGB(xyz) #只是能将开尔文转到 rgb 而已，并不能应用到图像上
    print(rgb)


if __name__ == '__main__':
    test_hald_np(2)