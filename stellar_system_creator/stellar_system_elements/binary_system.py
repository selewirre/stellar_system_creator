import copy
import inspect

import numpy as np
from typing import Union, Tuple
import warnings

from pint import UnitStrippedWarning

from stellar_system_creator.astrothings.astromechanical_calculations import \
    calculate_rough_inner_orbit_limit, calculate_rough_outer_orbit_limit, calculate_periapsis, calculate_apoapsis, \
    calculate_orbital_period, \
    calculate_wide_binary_critical_orbit, calculate_close_binary_critical_orbit, \
    calculate_roche_lobe, calculate_tidal_locking_radius, calculate_hill_sphere
from stellar_system_creator.astrothings.habitability_calculations import calculate_ptype_radiative_habitable_limit, \
    calculate_ptype_average_habitable_limit, calculate_ptype_permanent_habitable_limit, \
    calculate_stype_radiative_habitable_limit, calculate_stype_permanent_habitable_limit, \
    calculate_stype_average_habitable_limit, calculate_single_star_habitable_orbital_threshold
from stellar_system_creator.astrothings.insolation_models.insolation_models import InsolationThresholdModel, \
    BinaryInsolationModel, InsolationForWaterFrostline, BinaryInsolationForWaterFrostLine, InsolationForRockLine, \
    BinaryInsolationForRockLine
from stellar_system_creator.stellar_system_elements.stellar_body import StellarBody, Star, Planet
from stellar_system_creator.astrothings.units import ureg, Q_


class BinarySystem:

    def __init__(self, name, primary_body: Union["BinarySystem", StellarBody, Star, Planet] = None,
                 secondary_body: Union["BinarySystem", StellarBody, Star, Planet] = None,
                 mean_distance: Q_ = np.nan * ureg.au, eccentricity: float = np.nan,
                 parent: Union["BinarySystem", StellarBody, Star, Planet] = None) -> None:

        self.name = name
        self._set_children_list()
        self.primary_body = primary_body
        self.secondary_body = secondary_body
        self.mean_distance = mean_distance
        self.eccentricity = eccentricity
        self._set_parent(parent)

        self.__post_init__()

    def __post_init__(self, want_to_update_parent=False):
        if self.primary_body is None or self.secondary_body is None \
                or np.isnan(self.mean_distance.m) or np.isnan(self.eccentricity):
            return

        self.primary_body._set_parent(self)
        self.secondary_body._set_parent(self)

        if self.primary_body.mass < self.secondary_body.mass:
            temporary_body = self.primary_body
            self.primary_body = self.secondary_body
            self.secondary_body = temporary_body

        self._set_parent(self.parent)
        self.farthest_parent = self.get_farthest_parent()

        self.mean_distance = self.mean_distance
        self.eccentricity = self.eccentricity

        self.mass = self.calculate_total_mass()
        if self.primary_body.lifetime < self.secondary_body.lifetime:
            self.lifetime = self.primary_body.lifetime
            self.age = self.primary_body.age
        else:
            self.lifetime = self.secondary_body.lifetime
            self.age = self.secondary_body.age

        self.maximum_distance = self.calculate_maximum_distance()
        self.minimum_distance = self.calculate_minimum_distance()
        self.orbital_period = self.calculate_orbital_period()

        self._set_child_orbital_limits()
        self._set_orbit_values()

        self.contact = self.check_binary_contact()

        if want_to_update_parent:
            self.update_parent()

    def __repr__(self, precision=4) -> str:
        string = ''
        keys = list(self.__dict__.keys())
        keys.sort()
        for key in keys:
            if key not in ['primary_body', 'secondary_body', 'parent', 'farthest_parent', 'insolation_model',
                           '_children']:
                value = self.__dict__[key]
                if isinstance(value, dict):
                    string += f'{key}: {value}\n'
                elif isinstance(value, bool):
                    string += f'{key}: {value}\n'
                elif isinstance(value, (float, int, Q_)):
                    string += f'{key}: {value:.{precision}g}\n'
                else:
                    string += f'{key}: {value}\n'
            elif key in ['primary_body', 'secondary_body', 'parent', 'farthest_parent', 'insolation_model']:
                if self.__dict__[key] is not None:
                    value = self.__dict__[key].name
                    string += f'{key}: {value}\n'
            elif key in ['_children']:
                if self.__dict__[key] is not None:
                    value = [el.name for el in self.__dict__[key]]
                    string += f'{key}: {value}\n'
        return string

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
        if isinstance(self.parent, BinarySystem):
            if self.parent.primary_body == self or self.parent.secondary_body == self:
                self.parent.__post_init__()

    def _set_parent(self, parent):
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

    def calculate_total_mass(self) -> Q_:
        return self.primary_body.mass + self.secondary_body.mass

    def calculate_minimum_distance(self) -> Q_:
        return calculate_periapsis(self.mean_distance, self.eccentricity)

    def calculate_maximum_distance(self) -> Q_:
        return calculate_apoapsis(self.mean_distance, self.eccentricity)

    def calculate_orbital_period(self) -> Q_:
        return calculate_orbital_period(self.mean_distance, self.primary_body.mass, self.secondary_body.mass)

    def calculate_hill_sphere(self) -> Q_:
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

    def calculate_tidal_locking_radius(self):
        # TODO: spin period in binaries is dominated by their common rotation. Use that to calculate the tidal locking
        #  radius in a better way
        return calculate_tidal_locking_radius(self.mass, self.age)

    def check_binary_contact(self):
        primary_roche_lobe = calculate_roche_lobe(self.primary_body.mass, self.secondary_body.mass,
                                                  self.mean_distance, self.eccentricity)
        secondary_roche_lobe = calculate_roche_lobe(self.secondary_body.mass, self.primary_body.mass,
                                                    self.mean_distance, self.eccentricity)

        primary_distance_check = self.primary_body.radius if isinstance(self.primary_body, StellarBody) \
            else self.primary_body.maximum_distance + self.primary_body.primary_body.radius
        secondary_distance_check = self.secondary_body.radius if isinstance(self.secondary_body, StellarBody) \
            else self.secondary_body.maximum_distance + self.secondary_body.primary_body.radius

        contact = False
        if primary_roche_lobe < primary_distance_check or secondary_roche_lobe < secondary_distance_check:
            contact = True

        return contact

    def _set_child_orbital_limits(self) -> None:
        pass
        # get S-type circumstellar orbit maximum limit around each individual star
        # self.primary_stype_critical_orbit = calculate_wide_binary_critical_orbit(
        #     (self.primary_body.mass / self.mass).to_reduced_units().m, self.mean_distance, self.eccentricity)
        #
        # self.secondary_stype_critical_orbit = calculate_wide_binary_critical_orbit(
        #     (self.secondary_body.mass / self.mass).to_reduced_units().m, self.mean_distance, self.eccentricity)

        # get P-type circumbinary orbit minimum limit for both stars
        # self.binary_ptype_critical_orbit = calculate_close_binary_critical_orbit(
        #     (self.secondary_body.mass / self.mass).to_reduced_units().m, self.mean_distance, self.eccentricity)

    def _set_orbit_values(self):
        warnings.filterwarnings("ignore", category=UnitStrippedWarning)
        self.rough_inner_orbit_limit = calculate_rough_inner_orbit_limit(self.mass)
        self.rough_outer_orbit_limit = calculate_rough_outer_orbit_limit(self.mass)
        self.hill_sphere = self.calculate_hill_sphere()
        self.tidal_locking_radius = self.calculate_tidal_locking_radius()
        self.binary_ptype_critical_orbit = calculate_close_binary_critical_orbit(
            (self.secondary_body.mass / self.mass).to_reduced_units().m, self.mean_distance, self.eccentricity)
        if isinstance(self.parent, StellarBinary):
            self.stype_critical_orbit = calculate_wide_binary_critical_orbit(
                (self.mass / self.parent.mass).to_reduced_units().m, self.parent.mean_distance, self.parent.eccentricity)
        else:
            self.stype_critical_orbit = np.nan * self.hill_sphere.units

        binary_inner_limits = np.array([self.rough_inner_orbit_limit,
                                        self.binary_ptype_critical_orbit], dtype=Q_)
        binary_inner_limits = np.array([bil for bil in binary_inner_limits if not np.isnan(bil.m)], dtype=Q_)
        if len(binary_inner_limits):
            binary_maximum_inner_limit_index = np.nanargmax(binary_inner_limits)
            self.inner_orbit_limit = binary_inner_limits[binary_maximum_inner_limit_index]
        else:
            self.inner_orbit_limit = np.nan * self.binary_ptype_critical_orbit.units

        outer_limits = np.array([self.stype_critical_orbit,
                                 self.rough_outer_orbit_limit,
                                 self.hill_sphere], dtype=Q_)
        outer_limits = np.array([ol for ol in outer_limits if not np.isnan(ol.m)], dtype=Q_)
        if len(outer_limits):
            minimum_outer_limit_index = np.nanargmin(outer_limits)
            self.outer_orbit_limit = outer_limits[minimum_outer_limit_index]
        else:
            self.outer_orbit_limit = np.nan * self.stype_critical_orbit.units

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

    def copy(self):
        return copy.deepcopy(self)

    def __hash__(self):
        return super().__hash__()

    @property
    def children(self):
        return self._children

    @classmethod
    def load_with_args(cls, binary_system: "BinarySystem"):
        arg_keys = inspect.getfullargspec(cls)
        kwargs = {key: binary_system.__dict__[key] for key in arg_keys}
        cls_obj = cls(**kwargs)
        return cls_obj


class StellarBinary(BinarySystem):
    # TODO: Redo habitability and insolation model assignments to make it look nice. At least it works now
    # Add hill sphere, frost line, rock line and other star like elements.
    def __init__(self, name, primary_body: Union["StellarBinary", Star] = None,
                 secondary_body: Union["StellarBinary", Star] = None, mean_distance: Q_ = np.nan * ureg.au,
                 eccentricity: float = np.nan, parent: Union["StellarBinary", Star] = None) -> None:
        super().__init__(name, primary_body, secondary_body, mean_distance, eccentricity, parent)

    def __post_init__(self, want_to_update_parent=False):
        super().__post_init__()
        # self.reset_insolation_model_and_habitability_for_children()
        # self.reset_solo_habitability()
        self.reset_insolation_model_and_habitability()

        if want_to_update_parent:
            self.update_parent()

    def calculate_water_frost_lines(self):
        # setting ptype frost zone (not part of trinary/quaternary)
        if isinstance(self.primary_body, StellarBinary):
            prim_prim_insolation_model = InsolationForWaterFrostline(self.primary_body.primary_body.temperature,
                                                                     self.primary_body.primary_body.luminosity)
            prime_swl = BinaryInsolationForWaterFrostLine(self.primary_body.water_frost_lines,
                                                          prim_prim_insolation_model).swl
        else:
            prime_swl = InsolationForWaterFrostline(self.primary_body.temperature, self.primary_body.luminosity).swl
        if isinstance(self.secondary_body, StellarBinary):
            sec_prim_insolation_model = InsolationForWaterFrostline(self.secondary_body.primary_body.temperature,
                                                                    self.secondary_body.primary_body.luminosity)
            sec_swl = BinaryInsolationForWaterFrostLine(self.secondary_body.water_frost_lines,
                                                        sec_prim_insolation_model).swl
        else:
            sec_swl = InsolationForWaterFrostline(self.secondary_body.temperature, self.secondary_body.luminosity).swl

        sec_mass_ratio = self.secondary_body.mass / self.mass
        ss_water_frost_lines = {name: calculate_ptype_average_habitable_limit(
            prime_swl[name], sec_swl[name], self.mean_distance, self.eccentricity, sec_mass_ratio)
            for name in prime_swl}
        ss_water_frost_lines = {name: line if line > self.maximum_distance else np.nan * line.u
                                for (name, line) in ss_water_frost_lines.items()}

        # setting average frost zone if self is part of bigger binary as S-type
        if isinstance(self.parent, StellarBinary):
            if self.parent.primary_body == self:
                companion_body = self.parent.secondary_body
            else:
                companion_body = self.parent.primary_body
            if isinstance(companion_body, StellarBinary):
                comp_prim_insolation_model = InsolationForWaterFrostline(companion_body.primary_body.temperature,
                                                                         companion_body.primary_body.luminosity)
                comp_model = BinaryInsolationForWaterFrostLine(companion_body.water_frost_lines,
                                                               comp_prim_insolation_model)
            else:
                comp_model = InsolationForWaterFrostline(companion_body.temperature, companion_body.luminosity)

            mean_distance = self.parent.mean_distance
            eccentricity = self.parent.eccentricity
            model = BinaryInsolationForWaterFrostLine(ss_water_frost_lines, comp_model)
            water_frost_lines_in_binary = {name: calculate_stype_average_habitable_limit(
                model.swl[name], comp_model.swl[name], mean_distance, eccentricity) for name in model.names}
            water_frost_lines_in_binary = {name: line if self.parent.minimum_distance > line > 0 else np.nan * line.u
                                           for (name, line) in water_frost_lines_in_binary.items()}
        else:
            water_frost_lines_in_binary = None

        return ss_water_frost_lines, water_frost_lines_in_binary

    def calculate_rock_lines(self):
        # setting ptype frost zone (not part of trinary/quaternary)
        if isinstance(self.primary_body, StellarBinary):
            prim_prim_insolation_model = InsolationForRockLine(self.primary_body.primary_body.temperature,
                                                               self.primary_body.primary_body.luminosity)
            prime_swl = BinaryInsolationForRockLine(self.primary_body.rock_lines, prim_prim_insolation_model).swl
        else:
            prime_swl = InsolationForRockLine(self.primary_body.temperature, self.primary_body.luminosity).swl
        if isinstance(self.secondary_body, StellarBinary):
            sec_prim_insolation_model = InsolationForRockLine(self.secondary_body.primary_body.temperature,
                                                              self.secondary_body.primary_body.luminosity)
            sec_swl = BinaryInsolationForRockLine(self.secondary_body.rock_lines, sec_prim_insolation_model).swl
        else:
            sec_swl = InsolationForRockLine(self.secondary_body.temperature, self.secondary_body.luminosity).swl

        sec_mass_ratio = self.secondary_body.mass / self.mass
        ss_rock_lines = {name: calculate_ptype_average_habitable_limit(
            prime_swl[name], sec_swl[name], self.mean_distance, self.eccentricity, sec_mass_ratio)
            for name in prime_swl}
        ss_rock_lines = {name: line if line > self.maximum_distance else np.nan * line.u
                         for (name, line) in ss_rock_lines.items()}

        # setting average rock zone if self is part of bigger binary as S-type
        if isinstance(self.parent, StellarBinary):
            if self.parent.primary_body == self:
                companion_body = self.parent.secondary_body
            else:
                companion_body = self.parent.primary_body
            if isinstance(companion_body, StellarBinary):
                comp_prim_insolation_model = InsolationForRockLine(companion_body.primary_body.temperature,
                                                                   companion_body.primary_body.luminosity)
                comp_model = BinaryInsolationForRockLine(companion_body.rock_lines,
                                                         comp_prim_insolation_model)
            else:
                comp_model = InsolationForRockLine(companion_body.temperature, companion_body.luminosity)

            mean_distance = self.parent.mean_distance
            eccentricity = self.parent.eccentricity
            model = BinaryInsolationForRockLine(ss_rock_lines, comp_model)
            rock_lines_in_binary = {name: calculate_stype_average_habitable_limit(
                model.swl[name], comp_model.swl[name], mean_distance, eccentricity) for name in model.names}
            rock_lines_in_binary = {name: line if self.parent.minimum_distance > line > 0 else np.nan * line.u
                                    for (name, line) in rock_lines_in_binary.items()}
        else:
            rock_lines_in_binary = None

        return ss_rock_lines, rock_lines_in_binary

    def _set_orbit_values(self):
        super()._set_orbit_values()
        self.water_frost_lines, self.water_frost_lines_in_binary = self.calculate_water_frost_lines()
        self.rock_lines, self.rock_lines_in_binary = self.calculate_rock_lines()
        if isinstance(self.parent, StellarBinary):
            self.water_frost_line = self.water_frost_lines_in_binary['Sol Equivalent']
            self.rock_line = self.rock_lines_in_binary['Outer Limit']
            self.prevailing_water_frost_lines = self.water_frost_lines_in_binary
            self.prevailing_rock_lines = self.rock_lines_in_binary
        else:
            self.water_frost_line = self.water_frost_lines['Sol Equivalent']
            self.rock_line = self.rock_lines['Outer Limit']
            self.prevailing_water_frost_lines = self.water_frost_lines
            self.prevailing_rock_lines = self.rock_lines

    def reset_insolation_model_and_habitability_for_children(self, model_name=''):
        if model_name == '':
            model_name = self.primary_body.insolation_model.name

        changed = False
        if model_name != self.primary_body.insolation_model.name:
            self.primary_body.reset_insolation_model(model_name)
            self.primary_body.set_solo_habitable_zones()
            changed = True
        if model_name != self.secondary_body.insolation_model.name:
            self.secondary_body.reset_insolation_model(model_name)
            self.secondary_body.set_solo_habitable_zones()
            changed = True

        # if changed:
        self.primary_body.set_dual_habitable_zones()
        self.primary_body.do_habitability_check()
        self.secondary_body.set_dual_habitable_zones()
        self.secondary_body.do_habitability_check()

    def reset_insolation_model_and_habitability(self, model_name=''):
        self.reset_insolation_model(model_name)
        self.reset_solo_habitability()
        try:
            self.set_dual_habitable_zones()
            self.do_habitability_check()
        except Exception:
            pass

    def reset_insolation_model(self, model_name=''):
        self.reset_insolation_model_and_habitability_for_children(model_name)
        self.reset_solo_habitability()
        primary_im_swl = self.primary_body.insolation_model.swl
        secondary_im_swl = self.secondary_body.insolation_model.swl
        combinded_swl = {name: primary_im_swl[name] + secondary_im_swl[name]
                         for name in self.primary_body.insolation_model.names}
        self.insolation_model = BinaryInsolationModel(combinded_swl, self.primary_body.insolation_model)
        try:
            self.set_dual_habitable_zones()
            self.do_habitability_check()
        except Exception:
            pass
        self._set_orbit_values()  # here for cause the frost lines also depend on the binary

    def do_habitability_check(self):
        self.habitability, self.habitability_violations = self.check_habitability()

    def reset_solo_habitability(self):
        self.habitable_zone_limits = {}
        self.set_solo_habitable_zones()
        self.do_habitability_check()

    def set_habitable_zone(self, zone_type: str, binary_companion=None):
        prime_model: InsolationThresholdModel = self.primary_body.insolation_model
        sec_model: InsolationThresholdModel = self.secondary_body.insolation_model
        prime_swl = prime_model.swl
        sec_swl = sec_model.swl

        model = None
        model_swl = None
        comp_model_swl = None
        if binary_companion is not None:
            model = self.insolation_model
            model_swl = {name: self.habitable_zone_limits[f'ptype{zone_type}'][name] ** 2 for name in model.names}
            comp_model = binary_companion.insolation_model
            comp_model_swl = comp_model.swl

        if zone_type == 'ptypeRHZ':
            self.habitable_zone_limits['ptypeRHZ'] = {name: calculate_ptype_radiative_habitable_limit(
                prime_swl[name], sec_swl[name], self.mean_distance,
                prime_model.threshold_types[name]) for name in prime_model.names}
        elif zone_type == 'ptypePHZ':
            sec_mass_ratio = self.secondary_body.mass / self.mass
            self.habitable_zone_limits['ptypePHZ'] = {name: calculate_ptype_permanent_habitable_limit(
                prime_swl[name], sec_swl[name], self.mean_distance, self.eccentricity, sec_mass_ratio,
                prime_model.threshold_types[name]) for name in prime_model.names}
        elif zone_type == 'ptypeAHZ':
            sec_mass_ratio = self.secondary_body.mass / self.mass
            self.habitable_zone_limits['ptypeAHZ'] = {name: calculate_ptype_average_habitable_limit(
                prime_swl[name], sec_swl[name], self.mean_distance, self.eccentricity, sec_mass_ratio)
                for name in prime_model.names}
        elif zone_type == 'RHZ' and comp_model_swl is not None:
            mean_distance = self.parent.mean_distance
            self.habitable_zone_limits['RHZ'] = {name: calculate_stype_radiative_habitable_limit(
                model_swl[name], comp_model_swl[name], mean_distance, model.threshold_types[name])
                for name in model.names}
        elif zone_type == 'PHZ' and comp_model_swl is not None:
            mean_distance = self.parent.mean_distance
            eccentricity = self.parent.eccentricity
            self.habitable_zone_limits['PHZ'] = {name: calculate_stype_permanent_habitable_limit(
                model_swl[name], comp_model_swl[name], mean_distance, eccentricity, model.threshold_types[name])
                for name in model.names}
        elif zone_type == 'AHZ' and comp_model_swl is not None:
            mean_distance = self.parent.mean_distance
            eccentricity = self.parent.eccentricity
            self.habitable_zone_limits['AHZ'] = {name: calculate_stype_average_habitable_limit(
                model_swl[name], comp_model_swl[name], mean_distance, eccentricity) for name in model.names}

        if zone_type in self.habitable_zone_limits:
            if binary_companion is not None:
                if abs(self.habitable_zone_limits[zone_type][model.earth_equivalent]) > \
                        abs(self.habitable_zone_limits[zone_type][model.conservative_max_name]):
                    self.habitable_zone_limits[zone_type] = {name: np.nan * ureg.au for name in model.names}
            else:
                if abs(self.habitable_zone_limits[zone_type][prime_model.earth_equivalent]) > \
                        abs(self.habitable_zone_limits[zone_type][prime_model.conservative_max_name]):
                    self.habitable_zone_limits[zone_type] = {name: np.nan * ureg.au for name in prime_model.names}

    def set_solo_habitable_zones(self):
        self.set_habitable_zone('ptypeRHZ')
        self.set_habitable_zone('ptypePHZ')
        self.set_habitable_zone('ptypeAHZ')
        model = self.primary_body.insolation_model
        if np.isnan(self.habitable_zone_limits['ptypeRHZ'][model.earth_equivalent].m):
            self.habitable_zone_limits['ptypePHZ'] = {name: np.nan * ureg.au for name in model.names}
            self.habitable_zone_limits['ptypeAHZ'] = {name: np.nan * ureg.au for name in model.names}

    def set_dual_habitable_zones(self):
        model = self.primary_body.insolation_model
        if isinstance(self.parent, StellarBinary):
            if self.parent.primary_body == self:
                companion_body = self.parent.secondary_body
            else:
                companion_body = self.parent.primary_body
            self.set_habitable_zone('RHZ', companion_body)
            self.set_habitable_zone('PHZ', companion_body)
            self.set_habitable_zone('AHZ', companion_body)
            if np.isnan(self.habitable_zone_limits['RHZ'][model.relaxed_max_name].m):
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
        elif 'ptypeAHZ' in self.habitable_zone_limits.keys():
            relevant_zone_type = 'ptypeAHZ'
        elif 'ptypePHZ' in self.habitable_zone_limits.keys():
            relevant_zone_type = 'ptypePHZ'
        else:
            relevant_zone_type = 'ptypeRHZ'

        model = self.primary_body.insolation_model
        if self.habitable_zone_limits[relevant_zone_type][model.relaxed_max_name] \
                < self.habitable_zone_limits[relevant_zone_type][model.relaxed_min_name] or \
                np.isnan(self.habitable_zone_limits[relevant_zone_type][model.relaxed_min_name]):
            habitability = False
            habitability_violations.append('There are no habitable zones in this system.')
        elif self.inner_orbit_limit > self.habitable_zone_limits[relevant_zone_type][model.relaxed_max_name] \
                or self.outer_orbit_limit < self.habitable_zone_limits[relevant_zone_type][model.relaxed_min_name]:
            habitability = False
            habitability_violations.append('No overlap between the relaxed habitable zone and the stable orbit'
                                           ' boundaries.')

        # from https://link.springer.com/article/10.1007/BF00160399
        if self.lifetime < 1 * ureg.gigayears:
            habitability = False
            habitability_violations.append('Primary star lifetime is smaller than 1 billion years, making the'
                                           ' development of life unlikely in a p-type system.')

        if not len(habitability_violations):
            habitability_violations.append('None.')

        return habitability, ' '.join(habitability_violations)
