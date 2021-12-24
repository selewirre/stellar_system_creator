Radiative Habitable Zone
==========================
.. _radiative_habitable_zone:

The Radiative Habitable Zone (SSHZ) is the simplest type of habitable zone in a :ref:`binary system <binary_system>`.
It does *not* take into account the forced and periodically changing :ref:`eccentricity <eccentricity>`
of the :ref:`planets <planet>` due to the asymmetry
the two :ref:`stars <star>` of different :ref:`mass <mass>` introduce to the :ref:`stellar system <stellar_system>`.

Let us assume a :ref:`binary system <binary_system>` with :ref:`stars <star>` :math:`s = A,\, B`
of :ref:`luminosities <luminosity>` :math:`L_s` and
:ref:`temperatures <temperature>` :math:`T_s`.
They are separated by a mean :ref:`distance <semi_major_axis>` :math:`D`
and orbit around a common center with :ref:`eccentricity <eccentricity>` :math:`e`.
We aim to calculate the *radiative* habitable thresholds with insolation
:math:`S_{s,x}(T_s)` (where :math:`x = {\rm I, \, O}`).
For convenience, we define the
normalized luminosity: :math:`\tilde L_{s,x} = \frac{L_s}{S_{s,x}(T_s)}`, the
:ref:`SSHZ <single_star_habitable_zone>` :math:`r_{s, x} = \sqrt{\tilde L_{s,x}}`,
the double-star equivalent :math:`r_{\rm AB, x} = \sqrt{\tilde L_{A,x} + \tilde L_{B,x}}`,
and the half mean distance :math:`b = D/2`.

The S-type RHZ for :ref:`stars <star>` :math:`A`, namely :math:`r_{A, x}^{\rm S-type}`, thresholds are estimated by:

1. Inner: :math:`r_{\rm A, I}^{\rm S-type} = r_{\rm A, I} \left(1 + \frac{\tilde L_{B,\rm I}}{\left(D - r_{\rm A, I}\right)^2} \right)`.
2. Outer: :math:`r_{\rm A, O}^{\rm S-type} = r_{\rm A, O} \left(1 + \frac{\tilde L_{B,\rm O}}{\left(D + r_{\rm A, O}\right)^2} \right)`.

The P-type RHZ, namely :math:`r_{\rm AB, x}^{\rm P-type}`, thresholds are estimated by:

1. Inner: :math:`r_{\rm AB, I}^{\rm P-type} = \sqrt{ \tilde L_{A,\rm I} \frac{r_{\rm AB, I} + b}{r_{\rm AB, I} - b} + \tilde L_{B,\rm I} \frac{r_{\rm AB, I} - b}{r_{\rm AB, I} + b} - b^2}`
2. Outer: :math:`r_{\rm AB, O}^{\rm P-type} = \sqrt{ \tilde L_{A,\rm O} \frac{r_{\rm AB, O} - b}{r_{\rm AB, O} + b} + \tilde L_{B,\rm O} \frac{r_{\rm AB, O} + b}{r_{\rm AB, O} - b} - b^2}`
