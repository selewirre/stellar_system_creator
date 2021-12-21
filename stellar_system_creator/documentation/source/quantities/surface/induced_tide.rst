Induced Tide
============

.. _ induced_tide:

Induced tides :math:`h_{\rm tides}` are the height differences that occur due to tidal forces
on a planet's massive ocean's water level. The values provided are very
crued and are only meant as a suggestion to the user. Tide height depends
on many local parameters, as explained in `artifexian's video <https://youtu.be/wsuejZRqus4>`_.

For an object of :ref:`mass <mass>` :math:`m` and :ref:`radius <radius>` :math:`r`
that interacts with a companion object of :ref:`mass <mass>` :math:`m_c`
from a :ref:`mean distance <semi_major_axis>` :math:`a`
with orbital :ref:`eccentricity <eccentricity>` :math:`e`,
will experience a maximum tide height of:
:math:`h_{\rm tides} = 3 \frac{m_c}{m} \left(\frac{r}{a (1 - e)}\right)^3 \frac{r}{2}`.


More information on the model used can be found on
https://www.cambridge.org/resources/0521846560/7708_Tidal%20distortion.pdf (Eq. 20)
where mean distance is replaced by the periapsis (which yields the maximum observed tides).
A mistake must be noted: the example below eq. 20 needs :math:`m_1` to be the earth mass
and :math:`m_2` the moon mass.
