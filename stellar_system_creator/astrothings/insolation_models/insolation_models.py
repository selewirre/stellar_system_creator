import copy
from typing import Dict

import numpy as np

from stellar_system_creator.astrothings.astromechanical_calculations import calculate_spectrally_weighted_luminosity, \
    calculate_average_insolation_threshold
from stellar_system_creator.astrothings.units import ureg, Q_

"""
Insolation or effective stellar flux is the effective flux that reaches a specific "orbital" distance. 
Insolation changes with the star's effective temperature, as well as the climate of the target planet.
We use insolation for a specific climate to normalize the luminosity of a star, and then try and estimate the threshold
 at which distance from the star these environmental situations occur. 
By using extreme environmental conditions that can support life, we can determine minima and maxima for zones of 
habitability around a single- or multi-star system.   
"""


class InsolationThresholdModel:

    def __init__(self, name, star_temperature: Q_, star_luminosity: Q_, potential_orbit_eccentricity: float = 0):
        self.name = name
        self.star_temperature = star_temperature
        self.star_luminosity = star_luminosity
        self.potential_orbit_eccentricity = potential_orbit_eccentricity

        self._set_parameters()
        self._set_parameter_names()
        self._set_popular_limit_names()
        self._set_orbit_thresholds_in_sol()
        self._set_threshold_types()
        self._set_insolation_thresholds()
        self._set_spectrally_weighted_luminosities_on_thresholds()

    def _set_parameters(self):
        print('Insolation threshold model does not have a defined _set_parameters function.')
        self.parameters = {}

    def _set_parameter_names(self):
        self.names = list(self.parameters.keys())

    def _set_popular_limit_names(self):
        print('Insolation threshold model does not have a defined _set_popular_limit_names function.')
        self.conservative_min_name = ''
        self.conservative_max_name = ''
        self.relaxed_min_name = ''
        self.relaxed_max_name = ''
        self.earth_equivalent = ''

    def _set_orbit_thresholds_in_sol(self):
        print('Insolation threshold model does not have a defined _set_orbit_thresholds_in_sol function.')
        self.orbit_thresholds_in_sol = {}

    def _set_threshold_types(self):
        print('Insolation threshold model does not have a defined _set_orbit_thresholds_in_sol function.')
        self.threshold_types = {}

    def calculate_insolation_threshold(self, name) -> Q_:
        print('Insolation threshold model does not have a defined calculate_insolation_threshold function.')
        return np.nan * ureg.solar_flux

    def _set_insolation_thresholds(self):
        self.insolation_thresholds = {name: self.calculate_insolation_threshold(name) for name in self.names}

    def _set_spectrally_weighted_luminosities_on_thresholds(self):
        self.spectrally_weighted_luminosities_on_thresholds = {name: calculate_spectrally_weighted_luminosity(
            self.star_luminosity, self.insolation_thresholds[name], self.potential_orbit_eccentricity)
            for name in self.names}
        self.swl = self.spectrally_weighted_luminosities_on_thresholds

    def copy(self):
        return copy.deepcopy(self)


class InsolationByKopparapu(InsolationThresholdModel):

    def __init__(self, star_temperature: Q_, star_luminosity: Q_, potential_orbit_eccentricity: float = 0):
        super().__init__('Kopparapu', star_temperature, star_luminosity, potential_orbit_eccentricity)

    def _set_parameters(self):
        self.parameters = {
            'Recent Venus': {'Seff0': 1.776, 'a': 2.136E-4, 'b': 2.533E-8, 'c': -1.332E-11, 'd': -3.097E-15},
            'Runaway Greenhouse Effect, Subterran': {'Seff0': 0.99, 'a': 1.209E-4, 'b': 1.404E-8, 'c': -7.418E-12,
                                                     'd': -1.713E-15},
            'Runaway Greenhouse Effect, Terran': {'Seff0': 1.107, 'a': 1.332E-4, 'b': 1.58E-8, 'c': -8.308E-12,
                                                  'd': -1.931E-15},
            'Runaway Greenhouse Effect, Superterran': {'Seff0': 1.188, 'a': 1.433E-4, 'b': 1.707E-8, 'c': -8.968E-12,
                                                       'd': -2.084E-15},
            'Moist Greenhouse Effect': {'Seff0': 1.0140, 'a': 8.1774E-5, 'b': 1.7063E-9, 'c': -4.3241E-12,
                                        'd': -6.6462E-16},
            'Maximum Greenhouse Effect': {'Seff0': 0.356, 'a': 6.171E-5, 'b': 1.698E-9, 'c': -3.198E-12,
                                          'd': -5.575E-16},
            'Early Mars': {'Seff0': 0.32, 'a': 5.547E-5, 'b': 1.526E-9, 'c': -2.874E-12, 'd': -5.011E-16}
        }

    def _set_popular_limit_names(self):
        self.conservative_min_name = 'Runaway Greenhouse Effect, Terran'
        self.conservative_max_name = 'Maximum Greenhouse Effect'
        self.relaxed_min_name = 'Recent Venus'
        self.relaxed_max_name = 'Early Mars'
        self.earth_equivalent = 'Moist Greenhouse Effect'

    def _set_orbit_thresholds_in_sol(self):
        self.orbit_thresholds_in_sol = {name: calculate_average_insolation_threshold(
            self.parameters[name]['Seff0']) ** (-1 / 2) * ureg.au for name in self.names}

    def _set_threshold_types(self):
        self.threshold_types = {
            'Recent Venus': 'Inner',
            'Runaway Greenhouse Effect, Subterran': 'Inner',
            'Runaway Greenhouse Effect, Terran': 'Inner',
            'Runaway Greenhouse Effect, Superterran': 'Inner',
            'Moist Greenhouse Effect': 'Inner',
            'Maximum Greenhouse Effect': 'Outer',
            'Early Mars': 'Outer'
        }

    def calculate_insolation_threshold(self, name) -> Q_:
        Ts = self.star_temperature.to('K').m - 5780
        pars = self.parameters[name]
        Seff = pars['Seff0'] + pars['a'] * Ts + pars['b'] * Ts ** 2 + pars['c'] * Ts ** 3 + pars['d'] * Ts ** 4

        return Seff * ureg.solar_flux


class InsolationBySelsis(InsolationThresholdModel):

    def __init__(self, star_temperature: Q_, star_luminosity: Q_, potential_orbit_eccentricity: float = 0):
        super().__init__('Selsis', star_temperature, star_luminosity, potential_orbit_eccentricity)

    def _set_parameters(self):
        self.parameters = {
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

    def _set_popular_limit_names(self):
        self.conservative_min_name = 'Runaway Greenhouse Effect, 0% Clouds'
        self.conservative_max_name = 'Maximum Greenhouse Effect, 0% Clouds'
        self.relaxed_min_name = 'Runaway Greenhouse Effect, 100% Clouds'
        self.relaxed_max_name = 'Maximum Greenhouse Effect, 100% Clouds'
        self.earth_equivalent = 'Earth Equivalent'

    def _set_orbit_thresholds_in_sol(self):
        self.orbit_thresholds_in_sol = {name: self.parameters[name]['sl'] * ureg.au for name in self.names}

    def _set_threshold_types(self):
        self.threshold_types = {
            # Venus-Earth-Mars
            'Recent Venus': 'Inner',
            'Earth Equivalent': 'Inner',
            'Early Mars': 'Outer',
            # 0% Clouds
            'Runaway Greenhouse Effect, 0% Clouds': 'Inner',
            'Start of water loss, 0% Clouds': 'Inner',
            'First C02 Condensation, 0% Clouds': 'Outer',
            'Maximum Greenhouse Effect, 0% Clouds': 'Outer',
            # 50% Clouds
            'Runaway Greenhouse Effect, 50% Clouds': 'Inner',
            'Start of water loss, 50% Clouds': 'Inner',
            'Maximum Greenhouse Effect, 50% Clouds': 'Outer',
            # 100% Clouds
            'Runaway Greenhouse Effect, 100% Clouds': 'Inner',
            'Start of water loss, 100% Clouds': 'Inner',
            'Maximum Greenhouse Effect, 100% Clouds': 'Outer',
        }

    def calculate_insolation_threshold(self, name) -> Q_:
        Ts = self.star_temperature.to('K').m - 5700
        pars = self.parameters[name]
        Seff = (pars['sl'] - pars['a'] * Ts - pars['b'] * Ts ** 2) ** (-2)

        return Seff * ureg.solar_flux


class BinaryInsolationModel:

    def __init__(self, combined_spectral_weighted_luminosity: Dict, child_insolation_model: InsolationThresholdModel):
        self.name = child_insolation_model.name

        self._set_parameter_names(child_insolation_model)
        self._set_popular_limit_names(child_insolation_model)
        self._set_orbit_thresholds_in_sol(child_insolation_model)
        self._set_threshold_types(child_insolation_model)
        self._set_spectrally_weighted_luminosities_on_thresholds(combined_spectral_weighted_luminosity)

    def _set_parameter_names(self, child_insolation_model: InsolationThresholdModel):
        self.names = child_insolation_model.names

    def _set_popular_limit_names(self, child_insolation_model: InsolationThresholdModel):
        self.conservative_min_name = child_insolation_model.conservative_min_name
        self.conservative_max_name = child_insolation_model.conservative_max_name
        self.relaxed_min_name = child_insolation_model.relaxed_min_name
        self.relaxed_max_name = child_insolation_model.relaxed_max_name
        self.earth_equivalent = child_insolation_model.earth_equivalent

    def _set_orbit_thresholds_in_sol(self, child_insolation_model: InsolationThresholdModel):
        self.orbit_thresholds_in_sol = child_insolation_model.orbit_thresholds_in_sol

    def _set_threshold_types(self, child_insolation_model: InsolationThresholdModel):
        self.threshold_types = child_insolation_model.threshold_types

    def _set_spectrally_weighted_luminosities_on_thresholds(self, combined_spectral_weighted_luminosity: Dict):
        self.spectrally_weighted_luminosities_on_thresholds = {}
        self.spectrally_weighted_luminosities_on_thresholds = {name: combined_spectral_weighted_luminosity[name]
                                                               for name in self.names}
        self.swl = self.spectrally_weighted_luminosities_on_thresholds


class InsolationForWaterFrostline(InsolationBySelsis):
    """
     We use Selsis model since it allows for easy, Solar system comparisons.
    As shown on the wikipedia page https://en.wikipedia.org/wiki/Frost_line_(astrophysics), there are different
    frost lines for different compounds. Water is important and seems to determine the line between gas planets and
    rocky planets.
    The inner limit is taken from wiki's suggestion for big sized bodies at 200 K (~1.94 AU),
    the outer limit is taken from wiki's mention on the early-days frost line at 5 AU (~124.5 K),
    and the Sol equivalent limit is from the average of the newest finds ~3.1 AU (~ 158.2 K)
    """

    def _set_parameters(self):
        self.parameters = {
            'Inner Limit': {'sl': 1.94, 'a': 2.7619E-5, 'b': 3.8095E-9},
            'Sol Equivalent': {'sl': 3.1, 'a': 2.7619E-5, 'b': 3.8095E-9},
            'Outer Limit': {'sl': 5, 'a': 1.3786E-4, 'b': 1.4286E-9},
        }

    def _set_popular_limit_names(self):
        self.min_name = 'Inner Limit'
        self.max_name = 'Outer Limit'
        self.sol_equivalent = 'Sol Equivalent'

    def _set_threshold_types(self):
        self.threshold_types = {
            'Inner Limit': 'Inner',
            'Sol Equivalent': 'Inner',
            'Outer Limit': 'Outer',
        }


class InsolationForRockLine(InsolationBySelsis):
    """
     We use Selsis model since it allows for easy, Solar system comparisons.
    Rockline is the distance at which iron and rock can form clusters, planetesimals and eventually planets.
    Since the rockline is determined by when rock and iron are more or less solid, I decided to use:
    For the inner limit, the boiling point of a fast rotating iron ball (heating distribution 1, albedo 0.15) @ 2870 K.
    For the outer limit, the melting point of a slow rotating (tidally locked) (heating distribution 0.5, albedo 0.85)
     rock ball and multiply by 5/3.1 (similar to the early stellar system frostline) @ 600 K (lowest from
     http://hyperphysics.phy-astr.gsu.edu/hbase/Geophys/meltrock.html)
    Formula used: (To/Teff) ** 2 * sqrt((1-albedo)/heatdist)
    """

    def _set_parameters(self):
        self.parameters = {
            'Inner Limit': {'sl': 0.087, 'a': 2.7619E-5, 'b': 3.8095E-9},
            'Outer Limit': {'sl': 0.281, 'a': 1.3786E-4, 'b': 1.4286E-9},
        }

    def _set_popular_limit_names(self):
        self.min_name = 'Inner Limit'
        self.max_name = 'Outer Limit'

    def _set_threshold_types(self):
        self.threshold_types = {
            'Inner Limit': 'Inner',
            'Outer Limit': 'Outer',
        }


class BinaryInsolationForWaterFrostLine(BinaryInsolationModel):

    def __init__(self, frost_lines: Dict, child_insolation_model: InsolationForWaterFrostline):
        super().__init__(frost_lines, child_insolation_model)

    def _set_popular_limit_names(self, child_insolation_model: InsolationForWaterFrostline):
        self.min_name = child_insolation_model.min_name
        self.max_name = child_insolation_model.max_name
        self.sol_equivalent = child_insolation_model.sol_equivalent

    def _set_spectrally_weighted_luminosities_on_thresholds(self, frost_lines: Dict):
        self.spectrally_weighted_luminosities_on_thresholds = {}
        self.spectrally_weighted_luminosities_on_thresholds = {name: frost_lines[name] ** 2 for name in self.names}
        self.swl = self.spectrally_weighted_luminosities_on_thresholds


class BinaryInsolationForRockLine(BinaryInsolationModel):

    def __init__(self, rock_lines: Dict, child_insolation_model: InsolationForRockLine):
        super().__init__(rock_lines, child_insolation_model)

    def _set_popular_limit_names(self, child_insolation_model: InsolationForRockLine):
        self.min_name = child_insolation_model.min_name
        self.max_name = child_insolation_model.max_name

    def _set_spectrally_weighted_luminosities_on_thresholds(self, rock_lines: Dict):
        self.spectrally_weighted_luminosities_on_thresholds = {}
        self.spectrally_weighted_luminosities_on_thresholds = {name: rock_lines[name] ** 2 for name in self.names}
        self.swl = self.spectrally_weighted_luminosities_on_thresholds
