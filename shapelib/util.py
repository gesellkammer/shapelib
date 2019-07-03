##################################
#
# helpers
#
###################################
from __future__ import absolute_import
import itertools as _itertools
from numbers import Number as _Number

def window(iterable, size, step):
    """
    iterate over subseqs of iterable
    
    Example
    =======
    
    >>> seq = range(6)
    
    >>> list(window(seq, 3, 1))
    [(0, 1, 2), (1, 2, 3), (2, 3, 4), (3, 4, 5)]
    
    >>> list(window(seq, 3, 2))
    [(0, 1, 2), (2, 3, 4)]
    """
    iterators = _itertools.tee(iterable, size)
    for skip_steps, itr in enumerate(iterators):
        for ignored in _itertools.islice(itr, skip_steps):
            pass
    window_itr = _itertools.izip(*iterators)
    if step != 1:
        window_itr = _itertools.islice(window_itr, 0, 99999999, step)
    return window_itr

def geom_getbounds(geom, xr, yr):
    """
    Return the bounds of the geometry, with the possibility
    of selecting only a part of it

    geom: a geometry
    xr: x range -> width or (start, end)
    yr: y range -> height or (start, end)

    xr and yr can be None, in which case the
    result is the bounds of the geometry

    Returns
    =======

    (x0, y0, x1, y1)
    """
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
