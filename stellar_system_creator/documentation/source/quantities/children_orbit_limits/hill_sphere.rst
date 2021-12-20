Hill Sphere
===========

.. _hill_sphere:

Hill sphere is the maximum distance (:math:`r_H`) an object (child) can affect even smaller body (grandchild),
because of the presence of a bigger body around (parent).
For example the moon is within the hill sphere of earth, and the hill sphere of earth is determined
by earth's :ref:`mass <mass>` :math:`m` :ref:`semi-major axis <semi_major_axis>` :math:`a`,
and :ref:`eccentricity <eccentricity>` :math:`e`, and the sun's :ref:`mass <mass>` :math:`M`.

It is given by the equation: :math:`r_H = a (1 - e) \left(\frac{m}{3 M}\right)^{1/3}`.

If we looking at a single object that is part of a binary system, a more accurate determination
of the Hill sphere is given by the :ref:`Roche lobe <roche_lobe>`.
