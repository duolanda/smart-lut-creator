from lut import LUT
import numpy as np

def lut_to_numpy(lut, bgr = False):
    lattice  = lut.lattice
    size = lut.cubeSize

    lut_np = np.zeros((size, size, size, 3))

    #适应不同应用的需要，这里的“bgr”并非是理解上的“bgr”，准确的说更像是描述是否符合lut的映射关系，即table[r][g][b]对应值还是table[b][g][r]对应值，一个便于表示映射，一个便于表示lut文件读写
    if bgr:
        for i in range(size):
            for j in range(size):
                for k in range(size):
                    p = lattice[i][j][k]
                    lut_np[i][j][k] = [p.b, p.g, p.r] 
    else:
         for i in range(size):
            for j in range(size):
                for k in range(size):
                    p = lattice[i][j][k]
                    lut_np[i][j][k] = [p.r, p.g, p.b] 
    return lut_np




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
