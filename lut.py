import math
import numpy as np

class Lut:
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