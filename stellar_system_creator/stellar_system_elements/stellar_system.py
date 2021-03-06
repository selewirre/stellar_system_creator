import copy
import inspect
import uuid
from typing import List, Union

import numpy as np

from stellar_system_creator.stellar_system_elements.binary_system import BinarySystem
from stellar_system_creator.stellar_system_elements.planetary_system import PlanetarySystem
from stellar_system_creator.stellar_system_elements.stellar_body import Star, AsteroidBelt


class StellarSystem:

    def __init__(self, name, parent: Union[Star, BinarySystem] = None,
                 planetary_systems: List[PlanetarySystem] = None,
                 asteroid_belts: List[AsteroidBelt] = None) -> None:
        if planetary_systems is None:
            planetary_systems = []
        if asteroid_belts is None:
            asteroid_belts = []

        self._uuid = str(uuid.uuid4())
        self.name = name
        self.parent = parent
        self.planetary_systems = planetary_systems
        self.asteroid_belts = asteroid_belts

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
        for planetary_system in self.planetary_systems:
            planetary_system.parent._set_parent(new_parent)
            planetary_system.parent.__post_init__()
        for asteroid_belt in self.asteroid_belts:
            asteroid_belt._set_parent(new_parent)
            asteroid_belt.__post_init__()

    def remove_child(self, old_child) -> None:
        if old_child.__class__ == PlanetarySystem:
            self.remove_planetary_system(old_child)
        if old_child.__class__ == AsteroidBelt:
            self.remove_asteroid_belt(old_child)

    def add_planetary_system(self, planetary_system: PlanetarySystem):
        self.planetary_systems.append(planetary_system)
        self.sort_planetary_systems_by_distance()

    def add_planetary_systems(self, planetary_systems: List[PlanetarySystem]):
        for planetary_system in planetary_systems:
            self.planetary_systems.append(planetary_system)
        self.sort_planetary_systems_by_distance()

    def add_asteroid_belt(self, asteroid_belt: AsteroidBelt):
        self.asteroid_belts.append(asteroid_belt)
        self.sort_asteroid_belts_by_distance()

    def add_asteroid_belts(self, asteroid_belts: List[AsteroidBelt]):
        for asteroid_belt in asteroid_belts:
            self.asteroid_belts.append(asteroid_belt)
        self.sort_asteroid_belts_by_distance()

    def remove_planetary_system(self, garbage_planetary_system):
        self.planetary_systems = [planetary_system for planetary_system in self.planetary_systems
                                  if planetary_system != garbage_planetary_system]
        self.parent.remove_child(garbage_planetary_system.parent)

    def remove_asteroid_belt(self, garbage_asteroid_belt):
        self.asteroid_belts = [asteroid_belt for asteroid_belt in self.asteroid_belts
                               if asteroid_belt != garbage_asteroid_belt]
        self.parent.remove_child(garbage_asteroid_belt)

    def sort_planetary_systems_by_distance(self):
        if not len(self.planetary_systems):
            return

        units = self.planetary_systems[0].parent.semi_major_axis.units
        planet_semimajor_axis = np.array([ps.parent.semi_major_axis.to(units).m for ps in self.planetary_systems])

        sorted_planetary_systems = np.array(self.planetary_systems)[planet_semimajor_axis.argsort()]
        self.planetary_systems = list(sorted_planetary_systems)

    def sort_asteroid_belts_by_distance(self):
        if not len(self.asteroid_belts):
            return

        units = self.asteroid_belts[0].semi_major_axis.units
        ab_semimajor_axis = np.array([ab.semi_major_axis.to(units).m for ab in self.asteroid_belts])

        sorted_asteroid_belts = np.array(self.asteroid_belts)[ab_semimajor_axis.argsort()]
        self.asteroid_belts = list(sorted_asteroid_belts)

    def sort_all_by_distance(self):
        self.sort_planetary_systems_by_distance()
        self.sort_asteroid_belts_by_distance()

    def get_children(self):
        return self.planetary_systems + self.asteroid_belts

    def get_children_orbit_distances(self, units='au', system_plot=None):
        distances = []
        for ps in self.planetary_systems:
            distances.append(ps.parent.semi_major_axis.to(units).m)
        for ab in self.asteroid_belts:
            distances.append(ab.semi_major_axis.to(units).m)

        from stellar_system_creator.visualization.system_plot import SystemPlot
        if system_plot is not None:
            system_plot: SystemPlot
            if system_plot.system_rendering_preferences['want_orbit_limits']:
                distances.append(self.parent.inner_orbit_limit.to(units).m)
                distances.append(self.parent.outer_orbit_limit.to(units).m)
            if system_plot.system_rendering_preferences['want_rock_line']:
                distances.append(self.parent.rock_line.to(units).m)
            if system_plot.system_rendering_preferences['want_water_frost_line']:
                distances.append(self.parent.water_frost_line.to(units).m)
            if system_plot.system_rendering_preferences['want_tidal_locking_radius']:
                distances.append(self.parent.tidal_locking_radius.to(units).m)
            if system_plot.system_rendering_preferences['want_habitable_zones_extended']:
                rzt = system_plot.relevant_zone_type
                hz = self.parent.habitable_zone_limits[rzt]
                min_name = self.parent.insolation_model.relaxed_min_name
                max_name = self.parent.insolation_model.relaxed_max_name
                distances.append(hz[min_name].to(units).m)
                distances.append(hz[max_name].to(units).m)
            if system_plot.system_rendering_preferences['want_habitable_zones_conservative']:
                rzt = system_plot.relevant_zone_type
                hz = self.parent.habitable_zone_limits[rzt]
                min_name = self.parent.insolation_model.conservative_min_name
                max_name = self.parent.insolation_model.conservative_max_name
                distances.append(hz[min_name].to(units).m)
                distances.append(hz[max_name].to(units).m)

        return distances

    def _set_system_plot(self):
        from stellar_system_creator.visualization.system_plot import SystemPlot
        self.system_plot = SystemPlot(self)

    def reset_system_plot(self):
        self._set_system_plot()

    def clear_system_plot(self):
        self.system_plot.delete_plot()

    def draw_stellar_system(self, save=False, save_name: str = None, save_format='png', save_temp_file=None):
        self.system_plot.render_plot()

        if save:
            if save_name is None:
                save_name = self.name
            if save_temp_file is None:
                if save_name.endswith(save_format) and not save_name.startswith('~.'):
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
    def load_with_args(cls, stellar_system: "StellarSystem"):
        arg_keys = inspect.getfullargspec(cls)
        kwargs = {key: stellar_system.__dict__[key] for key in arg_keys}
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
        for ps in self.planetary_systems:
            ps.reset_system_uuids()
        for ab in self.asteroid_belts:
            ab.reset_uuid()


class MultiStellarSystemSType:

    def __init__(self, name, parent: BinarySystem = None, children: List[StellarSystem] = None) -> None:
        if children is None:
            children = []

        self._uuid = str(uuid.uuid4())
        self.name = name
        self.parent = parent
        self.children = children
        self.size = len(self.children)

        self._set_system_plot()

    def replace_parent(self, new_parent) -> None:
        self.parent = new_parent

    def add_child(self, stellar_system: StellarSystem) -> None:
        self.children.append(stellar_system)
        self.size = len(self.children)

    def add_children(self, stellar_systems: List[StellarSystem]) -> None:
        for stellar_system in stellar_systems:
            self.children.append(stellar_system)
        self.size = len(self.children)

    def remove_child(self, garbage_child) -> None:
        self.children = [child for child in self.children if child != garbage_child]
        self.parent.remove_child(garbage_child.parent)
        self.size = len(self.children)

    def remove_object(self, garbage_object):
        self.remove_child(garbage_object)

    def get_children(self):
        return self.children

    def _set_system_plot(self):
        from stellar_system_creator.visualization.system_plot import SystemMultiPlot
        self.system_plot = SystemMultiPlot(self)

    def reset_system_plot(self):
        self._set_system_plot()

    def clear_system_plot(self):
        self.system_plot.delete_plot()

    def draw_multi_stellar_system(self, save=False, save_name: str = None, save_format='png',
                                  save_temp_file=None) -> None:
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
    def load_with_args(cls, multi_stellar_system_s_type: "MultiStellarSystemSType"):
        arg_keys = inspect.getfullargspec(cls)
        kwargs = {key: multi_stellar_system_s_type.__dict__[key] for key in arg_keys}
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
        for child in self.children:
            child.reset_system_uuids()
