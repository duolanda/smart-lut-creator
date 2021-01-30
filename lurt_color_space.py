import colour
import cv2
import numpy as np
from skimage import io
from skimage.color import rgb2xyz, xyz2rgb, rgb2lab


img_in = colour.read_image('test_img/smpte_digital_leader_4k_24fps_2d_ar185_srgb.tif')

# trans = np.asarray([0.4185, -0.1587, -0.0828, -0.0912, 0.2524, 0.0157, 0.0009, -0.0025, 0.1786]).reshape(3,3)

# for i in range(len(img_in)):
#     if(i%100 == 0):
#         print(i)
#     for j in range(len(img_in[i])):
#         img_in[i][j] = np.dot(trans, img_in[i][j])

img_out = colour.XYZ_to_Lab(colour.sRGB_to_XYZ(img_in))
# img_out = img_in
colour.write_image(img_out, 'output.tif')



'''
尝试 skimage
'''
img = io.imread('test_img/smpte_digital_leader_4k_24fps_2d_ar185_srgb.tif')
img_xyz = rgb2lab(img)
io.imsave('test-2.png', img_xyz)

'''
尝试 opencv
'''
# img = cv2.imread('test_img/smpte_digital_leader_4k_24fps_2d_ar185_srgb.tif')
# xyz = cv2.cvtColor(img, cv2.COLOR_RGB2XYZ)
# cv2.imwrite('test.png', xyz)
