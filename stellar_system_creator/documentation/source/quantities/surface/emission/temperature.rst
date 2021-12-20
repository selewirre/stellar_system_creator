Temperature
===========

.. _temperature:

The surface temperature of an object can be defined differently for objects
that produce significant radiation (stars) and ones that are mostly heated
by another stellar body (planets, satellites).

For a star of :ref:`luminosity <luminosity>` :math:`L` in solar luminosities
and :ref:`radius <radius>` :math:`R` in solar radii, the surface temperature
is given by the ideal body equation: :math:`\frac{L}{R^2} \cdot 5778` K.

For a planet of :ref:`bond albedo <albedo>` :math:`A`, :ref:`emissivity <emissivity>` :math:`\epsilon`,
:ref:`heat distribution <heat_distribution>` :math:`\beta`,
:ref:`normalized greenhouse <normalized_greenhouse>` :math:`g` and
:ref:`incident flux <incident_flux>` :math:`S`,
the surface temperature is given by the equation:
:math:`\left(\frac{(1 - A) S}{\beta \epsilon (1 - g)}\right)^{1/4} \cdot 278.5` K.


For more information of the planetary surface temperature:
https://arxiv.org/pdf/1702.07314.pdf (eq. 6 and 16)
