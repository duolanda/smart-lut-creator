import math
import numpy as np

class Lut:
    def __init__(self, size, image_size):
        self.size = size
        self.image_size = image_size
        self.swatch_count = pow(self.size, 3)
        self.columns = math.ceil(math.sqrt(self.swatch_count))
        self.swatch_size = self.image_size / self.columns

    def cell_center(self, i, size=1):
        """
        Compute x/y center position for a 3D lattice node by index
        """
        row, column = self.grid_coords(i)
        x = int(column * self.swatch_size + self.swatch_size / 2)
        y = int(row * self.swatch_size + self.swatch_size / 2)
        if size == 1:
            return (x, y)
        else:
            hs = size / 2
            return (x-hs, y-hs, x+hs, y+hs)

    def cell_bounds(self, i):
        row, column = self.grid_coords(i)
        x = column * self.swatch_size
        y = row * self.swatch_size
        return (x, y, x + self.swatch_size, y + self.swatch_size)

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