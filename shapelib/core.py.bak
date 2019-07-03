"""
Utility functions for computational geometry 
Built around shapely.
"""

from __future__ import print_function, division, absolute_import
import math
from math import pi, sqrt
from numbers import Number as _Number 
import array
import numpy

from shapely.geometry import (
    LineString, Polygon, Point, box, asPoint, 
    asPolygon, MultiPoint, MultiLineString
    )
from shapely.geometry.polygon import LinearRing

from shapely.affinity import rotate
from shapely.topology import TopologicalError as _TopologicalError
from . import util

def _normalize_point(p):
    if isinstance(p, (tuple, list)):
        if isinstance(p[0], array.array):
            if len(p[0]) == 1:
                return p[0][0], p[1][0]
            else:
                raise TypeError("only points supported")
        else:
            if all(isinstance(n, _Number) for n in p):
                return p
            else:
                raise TypeError("each point must be a tuple (x, y) of float")
    elif hasattr(p, "x") and hasattr(p, "y"):
        return (p.x, p.y)
    else:
        raise TypeError("point not understood")

def _normalize_points(points):
    if all(isinstance(p, _Number) for p in points):
        points = util.window(points, 2, 2)
    coords = map(_normalize_point, points)
    return coords

###############################################
#
# Helpers to create shapely geometries
#
################################################

def linestr(*points):
    """
    create a line-segment from the given points

    Example
    =======

    >>> l = linestr((0, 0), (1, 1), (2, -1))
    >>> l.bounds
    (0.0, -1.0, 2.0, 1.0)
    >>> [coord for coord in l.coords]
    [(0.0, 0.0), (1.0, 1.0), (2.0, -1.0)]

    """
    coords = _normalize_points(points)
    return LineString(coords)

def rect_poly(x0, y0, x1, y1):
    """
    a rectangular polygon (filled)
    """
    return box(x0, y0, x1, y1)

def rect_line(x0, y0, x1, y1):
    """
    the perimeter of a rectangle, without any dimensions.
    """
    return LinearRing([(x0, y0), (x1, y0), (x1, y1), (x0, y1)])

def circle(centerx, centery, radius):
    return Point(centerx, centery).buffer(radius)

def line_at_x(line, x):
    _, y0, _, y1 = line.bounds
    linex = LineString([(x, y0), (x, y1)])
    return line.intersection(linex)

def ring(centerx, centery, radius, width):
    """
    a circular ring
    """
    c_out = Point(centerx, centery).buffer(radius)
    c_in  = Point(centerx, centery).buffer(radius - width)
    return c_out.difference(c_in)

def line(x0, y0, x1, y1, width=None):
    l = LineString([(x0, y0), (x1, y1)])
    if width is not None:
        l = l.buffer(width)
    return l

def linering(*points):
    """
    create a LinearRing (a closed unfilled polygon) from the points given.
    A LinearRing is the "border" of a polygon

    Example
    =======

    linering((0, 1), Point(1, 7), (10, 2))

    each point is a tuple (x, y) or (x, y, z) or a Point
    """
    coords = _normalize_points(points)
    return LinearRing(coords)


def line_extrapolate_point(l, p, length):
    """
    Return a Point p2 which would extend the line `l` so that it 
    would have a length of `length`

    l: a line
    p: a point within that line
    length: the length that a line from p to p2 would have

    """
    p = Point(*_normalize_point(p))
    a = line_angle_at(l, p)
    if a > pi:
        a = a % pi
    p2 = Point(p.x, p.y + length)
    c = l.centroid
    if p.x < c.x:
        if p.y < c.y:
            angle = pi-a
        else:
            angle = a
    elif p.x > c.x:
        if p.y < c.y:
            angle = -a
        else:
            angle = -a
    else:
        if p.y < c.y:
            angle = a + pi
        elif p.y > c.y:
            angle = a % pi
        else:
            angle = 100
    p3 = rotate(p2, math.degrees(angle), origin=p)
    return p3

def line_extend(l, p, distance):
    p2 = line_extrapolate_point(l, p, distance)
    l2 = linestr(p, p2)
    return l.union(l2)

def test_line_extrpolate_point():
    f = line_extrapolate_point
    assert f(linestr(0, 0, 1, 0), (0, 0), 1).equals(Point(-1, 0))
    assert f(linestr(0, 0, 1, 0), (1, 0), 1).equals(Point(2, 0))
    assert f(linestr(0, 0, 1, 1), (1, 1), 1).almost_equals(Point(1+sqrt(0.5), 1+sqrt(0.5)))
    assert f(linestr(0, 0, 1, 1), (0, 0), 1).almost_equals(Point(-sqrt(0.5), -sqrt(0.5)))
    assert f(linestr(0, 1, 1, 0), (0, 1), 1).almost_equals(Point(-sqrt(0.5), 1+sqrt(0.5)))
    assert f(linestr(0, 1, 1, 0), (1, 0), 1).almost_equals(Point(1+sqrt(0.5), -sqrt(0.5)))
    assert f(linestr(0, 0, 0, 1), (0, 1), 1).equals(Point(0, 2))
    assert f(linestr(0, 0, 0, 1), (0, 0), 1).equals(Point(0, -1))

def tube(points, diam, wallwidth=0.05, begin='closed', end='flat'):
    """
    create a tube.

    A tube is a set of two parallel lines, where the edges are either 
    closed (curved), open, or flat 
    """
    l = linestr(*points)
    return linestr_to_tube(l, diam=diam, wallwidth=wallwidth, begin=begin, end=end)

def linestr_to_tube(l, diam, wallwidth=0.05, begin='closed', end='flat'):
    """
    convert a linestring to a tube

    l:          a line string
    diam:       inner diameter of the tube
    wallwidth:  width of the wall of the tube
    begin, end: one of 'closed', 'flat', 'open'. 
                Indicates the shape of the extremes.
    """
    r = diam * 0.5
    t = l.buffer(r+wallwidth).difference(l.buffer(r))

    def get_mask(l, p):
        p = _normalize_point(p)
        total_diam = (r+wallwidth)*2
        perp0 = perpendicular_at(l, p, total_diam)
        p2 = line_extrapolate_point(l, p, (r+wallwidth)*1.01)
        perp1 = perpendicular_at(l, p2, total_diam)
        mask = asPolygon(linering(perp0.coords[0], perp0.coords[1], 
            perp1.coords[1], perp1.coords[0])).convex_hull
        return mask
    if begin == 'open':
        mask = get_mask(l, l.coords[0])
        t = t.difference(mask)
    elif begin == 'flat':
        mask = get_mask(l, l.coords[0])
        t = t.union(mask)
    if end == 'open':
        mask = get_mask(l, l.coords[-1])
        t = t.difference(mask)
    if end == 'flat':
        mask = get_mask(l, l.coords[-1])
        t = t.union(mask)
    return t

tube_from_line = linestr_to_tube


def perpendicular_at(line, point, length):
    """
    line: a linestring
    point: a point within the line at which to search for a perpendicular line
    length: length of the line
    """
    point = asPoint(point)
    E = 1e-8
    if line.intersects(point):
        refpoint = point
    else:
        r = 16
        while True:
            refpoint = point.buffer(
                line.distance(point)+E, resolution=r
            ).exterior.intersection(line)
            if not refpoint.is_empty:
                break
            else:
                r = r * 2
        assert not refpoint.is_empty
    a = line_angle_at(line, refpoint)
    a2 = a + pi/2
    p2 = Point(point.x, point.y + length*0.5)
    p3 = rotate(p2, -math.degrees(a2), origin=point)
    p4 = rotate(p2, (180 - math.degrees(a2)), origin=point)
    l = linestr(p3, p4)
    return l


def line_angle_at(line, point, h=0.001):
    """
    return the angle of `line` at the `point` given. I

    If point is not in the line, return the angle at the 
    nearest point within the line.
    """
    point = Point(*_normalize_point(point))
    if not line.intersects(point):
        point = nearest_point(line, point)
    bufdist = min(line.length, h)
    c = point.buffer(bufdist).exterior
    points = c.intersection(line)
    if isinstance(points, Point):   # only one intersection, point is one of the extremes
        a = points
        b = line.intersection(point.buffer(bufdist*2).exterior)
        if not isinstance(b, Point):
            b = b[0]
    else:
        assert len(points) == 2
        a, b = points
    return angle_from_points(a.centroid, b.centroid)


def angle_at(geom, point, h=0.00001):
    if not isinstance(point, Point):
        point = Point(*point)
    geomext = edge(geom)
    if geomext.contains(point):
        nearest = point
    else:
        nearest = nearest_point(geomext, point)
    c = nearest.buffer(h).exterior.intersection(geomext)
    if c.is_empty:
        return angle_at(geom, nearest, h*3)
    if isinstance(c, MultiPoint):
        a, b = c[:2]
        return angle_from_points(a, b)
    elif isinstance(c, LineString):
        a = Point(*c.coords[0])
        b = Point(*c.coords[-1])
        return angle_from_points(a, b)
    elif isinstance(c, MultiLineString):
        a = c[0].centroid
        b = c[0].centroid
        return angle_from_points(a, b)
    else:
        raise ValueError("ooops!")


def angle_from_points(a, b):
    """
    the angle between the points a and b in radians
    0: a and b are aligned with the y axis

    Example
    =======

    >>> angle_from_points((0, 0), (1, 1))   # 45 degrees
    0.7853981633974482
    >>> angle_from_points((0, 0), (0, 1))   # 0 deg
    0.0

    North = 0

    NB: convert to 360 with 'degrees' --> degrees(0.7853981633974482) = 45
    """
    a, b = _normalize_points((a, b))
    ax, ay = a
    bx, by = b
    A = by - ay
    O = bx - ax
    H = sqrt(O**2 + A**2)
    if H == 0:
        return 0
    sin_alpha = O/H
    alpha = math.asin(sin_alpha)
    if by < ay:
        if alpha > 0:
            alpha += pi
        else:
            alpha = pi + abs(alpha)
    alpha = alpha % (pi*2)
    return alpha

def edge(geom):
    """
    return a polygon representing the edge of `geom`
    """
    h = 1e-8
    try:
        geomext = geom.exterior
    except:
        try:
            geomext = geom.buffer(h).exterior
        except:
            geomext = geom
    return geomext


def nearest_point(geom, p, eps=None):
    """
    find the point in `geom` which is nearest from point `p`

    eps: epsilon
    """
    MINDIST = 1e-16
    if not isinstance(p, Point):
        p = Point(*p)
    if geom.contains(p):
        return p
    if eps is None:
        eps = geom.distance(p) * 0.0001
    dist = geom.distance(p)
    if dist < MINDIST:
        dist = 1e-12

    try:
        circunf = p.buffer(dist+eps)
        p2 = circunf.exterior.intersection(geom)
    except _TopologicalError:
        return nearest_point(geom, p, eps*3)

    if circunf.contains(geom):
        # we are probably near the centroid of the geom, inside it
        n = geom.representative_point()
        assert abs(n.distance(p) - geom.distance(p)) < 1e-3
        return n

    if p2.is_empty: # eps is too small, try with a larger one
        return nearest_point(geom, p, eps*6)

    if isinstance(p2, MultiPoint):
        a = p2[0]
        b = p2[1]
        p3 = linestr(a, b).centroid
    elif isinstance(p2, Polygon):
        p3 = linestr(p2.centroid, p).intersection(p2.exterior)
    elif isinstance(p2, LineString):
        p3 = p2.centroid
    elif isinstance(p2, MultiLineString):
        p3 = p2[0].centroid
    else:
        raise TypeError("other geometries not supported YET")
    assert not p3.is_empty and isinstance(p3, Point)
    return p3


def holes(geom):
    """
    return the geometry which would fill the holes in geom
    """
    return tight_envelope(geom).difference(geom)


def tight_envelope(geom):
    """
    return the geometry which builds an envelope around `geom`
    """
    if hasattr(geom, 'geoms'):
        g0 = max((sub.envelope.area, sub) for sub in geom.geoms)[1]
        g00 = asPolygon(g0.exterior)
    elif isinstance(geom, Polygon):
        g00 = asPolygon(geom.exterior)
    return g00





