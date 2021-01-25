import math
import numpy as np
import os

class LutM: #来自于 lut_maker 的 lut 类，未来可能与来自 pylut 的 lut 类合并
    def __init__(self, size):
        self.size = size
        self.swatch_count = size ** 3
        self.image_size = math.ceil(self.swatch_count**0.5)
        self.columns = self.image_size

    def cell_bounds(self, i):
        row, column = self.grid_coords(i)
        x = column
        y = row
        return (x, y, x + 1, y + 1)

    def grid_coords(self, i):
        row = math.floor(i / self.columns)
        column = i % self.columns
        return (row,column)

    def lattice_coords(self, i):
        column = i % self.size
        row = math.floor(i / self.size) % self.size
        z = math.floor(i / pow(self.size, 2))
        return (column, row, z)

    def generate_colors(self):
        """
        Generate and return the appropriate RGB colors for each node in a uniform lattice.
        """
        steps = np.linspace(0, 255, self.size, dtype=np.uint8)
        colors = np.array(
                [[[(r,g,b) for r in steps] for g in steps] for b in steps]
                ).reshape((self.swatch_count,3)).tolist()
        return colors



def EmptyLatticeOfSize(cubeSize):
	return np.zeros((cubeSize, cubeSize, cubeSize), object)

def Indices01(cubeSize): #这里的 01 是域为 0~1 的意思，即将其范围归一化到 0~1
	indices = []
	ratio = 1.0/float(cubeSize-1)
	for i in range(cubeSize):
		indices.append(float(i) * ratio)
	return indices

def Indices(cubeSize, maxVal):
	indices = []
	for i in Indices01(cubeSize):
		indices.append(int(i * (maxVal)))
	return indices

def RemapIntTo01(val, maxVal):
	return (float(val)/float(maxVal))

def Remap01ToInt(val, maxVal):
	return int(iround(float(val) * float(maxVal)))

def iround(num):
	if (num > 0):
		return int(num+.5)
	else:
		return int(num-.5)

def Clamp(value, min, max):
	if min > max:
		raise NameError("Invalid Clamp Values")
	if value < min:
		return float(min)
	if value > max:
		return float(max)
	return value

class Color:
	def __init__(self, r, g, b):
		self.r = r
		self.g = g
		self.b = b

	def __str__(self):
		return "(" + str(self.r) + ", " + str(self.g) + ", " + str(self.b) + ")"
	
	def Clamped01(self):
		return Color(Clamp(float(self.r), 0, 1), Clamp(float(self.g), 0, 1), Clamp(float(self.b), 0, 1))

	@staticmethod
	def FromRGBInteger(r, g, b, bitdepth):
		"""
		Instantiates a floating point color from RGB integers at a bitdepth.
		"""
		maxBits = 2**bitdepth - 1
		return Color(RemapIntTo01(r, maxBits), RemapIntTo01(g, maxBits), RemapIntTo01(b, maxBits))

	def FormattedAsFloat(self, format = '{:1.6f}'):
		return format.format(self.r) + " " + format.format(self.g) + " " + format.format(self.b)
	
	def FormattedAsInteger(self, maxVal):
		#rjust 用于数字右对齐
		#对其前：'0'
		#对齐后：'     0'
		rjustValue = len(str(maxVal)) + 1 
		return str(Remap01ToInt(self.r, maxVal)).rjust(rjustValue) + " " + str(Remap01ToInt(self.g, maxVal)).rjust(rjustValue) + " " + str(Remap01ToInt(self.b, maxVal)).rjust(rjustValue)

class LUT:
	def __init__(self, lattice, name = "Untitled LUT"):
		self.lattice = lattice
		self.cubeSize = self.lattice.shape[0]
		self.name = str(name)
	
	def _LatticeTo3DLString(self, bitdepth):
			"""
			Used for internal creating of 3DL files.
			"""
			string = ""
			cubeSize = self.cubeSize
			for currentCubeIndex in range(0, cubeSize**3):
				redIndex = currentCubeIndex // (cubeSize*cubeSize)
				greenIndex = ( (currentCubeIndex % (cubeSize*cubeSize)) // (cubeSize) )
				blueIndex = currentCubeIndex % cubeSize

				latticePointColor = self.lattice[redIndex, greenIndex, blueIndex].Clamped01()
				
				string += latticePointColor.FormattedAsInteger(2**bitdepth-1) + "\n"
			
			return string

	@staticmethod
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

	@staticmethod
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

		lattice = EmptyLatticeOfSize(cubeSize)
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

	@staticmethod
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

		lattice = EmptyLatticeOfSize(cubeSize)
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

	@staticmethod
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

		lattice = EmptyLatticeOfSize(cubeSize)
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

	def ToLustre3DLFile(self, fileOutPath, bitdepth = 12):
		cubeSize = self.cubeSize
		inputDepth = math.log(cubeSize-1, 2)

		if int(inputDepth) != inputDepth:
			raise NameError("Invalid cube size for 3DL. Cube size must be 2^x + 1")

		lutFile = open(fileOutPath, 'w')

		lutFile.write("3DMESH\n")
		lutFile.write("Mesh " + str(int(inputDepth)) + " " + str(bitdepth) + "\n")
		lutFile.write(' '.join([str(int(x)) for x in Indices(cubeSize, 2**10 - 1)]) + "\n")#和深度无关，这一行都是 0~1023
		
		lutFile.write(self._LatticeTo3DLString(bitdepth))

		lutFile.write("\n#Tokens required by applications - do not edit\nLUT8\ngamma 1.0")

		lutFile.close()

	def ToNuke3DLFile(self, fileOutPath, bitdepth = 16):
		cubeSize = self.cubeSize

		lutFile = open(fileOutPath, 'w')

		lutFile.write(' '.join([str(int(x)) for x in Indices(cubeSize, 2**bitdepth - 1)]) + "\n")

		lutFile.write(self._LatticeTo3DLString(bitdepth))

		lutFile.close()
	
	def ToCubeFile(self, cubeFileOutPath):
		cubeSize = self.cubeSize
		cubeFile = open(cubeFileOutPath, 'w')
		cubeFile.write("LUT_3D_SIZE " + str(cubeSize) + "\n")
		
		for currentCubeIndex in range(0, cubeSize**3):
			redIndex = currentCubeIndex % cubeSize
			greenIndex = ( (currentCubeIndex % (cubeSize*cubeSize)) // (cubeSize) )
			blueIndex = currentCubeIndex // (cubeSize*cubeSize)

			latticePointColor = self.lattice[redIndex, greenIndex, blueIndex].Clamped01()
			
			cubeFile.write( latticePointColor.FormattedAsFloat() )
			
			if(currentCubeIndex != cubeSize**3 - 1):
				cubeFile.write("\n")

		cubeFile.close()

	def ColorAtLatticePoint(self, redPoint, greenPoint, bluePoint):
		"""
		Returns a color at a specified lattice point - this value is pulled from the actual LUT file and is not interpolated.
		"""
		cubeSize = self.cubeSize
		if redPoint > cubeSize-1 or greenPoint > cubeSize-1 or bluePoint > cubeSize-1:
			raise NameError("Point Out of Bounds: (" + str(redPoint) + ", " + str(greenPoint) + ", " + str(bluePoint) + ")")
		redPoint = int(redPoint)
		greenPoint = int(greenPoint)
		bluePoint = int(bluePoint)
		return self.lattice[redPoint, greenPoint, bluePoint]
