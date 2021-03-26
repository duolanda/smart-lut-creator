import math
import numpy as np
import matplotlib.pyplot as plt 
from mpl_toolkits.mplot3d import Axes3D

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
	def __init__(self, lattice, name = "Untitled LUT", lattice_np = None):
		'''
		lattice：Color 对象表示的晶格点
		cubeSize：LUT 大小，数字
		name：LUT 名称，字符串
		lattice_np：numpy 矩阵表示的晶格点，形状为(n,n,n,3)
		'''
		self.lattice = lattice
		self.cubeSize = self.lattice.shape[0]
		self.name = str(name)

		if type(lattice_np) is np.ndarray:
			self.lattice_np = lattice_np
		else:
			self.lattice_np = self.lut_to_numpy(False)
	

	@staticmethod
	def FromCompute(cubeSize, HALD_data, name=None):
		'''
		与 HALD 模块的生成 lut 部分对接
		范围 0~1
		'''
		if name == None:
			name = "HALD"+str(cubeSize)
		HALD_data_reshape = np.array(HALD_data).reshape(cubeSize, cubeSize, cubeSize, 3)
		HALDLattice = EmptyLatticeOfSize(cubeSize)
		for b in range(cubeSize):
			for g in range(cubeSize):
				for r in range(cubeSize):
					HALD_lattice = HALD_data[b*cubeSize*cubeSize+g*cubeSize+r]
					HALDLattice[r, g, b] = Color(HALD_lattice[0], HALD_lattice[1], HALD_lattice[2])
		return LUT(HALDLattice, name = name, lattice_np = HALD_data_reshape)	

	

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
		三线性插值
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

	def Resize(self, newCubeSize, rename = True):
		"""
		Scales the lattice to a new cube size.
		"""
		if newCubeSize == self.cubeSize:
			return self

		if rename:
			new_name = self.name + "_Resized" + str(newCubeSize)
		else:
			new_name = self.name

		newLattice = EmptyLatticeOfSize(newCubeSize)
		ratio = float(self.cubeSize - 1.0) / float(newCubeSize-1.0)
		for x in range(newCubeSize):
			for y in range(newCubeSize):
				for z in range(newCubeSize):
					newLattice[x, y, z] = self.ColorAtInterpolatedLatticePoint(x*ratio, y*ratio, z*ratio)
		return LUT(newLattice, name = new_name)

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


	def lut_to_numpy(self, bgr = False):
		lattice  = self.lattice
		size = self.cubeSize

		lut_np = np.zeros((size, size, size, 3))

		#适应不同应用的需要，这里的“bgr”并非是理解上的“bgr”，准确的说更像是描述是否符合lut的映射关系，即table[r][g][b]对应值还是table[b][g][r]对应值，一个便于表示映射，一个便于表示lut文件读写
		if bgr:
			for i in range(size):
				for j in range(size):
					for k in range(size):
						p = lattice[k][j][i] #注意，pylut对r、g、b索引的理解与cube文件顺序不同，所以这里是kji对ijk
						lut_np[i][j][k] = [p.b, p.g, p.r] 
		else:
			for i in range(size):
				for j in range(size):
					for k in range(size):
						p = lattice[k][j][i]
						lut_np[i][j][k] = [p.r, p.g, p.b] 

		self.lattice_np = lut_np
		return lut_np

	def visualize(self, step):
		'''
		将 LUT 绘制到散点图上的函数
		step 是采样间隔，全画上太多了
		'''
		size = self.cubeSize
		lut = self.lattice_np

		norm = 1.0 / (size - 1) #归一化系数
		fig = plt.figure()
		ax = Axes3D(fig)
		for b in range(0, size, step):
			for g in range(0, size, step):
				r = np.arange(0, size, step)
				ax.scatter(b * norm * np.ones(len(r)),
						g * norm * np.ones(len(r)),
						r * norm,
						c=lut[b, g, r],
						marker='o',
						alpha=1)
		ax.set_xlabel('B')
		ax.set_ylabel('G')
		ax.set_zlabel('R')
		plt.show()

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