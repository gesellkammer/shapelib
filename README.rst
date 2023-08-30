===============================
shapelib
===============================

Python utilities to facilitate working with shapely (shape creation, rasterization, plotting)

* Free software: BSD license
* Documentation: http://shapelib.rtfd.org.

Features
--------

* provides easy methods to interact with shapely and other related libraries
* easy creation of complex geometric shapes
* geometric operations:
  - extend line
  - extrapolate points
  - generate perpendicular lines
  - calculate angles
  - find the nearest points between two geometries
* rasterization
  - convert a shape to an array
  - convert a shape to a picture
  - plot a complex shape with matplotlib

Incentive
---------

shapelib started as a set of utilities to build geometric shapes as part of acoustic simulations (walls, ducts, tubes). It proved to be useful outside of this specific domain.

Examples
--------

Rotate a geometry:

.. code-block:: python

    import shapelib
    l = shapelib.line(0, 0, 1, 1)
    rot = shapelib.rotate(l, 90)

Find the angle of a tangent at a point:

.. code-block:: python

    import shapelib
    circ = shapelib.circle(1, 1, 1)
    radians = shapelib.angle_at(circ, (1, 0))
    print(math.degrees(radians))
    # 270

Rasterize a geometry to an 2D array:

.. code-block:: python

    import shapelib
    circ = shapelib.circle(1, 1, 1)
    # convert to a 2D matrix, 300 pixels pro unit
    img = shapelib.rasterize(circ, 300)



Documentation
-------------

See the docs_

.. _docs : docs/index.rst
