Inner Rock Formation Limit
==========================

.. _inner_rock_formation_limit:

We use :ref:`Selsis insolation model <selsis_insolation_model>` since it allows for easy, Solar system comparisons.
Rock line is the distance at which iron and rock can form clusters, planetesimals and eventually planets.
Since the rock line is determined by when rock and iron are more or less solid, I decided to use
the boiling point of a fast rotating iron ball
(:ref:`heating distribution <heat_distribution>` :math:`\beta` 1, :ref:`albedo <albedo>` :math:`A` 0.15)
@ :math:`T = 2870` K.
for the optimistic inner rock line limit, giving a value of :math:`\approx 0.087` A.U for our sun.

Distance estimation: :math:`\left(\frac{T}{T_{\rm eff}}\right) ^ 2 \sqrt{\frac{1-A}{\beta}}`,
with :math:`T_{\rm eff} = 278.5` K (https://arxiv.org/pdf/1702.07314.pdf eq. 6 with :math:`L = 1`).
