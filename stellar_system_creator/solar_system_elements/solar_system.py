from typing import List, Union

import numpy as np
from matplotlib import pyplot as plt

from stellar_system_creator.solar_system_elements.binary_system import BinarySystem
from stellar_system_creator.visualization.drawing_systems import draw_orbit, draw_filled_orbit, draw_planet, draw_asteroids, draw_satellite
from stellar_system_creator.solar_system_elements.planetary_system import PlanetarySystem
from stellar_system_creator.solar_system_elements.stellar_body import Star, AsteroidBelt


class SolarSystem:

    def __init__(self, name, parent: Union[Star, BinarySystem] = None,
                 planetary_systems: List[PlanetarySystem] = None,
                 asteroid_belts: List[AsteroidBelt] = None) -> None:
        if planetary_systems is None:
            planetary_systems = []
        if asteroid_belts is None:
            asteroid_belts = []

        self.name = name
        self.parent = parent
        self.planetary_systems = planetary_systems
        self.asteroid_belts = asteroid_belts

        self.min_drawing_orbit = self.get_min_drawing_orbit()

        self.fig: plt.Figure = None
        self.ax: plt.Axes = None

        self.want_draw_solar_system_limits = True
        self.want_draw_extended_habitable_zone = True
        self.want_draw_conservative_habitable_zone = True
        self.want_draw_frost_line = True
        self.want_draw_orbit_lines = True
        self.wat_draw_asteroid_as_zone = True
        self.want_orbit_label = True
        self.draw_detailed_asteroid_belt = True
        self.draw_detailed_trojans = True
        self.relevant_zone_type = None

    def replace_parent(self, new_parent) -> None:
        self.parent = new_parent
        self.min_drawing_orbit = self.get_min_drawing_orbit()

    def add_planetary_system(self, planetary_system: PlanetarySystem):
        self.planetary_systems.append(planetary_system)

    def add_planetary_systems(self, planetary_systems: List[PlanetarySystem]):
        for planetary_system in planetary_systems:
            self.planetary_systems.append(planetary_system)

    def add_asteroid_belt(self, asteroid_belt: AsteroidBelt):
        self.asteroid_belts.append(asteroid_belt)

    def add_asteroid_belts(self, asteroid_belts: List[AsteroidBelt]):
        for asteroid_belt in asteroid_belts:
            self.asteroid_belts.append(asteroid_belt)

    def remove_planetary_system(self, garbage_planetary_system):
        self.planetary_systems = [planetary_system for planetary_system in self.planetary_systems
                                  if planetary_system != garbage_planetary_system]

    def remove_asteroid_belt(self, garbage_asteroid_belt):
        self.asteroid_belts = [asteroid_belt for asteroid_belt in self.asteroid_belts
                               if asteroid_belt != garbage_asteroid_belt]

    def draw_solar_system(self, save_fig=False, save_name=None, save_format='pdf', save_temp_file=None):
        if self.fig is None:
            self.fig: plt.Figure = plt.figure(figsize=(11, 3))
        else:
            plt.figure(self.fig.number)
        if self.ax is None:
            self.ax: plt.Axes = plt.gca()

        self.fig.set_facecolor('k')
        self.ax.patch.set_alpha(0)
        self.ax.set_xscale('log')
        self.ax.spines['bottom'].set_color('white')
        self.ax.spines['left'].set_alpha(0)
        self.ax.spines['right'].set_alpha(0)
        self.ax.spines['top'].set_alpha(0)
        self.ax.tick_params(axis='x', which='both', colors='white')
        self.ax.set_alpha(0)
        self.ax.axis('off')

        if self.want_draw_solar_system_limits:
            self.draw_solar_system_limits()
        if self.want_draw_frost_line:
            self.draw_frost_line()
        if self.want_draw_extended_habitable_zone:
            self.draw_habitable_zone('extended')
        if self.want_draw_conservative_habitable_zone:
            self.draw_habitable_zone('conservative')
        if self.want_draw_orbit_lines:
            self.draw_planet_orbits(self.want_orbit_label)
        self.fig.tight_layout(pad=0.03)

        self.draw_star()
        self.draw_asteroid_belts(self.draw_detailed_asteroid_belt)
        self.draw_trojans(self.draw_detailed_trojans)
        self.draw_planets()
        self.draw_satellites()
        if save_fig:
            if save_name is None:
                save_name = self.name
            if save_temp_file is None:
                plt.savefig(f"{save_name}.{save_format}", dpi=1200, format=save_format)
            else:
                plt.savefig(save_temp_file, dpi=1200, format=save_format)

    def get_min_drawing_orbit(self):
        if self.parent is not None:
            min_drawing_orbit = self.parent.inner_orbit_limit / 3
        else:
            min_drawing_orbit = np.nan

        return min_drawing_orbit

    def draw_planet_orbits(self, orbit_label=True):
        for planetary_system in self.planetary_systems:
            planet = planetary_system.parent
            draw_orbit(planet.semi_major_axis.to('au').m, self.ax, self.min_drawing_orbit.to('au').m,
                       color='darkorange', orbit_label=orbit_label)

    def draw_habitable_zone(self, limit='extended'):
        if limit == 'extended':
            min_name = self.parent.insolation_model.relaxed_min_name
            max_name = self.parent.insolation_model.relaxed_max_name
            alpha = 0.4
        else:
            min_name = self.parent.insolation_model.conservative_min_name
            max_name = self.parent.insolation_model.conservative_max_name
            alpha = 0.8

        habitable_zone_limit_keys = self.parent.habitable_zone_limits.keys()
        if self.relevant_zone_type is None:
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
        else:
            relevant_zone_type = self.relevant_zone_type

        return draw_filled_orbit(self.parent.habitable_zone_limits[relevant_zone_type][min_name].to('au').m,
                                 self.parent.habitable_zone_limits[relevant_zone_type][max_name].to('au').m,
                                 self.ax, self.min_drawing_orbit.to('au').m, color='forestgreen', alpha=alpha)

    def draw_frost_line(self):
        if 'frost_line' in self.parent.__dict__.keys():
            return draw_orbit(self.parent.frost_line.to('au').m, self.ax,
                              self.min_drawing_orbit.to('au').m, color='dodgerblue', text_top=False)
        else:
            return None

    def draw_solar_system_limits(self):
        x_in, y_in = draw_orbit(self.parent.inner_orbit_limit.to('au').m, self.ax,
                                self.min_drawing_orbit.to('au').m, color='navajowhite', text_top=False)
        x_out, y_out = draw_orbit(self.parent.outer_orbit_limit.to('au').m, self.ax,
                                  self.min_drawing_orbit.to('au').m, color='navajowhite', text_top=False)
        return x_in, y_in, x_out, y_out

    def draw_star(self):
        if isinstance(self.parent, Star):
            draw_planet(self.parent.radius.to('R_e').m, self.min_drawing_orbit.to('au').m,
                        self.parent.image_array, self.ax)
        elif isinstance(self.parent, BinarySystem):
            draw_planet(self.parent.primary_body.radius.to('R_e').m,
                        self.min_drawing_orbit.to('au').m,
                        self.parent.primary_body.image_array, self.ax, y0=0.2)
            draw_planet(self.parent.secondary_body.radius.to('R_e').m,
                        self.min_drawing_orbit.to('au').m,
                        self.parent.secondary_body.image_array, self.ax, y0=-0.2)

    def draw_planets(self):
        for planetary_system in self.planetary_systems:
            planet = planetary_system.parent
            draw_planet(planet.radius.to('R_e').m, planet.semi_major_axis.to('au').m, planet.image_array, self.ax)

    def draw_asteroid_belts(self, draw_detailed_asteroid_belt=True):
        if self.asteroid_belts is not None:
            for asteroid_belt in self.asteroid_belts:
                if draw_detailed_asteroid_belt:
                    draw_asteroids(asteroid_belt.relative_count, asteroid_belt.semi_major_axis.to('au').m,
                                   self.ax, self.min_drawing_orbit.to('au').m,
                                   asteroid_belt.extend.to('au').m, asteroid_belt.radius_distribution.to('R_e').m,
                                   asteroid_belt.image_array)
                else:
                    draw_filled_orbit(asteroid_belt.semi_major_axis.to('au').m - asteroid_belt.extend.to('au').m,
                                      asteroid_belt.semi_major_axis.to('au').m + asteroid_belt.extend.to('au').m,
                                      self.ax, self.min_drawing_orbit.to('au').m, color='gold', alpha=1)

    def draw_trojans(self, draw_detailed_trojans=True):
        for planetary_system in self.planetary_systems:
            if planetary_system.trojans_list is not None:
                for trojan in planetary_system.trojans_list:
                    if draw_detailed_trojans:
                        draw_asteroids(trojan.relative_count, trojan.semi_major_axis.to('au').m, self.ax,
                                       self.min_drawing_orbit.to('au').m, trojan.extend.to('au').m,
                                       trojan.radius_distribution.to('R_e').m, trojan.image_array,
                                       lagrange_position=trojan.lagrange_position)
                    else:
                        draw_filled_orbit(trojan.semi_major_axis.to('au').m - trojan.extend.to('au').m,
                                          trojan.semi_major_axis.to('au').m + trojan.extend.to('au').m,
                                          self.ax, self.min_drawing_orbit.to('au').m, color='gold', alpha=1,
                                          height_min=0.2, height_max=0.4)

    def draw_satellites(self):
        for planetary_system in self.planetary_systems:
            if planetary_system.satellite_list is not None:
                total_satellites = len(planetary_system.satellite_list)
                for i, satellite in enumerate(planetary_system.satellite_list):
                    draw_satellite(satellite.radius.to('R_e').m, satellite.parent.semi_major_axis.to('au').m,
                                   satellite.image_array, self.ax,
                                   normalization_factor=10, total_satellites_around_parent=total_satellites,
                                   satellite_no=i+1)


class MultiSolarSystemSType:

    def __init__(self, name, parent: BinarySystem = None, children: List[SolarSystem] = None) -> None:
        if children is None:
            children = []
        self.name = name
        self.parent = parent
        self.children = children
        self.size = len(self.children)

        self.fig: plt.Figure = None
        self.axs: plt.Axes = None

    def replace_parent(self, new_parent) -> None:
        self.parent = new_parent

    def add_child(self, solar_system: SolarSystem) -> None:
        self.children.append(solar_system)
        self.size = len(self.children)

    def add_children(self, solar_systems: List[SolarSystem]) -> None:
        for solar_system in solar_systems:
            self.children.append(solar_system)
        self.size = len(self.children)

    def remove_child(self, garbage_child) -> None:
        self.children = [child for child in self.children if child != garbage_child]

    def draw_multi_solar_system(self, save_fig=False) -> None:
        if self.fig is None and self.axs is None:
            fig, axs = plt.subplots(self.size, 1, figsize=(11, 3*self.size))
            self.fig: plt.Figure = fig
            if isinstance(axs, plt.Axes):
                self.axs: np.ndarray = np.array([axs])
            else:
                self.axs: np.ndarray = axs
        else:
            plt.figure(self.fig.number)

        for i in range(self.size):
            self.children[i].fig = self.fig
            self.children[i].ax = self.axs[i]
            self.children[i].draw_solar_system()

        if save_fig:
            plt.savefig(f"{self.name}.pdf", dpi=1200)
