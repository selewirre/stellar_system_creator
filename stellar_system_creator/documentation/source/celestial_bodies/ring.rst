Ring
====

.. _ring:

An ring is is a torus,
pancake or ring-shaped accumulation of matter composed of
gas, dust, asteroids, or collision fragments in :ref:`orbit <orbital>` around a :ref:`planet <planet>`.

In this package, a ring is always attached to a :ref:`planet <planet>`.
Ring objects are characterized by their inner and and outer :ref:`radius <radius>`,
forbidden bands and a radial gradient patterns.
The inner radius is given as :math:`1.1 R_p` where :math:`R_p` is the radius of the host
:ref:`planet <planet>`.
THe outer radius is given by the :ref:`dense Roche orbit limit <dense_roche_limit>`.
Forbidden bands are bands where material has moved away from, due to the gravitational
presence of a bigger body (:ref:`satellite <satellite>`).
The more :ref:`satellite <satellite>` a :ref:`planet <planet>` has, the more intricate the
forbidden bands of the ring will be.

Finally, the color gradient defines the color of the ring at a given distance from the center.
The color gradinet has 5 parameters. The first parameter can be from 0 to 1 and represents the position
at which the color will be - with 0 being the equivalent of the inner radius and 1 being the equivalent of
the outer radius). The next four parameters represent the RGBA (Red - Green - Blue - Alpha) color code
of the position of choice. These parameters take numbers between 0 and 255. The higher the alpha, the
less transparent the ring will be.
The user may add as many positions of color as they like.


