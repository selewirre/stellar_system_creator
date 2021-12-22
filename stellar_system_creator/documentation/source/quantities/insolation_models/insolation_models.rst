Insolation Models
=================

.. _insolation_models:

Insolation or effective stellar flux is the effective flux that
reaches a specific :ref:`orbital <orbital>` distance, called threshold (or limit).
Insolation changes with the :ref:`star's <star>` :ref:`temperature <temperature>`,
as well as the environmental conditions of the target :ref:`habitable <habitability>` world.
We use insolation for a specific climate to normalize the
:ref:`luminosity <luminosity>` of a :ref:`star's <star>`,
and try to estimate the threshold at which distance from
the :ref:`star's <star>` the aforementioned environmental conditions occur.
By using extreme environmental conditions that could potentially support life,
we can determine minima and maxima for :ref:`zones of habitability <habitable_zones>`
around single- or multi-star :ref:`systems <celestial_systems>`.

There are different types of insolation models. In this package,
we are using one that was designed by :ref:`Kopparapu <kopparapu_insolation_model>`, and
one that was designed by :ref:`Selsis <selsis_insolation_model>`.

These models have multiple different thresholds, from which
we only use a handful that are representative of the :ref:`habitability limits <habitable_zones>`.
These are designated as *earth equivalent*, *conservative* or *relaxed* and *minimum* (inner) or *maximum* (outer).

.. toctree::
    kopparapu/kopparapu
    selsis/selsis
    relaxed_minimum_limit
    relaxed_maximum_limit
    conservative_minimum_limit
    conservative_maximum_limit
    earth_equivalent_limit
