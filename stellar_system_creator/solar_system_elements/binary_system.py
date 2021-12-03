import numpy as np
from typing import Union

from stellar_system_creator.astrothings.astromechanical_calculations import \
    calculate_rough_inner_orbit_limit, calculate_rough_outer_orbit_limit, calculate_periapsis, calculate_apoapsis, calculate_orbital_period, \
    calculate_wide_binary_critical_orbit, calculate_close_binary_critical_orbit, \
    calculate_roche_lobe
from stellar_system_creator.astrothings.habitability_calculations import calculate_ptype_radiative_habitable_limit, \
    calculate_ptype_average_habitable_limit, calculate_ptype_permanent_habitable_limit, \
    calculate_stype_radiative_habitable_limit, calculate_stype_permanent_habitable_limit, \
    calculate_stype_average_habitable_limit
from stellar_system_creator.astrothings.insolation_models.insolation_models import InsolationThresholdModel, \
    BinaryInsolationModel
from stellar_system_creator.solar_system_elements.stellar_body import StellarBody, Star
from stellar_system_creator.astrothings.units import ureg, Q_


class BinarySystem:

    def __init__(self, name, primary_body: Union["BinarySystem", StellarBody] = None,
                 secondary_body: Union["BinarySystem", StellarBody] = None, mean_distance: Q_ = np.nan * ureg.au,
                 eccentricity: float = np.nan, parent: Union["BinarySystem", StellarBody] = None) -> None:

        self.name = name
        if primary_body is not None and secondary_body is not None \
                and not np.isnan(mean_distance.m) and not np.isnan(eccentricity):
            self.__post_init__(primary_body, secondary_body, mean_distance, eccentricity, parent)

    def __post_init__(self, primary_body: Union["BinarySystem", StellarBody],
                      secondary_body: Union["BinarySystem", StellarBody], mean_distance: Q_, eccentricity: float,
                      parent: Union["BinarySystem", StellarBody] = None):
        if primary_body.mass > secondary_body.mass:
            self.primary_body = primary_body
            self.secondary_body = secondary_body
        else:
            self.primary_body = secondary_body
            self.secondary_body = primary_body

        # self.unit_family = self.primary_body.unit_family
        self.parent = parent
        self.farthest_parent = self.get_farthest_parent()

        self.mean_distance = mean_distance
        self.eccentricity = eccentricity

        self.mass = self.calculate_total_mass()
        # self.luminosity = self.calculate_total_luminosity()
        # self.primary_body._set_binary_parameters(self.distance, self.mass)
        # self.secondary_body._set_binary_parameters(self.distance, self.mass)

        self.maximum_distance = self.calculate_maximum_distance()
        self.minimum_distance = self.calculate_minimum_distance()
        self.orbital_period = self.calculate_orbital_period()

        self._set_child_orbital_limits()
        self._set_orbit_values()

        self.contact = self.check_binary_contact()

    def __repr__(self, precision=4) -> str:
        string = ''
        keys = list(self.__dict__.keys())
        keys.sort()
        for key in keys:
            if key not in ['primary_body', 'secondary_body', 'parent', 'farthest_parent', 'insolation_model']:
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
        return string



    def calculate_total_mass(self) -> Q_:
        return self.primary_body.mass + self.secondary_body.mass

    # def calculate_total_luminosity(self) -> Q_:
    #     return self.primary_body.luminosity + self.secondary_body.luminosity

    def calculate_minimum_distance(self) -> Q_:
        return calculate_periapsis(self.mean_distance, self.eccentricity)

    def calculate_maximum_distance(self) -> Q_:
        return calculate_apoapsis(self.mean_distance, self.eccentricity)

    def calculate_orbital_period(self) -> Q_:
        return calculate_orbital_period(self.mean_distance, self.primary_body.mass, self.secondary_body.mass)

    def check_binary_contact(self):
        primary_roche_lobe = calculate_roche_lobe(self.primary_body.mass, self.secondary_body.mass, self.mean_distance)
        secondary_roche_lobe = calculate_roche_lobe(self.secondary_body.mass, self.primary_body.mass,
                                                    self.mean_distance)

        primary_distance_check = self.primary_body.radius if isinstance(self.primary_body, StellarBody) \
            else self.primary_body.maximum_distance + self.primary_body.primary_body.radius
        secondary_distance_check = self.secondary_body.radius if isinstance(self.secondary_body, StellarBody) \
            else self.secondary_body.maximum_distance + self.secondary_body.primary_body.radius

        contact = False
        if primary_roche_lobe < primary_distance_check or secondary_roche_lobe < secondary_distance_check:
            contact = True

        return contact

    def _set_child_orbital_limits(self) -> None:
        # get S-type circumstellar orbit maximum limit around each individual star
        self.primary_stype_critical_orbit = calculate_wide_binary_critical_orbit(
            (self.primary_body.mass / self.mass).to_reduced_units().m, self.mean_distance, self.eccentricity)

        self.secondary_stype_critical_orbit = calculate_wide_binary_critical_orbit(
            (self.secondary_body.mass / self.mass).to_reduced_units().m, self.mean_distance, self.eccentricity)

        # get P-type circumbinary orbit minimum limit for both stars
        self.binary_ptype_critical_orbit = calculate_close_binary_critical_orbit(
            (self.secondary_body.mass / self.mass).to_reduced_units().m, self.mean_distance, self.eccentricity)

    def _set_orbit_values(self):
        self.rough_inner_orbit_limit = calculate_rough_inner_orbit_limit(self.mass)
        self.rough_outer_orbit_limit = calculate_rough_outer_orbit_limit(self.mass)
        # self.frost_line = calculate_frost_line(self.luminosity)

        if self.rough_inner_orbit_limit > self.binary_ptype_critical_orbit:
            self.inner_orbit_limit = self.rough_inner_orbit_limit
        else:
            self.inner_orbit_limit = self.binary_ptype_critical_orbit

        self.outer_orbit_limit = self.rough_outer_orbit_limit

        if self.primary_stype_critical_orbit < self.primary_body.outer_orbit_limit:
            self.primary_body.outer_orbit_limit = self.primary_stype_critical_orbit
        if self.secondary_stype_critical_orbit < self.secondary_body.outer_orbit_limit:
            self.secondary_body.outer_orbit_limit = self.secondary_stype_critical_orbit

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


class StellarBinary(BinarySystem):
    # TODO: Redo habitability and insolation model assignments to make it look nice. At least it works now
    def __init__(self, name, primary_body: Union["StellarBinary", Star] = None,
                 secondary_body: Union["StellarBinary", Star] = None, mean_distance: Q_ = np.nan * ureg.au,
                 eccentricity: float = np.nan, parent: Union["StellarBinary", Star] = None) -> None:
        super().__init__(name, primary_body, secondary_body, mean_distance, eccentricity, parent)

    def __post_init__(self, primary_body: Union["StellarBinary", Star],
                      secondary_body: Union["StellarBinary", Star], mean_distance: Q_, eccentricity: float,
                      parent: Union["StellarBinary", Star] = None):
        primary_body.parent = self
        secondary_body.parent = self
        super().__post_init__(primary_body, secondary_body, mean_distance, eccentricity, parent)
        self.reset_insolation_model_and_habitability_for_children()
        self._set_insolation_model_and_habitability()

    def reset_insolation_model_and_habitability_for_children(self, model_name=''):
        if model_name == '':
            model_name = self.primary_body.insolation_model.name
        if model_name != self.primary_body.insolation_model.name:
            self.primary_body.reset_insolation_model_and_habitability(model_name)
        if model_name != self.secondary_body.insolation_model.name:
            self.secondary_body.reset_insolation_model_and_habitability(model_name)

    def _set_insolation_model_and_habitability(self):
        self.habitable_zone_limits = {}
        self.primary_body.reset_insolation_model_and_habitability()
        self.secondary_body.reset_insolation_model_and_habitability()
        self.set_habitable_zones()
        self.insolation_model = BinaryInsolationModel(self.habitable_zone_limits, self.primary_body.insolation_model)

    def reset_insolation_model_and_habitability(self, model_name=''):
        self.reset_insolation_model_and_habitability_for_children(model_name)
        self._set_insolation_model_and_habitability()

    def set_habitable_zone(self, zone_type: str, binary_companion=None):
        prime_model: InsolationThresholdModel = self.primary_body.insolation_model
        sec_model: InsolationThresholdModel = self.secondary_body.insolation_model
        prime_swl = prime_model.swl
        sec_swl = sec_model.swl

        if isinstance(self.primary_body, StellarBinary):
            prime_swl = prime_swl[f'{zone_type}']
        if isinstance(self.secondary_body, StellarBinary):
            sec_swl = sec_swl[f'{zone_type}']

        if binary_companion is not None:
            model = self.insolation_model
            model_swl = model.swl[f'ptype{zone_type}']
            comp_model = binary_companion.insolation_model
            comp_model_swl = comp_model.swl
            if isinstance(binary_companion, StellarBinary):
                comp_model_swl = comp_model_swl[f'ptype{zone_type}']

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
        elif zone_type == 'RHZ' and binary_companion is not None:
            mean_distance = self.parent.mean_distance
            self.habitable_zone_limits['RHZ'] = {name: calculate_stype_radiative_habitable_limit(
                model_swl[name], comp_model_swl[name], mean_distance, model.threshold_types[name])
                for name in model.names}
        elif zone_type == 'PHZ' and binary_companion is not None:
            mean_distance = self.parent.mean_distance
            eccentricity = self.parent.eccentricity
            self.habitable_zone_limits['PHZ'] = {name: calculate_stype_permanent_habitable_limit(
                model_swl[name], comp_model_swl[name], mean_distance, eccentricity, model.threshold_types[name])
                for name in model.names}
        elif zone_type == 'AHZ' and binary_companion is not None:
            mean_distance = self.parent.mean_distance
            eccentricity = self.parent.eccentricity
            self.habitable_zone_limits['AHZ'] = {name: calculate_stype_average_habitable_limit(
                model_swl[name], comp_model_swl[name], mean_distance, eccentricity) for name in model.names}

        if zone_type in self.habitable_zone_limits:
            if binary_companion is not None:
                if self.habitable_zone_limits[zone_type][model.earth_equivalent] > \
                        self.habitable_zone_limits[zone_type][model.conservative_max_name]:
                    self.habitable_zone_limits[zone_type] = {name: np.nan * ureg.au for name in model.names}
            else:
                if self.habitable_zone_limits[zone_type][prime_model.earth_equivalent] > \
                        self.habitable_zone_limits[zone_type][prime_model.conservative_max_name]:
                    self.habitable_zone_limits[zone_type] = {name: np.nan * ureg.au for name in prime_model.names}

    def set_habitable_zones(self) -> None:
        self.set_habitable_zone('ptypeRHZ')
        self.set_habitable_zone('ptypePHZ')
        self.set_habitable_zone('ptypeAHZ')
        if isinstance(self.parent, StellarBinary):
            if self.parent.primary_body == self:
                companion_star = self.parent.secondary_body
            else:
                companion_star = self.parent.primary_body
            self.set_habitable_zone('RHZ', companion_star)
            self.set_habitable_zone('PHZ', companion_star)
            self.set_habitable_zone('AHZ', companion_star)
