import math
import numpy as np
import os

from progress.bar import Bar

import kdtree

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

def LerpColor(beginning, end, value01):
	if value01 < 0 or value01 > 1:
		raise NameError("Improper Lerp")
	return Color(Lerp1D(beginning.r, end.r, value01), Lerp1D(beginning.g, end.g, value01), Lerp1D(beginning.b, end.b, value01))

def Lerp1D(beginning, end, value01):
	if value01 < 0 or value01 > 1:
		raise NameError("Improper Lerp")

	range = float(end) - float(beginning)
	return float(beginning) + float(range) * float(value01)

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
	
	@staticmethod
	def FromFloatArray(array):
		"""
		Creates Color from a list or tuple of 3 floats.
		"""
		return Color(array[0], array[1], array[2])

	def ToFloatArray(self):
		"""
		Creates a tuple of 3 floating point RGB values from the floating point color.
		"""
		return (self.r, self.g, self.b)

	def FormattedAsFloat(self, format = '{:.10f}'):
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
	def FromCompute(cubeSize, HALD_data):
		'''
		与 HALD 模块的生成 lut 部分对接
		'''
		HALDLattice = EmptyLatticeOfSize(cubeSize)
		for b in range(cubeSize):
			for g in range(cubeSize):
				for r in range(cubeSize):
					HALD_lattice = HALD_data[b*cubeSize*cubeSize+g*cubeSize+r]
					HALDLattice[r, g, b] = Color(HALD_lattice[0]/255, HALD_lattice[1]/255, HALD_lattice[2]/255)
		return LUT(HALDLattice, name = "HALD"+str(cubeSize))	

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

	def ColorFromColor(self, color):
		"""
		Returns what a color value should be transformed to when piped through the LUT.
		"""
		color = color.Clamped01()
		cubeSize = self.cubeSize
		return self.ColorAtInterpolatedLatticePoint(color.r * (cubeSize-1), color.g * (cubeSize-1), color.b * (cubeSize-1))

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

	def ColorAtInterpolatedLatticePoint(self, redPoint, greenPoint, bluePoint):
		"""
		Gets the interpolated color at an interpolated lattice point.
		"""
		cubeSize = self.cubeSize

		if 0 < redPoint > cubeSize-1 or 0 < greenPoint > cubeSize-1 or 0 < bluePoint > cubeSize-1:
			raise NameError("Point Out of Bounds")

		lowerRedPoint = Clamp(int(math.floor(redPoint)), 0, cubeSize-1)
		upperRedPoint = Clamp(lowerRedPoint + 1, 0, cubeSize-1)

		lowerGreenPoint = Clamp(int(math.floor(greenPoint)), 0, cubeSize-1)
		upperGreenPoint = Clamp(lowerGreenPoint + 1, 0, cubeSize-1)

		lowerBluePoint = Clamp(int(math.floor(bluePoint)), 0, cubeSize-1)
		upperBluePoint = Clamp(lowerBluePoint + 1, 0, cubeSize-1)

		C000 = self.ColorAtLatticePoint(lowerRedPoint, lowerGreenPoint, lowerBluePoint)
		C010 = self.ColorAtLatticePoint(lowerRedPoint, lowerGreenPoint, upperBluePoint)
		C100 = self.ColorAtLatticePoint(upperRedPoint, lowerGreenPoint, lowerBluePoint)
		C001 = self.ColorAtLatticePoint(lowerRedPoint, upperGreenPoint, lowerBluePoint)
		C110 = self.ColorAtLatticePoint(upperRedPoint, lowerGreenPoint, upperBluePoint)
		C111 = self.ColorAtLatticePoint(upperRedPoint, upperGreenPoint, upperBluePoint)
		C101 = self.ColorAtLatticePoint(upperRedPoint, upperGreenPoint, lowerBluePoint)
		C011 = self.ColorAtLatticePoint(lowerRedPoint, upperGreenPoint, upperBluePoint)

		C00  = LerpColor(C000, C100, 1.0 - (upperRedPoint - redPoint))
		C10  = LerpColor(C010, C110, 1.0 - (upperRedPoint - redPoint))
		C01  = LerpColor(C001, C101, 1.0 - (upperRedPoint - redPoint))
		C11  = LerpColor(C011, C111, 1.0 - (upperRedPoint - redPoint))

		C1 = LerpColor(C01, C11, 1.0 - (upperBluePoint - bluePoint))
		C0 = LerpColor(C00, C10, 1.0 - (upperBluePoint - bluePoint))

		return LerpColor(C0, C1, 1.0 - (upperGreenPoint - greenPoint))

	def Resize(self, newCubeSize):
		"""
		Scales the lattice to a new cube size.
		"""
		if newCubeSize == self.cubeSize:
			return self

		newLattice = EmptyLatticeOfSize(newCubeSize)
		ratio = float(self.cubeSize - 1.0) / float(newCubeSize-1.0)
		for x in range(newCubeSize):
			for y in range(newCubeSize):
				for z in range(newCubeSize):
					newLattice[x, y, z] = self.ColorAtInterpolatedLatticePoint(x*ratio, y*ratio, z*ratio)
		return LUT(newLattice, name = self.name + "_Resized"+str(newCubeSize))

	def CombineWithLUT(self, otherLUT):
		"""
		Combines LUT with another LUT.
		"""
		if self.cubeSize is not otherLUT.cubeSize:
			raise NameError("Lattice Sizes not equivalent")
		
		
		cubeSize = self.cubeSize
		newLattice = EmptyLatticeOfSize(cubeSize)
		
		for x in range(cubeSize):
			for y in range(cubeSize):
				for z in range(cubeSize):
					selfColor = self.lattice[x, y, z].Clamped01()
					newLattice[x, y, z] = otherLUT.ColorFromColor(selfColor)
		return LUT(newLattice, name = self.name + "+" + otherLUT.name)


	# 反求 lut 相关
	def _ResizeAndAddToData(self, newCubeSize, data):
		"""
		Scales the lattice to a new cube size.
		"""
		newLattice = EmptyLatticeOfSize(newCubeSize)
		ratio = float(self.cubeSize - 1.0) / float(newCubeSize-1.0)
		maxVal = newCubeSize-1

		bar = Bar("Building search tree", max = maxVal, suffix='%(percent)d%% - %(eta)ds remain')

		for x in range(newCubeSize):
			bar.next()
			for y in range(newCubeSize):
				for z in range(newCubeSize):
					data.add(self.ColorAtInterpolatedLatticePoint(x*ratio, y*ratio, z*ratio).ToFloatArray(), (RemapIntTo01(x,maxVal), RemapIntTo01(y,maxVal), RemapIntTo01(z,maxVal)))
		bar.finish()
		return data

	def Reverse(self):
		"""
		Reverses a LUT. Warning: This can take a long time depending on if the input/output is a bijection.
		"""
		tree = self.KDTree()
		newLattice = EmptyLatticeOfSize(self.cubeSize)
		maxVal = self.cubeSize - 1

		bar = Bar("Searching for matches", max = maxVal, suffix='%(percent)d%% - %(eta)ds remain')

		for x in range(self.cubeSize):
			bar.next()
			for y in range(self.cubeSize):
				for z in range(self.cubeSize):
					newLattice[x, y, z] = Color.FromFloatArray(tree.search_nn((RemapIntTo01(x,maxVal), RemapIntTo01(y,maxVal), RemapIntTo01(z,maxVal))).aux)
		bar.finish()
		return LUT(newLattice, name = self.name +"_Reverse")

	def KDTree(self):
		tree = kdtree.create(dimensions=3)
		
		tree = self._ResizeAndAddToData(self.cubeSize*3, tree)
	
		return tree