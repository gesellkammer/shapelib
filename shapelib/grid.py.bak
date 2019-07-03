###########################################
# Old and unused, will be probably removed
###########################################
import numpy
from shapely.topology import TopologicalError as _TopologicalError

class Grid(object):
    def __init__(self, x0, y0, x1, y1, stepx, stepy):
        self.x0, self.y0, self.x1, self.y1, self.stepx, self.stepy = x0, y0, x1, y1, stepx, stepy
        self.xs = numpy.arange(x0, x1, stepx)
        self.ys = numpy.arange(y0, y1, stepy)
        self.xlines = [box(x, y0, x+stepx, y1) for x in self.xs]

    def rasterize2(self, geom):
        x0, y0, x1, y1 = [int(value / self.stepx) for value in geom.bounds]
        xs = range(x0, x1+1)
        mat = numpy.zeros((len(self.xs), len(self.ys)), dtype=float)
        stepy = self.stepy
        for x, band in zip(xs, self.xlines[x0:x1+1]):
            intersect_x = band.intersection(geom)
            if not intersect_x.is_empty:
                if not hasattr(intersect_x, '__iter__'):
                    intersect_x = [intersect_x]
                for sub in intersect_x:
                    _, y0, _, y1 = (int(v/stepy) for v in sub.bounds)
                    mat[y0:y1+1, x] = 1
        return mat

    def rasterize(self, geom):
        x0, y0, x1, y1 = [int(value / self.stepx) for value in geom.bounds]
        mat = numpy.zeros((len(self.ys), len(self.xs)), dtype=float)
        xs = range(x0, x1+1)
        stepy = self.stepy
        times = []
        E = 1e-4
        for x, band in zip(xs, self.xlines[x0:x1+1]):
            try:
                intersect_x = band.intersection(geom)
            except _TopologicalError:
                band1 = band.buffer(E)
                try:
                    intersect_x = band1.intersection(geom)
                except _TopologicalError:
                    print("topological error at x: {0}".format(x))
                    continue
            if not hasattr(intersect_x, '__iter__'):
                intersect_x = [intersect_x]
            for sub in intersect_x:
                # faster calculation of upper and lower bounds, faster than _, y0, _, y1 = geom.bounds
                ys = sub.ctypes[1::2]
                y0 = int(min(ys)/stepy)
                y1 = int(max(ys)/stepy)
                mat[y0:y1+1, x] = 1
        return mat

