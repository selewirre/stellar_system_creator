Radiogenic Heating
==================

.. _radiogenic_heating:

Radiogenic heating :math:`Q_{\rm rad}` is the heating produced by slowly radiative isotopes in a planets mantle.
Since we only care for the mantle, we take into account the planetary composition
(we assume that only the rocky part of the planet is contributing to radiogenic heating).
This model assumes the same percentages of radioactive isotopes as earth, although these may vary
from planet to planet and stellar system to stellar system, depending on the age of the galaxy
and local isotope abundances.

For a radiogenic isotope of number :math:`k` with heating production :math:`H_k`, initial abundance :math:`n_k (0)`,
lifetime :math:`\tau_k`, the heating heating produced at a certain time (:ref:`age <age>`) :math:`t`
is given by: :math:`H_k(t) = H_k n_k (0) {\rm e}^{- t / \tau}`.

For a planet of :ref:`mass <mass>` :math:`M`, :ref:`surface area <surface_area>` :math:`S`,
:ref:`age <age>` :math:`T`, and rocky mantle percentage :math:`p_{\rm rocky}` (see :ref:`chemical composition <chemical_composition>`
and :ref:`composition type <composition_type>`), the total heating is given by:
:math:`Q_{\rm rad} = \sum_k \left(H_k(T)\right) p_{\rm rocky} M / S`.

More information on:
https://www.sciencedirect.com/science/article/abs/pii/S0019103514004473?via%3Dihub#b0415%20.
See table 1 for heat production and half-times, and table 2 for relative abundance.

