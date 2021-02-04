from lut import LUT

# in_lut = LUT.FromCubeFile('test_lut/Lattice_33.cube')
# out_lut = in_lut.Resize(24) #经测试，不管是放大还是缩小，结果都与 lattice 完全一致
# out_lut.ToCubeFile('test_lut/smart_33 to 24.cube')


# lut1 = LUT.FromCubeFile('test_lut/lut1_exposure_1.5.cube')
# lut2 = LUT.FromCubeFile('test_lut/lut2_saturation_1.5.cube')
# out_lut = lut1.CombineWithLUT(lut2)
# out_lut.ToCubeFile('test_lut/lut3_combine.cube')


in_lut = LUT.FromCubeFile('test_lut/lattice_33.cube')
out_lut = in_lut.Reverse() 
out_lut.ToCubeFile('test_lut/lut3_33_reverse.cube')