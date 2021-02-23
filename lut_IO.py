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

def FromLustre3DLFile(lutFilePath):
    lutFile = open(lutFilePath, 'rU')
    lutFileLines = lutFile.readlines()
    lutFile.close()

    meshLineIndex = 0
    cubeSize = -1

    for line in lutFileLines:
        if "Mesh" in line:
            inputDepth = int(line.split()[1])
            outputDepth = int(line.split()[2])
            cubeSize = 2**inputDepth + 1
            break
        meshLineIndex += 1

    if cubeSize == -1:
        raise NameError("Invalid .3dl file.")

    lattice = np.zeros((cubeSize, cubeSize, cubeSize), object)
    currentCubeIndex = 0
    
    for line in lutFileLines[meshLineIndex+1:]:
        if len(line) > 0 and len(line.split()) == 3 and "#" not in line:
            #valid cube line
            redValue = line.split()[0]
            greenValue = line.split()[1]
            blueValue = line.split()[2]

            redIndex = currentCubeIndex // (cubeSize*cubeSize) #r和b与cube文件是反着的
            greenIndex = ( (currentCubeIndex % (cubeSize*cubeSize)) // (cubeSize) )
            blueIndex = currentCubeIndex % cubeSize

            lattice[redIndex, greenIndex, blueIndex] = Color.FromRGBInteger(redValue, greenValue, blueValue, bitdepth = outputDepth) 
            currentCubeIndex += 1

    return LUT(lattice, name = os.path.splitext(os.path.basename(lutFilePath))[0])


def FromNuke3DLFile(lutFilePath):
    lutFile = open(lutFilePath, 'rU') 
    lutFileLines = lutFile.readlines()
    lutFile.close()

    meshLineIndex = 0
    cubeSize = -1

    for line in lutFileLines:
        if "#" in line or line == "\n":
            meshLineIndex += 1
        else:
            break #不加break是不合理的， 不然只要整个文件后面有空行或注释都会+1

    outputDepth = int(math.log(int(lutFileLines[meshLineIndex].split()[-1])+1,2)) #根据mesh行最后一个数算深度，如255得出的就是8
    cubeSize = len(lutFileLines[meshLineIndex].split()) #meshline 有几个数大小就是多少
    

    if cubeSize == -1:
        raise NameError("Invalid .3dl file.")

    lattice = np.zeros((cubeSize, cubeSize, cubeSize), object)
    currentCubeIndex = 0

    # for line in lutFileLines[meshLineIndex+1:]:
    for line in lutFileLines[meshLineIndex+1:]:
        # print line
        if len(line) > 0 and len(line.split()) == 3 and "#" not in line:
            #valid cube line
            redValue = line.split()[0]
            greenValue = line.split()[1]
            blueValue = line.split()[2]

            redIndex = currentCubeIndex // (cubeSize*cubeSize) #注意这里r和b与cube文件是反着的
            greenIndex = ( (currentCubeIndex % (cubeSize*cubeSize)) // (cubeSize) )
            blueIndex = currentCubeIndex % cubeSize

            lattice[redIndex, greenIndex, blueIndex] = Color.FromRGBInteger(redValue, greenValue, blueValue, bitdepth = outputDepth) #将整数换算到浮点
            currentCubeIndex += 1
    return LUT(lattice, name = os.path.splitext(os.path.basename(lutFilePath))[0])


def FromCubeFile(cubeFilePath):
    cubeFile = open(cubeFilePath, 'rU') #只读、通用换行
    cubeFileLines = cubeFile.readlines()
    cubeFile.close()

    cubeSizeLineIndex = 0
    cubeSize = -1

    for line in cubeFileLines:
        if "LUT_3D_SIZE" in line and line[0] != '#': #加一个注释判断
            cubeSize = int(line.split()[1])
            break
        cubeSizeLineIndex += 1

    #找 input range 的，但目前只是找到这两个数，不做进一步处理
    for i in range(len(cubeFileLines)):
        line = cubeFileLines[i]
        if 'LUT_3D_INPUT_RANGE' in line and line[0] != '#':
            domin_min = float(line.split()[1])
            domin_max = float(line.split()[2])
            cubeSizeLineIndex = i
            break

    if cubeSize == -1:
        raise NameError("Invalid .cube file.")

    lattice = np.zeros((cubeSize, cubeSize, cubeSize), object)
    currentCubeIndex = 0
    for line in cubeFileLines[cubeSizeLineIndex+1:]:
        if len(line) > 0 and len(line.split()) == 3 and "#" not in line:
            #lut 数据行
            redValue = float(line.split()[0])
            greenValue = float(line.split()[1])
            blueValue = float(line.split()[2])

            redIndex = currentCubeIndex % cubeSize
            greenIndex = ( (currentCubeIndex % (cubeSize*cubeSize)) // (cubeSize) ) 
            blueIndex = currentCubeIndex // (cubeSize*cubeSize)

            lattice[redIndex, greenIndex, blueIndex] = Color(redValue, greenValue, blueValue)
            currentCubeIndex += 1

    return LUT(lattice, name = os.path.splitext(os.path.basename(cubeFilePath))[0])


def ToLustre3DLFile(lut, fileOutPath, bitdepth = 12):
    cubeSize = lut.cubeSize
    inputDepth = math.log(cubeSize-1, 2)

    if int(inputDepth) != inputDepth:
        raise NameError("Invalid cube size for 3DL. Cube size must be 2^x + 1")

    lutFile = open(fileOutPath, 'w')

    lutFile.write("3DMESH\n")
    lutFile.write("Mesh " + str(int(inputDepth)) + " " + str(bitdepth) + "\n")
    lutFile.write(' '.join([str(int(x)) for x in Indices(cubeSize, 2**10 - 1)]) + "\n")#和深度无关，这一行都是 0~1023
    
    lutFile.write(lut._LatticeTo3DLString(bitdepth))

    lutFile.write("\n#Tokens required by applications - do not edit\nLUT8\ngamma 1.0")

    lutFile.close()


def ToNuke3DLFile(lut, fileOutPath, bitdepth = 16):
    cubeSize = lut.cubeSize

    lutFile = open(fileOutPath, 'w')

    lutFile.write(' '.join([str(int(x)) for x in Indices(cubeSize, 2**bitdepth - 1)]) + "\n")

    lutFile.write(lut._LatticeTo3DLString(bitdepth))

    lutFile.close()


def ToCubeFile(lut, cubeFileOutPath):
    cubeSize = lut.cubeSize
    cubeFile = open(cubeFileOutPath, 'w')
    cubeFile.write("LUT_3D_SIZE " + str(cubeSize) + "\n")
    
    for currentCubeIndex in range(0, cubeSize**3):
        redIndex = currentCubeIndex % cubeSize
        greenIndex = ( (currentCubeIndex % (cubeSize*cubeSize)) // (cubeSize) )
        blueIndex = currentCubeIndex // (cubeSize*cubeSize)

        latticePointColor = lut.lattice[redIndex, greenIndex, blueIndex].Clamped01()
        
        cubeFile.write( latticePointColor.FormattedAsFloat() )
        
        if(currentCubeIndex != cubeSize**3 - 1):
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
