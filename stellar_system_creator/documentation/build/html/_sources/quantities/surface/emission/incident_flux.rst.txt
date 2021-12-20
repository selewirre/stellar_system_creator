Incident Flux
=============

.. _incident_flux:

Incident flux is the incoming radiation flux from all major sources.
The total incident flux is added from the parent, the parent of the parent
etc.

The incident flux :math:`S` from a single source of :ref:`luminosity <luminosity>` :math:`L`
at effective distance :math:'r_{\rm eff}' is given by the equation: :math:`\frac{L}{r_{\rm eff}^2}`.

For a child orbiting at :ref:`mean distance <semi_major_axis>` :math:`a`
and :ref:`eccentricity <eccentricity>` :math:`e`,
there are two types of effective distance we care about.
The first is the one that is related to the average incoming flux and is given by:
:math:`r_F = a (1 − e^2)^{1/4}`.

The second is the one that is related to the average surface temperature and is given by:
:math:`r_T \approx a (1 + \frac{1}{8} e^2 + \frac{21}{512} e^4)`.


For more information: https://arxiv.org/pdf/1702.07314.pdf (eq. 3, 17, 19).
