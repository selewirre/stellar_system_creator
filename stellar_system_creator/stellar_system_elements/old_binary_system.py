import numpy as np
from typing import Union, Tuple

import pandas as pd

from stellar_system_creator.astrothings.astromechanical_calculations import \
    calculate_rough_inner_orbit_limit, calculate_rough_outer_orbit_limit, calculate_frost_line, \
    calculate_binary_forbidden_zone_minimum, calculate_binary_forbidden_zone_maximum, calculate_distance_to_barycenter,\
    calculate_minimum_distance_to_barycenter, calculate_maximum_distance_to_barycenter, calculate_roche_limit, \
    calculate_hill_sphere, \
    calculate_earth_equivalent_orbit
from stellar_system_creator.stellar_system_elements.stellar_body import StellarBody, Star, Planet
from stellar_system_creator.astrothings.units import ureg, Q_

# mass_dict_keys = ['mass']
# radius_dict_keys = ['radius', 'suggested_radius', 'circumference']
# radius2_dict_keys = []
# radius3_dict_keys = []
# density_dict_keys = []
# distance_dict_keys = ['distance', 'minimum_distance', 'maximum_distance', 'inner_orbit_limit', 'outer_orbit_limit',
#                       'frost_line', 'forbidden_zone_minimum', 'forbidden_zone_maximum',
#                       'distance_to_binary_barycenter',
#                       'minimum_distance_to_binary_barycenter', 'maximum_distance_to_binary_barycenter',
#                       'habitable_zone_minimum', 'habitable_zone_maximum', 'habitable_zone_earth_equivalent',
#                       'habitable_orbit_range']
# luminosity_dict_keys = ['luminosity']
# ignore_list_dict_keys = ['image_array', 'parent', 'farthest_parent', 'unit_family', 'primary_body', 'secondary_body']
#
# representation_for_unit_conversion_dict = {}
# for parameter in mass_dict_keys:
#     representation_for_unit_conversion_dict[parameter] = 'mass'
# for parameter in radius_dict_keys:
#     representation_for_unit_conversion_dict[parameter] = 'radius'
# for parameter in radius2_dict_keys:
#     representation_for_unit_conversion_dict[parameter] = 'radius2'
# for parameter in radius3_dict_keys:
#     representation_for_unit_conversion_dict[parameter] = 'radius3'
# for parameter in density_dict_keys:
#     representation_for_unit_conversion_dict[parameter] = 'density'
# for parameter in distance_dict_keys:
#     representation_for_unit_conversion_dict[parameter] = 'distance'
# for parameter in luminosity_dict_keys:
#     representation_for_unit_conversion_dict[parameter] = 'luminosity'


class BinarySystem:

    def __init__(self, name, primary_body: Union["BinarySystem", StellarBody],
                 secondary_body: Union["BinarySystem", StellarBody],
                 distance: Q_, system_type=None, eccentricity=np.nan) -> None:

        self.name = name

        if primary_body.mass > secondary_body.mass:
            self.primary_body = primary_body
            self.secondary_body = secondary_body
        else:
            self.primary_body = secondary_body
            self.secondary_body = primary_body

        self.parent = self.primary_body.parent
        self.farthest_parent = self.get_farthest_parent()

        self.distance = distance
        self.system_type = system_type

        self.eccentricity = eccentricity

        self.binary_stellar_body_types = self.get_binary_stellar_body_types()
        self.check_distance_and_system_type()

        self.luminosity = self.calculate_total_luminosity()
        self.mass = self.calculate_total_mass()
        self.primary_body._set_binary_parameters(self.distance, self.mass)
        self.secondary_body._set_binary_parameters(self.distance, self.mass)

        self.minimum_distance = self.calculate_minimum_distance()
        self.maximum_distance = self.calculate_maximum_distance()

        self._set_orbit_values()
        self.check_eccentricity()
        self._set_binary_parameters(np.nan * ureg.au, np.nan * self.mass.u)

        self.planetary_system_stability = self.check_planetary_system_stability()

        if self.system_type == 'P':
            self.habitable_zone_minimum = self.calculate_habitable_zone_minimum()
            self.habitable_zone_maximum = self.calculate_habitable_zone_maximum()
            self.habitable_zone_earth_equivalent = self.calculate_habitable_zone_earth_equivalent()
            self.habitable_orbit_range = self.calculate_habitable_orbit_range()
            self.habitability, self.habitability_violations = self.check_habitability_of_p_type_system()
        elif self.system_type == 'S':
            self.habitability = self.check_habitability_of_s_type_system()

    # @classmethod
    # def load(cls, binary_system: "BinarySystem") -> "BinarySystem":
    #     return cls(binary_system.name, binary_system.primary_body,
    #                binary_system.secondary_body,
    #                binary_system.distance, binary_system.system_type,
    #                binary_system.eccentricity)

    def __repr__(self) -> str:
        string = ''
        keys = list(self.__dict__.keys())
        keys.sort()
        for key in keys:
            if key not in ['image_array', 'parent', 'farthest_parent']:
                value = self.__dict__[key]
                string += f'{key}: {value}\n'
            elif key in ['parent', 'farthest_parent']:
                if self.__dict__[key] is not None:
                    value = self.__dict__[key].name
                    string += f'{key}: {value}\n'
        return string
        # for key in self.__dict__.keys():
        #     if key not in ignore_list_dict_keys:
        #         value = self.__dict__[key]
        #         if key in representation_for_unit_conversion_dict:
        #             # if representation_for_unit_conversion_dict[key] == 'distance' and isinstance(self.parent,
        #                                                                                            Planet):
        #             #     value /= self.unit_family['radius']
        #             # else:
        #             value /= self.unit_family[representation_for_unit_conversion_dict[key]]
        #         if isinstance(value, float):
        #             string += f'{key}: {value:.3g}\n'
        #         else:
        #             if key == 'habitable_orbit_range':
        #                 string += f'{key}: ({value[0]:.3g}, {value[1]:.3g})\n'
        #             else:
        #                 string += f'{key}: {value}\n'
        #     elif key == 'parent' or key == 'farthest_parent' or key == 'primary_body' or key == 'secondary_body':
        #         value = self.__dict__[key]
        #         if value is not None:
        #             value = value.name
        #         string += f'{key}: {value}\n'
        # return string

    def get_binary_stellar_body_types(self) -> str:
        if isinstance(self.primary_body, Star) and isinstance(self.secondary_body, Star):
            return 'Stars'
        elif isinstance(self.primary_body, BinarySystem) and isinstance(self.secondary_body, Star):
            if self.primary_body.binary_stellar_body_types == 'Stars':
                return 'Stars'
        elif isinstance(self.primary_body, Star) and isinstance(self.secondary_body, BinarySystem):
            if self.secondary_body.binary_stellar_body_types == 'Stars':
                return 'Stars'
        elif isinstance(self.primary_body, Planet) and isinstance(self.secondary_body, Planet):
            return 'Planet'
        elif isinstance(self.primary_body, BinarySystem) and isinstance(self.secondary_body, Planet):
            if self.primary_body.binary_stellar_body_types == 'Planet':
                return 'Planet'
        elif isinstance(self.primary_body, Planet) and isinstance(self.secondary_body, BinarySystem):
            if self.secondary_body.binary_stellar_body_types == 'Planet':
                return 'Planet'
        elif isinstance(self.primary_body, BinarySystem) and isinstance(self.secondary_body, BinarySystem):
            if self.primary_body.binary_stellar_body_types == self.secondary_body.binary_stellar_body_types:
                return self.primary_body.binary_stellar_body_types

        raise TypeError('All binary system must comprise of the same core stellar bodies, either planets or stars')

    def check_distance_and_system_type(self) -> None:
        if self.binary_stellar_body_types == 'Stars':
            if 0.15 <= self.distance.to('au').m <= 6:
                if self.system_type is None:
                    self.system_type = 'P'
                else:
                    if self.system_type != 'P':
                        print('Distances between 0.15 and 6 AU correspond to P-type dual star systems.')
                        self.system_type = 'P'
            elif 120 <= self.distance.to('au').m <= 600:
                if self.system_type is None:
                    self.system_type = 'S'
                else:
                    if self.system_type != 'S':
                        print('Distances between 120 and 600 AU correspond to S-type dual star systems.')
                        self.system_type = 'S'
            else:
                raise ValueError('Distance can only be between 0.15 and 6 AU for a P-type star system'
                                 'and between 120 and 600 AU for a S-type dual star system.')

    def calculate_total_mass(self) -> Q_:
        return self.primary_body.mass + self.secondary_body.mass

    def calculate_maximum_distance(self) -> Q_:
        return self.primary_body.maximum_distance_to_binary_barycenter +\
               self.secondary_body.maximum_distance_to_binary_barycenter

    def calculate_minimum_distance(self) -> Q_:
        return self.primary_body.minimum_distance_to_binary_barycenter +\
               self.secondary_body.minimum_distance_to_binary_barycenter

    def calculate_total_luminosity(self) -> Q_:
        return self.primary_body.luminosity + self.secondary_body.luminosity

    def _set_orbit_values(self) -> None:
        if self.system_type == 'P':
            self.rough_inner_orbit_limit = calculate_rough_inner_orbit_limit(self.mass)
            self.rough_outer_orbit_limit = calculate_rough_outer_orbit_limit(self.mass)
            self.frost_line = calculate_frost_line(self.luminosity)

        self.forbidden_zone_minimum = calculate_binary_forbidden_zone_minimum(self.minimum_distance)
        self.forbidden_zone_maximum = calculate_binary_forbidden_zone_maximum(self.maximum_distance)

    def check_planetary_system_stability(self) -> tuple:
        if self.system_type == 'P':
            if self.forbidden_zone_maximum > self.outer_orbit_limit:
                return False,
            else:
                return True,
        elif self.system_type == 'S':
            stability_of_primary_system = True
            if self.primary_body.outer_orbit_limit > self.forbidden_zone_minimum:
                stability_of_primary_system = False
            stability_of_secondary_system = True
            if self.secondary_body.outer_orbit_limit > self.forbidden_zone_minimum:
                stability_of_secondary_system = False
            return stability_of_primary_system, stability_of_secondary_system

    def calculate_distance_to_barycenter(self, distance, total_mass) -> Q_:
        return distance * (self.mass / total_mass)

    def calculate_minimum_distance_to_barycenter(self) -> Q_:
        return (1 - self.eccentricity) * self.distance_to_binary_barycenter

    def calculate_maximum_distance_to_barycenter(self) -> Q_:
        return (1 + self.eccentricity) * self.distance_to_binary_barycenter

    def _set_binary_parameters(self, distance: Q_, total_mass: Q_) -> None:
        self.distance_to_binary_barycenter = calculate_distance_to_barycenter(
            self.mass, distance, total_mass)
        self.minimum_distance_to_binary_barycenter = calculate_minimum_distance_to_barycenter(
            self.eccentricity, self.distance_to_binary_barycenter)
        self.maximum_distance_to_binary_barycenter = calculate_maximum_distance_to_barycenter(
            self.eccentricity, self.distance_to_binary_barycenter)

    def get_farthest_parent(self):
        parent = self.parent
        if parent is not None:
            keep_going_farther = True
            while keep_going_farther:
                if parent.parent is not None:
                    parent = self.parent
                else:
                    keep_going_farther = False
        return parent

    def check_eccentricity(self) -> None:
        if not np.isnan(self.eccentricity):
            if self.binary_stellar_body_types == 'Stars':
                if not 0.4 <= self.eccentricity <= 0.7:
                    raise ValueError('eccentricity values for star binaries must be between 0.4 and 0.7.')

    def calculate_habitable_zone_minimum(self) -> Q_:
        return calculate_habitable_zone_min(self.luminosity)

    def calculate_habitable_zone_maximum(self) -> Q_:
        return calculate_habitable_zone_max(self.luminosity)

    def calculate_habitable_zone_earth_equivalent(self) -> Q_:
        return calculate_earth_equivalent_orbit(self.luminosity)

    def calculate_habitable_orbit_range(self) -> Tuple[Q_, Q_]:
        return 2 * self.maximum_distance, 4 * self.maximum_distance

    def check_habitability_of_p_type_system(self) -> Tuple[bool, str]:
        habitability = True
        habitability_violations = []

        if self.inner_orbit_limit > self.habitable_orbit_range[1] or self.outer_orbit_limit < self.habitable_orbit_range[0]:
            habitability = False
            habitability_violations.append('Habitable orbit range is outside the system\'s limits.')

        if self.forbidden_zone_minimum < self.habitable_orbit_range[0] and self.forbidden_zone_maximum > self.habitable_orbit_range[1]:
            habitability = False
            habitability_violations.append('Habitable orbit range is within the system\'s forbidden zone.')

        if self.habitable_zone_minimum > self.habitable_orbit_range[1] or self.outer_orbit_limit < self.habitable_orbit_range[0]:
            habitability = False
            habitability_violations.append('Habitable orbit range is outside the system\'s habitable zone.')

        if not all(self.planetary_system_stability):
            habitability = False
            habitability_violations.append('The multi-star system is not stable.')

        return habitability, ' '.join(habitability_violations)

    def check_habitability_of_s_type_system(self) -> Tuple[bool, bool]:
        habitability_of_primary_system = self.primary_body.habitability and self.planetary_system_stability[0]
        habitability_of_secondary_system = self.secondary_body.habitability and self.planetary_system_stability[1]

        return habitability_of_primary_system, habitability_of_secondary_system

    def calculate_roche_limit_for_child(self, child) -> Q_:
        return calculate_roche_limit(child, self)

    def calculate_hill_sphere_for_child(self, child) -> Q_:
        return calculate_hill_sphere(child, self)

    def save_as_csv(self, filename) -> None:
        repr_string = self.__repr__()
        lines = repr_string.split('\n')[:-1]
        characteristics = [line.split(': ')[0] for line in lines]
        values = [line.split(': ')[1] for line in lines]
        dataframe = pd.DataFrame(data={'Characteristics': characteristics, 'Values': values})
        dataframe.to_csv(filename, index=False)
