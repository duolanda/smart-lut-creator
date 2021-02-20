from lut import LUT
import numpy as np


if __name__ == '__main__': 
    in_lut = LUT.FromCubeFile('test_lut/Lattice_cube3D_Resolve_33.cube')
    # in_lut = LUT.FromNuke3DLFile('test_lut/Lattice_3dl3D_Nuke_32.3dl')
    # in_lut = LUT.FromNuke3DLFile('test_lut/NukeGenerate.3dl')
    # in_lut = LUT.FromLustre3DLFile('test_lut/Lattice_3dl3D_Lustre_17.3dl')

    lut_np = lut_to_numpy(in_lut)
    print(lut_np)

    print(in_lut.ColorAtLatticePoint(1,0,0))

    # in_lut.ToCubeFile('test_lut/smart_cube.cube')
    # in_lut.ToNuke3DLFile('test_lut/smart_3dlNuke.3dl')
    # in_lut.ToLustre3DLFile('test_lut/smart_3dlLustre.3dl')

    # 当前问题，无法自定义范围，输出的 cube 范围只能是 0~1，Nuke 位深度只有 16，Lustre 只有 12
    # 事实上，输入的时候也没有读 cube 文件的范围
    # 精度也是 numpy 默认的浮点
