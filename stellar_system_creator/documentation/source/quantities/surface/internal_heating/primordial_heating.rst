Primordial Heating
==================

.. _primordial_heating:

Primordial heating :math:`Q_{\rm prim}` of a planet is heating that originates from the initial formation heating.
It is stored in the planet as an internal heating source that slowly (or quickly)
escapes, depending on the planet materials.

For a planet of :ref:`mass <mass>` :math:`M`, :ref:`surface area <surface_area>` :math:`S`,
:ref:`age <age>` :math:`T`, and initial heating :math:`H_o`, the primordial heating is given by:
:math:`Q_{\rm prim} = H_o {\rm e}^{- \lambda T} M / S`, where :math:`\lambda` is a decay constant.

For this package we use a constant :math:`H_o = 1.2 \cdot 10^{-11}` Watts/kg and
:math:`\lambda = \frac{0.3391}{\rm billion\,years}`.

More information on:
https://www.sciencedirect.com/science/article/abs/pii/S003206331300161X Eq. 2.1 :math:`\cdot M / S`
