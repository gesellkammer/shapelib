###########################################
#
#       R A S T E R I Z A T I O N
#
###########################################
from __future__ import print_function
from __future__ import absolute_import
import numpy as np
from collections import namedtuple as _namedtuple
from numbers import Number as _Number
import tempfile
import os

def _rasterize_matplotlib(geom, pixratio, xrange=None, yrange=None, imageout=None):
    """
    rasterize `geom` to a 2D array

    Uses matplotlibs image rendering

    NB: (0, 0) is left upper corner

    Returns
    =======

    (array, imageout) or None if the backend is not available
    """
    
    try:
        from matplotlib import image
    except ImportError:
        return None
    if imageout:
        filename = os.path.splitext(imageout)[0] + '.png'
        remove = False
    else:
        filename = tempfile.mktemp(suffix='.png')
        remove = True
    x0, y0, x1, y1 = _geomselectrange(geom, xrange, yrange)
    # cols = int(abs(x1-x0) * pixratio + 0.5)
    # rows = int(abs(y1-y0) * pixratio + 0.5)
    # save it to a black figure on white canvas
    geom_to_picture(geom, filename=filename, xrange=xrange, yrange=yrange,
                    pixratio=pixratio, patchkws={'color':'#000000'}, axis_visible=False)
    im = (image.imread(filename)[:, :, 0] < 0.9).astype(float)
    im = np.flipud(im)
    if remove:
        os.remove(filename)
        filename = None
    im = im.astype(np.uint8)
    return _rasterize_out(im, filename)


def geom_to_picture(geom, filename, xrange, yrange, pixratio, patchkws, axis_visible):
    pass


def _geomselectrange(geom, xr, yr):
    x0, y0, x1, y1 = geom.bounds
    
    def override(c0, c1, r):
        if r is not None:
            if isinstance(r, _Number):
                c1 = min(c1, r)
            else:
                c0, c1 = r
        return c0, c1
    
    x0, x1 = override(x0, x1, xr)
    y0, y1 = override(y0, y1, yr)
    return x0, y0, x1, y1


def _rasterize_rasterio(geom, pixratio, xrange=None, yrange=None, imageout=None):
    """
    rasterize `geom` to a 2D array

    Uses rasterio
    """
    try:
        import rasterio
        from rasterio import features
    except ImportError:
        return None
    geoms = [geom.__geo_interface__]
    x0, y0, x1, y1 = _geomselectrange(geom, xrange, yrange)
    cols = int(abs(x1-x0) * pixratio + 0.5)
    rows = int(abs(y1-y0) * pixratio + 0.5)
    transform = [0, 1.0/pixratio, 0, 0, 0, 1.0/pixratio]
    foreground = 'white'
    print("cols: {cols}, rows: {rows}".format(**locals()))
    with rasterio.drivers():
        array = features.rasterize(geoms, out_shape=(rows, cols), transform=transform)
        array_uint8 = array.astype(np.uint8)
        array_uint8 = np.flipud(array_uint8)
        if imageout:
            with rasterio.open(
                imageout, "w",
                driver='GTiff',
                width=cols, height=rows,
                transform=transform,
                count=1, dtype=np.uint8, nodata=0,
                crs={'init': 'EPSG:4326'}
            ) as out:
                if foreground == 'black':
                    outarray = array_uint8
                else:
                    outarray = 255 - array_uint8
                out.write_band(1, outarray)
    array_uint8 /= 255
    y, x = array_uint8.shape
    assert (x, y) == (cols, rows)
    return _rasterize_out(array_uint8, imageout)

_rasterize_out = _namedtuple("rasterize", "array imageout")
def rasterize(geom, pixratio, xrange=None, yrange=None, imageout=None):
    """
    rasterize the geometry

    geom: a shapely geometry
    pixratio: how many pixels pro unit
              x_pixels / x_size
    xrange, yrange: a selection of the geometry to be rendered,
                    or None to select all. It can be bigger than
                    the geometry itself.
    imageout: if given, it should be the path to save
              the rasterized geometry as a monochrome image

    Backends:
        rasterio, matplotlib

    Returns
    =======

    namedtup(array, imageout) where: 

        array:    2D array of rasterized values, uint8, 0-1
        imageout: filename of generated image or None
    """
    backends = [
        ('rasterio', _rasterize_rasterio),
        ('mastplotlib', _rasterize_matplotlib)
    ]

    for backendname, func in backends:
        out = func(geom, pixratio, xrange, yrange, imageout=imageout)
        if out:
            print("using backend: {backendname}".format(**locals()))
            return out

def geom_to_array(geom, pixratio, xrange=None, yrange=None):
    print("deprecated, use rasterize")
    return rasterize(geom, pixratio, xrange, yrange)
