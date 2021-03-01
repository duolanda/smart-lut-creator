from lut import LUT
from lut import Color
import numpy as np
import os
import math

def Indices(cubeSize, maxVal):
	indices = []
	for i in Indices01(cubeSize):
		indices.append(int(i * (maxVal)))
	return indices

def Indices01(cubeSize): #这里的 01 是域为 0~1 的意思，即将其范围归一化到 0~1
	indices = []
	ratio = 1.0/float(cubeSize-1)
	for i in range(cubeSize):
		indices.append(float(i) * ratio)
	return indices

def _LatticeTo3DLString(lut, bitdepth):
        """
        Used for internal creating of 3DL files.
        """
        string = ""
        cubeSize = lut.cubeSize
        for currentCubeIndex in range(0, cubeSize**3):
            redIndex = currentCubeIndex // (cubeSize*cubeSize)
            greenIndex = ( (currentCubeIndex % (cubeSize*cubeSize)) // (cubeSize) )
            blueIndex = currentCubeIndex % cubeSize

            latticePointColor = lut.lattice[redIndex, greenIndex, blueIndex].Clamped01()
            
            string += latticePointColor.FormattedAsInteger(2**bitdepth-1) + "\n"
        
        return string


def FromIdentity(cubeSize):
    """
    Creates an indentity LUT of specified size.
    """
    identityLattice = EmptyLatticeOfSize(cubeSize)
    indices01 = Indices01(cubeSize)
    for r in range(cubeSize):
        for g in range(cubeSize):
            for b in range(cubeSize):
                identityLattice[r, g, b] = Color(indices01[r], indices01[g], indices01[b])
    return LUT(identityLattice, name = "Identity"+str(cubeSize))	   

def FromLustre3DLFile(lut_path):
    with open(lut_path, 'rt') as f:
        lut_lines = f.readlines()

    data_line_index = 0
    name = os.path.splitext(os.path.basename(lut_path))[0]
    size = -1

    for i in range(len(lut_lines)):
        line = lut_lines[i]
        if line.startswith('Mesh'):
            input_depth = int(line.split()[1])
            output_depth = int(line.split()[2])
            size = 2**input_depth + 1
            continue
        if len(line.split()) == 3: #数据行开始
            data_line_index = i
            break

    if size == -1:
        raise NameError("Invalid .3dl file.")

    lattice = np.zeros((size, size, size), object)
    current_index = 0
    
    for line in lut_lines[data_line_index:]:
        if line.startswith('#'):
            continue
        if len(line) > 0 and len(line.split()) == 3:
            red_value = line.split()[0]
            green_value = line.split()[1]
            blue_value = line.split()[2]

            red_index = current_index // (size*size) #r和b与cube文件是反着的
            green_index = ( (current_index % (size*size)) // (size) )
            blue_index = current_index % size

            lattice[red_index, green_index, blue_index] = Color.FromRGBInteger(red_value, green_value, blue_value, bitdepth = output_depth) 
            current_index += 1

    return LUT(lattice, name = name)


def FromNuke3DLFile(lut_path):
    with open(lut_path, 'rt') as f:
        lut_lines = f.readlines()

    data_line_index = 0
    name = os.path.splitext(os.path.basename(lut_path))[0]
    size = -1


    for i in range(len(lut_lines)):
        line = lut_lines[i]
        if "#" in line or line == "\n":
            continue
        else:
            # mesh 行
            output_depth = int(math.log(int(line.split()[-1])+1,2)) #根据mesh行最后一个数算深度，如255得出的就是8
            size = len(line.split()) #meshline 有几个数大小就是多少
            data_line_index = i+1
            break

    if size == -1:
        raise NameError("Invalid .3dl file.")

    lattice = np.zeros((size, size, size), object)
    current_index = 0

    for line in lut_lines[data_line_index:]:
        if line.startswith('#'):
            continue
        if len(line) > 0 and len(line.split()) == 3:
            red_value = line.split()[0]
            green_value = line.split()[1]
            blue_value = line.split()[2]

            red_index = current_index // (size*size) #注意这里r和b与cube文件是反着的
            green_index = ( (current_index % (size*size)) // (size) )
            blue_index = current_index % size

            lattice[red_index, green_index, blue_index] = Color.FromRGBInteger(red_value, green_value, blue_value, bitdepth = output_depth) #将整数换算到浮点
            current_index += 1
    return LUT(lattice, name = name)


def FromCubeFile(lut_path):
    with open(lut_path, 'rt') as f:
        lut_lines = f.readlines()

    data_line_index = 0
    name = os.path.splitext(os.path.basename(lut_path))[0]
    size = -1

    for i in range(len(lut_lines)):
        line = lut_lines[i]
        if line.startswith('TITLE'):
            name = line.split('"')[1]
            continue
        if line.startswith('LUT_3D_SIZE'):
            size = int(line.split()[1])
            continue
        if line.startswith('LUT_1D_SIZE'):
            raise ValueError("1D LUT cube files aren't supported")
        if line.startswith('LUT_3D_INPUT_RANGE'):    #找 input range 的，但目前只是找到这两个数，不做进一步处理
            domin_min = float(line.split()[1])
            domin_max = float(line.split()[2])
            continue
        if line.startswith('DOMAIN_MIN'):
            domin_min_rgb = [float(i) for i in line.split()[1:4]]
            continue
        if line.startswith('DOMAIN_MAX'):
            domin_min_rgb = [float(i) for i in line.split()[1:4]]
            continue
         

        try:
            float(line.partition(' ')[0])
        except ValueError:
            pass
        else:
            # 数据行开始
            data_line_index = i
            break
            

    if size == -1:
        raise NameError("No size found in the file")

    lattice = np.zeros((size, size, size), object)
    current_index = 0
    for line in lut_lines[data_line_index:]:
        if line.startswith('#'):
            continue
        if len(line) > 0 and len(line.split()) == 3:
            #lut 数据行
            red_value = float(line.split()[0])
            green_value = float(line.split()[1])
            blue_value = float(line.split()[2])

            red_index = current_index % size
            green_index = ( (current_index % (size*size)) // (size) ) 
            blue_index = current_index // (size*size)

            lattice[red_index, green_index, blue_index] = Color(red_value, green_value, blue_value)
            current_index += 1

    return LUT(lattice, name = name)


def ToLustre3DLFile(lut, fileOutPath, bitdepth = 12):
    cubeSize = lut.cubeSize
    inputDepth = math.log(cubeSize-1, 2)

    if int(inputDepth) != inputDepth:
        raise NameError("Invalid cube size for 3DL. Cube size must be 2^x + 1")

    lutFile = open(fileOutPath, 'w')

    lutFile.write("3DMESH\n")
    lutFile.write("Mesh " + str(int(inputDepth)) + " " + str(bitdepth) + "\n")
    lutFile.write(' '.join([str(int(x)) for x in Indices(cubeSize, 2**10 - 1)]) + "\n")#和深度无关，这一行都是 0~1023
    
    lutFile.write(_LatticeTo3DLString(lut, bitdepth))

    lutFile.write("\n#Tokens required by applications - do not edit\nLUT8\ngamma 1.0")

    lutFile.close()


def ToNuke3DLFile(lut, fileOutPath, bitdepth = 16):
    cubeSize = lut.cubeSize

    lutFile = open(fileOutPath, 'w')

    lutFile.write(' '.join([str(int(x)) for x in Indices(cubeSize, 2**bitdepth - 1)]) + "\n")

    lutFile.write(_LatticeTo3DLString(lut, bitdepth))

    lutFile.close()


def ToCubeFile(lut, cubeFileOutPath):
    cubeSize = lut.cubeSize
    cubeFile = open(cubeFileOutPath, 'w')
    cubeFile.write("LUT_3D_SIZE " + str(cubeSize) + "\n")
    
    for current_index in range(0, cubeSize**3):
        red_index = current_index % cubeSize
        green_index = ( (current_index % (cubeSize*cubeSize)) // (cubeSize) )
        blue_index = current_index // (cubeSize*cubeSize)

        latticePointColor = lut.lattice[red_index, green_index, blue_index].Clamped01()
        
        cubeFile.write( latticePointColor.FormattedAsFloat() )
        
        if(current_index != cubeSize**3 - 1):
            cubeFile.write("\n")

    cubeFile.close()


if __name__ == '__main__': 
    in_lut = FromCubeFile('test_lut/Lattice_cube3D_Resolve_33.cube')
    in_lut = FromNuke3DLFile('test_lut/Lattice_3dl3D_Nuke_32.3dl')
    in_lut = FromNuke3DLFile('test_lut/NukeGenerate.3dl')
    in_lut = FromLustre3DLFile('test_lut/Lattice_3dl3D_Lustre_17.3dl')


    print(in_lut.ColorAtLatticePoint(1,0,0))

    ToCubeFile(in_lut, 'test_lut/smart_cube.cube')
    ToNuke3DLFile(in_lut, 'test_lut/smart_3dlNuke.3dl')
    ToLustre3DLFile(in_lut, 'test_lut/smart_3dlLustre.3dl')

    # 当前问题，无法自定义范围，输出的 cube 范围只能是 0~1，Nuke 位深度只有 16，Lustre 只有 12
    # 事实上，输入的时候也没有读 cube 文件的范围
    # 精度也是 numpy 默认的浮点
