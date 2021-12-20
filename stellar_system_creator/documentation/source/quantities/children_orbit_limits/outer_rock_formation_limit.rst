Outer Rock Formation Limit
==========================

.. _outer_rock_formation_limit:

We use :ref:`Selsis insolation model <selsis_insolation_model>` since it allows for easy, Solar system comparisons.
Rock line is the distance at which iron and rock can form clusters, planetesimals and eventually planets.
Since the rock line is determined by when rock and iron are more or less solid, I decided to use
the melting point of a slow rotating (:ref:`tidally locked <tidal_locking_radius>`) rock ball
(:ref:`heating distribution <heat_distribution>` :math:`\beta` 0.5, :ref:`albedo <albedo>` :math:`A` 0.85)
@ :math:`T = 600` K to find the equivalent solar system distance
and multiply by 5/3.1 (similar to the :ref:`early solar system water frost line <outer_water_frost_limit>`)
(lowest temperature from http://hyperphysics.phy-astr.gsu.edu/hbase/Geophys/meltrock.html)
for the optimistic outer rock line limit, giving a value of :math:`\approx 0.281` A.U for our sun.


Distance estimation: :math:`\frac{5}{3.1}\left(\frac{T}{T_{\rm eff}}\right) ^ 2 \sqrt{\frac{1-A}{\beta}}`,
with :math:`T_{\rm eff} = 278.5` K (https://arxiv.org/pdf/1702.07314.pdf eq. 6 with :math:`L = 1`).
