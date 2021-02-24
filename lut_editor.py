from lut import LUT
from lut_IO import FromCubeFile, ToCubeFile

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