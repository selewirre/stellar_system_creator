Selsis
======

.. _selsis_insolation_model:

Selsis' insolation model is a simple model that describes a multitude of
disparate thresholds of interest.
It's main assets are the distinction cloudy and non-cloudy greenhouse effect-based thresholds,
the provision of very relaxed thresholds, and the ability to make once own thresholds. This last part
is important in determining the :ref:`inner rock formation limit <inner_rock_formation_limit>`,
the :ref:`outer rock formation limit <outer_rock_formation_limit>`,
the :ref:`inner water frost limit <inner_water_frost_limit>`,
the :ref:`sol-equivalent water frost limit <sol_equivalent_water_frost_limit>`,
and the :ref:`outer water frost limit <outer_water_frost_limit>`.

The provided thresholds are:

1. Planet-based
    a. Recent Venus: *inner*.
    b. Earth Equivalent': *inner*, :ref:`earth equivalent limit <earth_equivalent_limit>`.
    c. Early Mars: *outer*.
2. 0% Clouds
    a. Runaway Greenhouse Effect, 0% Clouds: *inner*, :ref:`conservative minimum limit <conservative_minimum_limit>`.
    b. Start of water loss, 0% Clouds: *inner*.
    c. First C02 Condensation, 0% Clouds: *outer*.
    d. Maximum Greenhouse Effect, 0% Clouds: *outer*, :ref:`conservative maximum limit <conservative_maximum_limit>`.
3. 50% Clouds
    a. Runaway Greenhouse Effect, 50% Clouds: *inner*.
    b. Start of water loss, 50% Clouds: *inner*.
    c. Maximum Greenhouse Effect, 50% Clouds: *outer*.
4. 100% Clouds
    a. Runaway Greenhouse Effect, 100% Clouds: *inner*, :ref:`relaxed minimum limit <relaxed_minimum_limit>`.
    b. Start of water loss, 100% Clouds: *inner*.
    c. Maximum Greenhouse Effect, 100% Clouds: *outer*, :ref:`relaxed maximum limit <relaxed_maximum_limit>`.

Sources: Selsis. et al. 2007 [1], Wang and Cuntz 2019 [2]
1. https://www.aanda.org/articles/aa/pdf/2007/48
2. https://iopscience.iop.org/article/10.3847/1538-4357/ab0377 (overview of this and others models)
