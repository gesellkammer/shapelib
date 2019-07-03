##########################################
#
# Interface between shapely and matplotlib
#
###########################################
from __future__ import absolute_import
from matplotlib import pyplot
from . import util
from shapely.geometry import Polygon


def geom_to_fig(geom, xrange=None, yrange=None, axis_visible=True,
                patchkws={}, aspect=1, linewidth=0.01, fig=None):
    """
    convert a shapely geometry to a matplotlib figure

    If xrange and yrange are given, use them.
    If not, the bounds of the geometry are used

    xrange: a number (xmax) or a tuple (xmin, xmax) defining the range to plot
            in the x coord
    yrange: the same in the y coord. If these are not given, they are deduced
            from the coordinates of the geometry
    axis_visible: show the axis and labels
    patchkws: passed as kws to descartes.PolygonPatch
    aspect: parameter passed to axis.set_aspect (possible values: 'auto',
            or a number defining the ratio y/x)
    fig: used internally when called recursively for multi-geometries

    NB: This function relies on functionality provided by `descartes`
    (https://bitbucket.org/sgillies/descartes/)
    """
    try:
        import descartes
    except ImportError:
        raise ImportError("descartes is needed to plot geometries")
    x0, y0, x1, y1 = util.geom_getbounds(geom, xrange, yrange)
    if fig is None:
        #fig = pyplot.figure(1, figsize=(xsize, ysize))
        fig = pyplot.figure()
        ax = fig.add_subplot(111)
    else:
        ax = fig.gca()
    if isinstance(geom, Polygon):
        p = geom.__geo_interface__
    else:
        geom0 = geom.buffer(linewidth)
        if isinstance(geom0, Polygon):
            p = geom0.__geo_interface__
        else:
            for subgeom in geom.geoms:
                fig = geom_to_fig(subgeom, xrange=(x0, x1), yrange=(y0, y1),
                                  axis_visible=axis_visible, patchkws=patchkws,
                                  aspect=aspect, fig=fig)
            return fig
    if not axis_visible:
        ax.get_yaxis().set_visible(False)
        ax.get_xaxis().set_visible(False)
        ax.axis('off')
    ax.set_xlim(x0, x1)
    ax.set_ylim(y0, y1)
    ax.set_aspect(aspect)
    pa = descartes.PolygonPatch(p, **patchkws)
    ax.add_patch(pa)
    return fig


def geom_plot(geom, xrange=None, yrange=None, axis_visible=True, patchkws={}, aspect=1):
    """
    xrange: a number (xmax) or a tuple (xmin, xmax) defining the range to plot
            in the x coord
    yrange: the same in the y coord. If these are not given, they are deduced
            from the coordinates of the geometry
    width: used only when the geometry is not a polygon but a line or a ring.
    axis_visible: show the axis and labels
    patchkws: passed as kws to descartes.PolygonPatch
    aspect: parameter passed to axis.set_aspect (possible values: 'auto',
            or a number defining the ratio y/x)
    """
    fig = geom_to_fig(geom, xrange=xrange, yrange=yrange,
                      axis_visible=axis_visible, patchkws=patchkws,
                      aspect=aspect)
    fig.show()

    
def geom_to_picture(geom, filename, xrange=None, yrange=None, axis_visible=True,
                    pixratio=150, patchkws={'color': '#000000'}, dpi=None):
    """
    Save a geometry as a picture

    geom: a geometry
    filename: the filename of the picture. The extension determines the format
    xrange, yrange: use it to save a selection of the picture.
                    None => select the entire geometry

                  xsize
    pixratio = ---------
                 pixels

            If your image is 10x10 and pixratio=100,
            the resulting image will be 1000x1000 pixels

    NB: when saving to raster files (png, jpg, etc.) the size in pixels of
        the image will be (xsize * (dpi/2), ysize * (dpi/2))

    Returns
    =======

    a matplotlib figure
    """
    isinteractive = pyplot.isinteractive()
    if isinteractive:
        pyplot.ioff()
    fig = geom_to_fig(geom, xrange=xrange, yrange=yrange,
                      axis_visible=axis_visible, patchkws=patchkws)
    # ax = fig.gca()
    x0, y0, x1, y1 = util.geom_getbounds(geom, xrange, yrange)
    xsize = (x1 - x0) * pixratio
    if dpi is None:
        dpi = 200 * xsize / 1128.
    if not axis_visible:
        fig.tight_layout()
        fig.savefig(filename, dpi=dpi, bbox_inches='tight', pad_inches=0)
    else:
        fig.savefig(filename, dpi=dpi, bbox_inches='tight')
    if isinteractive:
        pyplot.ion()
    return fig
