from lut_IO import FromCubeFile
from colour import read_image, LUT3D
from pillow_lut import identity_table
import numpy as np
import itertools
from PIL import Image, ImageFilter


def _inter_linear(d, v0, v1):
    return v0 + (v1 - v0) * d

def _points_shift_np(size, points, left, right):
    size1D, size2D, size3D = size

    index1D = points[:, 0] * (size1D - 1)
    index2D = points[:, 1] * (size2D - 1)
    index3D = points[:, 2] * (size3D - 1)
    idx1D = index1D.astype(np.int32).clip(left, size1D - 1 - right)
    idx2D = index2D.astype(np.int32).clip(left, size2D - 1 - right)
    idx3D = index3D.astype(np.int32).clip(left, size3D - 1 - right)
    shift1D = np.subtract(index1D, idx1D, index1D).reshape(idx1D.shape[0], 1)
    shift2D = np.subtract(index2D, idx2D, index2D).reshape(idx2D.shape[0], 1)
    shift3D = np.subtract(index3D, idx3D, index3D).reshape(idx3D.shape[0], 1)
    idx = idx1D + idx2D * size1D + idx3D * size1D * size2D
    return idx, shift1D, shift2D, shift3D

def _sample_lut_linear_np(lut, points):
    s1D, s2D, s3D = lut.size
    s12D = s1D * s2D

    idx, shift1D, shift2D, shift3D = _points_shift_np(lut.size, points, 0, 1)
    table = np.array(lut.table, copy=False, dtype=np.float32)
    table = table.reshape(s1D * s2D * s3D, lut.channels)

    return _inter_linear(shift3D,
        _inter_linear(shift2D,
            _inter_linear(shift1D, table[idx + 0], table[idx + 1]),
            _inter_linear(shift1D, table[idx + s1D + 0],
                          table[idx + s1D + 1]),
        ),
        _inter_linear(shift2D,
            _inter_linear(shift1D, table[idx + s12D + 0],
                          table[idx + s12D + 1]),
            _inter_linear(shift1D, table[idx + s12D + s1D + 0],
                          table[idx + s12D + s1D + 1]),
        ),
    )

def resize_lut(source, target_size, interp=Image.LINEAR,
               cls=ImageFilter.Color3DLUT):
    """Resizes given lookup table to new size using interpolation.

    :param source: Source lookup table, ``ImageFilter.Color3DLUT`` object.
    :param target_size: Size of the resulting lookup table.
    :param interp: Interpolation type, ``Image.LINEAR`` or ``Image.CUBIC``.
                   Linear is default. Cubic is dramatically slower.
    """
    size1D, size2D, size3D = cls._check_size(target_size)

    if np and interp == Image.LINEAR:
        shape = (size1D * size2D * size3D, 3)
        b, g, r = np.mgrid[
            0 : 1 : size3D*1j,
            0 : 1 : size2D*1j,
            0 : 1 : size1D*1j
        ].astype(np.float32)
        points = np.stack((r, g, b), axis=-1).reshape(shape)
        points = _sample_lut_linear_np(source, points)

        table = points.reshape(points.size)

    else:  # Native implementation
        table = []
        for b in range(size3D):
            for g in range(size2D):
                for r in range(size1D):
                    point = (r / (size1D-1), g / (size2D-1), b / (size3D-1))
                    table.extend(sample_lut(source, point))

    return cls((size1D, size2D, size3D), table,
               channels=source.channels, target_mode=source.mode,
               _copy_table=False)


#####################################################################################
def tsplit(a):
    """
    >>> a = np.array(
    ...     [[0, 0, 0],
    ...      [1, 1, 1],
    ...      [2, 2, 2],
    ...      [3, 3, 3],
    ...      [4, 4, 4],
    ...      [5, 5, 5]]
    ... )
    >>> tsplit(a)
    array([[ 0.,  1.,  2.,  3.,  4.,  5.],
           [ 0.,  1.,  2.,  3.,  4.,  5.],
           [ 0.,  1.,  2.,  3.,  4.,  5.]])
    """

    a = np.asarray(a)

    return np.array([a[..., x] for x in range(a.shape[-1])])

def tstack(a):
    """
    Examples
    --------
    >>> a = np.arange(0, 6)
    >>> tstack([a, a, a])
    array([[ 0.,  0.,  0.],
           [ 1.,  1.,  1.],
           [ 2.,  2.,  2.],
           [ 3.,  3.,  3.],
           [ 4.,  4.,  4.],
           [ 5.,  5.,  5.]])
    """

    return np.concatenate([x[..., np.newaxis] for x in a], axis=-1)

def linear_conversion(a, old_range, new_range):
    """
    Performs a simple linear conversion of given array between the old and new
    ranges.

    Parameters
    ----------
    a : array_like
        Array to perform the linear conversion onto.
    old_range : array_like
        Old range.
    new_range : array_like
        New range.

    Returns
    -------
    ndarray
        Linear conversion result.

    Examples
    --------
    >>> a = np.linspace(0, 1, 10)
    >>> linear_conversion(a, np.array([0, 1]), np.array([1, 10]))
    array([  1.,   2.,   3.,   4.,   5.,   6.,   7.,   8.,   9.,  10.])
    """

    a = np.asarray(a, dtype='float64')

    in_min, in_max = tsplit(old_range)
    out_min, out_max = tsplit(new_range)

    return ((a - in_min) / (in_max - in_min)) * (out_max - out_min) + out_min

def vertices_and_relative_coordinates(V_xyz, table):
    """
    Computes the vertices coordinates and indexes relative :math:`V_{xyzr}`
    coordinates from given :math:`V_{xyzr}` values and interpolation table.

    Parameters
    ----------
    V_xyz : array_like
        :math:`V_{xyz}` values to transform to indexes relative
        :math:`V_{xyzr}` values.
    table : array_like
        4-Dimensional (NxNxNx3) interpolation table.

    Returns
    -------
    tuple
        Vertices coordinates and indexes relative :math:`V_{xyzr}` coordinates.

    Examples
    --------
    >>> import os
    >>> import colour
    >>> path = os.path.join(
    ...     os.path.dirname(__file__),'..', 'io', 'luts', 'tests', 'resources',
    ...     'iridas_cube', 'Colour_Correct.cube')
    >>> LUT = colour.read_LUT(path)
    >>> table = LUT.table
    >>> prng = np.random.RandomState(4)
    >>> V_xyz = colour.algebra.random_triplet_generator(3, random_state=prng)
    >>> print(V_xyz)  # doctest: +ELLIPSIS
    [[ 0.9670298...  0.7148159...  0.9762744...]
     [ 0.5472322...  0.6977288...  0.0062302...]
     [ 0.9726843...  0.2160895...  0.2529823...]]
    >>> vertices, V_xyzr = vertices_and_relative_coordinates(V_xyz, table)
    >>> print(vertices)
    [[[ 0.833311  0.833311  0.833311]
      [ 0.349416  0.657749  0.041083]
      [ 0.797894 -0.035412 -0.035412]]
    <BLANKLINE>
     [[ 0.833311  0.833311  1.249963]
      [ 0.340435  0.743769  0.340435]
      [ 0.752767 -0.028479  0.362144]]
    <BLANKLINE>
     [[ 0.707102  1.110435  0.707102]
      [ 0.344991  1.050213 -0.007621]
      [ 0.633333  0.316667  0.      ]]
    <BLANKLINE>
     [[ 0.519714  0.744729  0.744729]
      [ 0.314204  1.120871  0.314204]
      [ 0.732278  0.315626  0.315626]]
    <BLANKLINE>
     [[ 1.06561   0.648957  0.648957]
      [ 0.589195  0.589195  0.139164]
      [ 1.196841 -0.053117 -0.053117]]
    <BLANKLINE>
     [[ 1.        0.666667  1.      ]
      [ 0.594601  0.594601  0.369586]
      [ 1.162588 -0.050372  0.353948]]
    <BLANKLINE>
     [[ 0.894606  0.894606  0.66959 ]
      [ 0.663432  0.930188  0.12992 ]
      [ 1.038439  0.310899 -0.05287 ]]
    <BLANKLINE>
     [[ 1.249966  1.249966  1.249966]
      [ 0.682749  0.991082  0.374416]
      [ 1.131225  0.29792   0.29792 ]]]
    >>> print(V_xyzr)  # doctest: +ELLIPSIS
    [[ 0.9010895...  0.1444479...  0.9288233...]
     [ 0.6416967...  0.0931864...  0.0186907...]
     [ 0.9180530...  0.6482684...  0.7589470...]]
    """

    V_xyz = np.clip(V_xyz, 0, 1)
    table = np.asarray(table, dtype='float64')

    V_xyz = np.reshape(V_xyz, (-1, 3))

    # Indexes computations where ``i_m`` is the maximum index value on a given
    # table axis, ``i_f`` and ``i_c`` respectively the floor and ceiling
    # indexes encompassing a given V_xyz value.
    i_m = np.array(table.shape[0:-1]) - 1
    i_f = np.floor(V_xyz * i_m).astype('int64')
    i_c = np.clip(i_f + 1, 0, i_m)

    # Relative to indexes ``V_xyz`` values.
    V_xyzr = i_m * V_xyz - i_f

    i_f_c = i_f, i_c

    # Vertices computations by indexing ``table`` with the ``i_f`` and ``i_c``
    # indexes. 8 encompassing vertices are computed for a given V_xyz value
    # forming a cube around it:
    vertices = np.array([
        table[i_f_c[i[0]][..., 0], i_f_c[i[1]][..., 1], i_f_c[i[2]][..., 2]]
        for i in itertools.product(*zip([0, 0, 0], [1, 1, 1]))
    ])

    return vertices, V_xyzr

def table_interpolation_trilinear(V_xyz, table):
    V_xyz = np.asarray(V_xyz, dtype='float64')

    vertices, V_xyzr = vertices_and_relative_coordinates(V_xyz, table)

    vertices = np.moveaxis(vertices, 0, 1)
    x, y, z = [f[:, np.newaxis] for f in tsplit(V_xyzr)]

    weights = np.moveaxis(
        np.transpose(
            [(1 - x) * (1 - y) * (1 - z), (1 - x) * (1 - y) * z,
             (1 - x) * y * (1 - z), (1 - x) * y * z, x * (1 - y) * (1 - z),
             x * (1 - y) * z, x * y * (1 - z), x * y * z]), 0, -1)

    xyz_o = np.reshape(np.sum(vertices * weights, 1), V_xyz.shape)

    return xyz_o

def apply(lut, RGB, interpolator=table_interpolation_trilinear):

    R, G, B = tsplit(RGB)

    domain_min, domain_max = lut.domain

    RGB_l = [
        linear_conversion(j, (domain_min[i], domain_max[i]), (0, 1))
        for i, j in enumerate((R, G, B))
    ]

    return interpolator(tstack(RGB_l), lut._table)

img = read_image('test_img/Color_Checker.png')
# lut = identity_table(33)
lut = LUT3D(LUT3D.linear_table())
apply(lut, img)
# resize_lut(lut, 17)