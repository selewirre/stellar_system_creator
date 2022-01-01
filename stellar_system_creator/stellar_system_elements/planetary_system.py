import copy
from typing import List, Union
import numpy as np
from matplotlib import pyplot as plt

from stellar_system_creator.astrothings.units import Q_
from stellar_system_creator.stellar_system_elements.binary_system import BinarySystem
from stellar_system_creator.visualization.drawing_systems import draw_orbit, draw_planet
from stellar_system_creator.stellar_system_elements.stellar_body import Planet, Satellite, Trojan


class PlanetarySystem:

    def __init__(self, name, parent: Union[Planet, BinarySystem] = None,
                 satellite_list: List[Satellite] = None,
                 trojans_list: List[Trojan] = None) -> None:
        if satellite_list is None:
            satellite_list = []
        if trojans_list is None:
            trojans_list = []

        self.name = name
        self.parent = parent
        self.satellite_list = satellite_list
        self.trojans_list = trojans_list

        self.min_drawing_orbit = self.get_min_drawing_orbit()
        self.normalization_factor = 25

        self.fig: plt.Figure = None
        self.ax: plt.Axes = None

        self.want_draw_planetary_system_limits = True
        self.want_draw_satellite_orbits = True
        self.want_orbit_label = True

    def remove_object(self, garbage_object):
        if garbage_object == self.parent:
            self.remove_parent()
        else:
            self.remove_child(garbage_object)

    def remove_parent(self) -> None:
        for child in self.parent._children:
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
        self.min_drawing_orbit = self.get_min_drawing_orbit()

    def remove_child(self, old_child) -> None:
        if old_child.__class__ == Satellite:
            self.remove_satellite(old_child)
        if old_child.__class__ == Trojan:
            self.remove_trojan(old_child)

    def add_satellite(self, satellite: Satellite):
        self.satellite_list.append(satellite)

    def add_satellites(self, satellites: List[Satellite]):
        for satellite in satellites:
            self.satellite_list.append(satellite)

    def add_trojan(self, trojan: Trojan):
        self.trojans_list.append(trojan)

    def add_trojans(self, trojans: List[Trojan]):
        for trojan in trojans:
            self.trojans_list.append(trojan)

    def remove_satellite(self, garbage_satellite):
        self.satellite_list = [satellite for satellite in self.satellite_list
                               if satellite != garbage_satellite]

    def remove_trojan(self, garbage_trojan):
        self.trojans_list = [trojan for trojan in self.trojans_list
                             if trojan != garbage_trojan]

    def set_fig_and_ax(self):
        if self.fig is None:
            self.fig: plt.Figure = plt.figure(figsize=(11, 3))
        else:
            plt.figure(self.fig.number)
        if self.ax is None:
            self.ax: plt.Axes = plt.gca()

    def clear_fig_and_ax(self):
        self.fig = None
        self.ax = None

    def draw_planetary_system(self, save_fig=False, save_name=None, save_format='pdf', save_temp_file=None):
        self.set_fig_and_ax()

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

        if self.want_draw_planetary_system_limits:
            self.draw_planetary_system_limits()
        # self.draw_binary_forbidden_zone()
        # self.draw_rings()
        if self.want_draw_satellite_orbits:
            self.draw_satellite_orbits(self.want_orbit_label)
        self.fig.tight_layout(pad=0.03)

        self.draw_planet()
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
            if len(self.satellite_list):
                min_drawing_orbit = Q_(np.min([sat.semi_major_axis_minimum_limit.to('R_e').m
                                               for sat in self.satellite_list])/3, 'R_e')
            else:
                min_drawing_orbit = self.parent.radius
            if isinstance(self.parent, BinarySystem):
                if self.parent.system_type == 'P' and self.parent.forbidden_zone_minimum < self.parent.rough_inner_orbit_limit:
                    min_drawing_orbit = self.parent.forbidden_zone_minimum / 3
        else:
            min_drawing_orbit = np.nan

        return min_drawing_orbit

    def draw_planetary_system_limits(self):
        # x_in, y_in = draw_orbit(self.parent.inner_orbit_limit.to('R_e').m / self.parent.radius.to('R_e').m, self.ax,
        #                         self.min_drawing_orbit.to('R_e').m / self.parent.radius.to('R_e').m, color='tab:red', text_top=False,
        #                         text_units='$R_p$')
        x_out, y_out = draw_orbit(self.parent.outer_orbit_limit.to('R_e').m / self.parent.radius.to('R_e').m, self.ax,
                                  self.min_drawing_orbit.to('R_e').m / self.parent.radius.to('R_e').m, color='tab:red', text_top=False,
                                  text_units='$R_p$')
        # return x_in, y_in, x_out, y_out
        return x_out, y_out

    def draw_satellite_orbits(self, orbit_label=True):
        for satellite in self.satellite_list:
            draw_orbit(satellite.semi_major_axis.to('R_e').m / self.parent.radius.to('R_e').m, self.ax, self.min_drawing_orbit.to('R_e').m / self.parent.radius.to('R_e').m,
                       color='chocolate', text_units='$R_p$', orbit_label=orbit_label)

    def draw_planet(self):
        if isinstance(self.parent, Planet):
            draw_planet(self.parent.radius.to('R_e').m, self.min_drawing_orbit.to('R_e').m / self.parent.radius.to('R_e').m,
                        np.fliplr(self.parent.image_array),
                        self.ax, normalization_factor=self.normalization_factor)
        elif isinstance(self.parent, BinarySystem):
            draw_planet(self.parent.primary_body.radius.to('R_e').m,
                        self.min_drawing_orbit.to('R_e').m / self.parent.radius.to('R_e').m,
                        np.fliplr(self.parent.primary_body.image_array),
                        self.ax, normalization_factor=self.normalization_factor, y0=0.2)
            draw_planet(self.parent.secondary_body.radius.to('R_e').m,
                        self.min_drawing_orbit.to('R_e').m / self.parent.radius.to('R_e').m,
                        np.fliplr(self.parent.secondary_body.image_array),
                        self.ax, normalization_factor=self.normalization_factor, y0=-0.2)

    def draw_satellites(self):
        for satellite in self.satellite_list:
            draw_planet(satellite.radius.to('R_e').m,
                        satellite.semi_major_axis.to('R_e').m / self.parent.radius.to('R_e').m,
                        np.fliplr(satellite.image_array), self.ax, normalization_factor=self.normalization_factor)

    def copy(self):
        return copy.deepcopy(self)

    def __hash__(self):
        return super().__hash__()