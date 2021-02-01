import lut_color_space as cs
import lut_compute as cp
import colour

# # 色彩空间转换
# img_in = colour.read_image('HALD_36.png')
# img_out = cs.cs_convert('srgb', 'xyz', img_in)
# colour.write_image(img_out,'HALD_out.png')
# cp.compute_lut('', 36, 'gen_lut/srgb to xyz.cube', 'out')

# img_in = colour.read_image('HALD_36.png')
# img_out = cs.cs_convert('srgb', 'lab', img_in, clip = False)
# colour.write_image(img_out,'HALD_out.png')
# cp.compute_lut('', 36, 'gen_lut/srgb to lab.cube', 'out')

# img_in = colour.read_image('HALD_36.png')
# img_out = cs.cs_convert('srgb', 'hsv', img_in)
# colour.write_image(img_out,'HALD_out.png')
# cp.compute_lut('', 36, 'gen_lut/srgb to hsv.cube', 'out')

# img_in = colour.read_image('HALD_36.png')
# img_out = cs.cs_convert('srgb', 'ycbcr', img_in)
# colour.write_image(img_out,'HALD_out.png')
# cp.compute_lut('', 36, 'gen_lut/srgb to ycbcr.cube', 'out')

# img_in = colour.read_image('HALD_36.png')
# img_out = cs.cs_convert('xyz', 'srgb', img_in)
# colour.write_image(img_out,'HALD_out.png')
# cp.compute_lut('', 36, 'gen_lut/xyz to srgb.cube', 'out')

# img_in = colour.read_image('HALD_36.png')
# img_out = cs.cs_convert('srgb', 'srgb', img_in, input_gamma=2.6, output_gamma=2.2)
# colour.write_image(img_out,'HALD_out.png')
# cp.compute_lut('', 36, 'gen_lut/gamma 2.6 to 2.2.cube', 'out')

# # 色域转换
# img_in = colour.read_image('HALD_36.png')
# img_out = cs.gamut_convert('sgamut', 'srgb', img_in, False)
# img_out = cs.gamma_convert(img_out, 2.2, 1) #完成色域转换必须调 gamma
# colour.write_image(img_out,'HALD_out.png')
# cp.compute_lut('', 36, 'gen_lut/sgamut to srgb.cube', 'out')

img_in = colour.read_image('HALD_36.png')
img_out = cs.gamut_convert('srgb', 'sgamut', img_in)
img_out = cs.gamma_convert(img_out, 1, 2.2) 
colour.write_image(img_out,'HALD_out.png')
cp.compute_lut('', 36, 'gen_lut/srgb to sgamut.cube', 'out')

# img_in = colour.read_image('HALD_36.png')
# img_out = cs.gamut_convert('alexawg', 'srgb', img_in, False)
# img_out = cs.gamma_convert(img_out, 2.2, 1)
# colour.write_image(img_out,'HALD_out.png')
# cp.compute_lut('', 36, 'gen_lut/alexawg to srgb.cube', 'out')

# img_in = colour.read_image('HALD_36.png')
# img_out = cs.gamut_convert('srgb', 'alexawg', img_in)
# img_out = cs.gamma_convert(img_out, 1, 2.2) 
# colour.write_image(img_out,'HALD_out.png')
# cp.compute_lut('', 36, 'gen_lut/srgb to alexawg.cube', 'out')


# # gamma 转换

# img_in = colour.read_image('HALD_36.png')
# img_out = cs.gamma_convert(img_in, input_gamma='slog3', output_gamma='rec709')
# colour.write_image(img_out,'HALD_out.png')
# cp.compute_lut('', 36, 'gen_lut/slog3 to rec709.cube', 'out')

# img_in = colour.read_image('HALD_36.png')
# img_out = cs.gamma_convert(img_in, input_gamma='rec709', output_gamma='slog3')
# colour.write_image(img_out,'HALD_out.png')
# cp.compute_lut('', 36, 'gen_lut/rec709 to slog3.cube', 'out')

# img_in = colour.read_image('HALD_36.png')
# img_out = cs.gamma_convert(img_in, input_gamma='logc', output_gamma='rec709')
# colour.write_image(img_out,'HALD_out.png')
# cp.compute_lut('', 36, 'gen_lut/logc to rec709.cube', 'out')

# img_in = colour.read_image('HALD_36.png')
# img_out = cs.gamma_convert(img_in, input_gamma='rec709', output_gamma='logc')
# colour.write_image(img_out,'HALD_out.png')
# cp.compute_lut('', 36, 'gen_lut/rec709 to logc.cube', 'out')

# img_in = colour.read_image('HALD_36.png')
# img_out = cs.gamma_convert(img_in, input_gamma='rec709', output_gamma='srgb')
# colour.write_image(img_out,'HALD_out.png')
# cp.compute_lut('', 36, 'gen_lut/rec709 to srgb.cube', 'out')




