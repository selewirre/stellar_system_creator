from stellar_system_creator.astrothings.units import ureg, Q_

"""
Sources: Selsis. et al. 2007 [1], Wang and Cuntz 2019 [2]
[1] https://www.aanda.org/articles/aa/pdf/2007/48
[2] https://iopscience.iop.org/article/10.3847/1538-4357/ab0377 (overview of this and others models)
"""


predefined_insolation_threshold_parameters = \
    {
     # Venus-Earth-Mars
     'Recent Venus': {'sl': 0.72, 'a': 2.7619E-5, 'b': 3.8095E-9},
     'Earth Equivalent': {'sl': 0.993, 'a': 2.7619E-5, 'b': 3.8095E-9},
     'Early Mars': {'sl': 1.77, 'a': 1.3786E-4, 'b': 1.4286E-9},
     # 0% Clouds
     'Runaway Greenhouse Effect, 0% Clouds': {'sl': 0.84, 'a': 2.7619E-5, 'b': 3.8095E-9},
     'Start of water loss, 0% Clouds': {'sl': 0.95, 'a': 2.7619E-5, 'b': 3.8095E-9},
     'First C02 Condensation, 0% Clouds': {'sl': 1.37, 'a': 1.3786E-4, 'b': 1.4286E-9},
     'Maximum Greenhouse Effect, 0% Clouds': {'sl': 1.67, 'a': 1.3786E-4, 'b': 1.4286E-9},
     # 50% Clouds
     'Runaway Greenhouse Effect, 50% Clouds': {'sl': 0.68, 'a': 2.7619E-5, 'b': 3.8095E-9},
     'Start of water loss, 50% Clouds': {'sl': 0.76, 'a': 2.7619E-5, 'b': 3.8095E-9},
     'Maximum Greenhouse Effect, 50% Clouds': {'sl': 1.95, 'a': 1.3786E-4, 'b': 1.4286E-9},
     # 100% Clouds
     'Runaway Greenhouse Effect, 100% Clouds': {'sl': 0.46, 'a': 2.7619E-5, 'b': 3.8095E-9},
     'Start of water loss, 100% Clouds': {'sl': 0.51, 'a': 2.7619E-5, 'b': 3.8095E-9},
     'Maximum Greenhouse Effect, 100% Clouds': {'sl': 2.40, 'a': 1.3786E-4, 'b': 1.4286E-9},
     }

conservative_min_limit_name = 'Runaway Greenhouse Effect, 0% Clouds'
conservative_max_limit_name = 'Maximum Greenhouse Effect, 0% Clouds'
earth_equivalent_name = 'Earth Equivalent'

relaxed_min_limit_name = 'Runaway Greenhouse Effect, 100% Clouds'
relaxed_max_limit_name = 'Maximum Greenhouse Effect, 100% Clouds'

orbit_thresholds_in_sol = {key: predefined_insolation_threshold_parameters[key]['sl'] * ureg.au
                           for key in predefined_insolation_threshold_parameters.keys()}


def calculate_insolation_threshold(star_temperature: Q_, threshold_name: str) -> Q_:
    Ts = star_temperature.to('K').m - 5700
    pars = predefined_insolation_threshold_parameters[threshold_name]
    Seff = (pars['sl'] - pars['a'] * Ts - pars['b'] * Ts ** 2) ** (-2)

    return Seff * ureg.solar_flux

