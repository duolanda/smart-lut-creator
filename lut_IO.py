from lut import LUT
in_lut = LUT.FromCubeFile('test_lut/Lattice_cube3D_Resolve_33.cube')
# in_lut = LUT.FromNuke3DLFile('test_lut/Lattice_3dl3D_Nuke_32.3dl')
# in_lut = LUT.FromNuke3DLFile('test_lut/NukeGenerate.3dl')
# in_lut = LUT.FromLustre3DLFile('test_lut/Lattice_3dl3D_Lustre_17.3dl')

# print(in_lut.ColorAtLatticePoint(1,0,0))

in_lut.ToCubeFile('test_lut/smart_cube.cube')
in_lut.ToNuke3DLFile('test_lut/smart_3dlNuke.3dl')
in_lut.ToLustre3DLFile('test_lut/smart_3dlLustre.3dl')