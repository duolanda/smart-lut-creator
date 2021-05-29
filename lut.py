import math
import numpy as np

import open3d as o3d

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
        # steps = np.linspace(0, 255, self.size, dtype=np.uint8)
        steps = np.linspace(0, 1, self.size)

        colors = np.array(
                [[[(r,g,b) for r in steps] for g in steps] for b in steps]
                ).reshape((self.swatch_count,3)).tolist()
        return colors



def empty_lattice_of_size(size):
    return np.zeros((size, size, size), object)

def remap_int_to_01(val, maxVal):
    return (float(val)/float(maxVal))

def remap_01_to_int(val, maxVal):
    return int(iround(float(val) * float(maxVal)))

def iround(num):
    if (num > 0):
        return int(num+.5)
    else:
        return int(num-.5)

def lerp_color(beginning, end, value01):
    if value01 < 0 or value01 > 1:
        raise NameError("Improper Lerp")
    return Color(lerp_1D(beginning.r, end.r, value01), lerp_1D(beginning.g, end.g, value01), lerp_1D(beginning.b, end.b, value01))

def lerp_1D(beginning, end, value01):
    if value01 < 0 or value01 > 1:
        raise NameError("Improper Lerp")

    range = float(end) - float(beginning)
    return float(beginning) + float(range) * float(value01)

def clamp(value, min, max):
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
    
    def clamped01(self):
        return Color(clamp(float(self.r), 0, 1), clamp(float(self.g), 0, 1), clamp(float(self.b), 0, 1))

    @staticmethod
    def from_RGB_integer(r, g, b, bitdepth):
        """
        Instantiates a floating point color from RGB integers at a bitdepth.
        """
        maxBits = 2**bitdepth - 1
        return Color(remap_int_to_01(r, maxBits), remap_int_to_01(g, maxBits), remap_int_to_01(b, maxBits))
    
    @staticmethod
    def from_float_array(array):
        """
        Creates Color from a list or tuple of 3 floats.
        """
        return Color(array[0], array[1], array[2])

    def to_float_array(self):
        """
        Creates a tuple of 3 floating point RGB values from the floating point color.
        """
        return (self.r, self.g, self.b)

    def formatted_as_float(self, format = '{:.10f}'):
        return format.format(self.r) + " " + format.format(self.g) + " " + format.format(self.b)
    
    def formatted_as_integer(self, maxVal):
        #rjust 用于数字右对齐
        #对其前：'0'
        #对齐后：'     0'
        rjustValue = len(str(maxVal)) + 1 
        return str(remap_01_to_int(self.r, maxVal)).rjust(rjustValue) + " " + str(remap_01_to_int(self.g, maxVal)).rjust(rjustValue) + " " + str(remap_01_to_int(self.b, maxVal)).rjust(rjustValue)

class LUT:
    def __init__(self, lattice, name = "Untitled LUT", lattice_np = None):
        '''
        lattice：Color 对象表示的晶格点
        size：LUT 大小，数字
        name：LUT 名称，字符串
        lattice_np：numpy 矩阵表示的晶格点，形状为(n,n,n,3)
        '''
        self.lattice = self if lattice_np is not None else lattice
        self._size=None
        if type(lattice_np) is np.ndarray:
            self.lattice_np = lattice_np
        else:
            self.lattice_np = self.lut_to_numpy(False)
        
        #self.size = 
        self.name = str(name)
    
    @property
    def size(self):
        if self._size is None:
            self._size= (getattr(self.lattice,"shape",None) or getattr(self.lattice_np,"shape"))[0]
        return self._size
            
    
    def __getitem__(self, value):
        lattice = self.lattice_np[(value[2], value[1], value[0])]
        return Color(lattice[0], lattice[1], lattice[2])
        
    

    @staticmethod
    def from_compute(size, HALD_data, name=None):
        '''
        与 HALD 模块的生成 lut 部分对接
        范围 0~1
        '''
        if name == None:
            name = "HALD"+str(size)
        HALD_data_reshape = np.array(HALD_data).reshape(size, size, size, 3)
        HALDLattice = empty_lattice_of_size(size)
        # for b in range(size):
        #     for g in range(size):
        #         for r in range(size):
        #             HALD_lattice = HALD_data[b*size*size+g*size+r]
        #             HALDLattice[r, g, b] = Color(HALD_lattice[0], HALD_lattice[1], HALD_lattice[2])
        return LUT(lattice = None, name = name, lattice_np = HALD_data_reshape)    

    

    def ColorFromColor(self, color):
        """
        Returns what a color value should be transformed to when piped through the LUT.
        """
        color = color.clamped01()
        size = self.size
        return self.ColorAtInterpolatedLatticePoint(color.r * (size-1), color.g * (size-1), color.b * (size-1))
        # 索引是 0~size-1，大小是 size

    def ColorAtLatticePoint(self, redPoint, greenPoint, bluePoint):
        """
        Returns a color at a specified lattice point - this value is pulled from the actual LUT file and is not interpolated.
        """
        size = self.size
        if redPoint > size-1 or greenPoint > size-1 or bluePoint > size-1:
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
        size = self.size

        if 0 < redPoint > size-1 or 0 < greenPoint > size-1 or 0 < bluePoint > size-1:
            raise NameError("Point Out of Bounds")

        lowerRedPoint = clamp(int(math.floor(redPoint)), 0, size-1)
        upperRedPoint = clamp(lowerRedPoint + 1, 0, size-1)

        lowerGreenPoint = clamp(int(math.floor(greenPoint)), 0, size-1)
        upperGreenPoint = clamp(lowerGreenPoint + 1, 0, size-1)

        lowerBluePoint = clamp(int(math.floor(bluePoint)), 0, size-1)
        upperBluePoint = clamp(lowerBluePoint + 1, 0, size-1)

        C000 = self.ColorAtLatticePoint(lowerRedPoint, lowerGreenPoint, lowerBluePoint)
        C010 = self.ColorAtLatticePoint(lowerRedPoint, lowerGreenPoint, upperBluePoint)
        C100 = self.ColorAtLatticePoint(upperRedPoint, lowerGreenPoint, lowerBluePoint)
        C001 = self.ColorAtLatticePoint(lowerRedPoint, upperGreenPoint, lowerBluePoint)
        C110 = self.ColorAtLatticePoint(upperRedPoint, lowerGreenPoint, upperBluePoint)
        C111 = self.ColorAtLatticePoint(upperRedPoint, upperGreenPoint, upperBluePoint)
        C101 = self.ColorAtLatticePoint(upperRedPoint, upperGreenPoint, lowerBluePoint)
        C011 = self.ColorAtLatticePoint(lowerRedPoint, upperGreenPoint, upperBluePoint)

        C00  = lerp_color(C000, C100, 1.0 - (upperRedPoint - redPoint))
        C10  = lerp_color(C010, C110, 1.0 - (upperRedPoint - redPoint))
        C01  = lerp_color(C001, C101, 1.0 - (upperRedPoint - redPoint))
        C11  = lerp_color(C011, C111, 1.0 - (upperRedPoint - redPoint))

        C1 = lerp_color(C01, C11, 1.0 - (upperBluePoint - bluePoint))
        C0 = lerp_color(C00, C10, 1.0 - (upperBluePoint - bluePoint))

        return lerp_color(C0, C1, 1.0 - (upperGreenPoint - greenPoint))

    def resize(self, newsize, rename = True):
        """
        Scales the lattice to a new cube size.
        """
        if newsize == self.size:
            return self

        if rename:
            new_name = self.name + "_Resized" + str(newsize)
        else:
            new_name = self.name

        newLattice = empty_lattice_of_size(newsize)
        ratio = float(self.size - 1.0) / float(newsize-1.0)
        for x in range(newsize):
            for y in range(newsize):
                for z in range(newsize):
                    newLattice[x, y, z] = self.ColorAtInterpolatedLatticePoint(x*ratio, y*ratio, z*ratio)
        return LUT(newLattice, name = new_name)

    def combine_with_lut(self, other_lut):
        """
        Combines LUT with another LUT.
        """
        if self.size is not other_lut.size:
            raise NameError("Lattice Sizes not equivalent")
        
        
        size = self.size
        newLattice = empty_lattice_of_size(size)
        
        for x in range(size):
            for y in range(size):
                for z in range(size):
                    selfColor = self.lattice[x, y, z].clamped01()
                    newLattice[x, y, z] = other_lut.ColorFromColor(selfColor)
        
        return LUT(newLattice, name = self.name + "+" + other_lut.name)


    def lut_to_numpy(self, bgr = False):
        lattice  = self.lattice
        size = self.size

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
        size = self.size
        lut = self.lattice_np

        norm = 1.0 / (size - 1) #归一化系数

        pcd=o3d.geometry.PointCloud()

        for b in range(0, size, step):
            for g in range(0, size, step):
                for r in range(0, size, step):
                    pcd.points.append( np.asarray([b,g,r],dtype=np.float64)*norm )
                    pcd.colors.append( lut[r, g, b].T ) #其实应该是bgr
                    
        mesh_frame = o3d.geometry.TriangleMesh.create_coordinate_frame(size=1, origin=[0, 0, 0]) #画轴
        # mesh_frame = o3d.geometry.TriangleMesh.create_coordinate_frame(size=1, origin=[0, 0, 1]) #通过旋转解决问题
        # R=mesh_frame.get_rotation_matrix_from_axis_angle(np.asarray([0,np.pi/2,0]))
        # mesh_frame.rotate(R)
        o3d.visualization.draw_geometries([pcd, mesh_frame])
