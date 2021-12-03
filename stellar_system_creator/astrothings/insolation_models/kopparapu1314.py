from stellar_system_creator.astrothings.astromechanical_calculations import calculate_average_insolation_threshold
from stellar_system_creator.astrothings.units import ureg, Q_

"""
Sources: Kopparapu. et al. 2013 [1], 2014 [2], Wang and Cuntz 2019 [3]
[1] https://iopscience.iop.org/article/10.1088/0004-637X/765/2/131
[2] https://iopscience.iop.org/article/10.1088/2041-8205/787/2/L29
[3] https://iopscience.iop.org/article/10.3847/1538-4357/ab0377 (overview of this and other models)
"""

predefined_insolation_threshold_parameters = \
    {
     'Recent Venus': {'Seff0': 1.776, 'a': 2.136E-4, 'b': 2.533E-8, 'c': -1.332E-11, 'd': -3.097E-15},
     'Runaway Greenhouse Effect, Subterran': {'Seff0': 0.99, 'a': 1.209E-4, 'b': 1.404E-8, 'c': -7.418E-12,
                                              'd': -1.713E-15},
     'Runaway Greenhouse Effect, Terran': {'Seff0': 1.107, 'a': 1.332E-4, 'b': 1.58E-8, 'c': -8.308E-12,
                                           'd': -1.931E-15},
     'Runaway Greenhouse Effect, Superterran': {'Seff0': 1.188, 'a': 1.433E-4, 'b': 1.707E-8, 'c': -8.968E-12,
                                                'd': -2.084E-15},
     'Moist Greenhouse Effect': {'Seff0': 1.0140, 'a': 8.1774E-5, 'b': 1.7063E-9, 'c': -4.3241E-12, 'd': -6.6462E-16},
     'Maximum Greenhouse Effect': {'Seff0': 0.356, 'a': 6.171E-5, 'b': 1.698E-9, 'c': -3.198E-12, 'd': -5.575E-16},
     'Early Mars': {'Seff0': 0.32, 'a': 5.547E-5, 'b': 1.526E-9, 'c': -2.874E-12, 'd': -5.011E-16}
     }

predefined_insolation_threshold_names = list(predefined_insolation_threshold_parameters.keys())

conservative_min_limit_name = 'Runaway Greenhouse Effect, Terran'
conservative_max_limit_name = 'Maximum Greenhouse Effect'
earth_equivalent_name = 'Moist Greenhouse Effect'

relaxed_min_limit_name = 'Recent Venus'
relaxed_max_limit_name = 'Early Mars'

orbit_thresholds_in_sol = {key: calculate_average_insolation_threshold(
    predefined_insolation_threshold_parameters[key]['Seff0'], 0.01671) ** (-1/2) * ureg.au
                           for key in predefined_insolation_threshold_names}


def calculate_insolation_threshold(star_temperature: Q_, threshold_name: str) -> Q_:
    Ts = star_temperature.to('K').m - 5780
    pars = predefined_insolation_threshold_parameters[threshold_name]
    Seff = pars['Seff0'] + pars['a'] * Ts + pars['b'] * Ts ** 2 + pars['c'] * Ts ** 3 + pars['d'] * Ts ** 4

    return Seff * ureg.solar_flux

