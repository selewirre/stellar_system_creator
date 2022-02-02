import copy
import inspect
import uuid
from typing import List, Union

import numpy as np

from stellar_system_creator.stellar_system_elements.binary_system import BinarySystem
from stellar_system_creator.stellar_system_elements.stellar_body import Planet, Satellite, Trojan


class PlanetarySystem:

    def __init__(self, name, parent: Union[Planet, BinarySystem] = None,
                 satellite_list: List[Satellite] = None,
                 trojans_list: List[Trojan] = None) -> None:
        if satellite_list is None:
            satellite_list = []
        if trojans_list is None:
            trojans_list = []

        self._uuid = str(uuid.uuid4())
        self.name = name
        self.parent = parent
        self.satellite_list = satellite_list
        self.trojans_list = trojans_list

        self._set_system_plot()

    def remove_object(self, garbage_object):
        if garbage_object == self.parent:
            self.remove_parent()
        else:
            self.remove_child(garbage_object)

    def remove_parent(self) -> None:
        for child in self.parent.children:
            child.parent = None
            child.__post_init__()
        self.parent = None

    def replace_parent(self, new_parent) -> None:
        self.parent = new_parent
        for satellite in self.satellite_list:
            satellite.parent = new_parent
            satellite.__post_init__()
        for trojan in self.trojans_list:
            trojan.parent = new_parent
            trojan.__post_init__()

    def remove_child(self, old_child) -> None:
        if old_child.__class__ == Satellite:
            self.remove_satellite(old_child)
        if old_child.__class__ == Trojan:
            self.remove_trojan(old_child)

    def add_satellite(self, satellite: Satellite):
        self.satellite_list.append(satellite)
        self.sort_satellites_by_distance()

    def add_satellites(self, satellites: List[Satellite]):
        for satellite in satellites:
            self.satellite_list.append(satellite)
        self.sort_satellites_by_distance()

    def add_trojan(self, trojan: Trojan):
        self.trojans_list.append(trojan)

    def add_trojans(self, trojans: List[Trojan]):
        for trojan in trojans:
            self.trojans_list.append(trojan)

    def remove_satellite(self, garbage_satellite):
        self.satellite_list = [satellite for satellite in self.satellite_list
                               if satellite != garbage_satellite]
        self.parent.remove_child(garbage_satellite)

    def remove_trojan(self, garbage_trojan):
        self.trojans_list = [trojan for trojan in self.trojans_list
                             if trojan != garbage_trojan]
        self.parent.remove_child(garbage_trojan)

    def sort_satellites_by_distance(self):
        if not len(self.satellite_list):
            return
        units = self.satellite_list[0].semi_major_axis.units
        sat_semimajor_axis = np.array([sat.semi_major_axis.to(units).m for sat in self.satellite_list])

        sorted_satellite_list = np.array(self.satellite_list)[sat_semimajor_axis.argsort()]
        self.satellite_list = list(sorted_satellite_list)

    def sort_all_by_distance(self):
        self.sort_satellites_by_distance()

    def get_children(self):
        return self.satellite_list + self.trojans_list

    def get_children_orbit_distances(self, units='au', system_plot=None):
        distances = []
        for satellite in self.satellite_list:
            distances.append(satellite.semi_major_axis.to(units).m)
        if self.parent.has_ring:
            distances.append(self.parent.ring.inner_radius.to(units).m)
            distances.append(self.parent.ring.outer_radius.to(units).m)

        from stellar_system_creator.visualization.system_plot import SystemPlot
        if system_plot is not None:
            system_plot: SystemPlot
            if system_plot.system_rendering_preferences['want_orbit_limits']:
                distances.append(self.parent.outer_orbit_limit.to(units).m)
            if system_plot.system_rendering_preferences['want_tidal_locking_radius']:
                distances.append(self.parent.tidal_locking_radius.to(units).m)

        return distances

    def _set_system_plot(self):
        from stellar_system_creator.visualization.system_plot import SystemPlot
        self.system_plot = SystemPlot(self)

    def reset_system_plot(self):
        self._set_system_plot()

    def clear_system_plot(self):
        self.system_plot.delete_plot()

    def draw_planetary_system(self, save=False, save_name: str = None, save_format='png', save_temp_file=None):
        self.system_plot.render_plot()

        if save:
            if save_name is None:
                save_name = self.name
            if save_temp_file is None:
                if save_name.endswith(save_format):
                    self.system_plot.save_image(f"{save_name}.{save_format}")
                else:
                    self.system_plot.save_image(save_name)
            else:
                self.system_plot.save_image(save_temp_file)

    def copy(self):
        return copy.deepcopy(self)

    def __hash__(self):
        return super().__hash__()

    @classmethod
    def load_with_args(cls, planetary_system: "PlanetarySystem"):
        arg_keys = inspect.getfullargspec(cls)
        kwargs = {key: planetary_system.__dict__[key] for key in arg_keys}
        cls_obj = cls(**kwargs)
        return cls_obj

    @property
    def uuid(self):
        return self._uuid

    def reset_uuid(self):
        self._uuid = str(uuid.uuid4())

    def reset_system_uuids(self):
        self.parent.reset_uuid()
        if isinstance(self.parent, BinarySystem):
            self.parent.primary_body.reset_uuid()
            self.parent.secondary_body.reset_uuid()
        for sat in self.satellite_list:
            sat.reset_uuid()
        for trojan in self.trojans_list:
            trojan.reset_uuid()
