import copy
import warnings

import inspect
import pandas as pd
from pint import UnitStrippedWarning

from stellar_system_creator.astrothings.astromechanical_calculations import *
from stellar_system_creator.astrothings.habitability_calculations import *
from stellar_system_creator.astrothings.find_mass_class import get_star_mass_class, get_star_appearance_frequency, \
    get_planetary_mass_class
from stellar_system_creator.astrothings.luminosity_models.solar_luminosity_model import \
    calculate_main_sequence_luminosity, calculate_blackhole_luminosity
from stellar_system_creator.astrothings.luminosity_models.planetary_luminosity_model import \
    calculate_planetary_luminosity
from stellar_system_creator.astrothings.radius_models.hot_gasgiant_radius_model import is_gasgiant_hot, \
    get_hot_gas_giant_mass_class
from stellar_system_creator.astrothings.radius_models.planetary_radius_model import calculate_planet_radius, \
    image_composition_dict, \
    planet_chemical_abundance_ratios
from stellar_system_creator.astrothings.radius_models.solar_radius_model import calculate_main_sequence_radius, \
    calculate_blackhole_radius
from stellar_system_creator.astrothings.rotation_models.planetary_rotation_model import \
    calculate_planetary_rotation_period
from stellar_system_creator.astrothings.insolation_models.insolation_models import InsolationByKopparapu, \
    InsolationBySelsis, InsolationForWaterFrostline, BinaryInsolationForWaterFrostLine, InsolationForRockLine, \
    BinaryInsolationForRockLine
from stellar_system_creator.astrothings.units import Q_, ureg
from stellar_system_creator.visualization.drawing_tools import GradientColor
from stellar_system_creator.visualization.stellar_body_images import adjust_star_image_by_temp, \
    stellar_body_marker_dict, load_user_image
import numpy as np
import scipy.stats as stats
from typing import Tuple, Union, List


class StellarBody:

    def __init__(self, name, mass: Q_, radius: Q_ = np.nan * ureg.R_s, luminosity: Q_ = np.nan * ureg.L_s,
                 spin_period: Q_ = np.nan * ureg.hours, age: Q_ = np.nan * ureg.solar_lifetime,
                 parent=None, image_filename: str = None) -> None:

        self._set_children_list()
        self.name = name
        self.mass = mass
        self.radius = radius
        self.luminosity = luminosity
        self.spin_period = spin_period
        self.age = age
        self._set_parent(parent)
        self.image_filename = image_filename
        self.__post_init__()

    def __post_init__(self, want_to_update_parent=False):

        from stellar_system_creator.stellar_system_elements.binary_system import BinarySystem
        self.part_of_binary = isinstance(self.parent, BinarySystem)

        self.farthest_parent = self.get_farthest_parent()
        self._get_radius()
        self._set_geometrical_values()
        self._get_luminosity()

        self.temperature = self.calculate_temperature()
        self.lifetime = self.calculate_lifetime()
        self._get_age()

        self._set_orbit_values()
        self._get_spin_period()

        self.mass_class = self.get_mass_class()

        self._set_other_characteristics()
        self.habitability, self.habitability_violations = self.check_habitability()

        self._get_image()

        if want_to_update_parent:
            self.update_parent()

    def __repr__(self, precision=4) -> str:
        string = ''
        keys = list(self.__dict__.keys())
        keys.sort()
        for key in keys:
            if key not in ['image_array', 'parent', 'farthest_parent', 'insolation_model', '_children']:
                value = self.__dict__[key]
                if isinstance(value, dict):
                    if isinstance(list(value.values())[0], Q_):
                        value_string = ', '.join([f"'{k}': {value[k]:.{precision}g~P}" for k in value.keys()])
                        string += f'{key}: {{{value_string}}}\n'
                    elif isinstance(list(value.values())[0], dict):
                        part_strings = []
                        for k in value.keys():
                            val: dict = value[k]
                            if isinstance(list(val.values())[0], Q_):
                                value_string = ', '.join([f'{k2}: {val[k2]:.{precision}g~P}' for k2 in val.keys()])
                                part_strings.append(f'{k}: {{{value_string}}}')
                            else:
                                part_strings.append(f'{k}: {val}')
                        string += f'{key}: {{' + ', '.join(part_strings) + "}\n"
                    else:
                        string += f'{key}: {value}\n'
                elif isinstance(value, bool):
                    string += f'{key}: {value}\n'
                elif isinstance(value, (float, int)):
                    string += f'{key}: {value:.{precision}g}\n'
                elif isinstance(value, Q_):
                    string += f'{key}: {value:.{precision}g~P}\n'
                else:
                    string += f'{key}: {value}\n'
            elif key in ['parent', 'farthest_parent', 'insolation_model']:
                if self.__dict__[key] is not None:
                    value = self.__dict__[key].name
                    string += f'{key}: {value}\n'
            elif key in ['_children']:
                if self.__dict__[key] is not None:
                    value = [el.name for el in self.__dict__[key]]
                    string += f'{key}: {value}\n'
        return string

    def calculate_suggested_radius(self) -> Q_:
        print(f'The radius function for {self.name} was not defined')
        return np.nan * ureg.R_s

    def calculate_suggested_luminosity(self) -> Q_:
        print(f'The luminosity function for {self.name} was not defined')
        return np.nan * ureg.L_s

    def calculate_suggested_spin_period(self) -> Q_:
        print(f'The spin period function for {self.name} was not defined')
        return np.nan * ureg.hours

    def calculate_temperature(self) -> Q_:
        print(f'The temperature function for {self.name} was not defined')
        return np.nan * ureg.kelvin

    def _set_children_list(self):
        self._children = []

    def add_child(self, new_child):
        if new_child not in self._children:
            self._children.append(new_child)

    def remove_child(self, old_child):
        if old_child in self._children:
            self._children.remove(old_child)

    def update_children(self):
        for child in self._children:
            child.__post_init__()

    def update_parent(self):
        from stellar_system_creator.stellar_system_elements.binary_system import BinarySystem
        if isinstance(self.parent, BinarySystem):
            if self.parent.primary_body == self or self.parent.secondary_body == self:
                self.parent.__post_init__()

    def _set_parent(self, parent):
        from stellar_system_creator.stellar_system_elements.binary_system import StellarBinary
        self.parent: Union[Star, Planet, StellarBinary]
        if parent is None:
            self.parent = parent
        elif 'parent' not in self.__dict__:
            self.parent = parent
            self.parent.add_child(self)
        elif self.parent is None:
            self.parent = parent
            self.parent.add_child(self)
        elif self.parent != parent:
            self.parent.remove_child(self)
            self.parent = parent
            self.parent.add_child(self)
        self.part_of_binary = isinstance(self.parent, StellarBinary)

    def _get_radius(self) -> None:
        if 'suggested_radius' in self.__dict__:
            previous_suggested_radius = self.suggested_radius
        else:
            previous_suggested_radius = -999 * ureg.R_s
        self.suggested_radius = self.calculate_suggested_radius()
        if np.isnan(self.radius.m) or previous_suggested_radius == self.radius:
            self.radius = self.suggested_radius

    def _get_luminosity(self) -> None:
        if 'suggested_luminosity' in self.__dict__:
            previous_suggested_luminosity = self.suggested_luminosity
        else:
            previous_suggested_luminosity = -999 * ureg.L_s
        self.suggested_luminosity = self.calculate_suggested_luminosity()
        if np.isnan(self.luminosity.m) or previous_suggested_luminosity == self.luminosity:
            self.luminosity = self.suggested_luminosity

    def _get_spin_period(self) -> None:
        if 'suggested_spin_period' in self.__dict__:
            previous_suggested_spin_period = self.suggested_spin_period
        else:
            previous_suggested_spin_period = -999 * ureg.days
        self.suggested_spin_period = self.calculate_suggested_spin_period()
        if np.isnan(self.spin_period.m) or previous_suggested_spin_period == self.spin_period:
            self.spin_period = self.suggested_spin_period

    def _get_age(self) -> None:
        if 'suggested_age' in self.__dict__:
            previous_suggested_age = self.suggested_age
        else:
            previous_suggested_age = -999 * ureg.T_s
        if self.part_of_binary:
            if self.parent.primary_body.lifetime < self.parent.secondary_body.lifetime:
                self.suggested_age = self.parent.primary_body.lifetime / 2
            else:
                self.suggested_age = self.parent.secondary_body.lifetime / 2
        else:
            self.suggested_age = self.lifetime / 2
        if np.isnan(self.age.m) or previous_suggested_age == self.age:
            self.age = self.suggested_age

    def _set_geometrical_values(self) -> None:
        self.circumference = calculate_circumference(self.radius)
        self.surface_area = calculate_surface_area(self.radius)
        self.volume = calculate_volume(self.radius)
        self.density = calculate_density(self.mass, self.volume)

    def _set_orbit_values(self) -> None:
        pass

    def _get_image(self):
        # self.suggested_image_filename = None
        if self.image_filename is None or self.image_filename.lower() == 'none' or self.image_filename == '':
            self.image_array = self.get_image_array()
        else:
            try:
                self.image_array = self.load_image_array()
            except FileNotFoundError:
                self.image_filename = None
                self.image_array = self.get_image_array()

    def calculate_tidal_locking_radius(self):
        return calculate_tidal_locking_radius(self.mass, self.age)

    def _set_other_characteristics(self):
        print(f'The _set_other_characteristics function for {self.name} was not defined')

    def get_farthest_parent(self):
        parent = self.parent
        if parent is not None:
            keep_going_farther = True
            while keep_going_farther:
                if parent.parent is not None:
                    parent = parent.parent
                else:
                    keep_going_farther = False
        return parent

    def get_image_array(self) -> np.ndarray:
        print(f'The image array function for {self.name} was not defined')
        return np.nan

    def load_image_array(self) -> np.ndarray:
        return load_user_image(self.image_filename)

    def get_mass_class(self) -> str:
        print(f'The mass class identification function for {self.name} was not defined')
        return ''

    def check_habitability(self) -> Tuple[bool, str]:
        print(f'The habitability checking function for {self.name} was not defined')
        return False, 'Could not perform habitability check'

    def calculate_roche_limit(self) -> Q_:
        if self.parent is not None:
            return calculate_roche_limit(self, self.parent)
        else:
            return np.nan * ureg.au

    def calculate_hill_sphere(self) -> Q_:
        from .binary_system import BinarySystem
        if self.parent is not None:
            if isinstance(self.parent, BinarySystem):
                if self.parent.primary_body == self:
                    return calculate_roche_lobe(self.parent.primary_body.mass, self.parent.secondary_body.mass,
                                                self.parent.mean_distance, self.parent.eccentricity)
                    # return calculate_hill_sphere(self, self.parent.secondary_body)
                elif self.parent.secondary_body == self:
                    return calculate_roche_lobe(self.parent.secondary_body.mass, self.parent.primary_body.mass,
                                                self.parent.mean_distance, self.parent.eccentricity)
                    # return calculate_hill_sphere(self, self.parent.primary_body)
                else:
                    return calculate_hill_sphere(self, self.parent)
            else:
                return calculate_hill_sphere(self, self.parent)
        else:
            return 2 * ureg.lightyears

    def calculate_lifetime(self) -> Q_:
        print(f'The lifetime function for {self.name} was not defined')
        return np.nan * ureg.T_s

    def save_as_csv(self, filename, precision=4) -> None:
        repr_string = self.__repr__(precision)
        lines = repr_string.split('\n')[:-1]
        characteristics = [line.split(': ')[0] for line in lines]
        values = [line.split(': ')[1:] for line in lines]
        final_output = []
        for value in values:
            if len(value) == 1:
                value = value[0]
            else:
                value = ': '.join([v for v in value])
            final_output.append(value)
        dataframe = pd.DataFrame(data={'Characteristics': characteristics, 'Values': final_output})
        dataframe.to_csv(filename, index=False)

    def copy(self):
        return copy.deepcopy(self)

    def __hash__(self):
        return super().__hash__()

    @property
    def children(self):
        return self._children

    @classmethod
    def load_with_args(cls, stellar_body: "StellarBody"):
        arg_keys = inspect.getfullargspec(cls)
        kwargs = {key: stellar_body.__dict__[key] for key in arg_keys}
        kwargs.pop('image_filename')
        cls_obj = cls(**kwargs)
        cls_obj.image_filename = stellar_body.image_filename
        cls_obj.image_array = stellar_body.image_array
        return cls_obj


class Star(StellarBody):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    def get_mass_class(self) -> Q_:
        return get_star_mass_class(self.mass)

    def get_frequency(self) -> float:
        return get_star_appearance_frequency(self.mass_class)

    def get_luminosity_class(self) -> str:
        print(f'The luminosity identification class for {self.name} was not defined')
        return ''

    def calculate_water_frost_lines(self):
        # setting single star frost zone
        model = InsolationForWaterFrostline(self.temperature, self.luminosity)
        ss_water_frost_lines = {name: calculate_single_star_habitable_orbital_threshold(
            model.swl[name]) for name in model.names}

        # setting average frost zone for S-type binary
        from stellar_system_creator.stellar_system_elements.binary_system import StellarBinary
        if isinstance(self.parent, StellarBinary):
            if self.parent.primary_body == self:
                companion_body = self.parent.secondary_body
            else:
                companion_body = self.parent.primary_body
            if isinstance(companion_body, StellarBinary):
                comp_prim_insolation_model = InsolationForWaterFrostline(companion_body.primary_body.temperature,
                                                                         companion_body.primary_body.luminosity)
                comp_model_swl = BinaryInsolationForWaterFrostLine(companion_body.water_frost_lines,
                                                                   comp_prim_insolation_model).swl
            else:
                comp_model_swl = InsolationForWaterFrostline(companion_body.temperature, companion_body.luminosity).swl

            mean_distance = self.parent.mean_distance
            eccentricity = self.parent.eccentricity

            water_frost_lines_in_binary = {name: calculate_stype_average_habitable_limit(
                model.swl[name], comp_model_swl[name], mean_distance, eccentricity) for name in model.names}
            water_frost_lines_in_binary = {name: line if self.parent.minimum_distance > line > 0 else np.nan * line.u
                                           for (name, line) in water_frost_lines_in_binary.items()}
        else:
            water_frost_lines_in_binary = None

        return ss_water_frost_lines, water_frost_lines_in_binary

    def calculate_rock_lines(self):
        # setting single star frost zone
        model = InsolationForRockLine(self.temperature, self.luminosity)
        ss_rock_lines = {name: calculate_single_star_habitable_orbital_threshold(
            model.swl[name]) for name in model.names}

        # setting average frost zone for S-type binary
        from stellar_system_creator.stellar_system_elements.binary_system import StellarBinary
        if isinstance(self.parent, StellarBinary):
            if self.parent.primary_body == self:
                companion_body = self.parent.secondary_body
            else:
                companion_body = self.parent.primary_body
            if isinstance(companion_body, StellarBinary):
                comp_prim_insolation_model = InsolationForRockLine(companion_body.primary_body.temperature,
                                                                   companion_body.primary_body.luminosity)
                comp_model_swl = BinaryInsolationForRockLine(companion_body.rock_lines, comp_prim_insolation_model).swl
            else:
                comp_model_swl = InsolationForRockLine(companion_body.temperature, companion_body.luminosity).swl

            mean_distance = self.parent.mean_distance
            eccentricity = self.parent.eccentricity

            rock_lines_in_binary = {name: calculate_stype_average_habitable_limit(
                model.swl[name], comp_model_swl[name], mean_distance, eccentricity) for name in model.names}
            rock_lines_in_binary = {name: line if self.parent.minimum_distance > line > 0 else np.nan * line.u
                                    for (name, line) in rock_lines_in_binary.items()}
        else:
            rock_lines_in_binary = None

        return ss_rock_lines, rock_lines_in_binary

    def calculate_temperature(self) -> Q_:
        return calculate_temperature(self.luminosity, self.radius)  # in Kelvin

    def calculate_spectrum_peak_wavelength(self) -> Q_:
        return calculate_spectrum_peak_wavelength(self.temperature)  # in nanometers

    def _set_orbit_values(self) -> None:
        warnings.filterwarnings("ignore", category=UnitStrippedWarning)
        self.rough_inner_orbit_limit = calculate_rough_inner_orbit_limit(self.mass)
        self.rough_outer_orbit_limit = calculate_rough_outer_orbit_limit(self.mass)
        self.hill_sphere = self.calculate_hill_sphere()
        self.dense_roche_limit = calculate_approximate_inner_orbit_limit(self.radius)
        self.tidal_locking_radius = self.calculate_tidal_locking_radius()

        self.water_frost_lines, self.water_frost_lines_in_binary = self.calculate_water_frost_lines()
        self.rock_lines, self.rock_lines_in_binary = self.calculate_rock_lines()
        if self.part_of_binary:
            self.water_frost_line = self.water_frost_lines_in_binary['Sol Equivalent']
            self.rock_line = self.rock_lines_in_binary['Outer Limit']
            self.prevailing_water_frost_lines = self.water_frost_lines_in_binary
            self.prevailing_rock_lines = self.rock_lines_in_binary
        else:
            self.water_frost_line = self.water_frost_lines['Sol Equivalent']
            self.rock_line = self.rock_lines['Outer Limit']
            self.prevailing_water_frost_lines = self.water_frost_lines
            self.prevailing_rock_lines = self.rock_lines
        from stellar_system_creator.stellar_system_elements.binary_system import StellarBinary
        if isinstance(self.parent, StellarBinary):
            self.stype_critical_orbit = calculate_wide_binary_critical_orbit(
                (self.mass / self.parent.mass).to_reduced_units().m, self.parent.mean_distance,
                self.parent.eccentricity)
        else:
            self.stype_critical_orbit = np.nan * self.rough_outer_orbit_limit.units

        # self_inner_limits = np.array([self.rough_inner_orbit_limit, self.rock_line], dtype=Q_)
        # self_maximum_inner_limit_index = np.nanargmax(self_inner_limits)
        # self.inner_orbit_limit = self_inner_limits[self_maximum_inner_limit_index]
        self.inner_orbit_limit = self.rough_inner_orbit_limit

        outer_limits = np.array([self.stype_critical_orbit,
                                 self.rough_outer_orbit_limit,
                                 self.hill_sphere], dtype=Q_)
        outer_limits = np.array([ol for ol in outer_limits if not np.isnan(ol.m)], dtype=Q_)
        if len(outer_limits):
            minimum_outer_limit_index = np.nanargmin(outer_limits)
            self.outer_orbit_limit = outer_limits[minimum_outer_limit_index]
        else:
            self.outer_orbit_limit = np.nan * self.stype_critical_orbit.units

    def _set_other_characteristics(self):
        self.luminosity_class = self.get_luminosity_class()
        self.appearance_frequency = self.get_frequency()
        self.temperature = self.calculate_temperature()
        self.peak_wavelength = self.calculate_spectrum_peak_wavelength()
        self.reset_insolation_model_and_habitability()

    def _set_insolation_model(self, model_name=None):
        if 'insolation_model' not in self.__dict__:
            if model_name is None:
                self.insolation_model = InsolationByKopparapu(self.temperature, self.luminosity)
            elif model_name == 'Kopparapu':
                self.insolation_model = InsolationByKopparapu(self.temperature, self.luminosity)
            else:
                self.insolation_model = InsolationBySelsis(self.temperature, self.luminosity)
        elif model_name is not None:
            if model_name != self.insolation_model.name:
                if model_name == 'Kopparapu':
                    self.insolation_model = InsolationByKopparapu(self.temperature, self.luminosity)
                else:
                    self.insolation_model = InsolationBySelsis(self.temperature, self.luminosity)
        elif self.temperature != self.insolation_model.star_temperature \
                or self.luminosity != self.insolation_model.star_luminosity:
            if self.insolation_model.name == 'Kopparapu':
                self.insolation_model = InsolationByKopparapu(self.temperature, self.luminosity)
            else:
                self.insolation_model = InsolationBySelsis(self.temperature, self.luminosity)

    def set_habitable_zone(self, zone_type: str, binary_companion=None):
        model = self.insolation_model
        comp_model_swl = None
        if binary_companion is not None:
            comp_model = binary_companion.insolation_model
            comp_model_swl = comp_model.swl

        if zone_type == 'SSHZ':
            self.habitable_zone_limits['SSHZ'] = {name: calculate_single_star_habitable_orbital_threshold(
                model.swl[name]) for name in model.names}
        elif zone_type == 'RHZ' and binary_companion is not None:
            mean_distance = self.parent.mean_distance
            self.habitable_zone_limits['RHZ'] = {name: calculate_stype_radiative_habitable_limit(
                model.swl[name], comp_model_swl[name], mean_distance, model.threshold_types[name])
                for name in model.names}
        elif zone_type == 'PHZ' and binary_companion is not None:
            mean_distance = self.parent.mean_distance
            eccentricity = self.parent.eccentricity
            self.habitable_zone_limits['PHZ'] = {name: calculate_stype_permanent_habitable_limit(
                model.swl[name], comp_model_swl[name], mean_distance, eccentricity, model.threshold_types[name])
                for name in model.names}
        elif zone_type == 'AHZ' and binary_companion is not None:
            mean_distance = self.parent.mean_distance
            eccentricity = self.parent.eccentricity
            self.habitable_zone_limits['AHZ'] = {name: calculate_stype_average_habitable_limit(
                model.swl[name], comp_model_swl[name], mean_distance, eccentricity) for name in model.names}

        if zone_type in self.habitable_zone_limits:
            if self.habitable_zone_limits[zone_type][model.earth_equivalent] > \
                    self.habitable_zone_limits[zone_type][model.conservative_max_name]:
                self.habitable_zone_limits[zone_type] = {name: np.nan * ureg.au for name in model.names}

    def set_solo_habitable_zones(self):
        self.set_habitable_zone('SSHZ')

    def set_dual_habitable_zones(self):
        from stellar_system_creator.stellar_system_elements.binary_system import StellarBinary
        if isinstance(self.parent, StellarBinary):
            if self.parent.primary_body == self:
                companion_body = self.parent.secondary_body
            else:
                companion_body = self.parent.primary_body
            self.set_habitable_zone('RHZ', companion_body)
            self.set_habitable_zone('PHZ', companion_body)
            self.set_habitable_zone('AHZ', companion_body)
            model = self.insolation_model
            if np.isnan(self.habitable_zone_limits['RHZ'][model.earth_equivalent].m):
                self.habitable_zone_limits['PHZ'] = {name: np.nan * ureg.au for name in model.names}
                self.habitable_zone_limits['AHZ'] = {name: np.nan * ureg.au for name in model.names}

    def set_habitable_zones(self) -> None:
        self.set_solo_habitable_zones()
        self.set_dual_habitable_zones()

    def check_habitability(self) -> Tuple[bool, str]:
        habitability = True
        habitability_violations = []

        if 'AHZ' in self.habitable_zone_limits.keys():
            relevant_zone_type = 'AHZ'
        elif 'PHZ' in self.habitable_zone_limits.keys():
            relevant_zone_type = 'PHZ'
        elif 'RHZ' in self.habitable_zone_limits.keys():
            relevant_zone_type = 'RHZ'
        else:
            relevant_zone_type = 'SSHZ'

        model = self.insolation_model
        if self.habitable_zone_limits[relevant_zone_type][model.relaxed_max_name] \
                < self.habitable_zone_limits[relevant_zone_type][model.relaxed_min_name] or \
                np.isnan(self.habitable_zone_limits[relevant_zone_type][model.relaxed_min_name]):
            habitability = False
            habitability_violations.append('There are no habitable zones in this system.')
        elif self.inner_orbit_limit > self.habitable_zone_limits[relevant_zone_type][model.relaxed_max_name] \
                or self.outer_orbit_limit < self.habitable_zone_limits[relevant_zone_type][model.relaxed_min_name]:
            habitability = False
            habitability_violations.append('No overlap between the relaxed habitable zone and the orbit'
                                           ' boundaries.')

        # from https://link.springer.com/article/10.1007/BF00160399
        if self.lifetime < 1 * ureg.gigayears:
            habitability = False
            habitability_violations.append('Star lifetime is smaller than 1 billion years, making the development'
                                           ' of life unlikely.')

        if not len(habitability_violations):
            habitability_violations.append('None.')

        return habitability, ' '.join(habitability_violations)

    def reset_insolation_model(self, model_name='Kopparapu'):
        self._set_insolation_model(model_name)
        self._set_orbit_values()  # here for cause the frost lines also depend on the binary

    def reset_solo_habitability(self):
        self.habitable_zone_limits = {}
        self.set_solo_habitable_zones()
        self.do_habitability_check()

    def do_habitability_check(self):
        self.habitability, self.habitability_violations = self.check_habitability()

    def reset_insolation_model_and_habitability(self, model_name='Kopparapu'):
        self.reset_insolation_model(model_name)
        self.reset_solo_habitability()
        try:
            self.set_dual_habitable_zones()
            self.do_habitability_check()
        except Exception:
            pass


class MainSequenceStar(Star):

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    def get_luminosity_class(self) -> str:
        return 'V'

    def calculate_suggested_radius(self) -> Q_:
        return calculate_main_sequence_radius(self.mass)

    def calculate_suggested_spin_period(self) -> Q_:
        return np.nan * ureg.hours

    def calculate_suggested_luminosity(self) -> Q_:
        return calculate_main_sequence_luminosity(self.mass)

    def calculate_lifetime(self) -> Q_:
        return calculate_main_sequence_stellar_lifetime(self.mass, self.luminosity)

    def get_image_array(self) -> np.ndarray:
        image_array = stellar_body_marker_dict['star'].copy()
        image_array = adjust_star_image_by_temp(image_array, self.temperature.to('kelvin').magnitude)
        return image_array


class BlackHole(Star):

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    def get_luminosity_class(self) -> str:
        return 'Black hole'

    def calculate_suggested_radius(self) -> Q_:
        return calculate_blackhole_radius(self.mass)

    def calculate_suggested_spin_period(self) -> Q_:
        return np.nan * ureg.hours

    def calculate_suggested_luminosity(self) -> Q_:
        return calculate_blackhole_luminosity(self.mass)

    def calculate_lifetime(self) -> Q_:
        return calculate_blackhole_lifetime(self.mass)

    def get_image_array(self) -> np.ndarray:
        image_array = stellar_body_marker_dict['blackhole'].copy()
        return image_array


class Planet(StellarBody):

    def __init__(self, name, mass: Q_, radius: Q_ = np.nan * ureg.R_e, parent=None,
                 semi_major_axis: Q_ = np.nan * ureg.au, orbital_eccentricity: float = np.nan, orbit_type='prograde',
                 composition='Rockworld70', spin_period: Q_ = np.nan * ureg.days, inclination: Q_ = 0 * ureg.deg,
                 longitude_of_ascending_node: Q_ = 0 * ureg.deg, argument_of_periapsis: Q_ = np.nan * ureg.deg,
                 axial_tilt: Q_ = 0 * ureg.deg, albedo: float = 0, normalized_greenhouse: float = 0,
                 heat_distribution: float = 1, emissivity: float = 1,
                 luminosity: Q_ = np.nan * ureg.L_s, age: Q_ = np.nan * ureg.T_s, image_filename=None,
                 has_ring: bool = False) -> None:

        self.semi_major_axis = semi_major_axis
        self.orbital_eccentricity = orbital_eccentricity
        self.orbit_type = orbit_type
        self.composition = composition
        self.inclination = inclination
        self.longitude_of_ascending_node = longitude_of_ascending_node
        self.argument_of_periapsis = argument_of_periapsis
        self.axial_tilt = axial_tilt
        self.albedo = albedo  # earth, uranus, neptune ~ 0.3. jupiter, saturn ~ 0.34. mercury, mars ~0.14. venus ~ 0.75
        self.normalized_greenhouse = normalized_greenhouse  # for earth ~ 0.34
        self.heat_distribution = heat_distribution  # ~ 1 for all fast rotating planets (not tidally locked)
        # ~0.5 for tidally locked planets with no atmosphere and no oceans
        self.emissivity = emissivity
        self.has_ring = has_ring

        super().__init__(name, mass, radius, luminosity, spin_period, age, parent, image_filename)

    def __post_init__(self, want_to_update_parent=False):
        self._get_suggested_orbital_eccentricity()
        self.incident_flux = self.calculate_incident_flux()
        self.temperature = self.calculate_temperature()

        super().__post_init__(want_to_update_parent)
        self.ring = self.get_ring()

    def _get_suggested_orbital_eccentricity(self) -> None:
        if 'suggested_orbital_eccentricity' in self.__dict__:
            previous_suggested_orbital_eccentricity = self.suggested_orbital_eccentricity
        else:
            previous_suggested_orbital_eccentricity = -999
        self.suggested_orbital_eccentricity = self.calculate_suggested_orbital_eccentricity()
        if np.isnan(self.orbital_eccentricity) or previous_suggested_orbital_eccentricity == self.orbital_eccentricity:
            self.orbital_eccentricity = self.suggested_orbital_eccentricity

    def _get_age(self) -> None:
        if 'suggested_age' in self.__dict__:
            previous_suggested_age = self.suggested_age
        else:
            previous_suggested_age = -999 * ureg.T_s
        if self.parent is not None:
            self.suggested_age = self.parent.age - 0.1 * ureg.Gyr
        else:
            self.suggested_age = np.nan * ureg.T_s
        if np.isnan(self.age.m) or previous_suggested_age == self.age:
            self.age = self.suggested_age

    def calculate_suggested_orbital_eccentricity(self) -> float:
        from stellar_system_creator.stellar_system_elements.binary_system import BinarySystem
        if self.parent is None:
            return 0
        elif isinstance(self.parent, BinarySystem):
            secondary_star_mass_ratio = self.parent.secondary_body.mass / self.parent.mass
            return calculate_forced_eccentricity_in_close_binary(self.semi_major_axis, self.parent.mean_distance,
                                                                 self.parent.eccentricity, secondary_star_mass_ratio)
        elif isinstance(self.parent, Star) and self.parent.parent is None:
            return 0
        elif isinstance(self.parent, Star) and isinstance(self.parent.parent, BinarySystem):
            return calculate_forced_eccentricity_in_wide_binary(self.semi_major_axis, self.parent.parent.mean_distance,
                                                                self.parent.parent.eccentricity)
        elif isinstance(self.parent, Planet) and self.parent.parent is not None:
            return 0
        else:
            return np.nan

    def calculate_suggested_radius(self) -> Q_:
        return calculate_planet_radius(self.mass, self.composition, self.incident_flux)

    def calculate_suggested_luminosity(self) -> Q_:
        temperature_average_incident_flux = self.calculate_incident_flux(ecc_correction='temp')
        return calculate_planetary_luminosity(self.temperature, temperature_average_incident_flux, self.albedo,
                                              self.surface_area)

    def calculate_suggested_spin_period(self) -> Q_:
        """
        From our own stellar system averages. Does not account for atmospheric tides (like Venus) or tidal locking
        (like Mercury). Spin is also going to be affected by other crushing objects, and exchange of angular momentum with
        heavy satellites (e.g. moon).
        """
        if self.parent is not None:
            if self.parent.tidal_locking_radius > self.semi_major_axis:
                return self.orbital_period
            else:
                return calculate_planetary_rotation_period(self.mass, self.radius)
        else:
            return np.nan * ureg.days

    def get_mass_class(self) -> str:
        return get_planetary_mass_class(self.mass)

    def get_image_array(self) -> np.ndarray:
        if self.composition != '':
            if self.habitability and not self.composition.startswith('Waterworld'):
                image = stellar_body_marker_dict['habitableworld'].copy()
            else:
                image = stellar_body_marker_dict[image_composition_dict[self.composition]].copy()
            if self.composition == 'Gasgiant' and self.is_gasgiant_hot():
                image = stellar_body_marker_dict['hotgasgiant'].copy()
            if self.composition.startswith('Waterworld') and self.temperature.m < 250:
                image = stellar_body_marker_dict['cold_waterworld'].copy()
            return image
        else:
            return np.nan

    def calculate_incident_flux(self, ecc_correction='flux') -> Q_:
        from stellar_system_creator.stellar_system_elements.binary_system import BinarySystem
        if isinstance(self.parent, BinarySystem):
            incident_flux_from_primary = calculate_part_incident_flux_in_close_binary(
                self.parent.primary_body.luminosity, self.parent.primary_body.mass / self.parent.mass,
                self.semi_major_axis, self.parent.mean_distance, self.orbital_eccentricity, self.parent.eccentricity,
                ecc_correction)
            incident_flux_from_secondary = calculate_part_incident_flux_in_close_binary(
                self.parent.secondary_body.luminosity, self.parent.secondary_body.mass / self.parent.mass,
                self.semi_major_axis, self.parent.mean_distance, self.orbital_eccentricity, self.parent.eccentricity,
                ecc_correction)
            incident_flux = incident_flux_from_primary + incident_flux_from_secondary
        elif self.parent is not None:
            incident_flux = calculate_incident_flux(self.parent.luminosity, self.semi_major_axis,
                                                    self.orbital_eccentricity, ecc_correction)
            if self.parent.part_of_binary:
                if self.parent.parent.primary_body == self:
                    companion_body = self.parent.parent.primary_body
                else:
                    companion_body = self.parent.parent.secondary_body
                incident_flux = incident_flux + calculate_companion_incident_flux_in_wide_binary(
                    companion_body.luminosity, self.semi_major_axis, self.parent.parent.mean_distance,
                    self.orbital_eccentricity, self.parent.parent.eccentricity, ecc_correction)
        else:
            incident_flux = np.nan * ureg.S_s

        return incident_flux

    def calculate_temperature(self) -> Q_:
        temperature_average_incident_flux = self.calculate_incident_flux(ecc_correction='temp')
        return calculate_planetary_effective_surface_temperature(
            temperature_average_incident_flux, self.albedo, self.normalized_greenhouse, self.heat_distribution,
            self.emissivity)

        # return calculate_planetary_effective_surface_temperature(self.albedo, self.normalized_greenhouse,
        #                                                          self.parent.luminosity, self.semi_major_axis,
        #                                                          self.orbital_eccentricity, self.heat_distribution)

    def get_chemical_composition(self):
        return planet_chemical_abundance_ratios[self.composition]

    def calculate_lifetime(self) -> Q_:
        if self.farthest_parent is not None:
            return self.farthest_parent.lifetime
        else:
            return np.nan * ureg.T_s

    def calculate_semi_minor_axis(self) -> Q_:
        return calculate_semi_minor_axis(self.semi_major_axis, self.orbital_eccentricity)

    def calculate_periapsis(self) -> Q_:
        return calculate_periapsis(self.semi_major_axis, self.orbital_eccentricity)

    def calculate_apoapsis(self) -> Q_:
        return calculate_apoapsis(self.semi_major_axis, self.orbital_eccentricity)

    def calculate_orbital_period(self) -> Q_:
        if self.parent is not None:
            return calculate_orbital_period(self.semi_major_axis, self.parent.mass, self.mass)
        else:
            return np.nan * ureg.years

    def calculate_orbital_velocity(self) -> Q_:
        if self.parent is not None:
            return calculate_orbital_velocity(self.semi_major_axis, self.parent.mass)
        else:
            return np.nan * ureg.vorb_e

    def calculate_surface_gravity(self) -> Q_:
        return calculate_surface_gravity(self.mass, self.radius)

    def calculate_escape_velocity(self) -> Q_:
        return calculate_planet_escape_velocity(self.mass, self.radius)

    def calculate_surface_pressure(self) -> Q_:
        return calculate_surface_pressure(self.mass, self.radius)

    def calculate_day_period(self):
        return calculate_synodic_period(self.spin_period, self.orbital_period)

    def calculate_induced_tides(self) -> Tuple[Q_, Q_]:
        if self.parent is not None:
            from .binary_system import StellarBinary
            if not isinstance(self.parent, StellarBinary):
                to_self = calculate_tide_height(self.parent.mass, self.mass, self.radius,
                                                self.semi_major_axis, self.orbital_eccentricity)
                to_parent = calculate_tide_height(self.mass, self.parent.mass, self.parent.radius,
                                                  self.semi_major_axis, self.orbital_eccentricity)
            else:
                to_self = calculate_tide_height(self.parent.mass, self.mass, self.radius,
                                                self.semi_major_axis, self.orbital_eccentricity)
                to_parent = {parent_body.name: calculate_tide_height(
                    self.mass, parent_body.mass, parent_body.radius, self.semi_major_axis, self.orbital_eccentricity)
                    for parent_body in [self.parent.primary_body, self.parent.secondary_body]}
        else:
            to_self = to_parent = np.nan * ureg.meter
        return to_self, to_parent

    def calculate_angular_diameters(self) -> Tuple[Q_, Q_]:
        if self.parent is not None:
            from .binary_system import StellarBinary
            if not isinstance(self.parent, StellarBinary):
                of_parent = calculate_angular_diameter(self.parent.radius, self.semi_major_axis)
                from_parent = calculate_angular_diameter(self.radius, self.semi_major_axis)
            else:
                of_parent = {parent_body.name: calculate_angular_diameter(parent_body.radius, self.semi_major_axis)
                             for parent_body in [self.parent.primary_body, self.parent.secondary_body]}
                from_parent = calculate_angular_diameter(self.radius, self.semi_major_axis)
        else:
            of_parent = np.nan * ureg.degrees
            from_parent = np.nan * ureg.degrees
        return of_parent, from_parent

    def calculate_internal_heating_fluxes(self):
        if self.composition != 'Icegiant' and self.composition != 'Gasgiant' \
                and not self.composition.startswith('Ironworld'):
            primordial_heating_flux = calculate_primordial_heating_rocky_planets(
                self.age, self.mass, self.surface_area)
        else:
            primordial_heating_flux = 0 * ureg.watt / ureg.m ** 2

        radiogenic_heating_flux = calculate_radiogenic_heating(
            self.age, self.mass, self.surface_area, self.chemical_composition)
        if self.parent is not None:
            tidal_heating_flux = calculate_tidal_heating(
                self.parent.mass, self.semi_major_axis, self.orbital_eccentricity, self.radius)
        else:
            tidal_heating_flux = 0 * ureg.W / ureg.meter ** 2
        total_heating_flux = primordial_heating_flux + radiogenic_heating_flux + tidal_heating_flux

        internal_heating_fluxes = {'Primordial': primordial_heating_flux, 'Radiogenic': radiogenic_heating_flux,
                                   'Tidal': tidal_heating_flux, 'Total': total_heating_flux}
        return internal_heating_fluxes

    def calculate_distance_to_horizon(self, height: Q_) -> Q_:
        return calculate_distance_to_horizon(self.radius, height)

    def get_semi_major_axis_minimum_limit(self):
        minimum_limit = self.calculate_roche_limit()
        from stellar_system_creator.stellar_system_elements.binary_system import BinarySystem
        if self.parent is not None:
            if isinstance(self.parent, BinarySystem):
                if minimum_limit < self.parent.binary_ptype_critical_orbit:
                    minimum_limit = self.parent.binary_ptype_critical_orbit

        return minimum_limit

    def get_semi_major_axis_maximum_limit(self):
        if self.parent is not None:
            return self.parent.outer_orbit_limit * self.orbit_type_factor
        else:
            return np.nan * self.semi_major_axis_minimum_limit.units

    def get_orbit_type_factor(self):
        return 1

    def _set_orbit_values(self) -> None:
        warnings.filterwarnings("ignore", category=UnitStrippedWarning)
        self.orbit_type_factor = self.get_orbit_type_factor()
        self.outer_orbit_limit = self.hill_sphere = self.calculate_hill_sphere()
        self.inner_orbit_limit = self.dense_roche_limit = calculate_approximate_inner_orbit_limit(self.radius)

        from stellar_system_creator.stellar_system_elements.binary_system import BinarySystem
        if isinstance(self.parent, BinarySystem):
            if self.parent.primary_body == self or self.parent.secondary_body == self:
                self.stype_critical_orbit = calculate_wide_binary_critical_orbit(
                    (self.mass / self.parent.mass).to_reduced_units().m,
                    self.parent.mean_distance, self.parent.eccentricity)
            else:
                self.stype_critical_orbit = np.nan * self.hill_sphere.units
        else:
            self.stype_critical_orbit = np.nan * self.hill_sphere.units

        outer_limits = np.array([self.stype_critical_orbit,
                                 self.hill_sphere], dtype=Q_)
        outer_limits = np.array([ol for ol in outer_limits if not np.isnan(ol.m)], dtype=Q_)
        if len(outer_limits):
            minimum_outer_limit_index = np.nanargmin(outer_limits)
            self.outer_orbit_limit = outer_limits[minimum_outer_limit_index]
        else:
            self.outer_orbit_limit = np.nan * self.stype_critical_orbit.units

        self.semi_major_axis_minimum_limit = self.get_semi_major_axis_minimum_limit()
        self.semi_major_axis_maximum_limit = self.get_semi_major_axis_maximum_limit()

        self.tidal_locking_radius = self.calculate_tidal_locking_radius()

        self.semi_minor_axis = self.calculate_semi_minor_axis()
        self.periapsis = self.calculate_periapsis()
        self.apoapsis = self.calculate_apoapsis()
        self.orbital_velocity = self.calculate_orbital_velocity()
        self.orbital_period = self.calculate_orbital_period()

    def _set_other_characteristics(self):
        self.day_period = self.calculate_day_period()

        self.escape_velocity = self.calculate_escape_velocity()
        self.surface_pressure = self.calculate_surface_pressure()
        self.surface_gravity = self.calculate_surface_gravity()

        self.orbital_stability, self.stability_violations = self.get_orbital_stability()

        self.induced_tide_height_to_self, self.induced_tide_height_to_parent = self.calculate_induced_tides()
        self.angular_diameter_of_parent, self.angular_diameter_from_parent = self.calculate_angular_diameters()

        self.chemical_composition = self.get_chemical_composition()
        self.internal_heating_fluxes = self.calculate_internal_heating_fluxes()
        self.tectonic_activity = self.get_tectonic_activity()

    def is_gasgiant_hot(self):
        return is_gasgiant_hot(np.log10(self.incident_flux.to('watts/meter^2').m),
                               get_hot_gas_giant_mass_class(self.mass))

    def check_habitability(self) -> Tuple[bool, str]:
        habitability = True
        habitability_violation = []

        if not self.composition.startswith('Waterworld') and not self.composition.startswith('Rockworld'):
            habitability = False
            habitability_violation.append(f'Life on worlds with composition type {self.composition} is unlikely')
            return habitability, ' '.join(habitability_violation)

        # https://en.wikipedia.org/wiki/Planetary_habitability - Mass
        low_mass_limit = 0.0268 if self.composition.startswith('Waterworld') else 0.1
        high_mass_limit = 12 if self.composition.startswith('Waterworld') else 5
        if not low_mass_limit <= self.mass.to('M_e').magnitude <= high_mass_limit:
            habitability = False
            habitability_violation.append('Planetary mass must be between 0.1 and 5 earth masses for earth like planets'
                                          'and 0.0268 and 12 for water-worlds.')

        # https://en.wikipedia.org/wiki/Planetary_habitability - Radius
        high_radius_limit = 2.8 if self.composition.startswith('Waterworld') else 2
        if not 0.45 <= self.radius.to('R_e').magnitude <= high_radius_limit:
            habitability = False
            habitability_violation.append('Planetary radius must be between 0.45 and 2 earth radii for earth-like'
                                          ' planets and 0.45 and 2.8 earth radii for water-worlds.')

        # if not 0.4 < self.surface_gravity.to('g_e').magnitude < 1.6:
        #     habitability = False
        #     habitability_violation.append('Planetary surface gravity must be between 0.4 and 1.6 earth surface'
        #                                   ' gravity units.')

        # checking habitable zone. First we regard the s-type HZ on the system caused by another system, and then p-type
        if self.parent is not None:
            habitable_zone_limit_keys = self.parent.habitable_zone_limits.keys()
            if 'AHZ' in habitable_zone_limit_keys:
                relevant_zone_type = 'AHZ'
            elif 'PHZ' in habitable_zone_limit_keys:
                relevant_zone_type = 'PHZ'
            elif 'RHZ' in habitable_zone_limit_keys:
                relevant_zone_type = 'RHZ'
            elif 'ptypeAHZ' in habitable_zone_limit_keys:
                relevant_zone_type = 'ptypeAHZ'
            elif 'ptypePHZ' in habitable_zone_limit_keys:
                relevant_zone_type = 'ptypePHZ'
            elif 'ptypeRHZ' in habitable_zone_limit_keys:
                relevant_zone_type = 'ptypeRHZ'
            else:
                relevant_zone_type = 'SSHZ'

            model = self.parent.insolation_model
            inner_limit = self.parent.habitable_zone_limits[relevant_zone_type][model.relaxed_min_name]
            outer_limit = self.parent.habitable_zone_limits[relevant_zone_type][model.relaxed_max_name]

            if inner_limit > outer_limit:
                habitability = False
                habitability_violation.append('Parent lacks a proper HZ.')
            elif not inner_limit < self.semi_major_axis < outer_limit:
                habitability = False
                habitability_violation.append('Planetary semi-major axis is not within the habitable'
                                              ' zone of the parent.')

        if not self.orbital_stability:
            habitability = False
            habitability_violation.append('The orbit is unstable.')

        if not self.tectonic_activity.startswith('Medium'):
            habitability = False
            habitability_violation.append(f'The tectonic activity is probably {self.tectonic_activity.lower()}.')

        if not len(habitability_violation):
            habitability_violation.append('None')

        if self.composition.startswith('Waterworld'):
            habitability_violation.append(f'\n\nNote: Life on water-worlds could emerge around the warm water close '
                                          f'to the surface, in the oceanic depths close to the rocky interior (if any),'
                                          f' or underneath a cold exterior surface (ice) even if the planet is not '
                                          f'within the habitable zone of the stellar parent.')

        return habitability, ' '.join(habitability_violation)

    def get_orbital_stability(self) -> Tuple[bool, str]:
        stability = True
        stability_violation = []

        if self.calculate_roche_limit() > self.periapsis:
            stability = False
            stability_violation.append('Periapsis is closer to the parent than the Roche limit.')
        if self.parent is not None:
            from stellar_system_creator.stellar_system_elements.binary_system import BinarySystem
            if isinstance(self.parent, BinarySystem):
                if self.parent.binary_ptype_critical_orbit > self.semi_major_axis:
                    stability = False
                    stability_violation.append('Semi-major axis is closer to the binary parent than the P-type'
                                               ' stability limit.')

        if self.parent is not None:
            if self.parent.inner_orbit_limit > self.semi_major_axis:
                stability = False
                stability_violation.append('Semi-major axis is closer to the parent than the rough inner orbit limit.')
            if (self.composition.startswith('Rockworld') or self.composition.startswith('Ironworld')) \
                    and 'rock_line' in self.parent.__dict__:
                if self.parent.rock_line > self.semi_major_axis:
                    stability = False
                    stability_violation.append('Semi-major axis is closer to the parent than the Rocky/Iron-planet '
                                               'formation line.')

            if self.semi_major_axis > self.semi_major_axis_maximum_limit:
                stability = False
                stability_violation.append('Semi-major axis is farther from the parent than the outer orbit limit.')

        if not len(stability_violation):
            stability_violation.append('None')

        return stability, ' '.join(stability_violation)

    def get_tectonic_activity(self) -> str:
        if self.composition == 'Icegiant' or self.composition == 'Gasgiant':
            tectonic_activity = 'Not applicable'
        else:
            total_heating_flux = self.internal_heating_fluxes['Total']
            if np.isnan(total_heating_flux):
                tectonic_activity = 'Unknown'
            elif total_heating_flux < 0.01 * ureg.watt / ureg.m ** 2:
                tectonic_activity = 'Stagnant'
            elif total_heating_flux < 0.04 * ureg.watt / ureg.m ** 2:
                tectonic_activity = 'Low'
            elif total_heating_flux < 0.07 * ureg.watt / ureg.m ** 2:
                tectonic_activity = 'Medium Low'
            elif total_heating_flux < 0.15 * ureg.watt / ureg.m ** 2:
                tectonic_activity = 'Medium'
            elif total_heating_flux < 0.2 * ureg.watt / ureg.m ** 2:
                tectonic_activity = 'Medium High'
            elif total_heating_flux < 0.35 * ureg.watt / ureg.m ** 2:
                tectonic_activity = 'High'
            else:
                tectonic_activity = 'Extreme'

        return tectonic_activity

    def get_ring(self) -> Union[None, "Ring"]:
        if 'ring' not in self.__dict__.keys():
            return Ring(self)
        else:
            self.ring.__post_init__()
            return self.ring


class AsteroidBelt(Planet):

    def __init__(self, name, mass: Q_ = 0.0004 * ureg.M_e, relative_count: int = 250, extend: Q_ = np.nan * ureg.au,
                 parent=None, semi_major_axis: Q_ = np.nan * ureg.au, orbital_eccentricity: float = np.nan,
                 orbit_type='prograde', composition='', inclination: Q_ = 0 * ureg.deg,
                 longitude_of_ascending_node: Q_ = 0 * ureg.deg, argument_of_periapsis: Q_ = np.nan * ureg.deg,
                 axial_tilt: Q_ = 0 * ureg.deg, albedo: float = 0,
                 age: Q_ = np.nan * ureg.T_s, image_filename=None) -> None:

        self.extend = extend
        self.relative_count = relative_count
        super().__init__(name, mass, np.nan * ureg.R_e, parent,
                         semi_major_axis, orbital_eccentricity, orbit_type, composition, np.nan * ureg.days,
                         inclination, longitude_of_ascending_node, argument_of_periapsis, axial_tilt, albedo,
                         age=age, image_filename=image_filename)

    def __post_init__(self, want_to_update_parent=False):
        if np.isnan(self.extend.m):
            self.extend = self.semi_major_axis / 8
        if self.composition == '':
            if self.semi_major_axis < self.parent.water_frost_line or np.isnan(self.semi_major_axis.m):
                self.composition = 'Rockworld70'
            else:
                self.composition = 'Waterworld100'

        super().__post_init__(want_to_update_parent)

        self._set_mass_distribution()
        self._set_radius_distribution()
        self._set_semi_major_axis_distribution()

    # def calculate_suggested_radius(self) -> float:
    #     return np.nan

    def _set_mass_distribution(self):
        mass_distribution = 1 / np.random.power(1.001, self.relative_count)
        self.mass_distribution = (mass_distribution / np.sum(mass_distribution) * self.mass / 100).to_reduced_units()

    def _set_radius_distribution(self):
        self.radius_distribution: Q_ = (self.mass_distribution / (4 * np.pi / 3 * self.density)).to_reduced_units() \
                                       ** (1 / 3)

    def _set_semi_major_axis_distribution(self):
        # semi_major_axis_distribution is a gaussian distribution in the area of a disc with radius r and thickness dr
        sma = self.semi_major_axis.m ** 2
        extend = self.extend.to(self.extend.u).m ** 2

        self.semi_major_axis_distribution: Q_ = np.sqrt(stats.truncnorm(
            (0 - sma) / extend, np.inf, loc=sma, scale=extend).rvs(self.relative_count)) * self.semi_major_axis.u

    def calculate_suggested_luminosity(self) -> Q_:
        return 0 * ureg.L_s

    def get_image_array(self) -> list:
        image_arrays = [stellar_body_marker_dict[f"asteroid{i + 1}"].copy() for i in range(3)]
        return image_arrays

    # def get_orbital_stability(self) -> bool:
    #     if self.parent.radius * 1.1 < self.semi_major_axis < self.parent.outer_orbit_limit:
    #         return True
    #     else:
    #         return False


class Trojan(Planet):

    def __init__(self, name, parent: Planet, lagrange_position: int, mass: Q_ = 0.0001 * ureg.M_e,
                 extend: Q_ = np.nan * ureg.au, relative_count: int = 50, composition='',
                 albedo: float = 0, age: Q_ = np.nan * ureg.T_s, image_filename=None) -> None:

        self.lagrange_position = lagrange_position
        self.extend = extend
        self.relative_count = relative_count

        super().__init__(name, mass, np.nan * ureg.R_e, parent,
                         parent.semi_major_axis, parent.orbital_eccentricity, parent.orbit_type,
                         composition, np.nan * ureg.days, parent.inclination,
                         parent.longitude_of_ascending_node, parent.argument_of_periapsis,
                         parent.axial_tilt, albedo, age=age, image_filename=image_filename)

    def __post_init__(self, want_to_update_parent=False):
        if self.parent is not None:
            self.semi_major_axis = self.parent.semi_major_axis
            self.orbital_eccentricity = self.parent.orbital_eccentricity
            self.orbit_type = self.parent.orbit_type
            self.inclination = self.parent.inclination
            self.longitude_of_ascending_node = self.parent.longitude_of_ascending_node
            self.argument_of_periapsis = self.parent.argument_of_periapsis
            self.axial_tilt = self.parent.axial_tilt
        else:
            self.semi_major_axis = np.nan * ureg.au
            self.orbital_eccentricity = np.nan
            self.orbit_type = 'prograde'
            self.inclination = np.nan * ureg.deg
            self.longitude_of_ascending_node = np.nan * ureg.deg
            self.argument_of_periapsis = np.nan * ureg.deg
            self.axial_tilt = np.nan * ureg.deg

        if self.parent is not None:
            if np.isnan(self.extend):
                self.extend = self.parent.semi_major_axis / 8
            if self.composition == '':
                if self.semi_major_axis < self.parent.parent.water_frost_line or np.isnan(self.semi_major_axis.m):
                    self.composition = 'Rockworld70'
                else:
                    self.composition = 'Waterworld100'
        else:
            if self.composition == '':
                self.composition = 'Waterworld45'

        super().__post_init__(want_to_update_parent)

        self._set_mass_distribution()
        self._set_radius_distribution()
        self._set_semi_major_axis_distribution()

    # def calculate_suggested_radius(self) -> float:
    #     return np.nan

    def _set_mass_distribution(self):
        mass_distribution = 1 / np.random.power(1.001, self.relative_count)
        self.mass_distribution = (mass_distribution / np.sum(mass_distribution) * self.mass / 100).to_reduced_units()

    def _set_radius_distribution(self):
        self.radius_distribution: Q_ = (self.mass_distribution / (4 * np.pi / 3 * self.density)).to_reduced_units() \
                                       ** (1 / 3)

    def _set_semi_major_axis_distribution(self):
        # semi_major_axis_distribution is a gaussian distribution in the area of a disc with radius r and thickness dr
        sma = self.semi_major_axis.m ** 2
        extend = self.extend.to(self.extend.u).m ** 2

        self.semi_major_axis_distribution: Q_ = np.sqrt(stats.truncnorm(
            (0 - sma) / extend, np.inf, loc=sma, scale=extend).rvs(self.relative_count)) * self.semi_major_axis.u

    def calculate_suggested_orbital_eccentricity(self) -> float:
        if self.parent is not None:
            return self.parent.suggested_orbital_eccentricity
        else:
            return 0

    def calculate_suggested_luminosity(self) -> Q_:
        return 0 * ureg.L_s

    def get_image_array(self) -> list:
        image_arrays = [stellar_body_marker_dict[f"asteroid{i + 1}"].copy() for i in range(3)]
        return image_arrays

    def calculate_orbital_period(self):
        if self.parent is not None:
            return self.parent.orbital_period
        else:
            return np.nan * ureg.days

    def calculate_orbital_velocity(self):
        if self.parent is not None:
            return self.parent.orbital_velocity
        else:
            return np.nan * ureg.vorb_e

    def calculate_incident_flux(self, ecc_correction='flux') -> Q_:
        if self.parent is not None:
            flux_on_parent = self.parent.incident_flux
        else:
            flux_on_parent = np.nan * ureg.S_s
        return flux_on_parent

    def calculate_roche_limit(self) -> Q_:
        if self.parent is not None:
            if self.parent.parent is not None:
                return calculate_roche_limit(self, self.parent.parent)
            else:
                return np.nan * self.semi_major_axis.units
        else:
            return np.nan * self.semi_major_axis.units

    def get_semi_major_axis_minimum_limit(self):
        return self.calculate_roche_limit()

    def get_semi_major_axis_maximum_limit(self):
        if self.parent is not None:
            if self.parent.parent is not None:
                return self.parent.parent.outer_orbit_limit
            else:
                return np.nan * self.semi_major_axis_minimum_limit.units
        else:
            return np.nan * self.semi_major_axis_minimum_limit.units

    def _set_orbit_values(self) -> None:
        Planet._set_orbit_values(self)

    # def _set_orbital_characteristics(self):
    #     self.orbital_period = self.calculate_orbital_period()
    #     self.orbital_velocity = self.calculate_orbital_velocity()

    def get_orbital_stability(self) -> Tuple[bool, str]:
        if self.parent is not None:
            return self.parent.orbital_stability, self.parent.stability_violations
        else:
            return False, 'Parent was not defined'

    def check_habitability(self) -> Tuple[bool, str]:
        return Satellite.check_habitability(self)
        # return self.parent.check_habitability()


class Satellite(Planet):

    def __init__(self, name, mass: Q_, parent: Planet, radius: Q_ = np.nan * ureg.R_e,
                 semi_major_axis: Q_ = np.nan * ureg.R_e, orbital_eccentricity: float = np.nan, orbit_type='prograde',
                 composition='', spin_period: Q_ = np.nan * ureg.days, inclination: Q_ = 0 * ureg.deg,
                 longitude_of_ascending_node: Q_ = 0 * ureg.deg, argument_of_periapsis: Q_ = np.nan * ureg.deg,
                 axial_tilt: Q_ = 0 * ureg.deg, albedo: float = 0, normalized_greenhouse: float = 0,
                 heat_distribution: float = 1, emissivity: float = 1,
                 luminosity=np.nan * ureg.L_s, age: Q_ = np.nan * ureg.T_s, image_filename=None) -> None:

        if not isinstance(parent, Planet):
            raise TypeError(f'Parent of {name} must be a planetary class object')
        Planet.__init__(self, name, mass, radius, parent, semi_major_axis, orbital_eccentricity, orbit_type,
                        composition, spin_period, inclination, longitude_of_ascending_node, argument_of_periapsis,
                        axial_tilt, albedo, normalized_greenhouse, heat_distribution, emissivity, luminosity, age,
                        image_filename)

    def __post_init__(self, want_to_update_parent=False):
        if self.composition == '' and self.parent is not None:
            if self.parent.semi_major_axis < self.parent.parent.water_frost_line \
                    or np.isnan(self.parent.semi_major_axis.m):
                self.composition = 'Rockworld70'
            else:
                self.composition = 'Waterworld100'
        elif self.composition == '':
            self.composition = 'Waterworld45'

        Planet.__post_init__(self, want_to_update_parent)
        self._update_parent_rings()

    def _update_parent_rings(self):
        if self.parent is not None:
            if self.parent.has_ring:
                self.parent.ring.__post_init__()

    def get_image_array(self) -> np.ndarray:
        if self.mass > 0.03 * ureg.M_e:
            image = Planet.get_image_array(self)
        elif self.mass > 0.0003 * ureg.M_e:
            image = stellar_body_marker_dict['big_moon'].copy()
        elif self.mass > 0.000003 * ureg.M_e:
            image = stellar_body_marker_dict['medium_moon'].copy()
        else:
            image = stellar_body_marker_dict['asteroid3'].copy()

        return image

    def calculate_incident_flux(self, ecc_correction='flux') -> Q_:
        if self.parent is not None:
            flux_from_parent = calculate_incident_flux(self.parent.luminosity, self.semi_major_axis,
                                                       self.orbital_eccentricity, ecc_correction)
            flux_on_parent = self.parent.calculate_incident_flux(ecc_correction)
            incident_flux = flux_on_parent + flux_from_parent
        else:
            incident_flux = np.nan * ureg.S_s
        return incident_flux

    def calculate_prograde_orbit_limit_factor(self) -> float:
        if self.parent is not None:
            return calculate_satellite_prograde_orbit_limit_factor(
                self.parent.orbital_eccentricity, self.orbital_eccentricity)
        else:
            return 1

    def calculate_retrograde_orbit_limit_factor(self) -> float:
        if self.parent is not None:
            return calculate_satellite_retrograde_orbit_limit_factor(
                self.parent.orbital_eccentricity, self.orbital_eccentricity)
        else:
            return 1

    def calculate_max_satellite_mass(self):
        if self.parent is not None:
            # return calculate_max_satellite_mass(self.parent.mass, self.parent.radius, self.parent.outer_orbit_limit,
            #                                     self.orbit_type_factor, self.farthest_parent.lifetime)
            return calculate_max_satellite_mass(self.parent.mass, self.parent.radius,
                                                self.semi_major_axis, self.age, self.lifetime)
        else:
            return np.nan * self.mass.u

    def calculate_day_period(self):
        if self.parent is not None:
            return calculate_synodic_period(self.spin_period, self.parent.orbital_period)
        else:
            return np.nan * ureg.days

    def get_orbit_type_factor(self):
        if self.orbit_type.lower() == 'prograde':
            return self.calculate_prograde_orbit_limit_factor()
        elif self.orbit_type.lower() == 'retrograde':
            return self.calculate_retrograde_orbit_limit_factor()

    def _set_orbit_values(self) -> None:
        Planet._set_orbit_values(self)

    #     self.semi_major_axis_maximum_limit = self.parent.outer_orbit_limit * self.orbit_type_factor

    def _set_other_characteristics(self):
        Planet._set_other_characteristics(self)
        self.maximum_mass_limit = self.calculate_max_satellite_mass()

    def check_habitability(self: Union["Satellite", Trojan]) -> Tuple[bool, str]:
        habitability = True
        habitability_violation = []

        if not self.composition.startswith('Waterworld') and not self.composition.startswith('Rockworld'):
            habitability = False
            habitability_violation.append(f'Life on worlds with composition type {self.composition} is unlikely')
            return habitability, ' '.join(habitability_violation)

        # https://en.wikipedia.org/wiki/Planetary_habitability - Mass
        low_mass_limit = 0.0268 if self.composition.startswith('Waterworld') else 0.1
        high_mass_limit = 12 if self.composition.startswith('Waterworld') else 5
        if not low_mass_limit <= self.mass.to('M_e').magnitude <= high_mass_limit:
            habitability = False
            habitability_violation.append('Planetary mass must be between 0.1 and 5 earth masses for earth like planets'
                                          'and 0.0268 and 12 for water-worlds.')

        # https://en.wikipedia.org/wiki/Planetary_habitability - Radius
        high_radius_limit = 2.8 if self.composition.startswith('Waterworld') else 2
        if not 0.45 <= self.radius.to('R_e').magnitude <= high_radius_limit:
            habitability = False
            habitability_violation.append('Planetary radius must be between 0.45 and 2 earth radii for earth-like'
                                          ' planets and 0.45 and 2.8 earth radii for water-worlds.')

        # if not 0.4 < self.surface_gravity.to('g_e').magnitude < 1.6:
        #     habitability = False
        #     habitability_violation.append('Planetary surface gravity must be between 0.4 and 1.6 earth surface'
        #                                   ' gravity units.')

        # checking habitable zone. First we regard the s-type HZ on the system caused by another system, and then p-type
        if self.parent is not None:
            habitable_zone_limit_keys = self.parent.parent.habitable_zone_limits.keys()
            if 'AHZ' in habitable_zone_limit_keys:
                relevant_zone_type = 'AHZ'
            elif 'PHZ' in habitable_zone_limit_keys:
                relevant_zone_type = 'PHZ'
            elif 'RHZ' in habitable_zone_limit_keys:
                relevant_zone_type = 'RHZ'
            elif 'ptypeAHZ' in habitable_zone_limit_keys:
                relevant_zone_type = 'ptypeAHZ'
            elif 'ptypePHZ' in habitable_zone_limit_keys:
                relevant_zone_type = 'ptypePHZ'
            elif 'ptypeRHZ' in habitable_zone_limit_keys:
                relevant_zone_type = 'ptypeRHZ'
            else:
                relevant_zone_type = 'SSHZ'

            model = self.parent.parent.insolation_model
            inner_limit = self.parent.parent.habitable_zone_limits[relevant_zone_type][model.relaxed_min_name]
            outer_limit = self.parent.parent.habitable_zone_limits[relevant_zone_type][model.relaxed_max_name]

            if inner_limit > outer_limit:
                habitability = False
                habitability_violation.append('Parent lacks a proper HZ.')
            elif not inner_limit < self.parent.semi_major_axis < outer_limit:
                habitability = False
                habitability_violation.append(
                    'Planetary semi-major axis is not within the habitable zone of the parent.')
        else:
            habitability = False
            habitability_violation.append('Parent planet was not defined.')

        if not self.orbital_stability:
            habitability = False
            habitability_violation.append('The orbit is unstable.')

        if not self.tectonic_activity.startswith('Medium'):
            habitability = False
            habitability_violation.append(f'The tectonic activity is probably {self.tectonic_activity.lower()}.')

        if 'maximum_mass_limit' in self.__dict__.keys():
            if self.mass > self.maximum_mass_limit:
                habitability = False
                habitability_violation.append('The satellite mass exceeds the mass limit set by its parent'
                                              ' and its orbit.')

        if not len(habitability_violation):
            habitability_violation.append('None')

        if self.composition.startswith('Waterworld'):
            habitability_violation.append(f'\n\nNote: Life on water-worlds could emerge around the warm water close '
                                          f'to the surface, in the oceanic depths close to the rocky interior (if any),'
                                          f' or underneath a cold exterior surface (ice) even if the planet is not '
                                          f'within the habitable zone of the stellar parent.')

        return habitability, ' '.join(habitability_violation)


class TrojanSatellite(Satellite, Trojan):

    def __init__(self, name, parent: Planet, lagrange_position: int, mass: Q_, radius: Q_ = np.nan * ureg.R_e,
                 composition='', spin_period: Q_ = np.nan * ureg.days, axial_tilt: Q_ = 0 * ureg.deg,
                 albedo: float = 0, normalized_greenhouse: float = 0, heat_distribution: float = 1,
                 emissivity: float = 1, luminosity=np.nan * ureg.L_s,
                 age: Q_ = np.nan * ureg.T_s, image_filename=None) -> None:

        self.lagrange_position = lagrange_position

        Satellite.__init__(self, name, mass, parent, radius,
                           parent.semi_major_axis, parent.orbital_eccentricity, parent.orbit_type,
                           composition, spin_period, parent.inclination,
                           parent.longitude_of_ascending_node, parent.argument_of_periapsis,
                           axial_tilt, albedo, normalized_greenhouse, heat_distribution, emissivity,
                           luminosity, age=age, image_filename=image_filename)

    def __post_init__(self, want_to_update_parent=False):
        if self.parent is not None:
            self.semi_major_axis = self.parent.semi_major_axis
            self.orbital_eccentricity = self.parent.orbital_eccentricity
            self.orbit_type = self.parent.orbit_type
            self.inclination = self.parent.inclination
            self.longitude_of_ascending_node = self.parent.longitude_of_ascending_node
            self.argument_of_periapsis = self.parent.argument_of_periapsis
        else:
            self.semi_major_axis = np.nan * ureg.au
            self.orbital_eccentricity = np.nan
            self.orbit_type = 'prograde'
            self.inclination = np.nan * ureg.deg
            self.longitude_of_ascending_node = np.nan * ureg.deg
            self.argument_of_periapsis = np.nan * ureg.deg
        super().__post_init__(want_to_update_parent)

    def calculate_orbital_period(self):
        if self.parent is not None:
            return self.parent.orbital_period
        else:
            return np.nan * ureg.years

    def calculate_orbital_velocity(self):
        if self.parent is not None:
            return self.parent.orbital_velocity
        else:
            return np.nan * ureg.vorb_e

    def calculate_incident_flux(self, ecc_correction='flux') -> Q_:
        if self.parent is not None:
            flux_on_parent = self.parent.incident_flux
        else:
            flux_on_parent = np.nan * ureg.S_s
        return flux_on_parent

    def calculate_roche_limit(self) -> Q_:
        if self.parent is not None:
            if self.parent.parent is not None:
                return calculate_roche_limit(self, self.parent.parent)
            else:
                return np.nan * self.semi_major_axis.units
        else:
            return np.nan * self.semi_major_axis.units

    def get_orbital_stability(self) -> Tuple[bool, str]:
        if self.parent is not None:
            return self.parent.orbital_stability, self.parent.stability_violations
        else:
            return False, 'Parent was not defined'

    def get_orbit_type_factor(self):
        Planet.get_orbit_type_factor(self)

    def get_semi_major_axis_maximum_limit(self):
        if self.parent is not None:
            if self.parent.parent is not None:
                return self.parent.parent.outer_orbit_limit
            else:
                return np.nan * self.semi_major_axis_minimum_limit.units
        else:
            return np.nan * self.semi_major_axis_minimum_limit.units

    def _set_orbit_values(self) -> None:
        Planet._set_orbit_values(self)

    def calculate_max_satellite_mass(self):
        if self.parent is not None:
            return calculate_three_body_lagrange_point_smallest_body_mass_limit(self.parent.parent.mass,
                                                                                self.parent.mass)
        else:
            return np.nan * self.mass.u


class Ring:
    def __init__(self, parent: Planet):
        self.parent = parent
        self.ring_radial_gradient_colors = [GradientColor(0, 0.8, 0.7, 0.6, 1), GradientColor(1, 0.8, 0.7, 0.6, 0)]
        self.__post_init__()

    def __post_init__(self, want_to_update_parent=False):
        self.inner_radius = self.get_inner_radius()
        self.outer_radius = self.get_outer_radius()
        self.parents_satellites = self.get_parent_satellites()
        self.forbidden_bands = self.get_forbidden_bands()

    def get_inner_radius(self) -> Q_:
        return 1.1 * self.parent.radius

    def get_outer_radius(self) -> Q_:
        return self.parent.dense_roche_limit

    def get_parent_satellites(self) -> List[Satellite]:
        satellite_list = []
        for child in self.parent.children:
            if isinstance(child, Satellite) and not isinstance(child, TrojanSatellite):
                satellite_list.append(child)
        return satellite_list

    def get_forbidden_bands(self) -> List[List[Q_]]:
        all_forbidden_bands = []
        for satellite in self.parents_satellites:
            basic_band_center = satellite.semi_major_axis.to('km').m
            basic_band_extend = satellite.hill_sphere.to('km').m

            forbidden_bands = [[basic_band_center*resonance - basic_band_extend *
                                (resonance / res_orders[i]) ** res_orders[i],
                                basic_band_center*resonance + basic_band_extend *
                                (resonance / res_orders[i]) ** res_orders[i]]
                               for i, resonance in enumerate(resonances)]
            all_forbidden_bands += forbidden_bands

        all_forbidden_bands = merge_intervals(all_forbidden_bands)

        final_forbidden_bands = []
        for fb in all_forbidden_bands:
            if min(fb) < self.outer_radius.to('km').m and max(fb) > self.inner_radius.to('km').m:
                final_forbidden_bands.append(fb)

        final_forbidden_bands.sort()
        final_forbidden_bands = final_forbidden_bands * ureg.km
        return final_forbidden_bands

    def change_ring_radial_gradient_colors(self, new_colors_pos_rgba: List[Union[List[float], GradientColor]]):
        """
        This functions takes as input a list of lists.
        Each sublist contains 5 parameters:
         pos: from 0 to 1, the position of the color in a circle (0 is center, 1 is the edge)
         r: from 0 to 1, the red part of the color
         g: from 0 to 1, the green part of the color
         b: from 0 to 1, the blue part of the color
         a: from 0 to 1, the alpha part of the color (0 is fully transparent)
        """
        self.ring_radial_gradient_colors = []
        for elements in new_colors_pos_rgba:
            if isinstance(elements, GradientColor):
                self.ring_radial_gradient_colors.append(elements)
            else:
                self.ring_radial_gradient_colors.append(GradientColor(*elements))

    def copy(self):
        return copy.deepcopy(self)

resonances = [1]
res_orders = [1]
for m in range(1, 10):
    for order in range(1, 10):
        r = m / (m + order)
        if r < 1 and r not in resonances and (r / order) ** (order+1) > 1.0E-6:
            resonances.append(r)
            res_orders.append(order)

zipped_lists = zip(resonances, res_orders)
sorted_pairs = sorted(zipped_lists)
tuples = zip(*sorted_pairs)
resonances, res_orders = [list(tpl) for tpl in tuples]

res_orders = np.array(res_orders)
resonances = np.array(resonances)


def merge_intervals(intervals):
    """Source: https://www.geeksforgeeks.org/merging-intervals/"""
    # Sorting based on the increasing order of the start intervals
    intervals.sort(key=lambda x: x[0])

    max_val = -np.inf  # 'max_val' gives the last point of that particular interval
    min_val = -np.inf  # 's' gives the starting point of that interval
    merged_intervals = []  # 'm' array contains the list of all merged intervals
    for i in range(len(intervals)):
        a = intervals[i]
        if a[0] > max_val:
            if i != 0:
                merged_intervals.append([min_val, max_val])
            min_val = a[0]
            max_val = a[1]
        else:
            if a[1] >= max_val:
                max_val = a[1]

    if max_val != -np.inf and [min_val, max_val] not in merged_intervals:
        merged_intervals.append([min_val, max_val])

    return merged_intervals
