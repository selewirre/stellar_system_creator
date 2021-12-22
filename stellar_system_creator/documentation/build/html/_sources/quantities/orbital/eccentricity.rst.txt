Eccentricity
============

.. _eccentricity:

Eccentricity :math:`e` determines how elliptic the orbit of a child around a parent body is.
:math:`e = 0` means that the orbit is circular, and :math:`e = 1` means
that the orbit resembles a line (not a stable orbit).

The suggested eccentricity is :math:`e = 0` for single :ref:`star <star>` systems.
For :ref:`binary systems <binary_system>`, the suggested eccentricity depends on the
eccentricity of the binary :math:`e_c`,
the :ref:`semi-major axis <semi_major_axis>` :math:`a_c` of the child, the
:ref:`mean distance <semi_major_axis>` :math:`a_b` between the two binary system objects,
and the secondary to total :ref:`mass <mass>` ratio :math:`\mu` of the binary. Small
variations of the eccentricity (e.g. :math:`\pm 0.05`) are suggested for a more realistic
:ref:`orbit <orbital>`.

For S-type :ref:`binary systems <binary_system>`, the suggested eccentricity is given by:
:math:`e_S = \frac{5}{4} \frac{a_c}{a_b} \frac{e_b}{1-e_b^2}`.

For P-type :ref:`binary systems <binary_system>`, the suggested eccentricity is given by:
:math:`e_P = \frac{5}{4} \frac{a_b}{a_c} (1-2\mu) \frac{4 e_b + 3e_b^3}{4 + 6e_b^2}`.

