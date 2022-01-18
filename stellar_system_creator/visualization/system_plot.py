from typing import Union, Tuple, List

import cairo
import numpy as np
from PIL import Image

from stellar_system_creator.stellar_system_elements.binary_system import BinarySystem
from stellar_system_creator.stellar_system_elements.planetary_system import PlanetarySystem
from stellar_system_creator.stellar_system_elements.stellar_body import StellarBody, BlackHole, Planet, Satellite, \
    TrojanSatellite
from stellar_system_creator.stellar_system_elements.stellar_system import StellarSystem, MultiStellarSystemSType

# https://www.nature.com/articles/nmeth.1618 for colors that are colorblind friendly
# colors = {'navajowhite': [1, 222/255, 173/255, 1],
#           'orange': [230/255, 159/255, 0, 1],
#           'green': [0, 158/255, 115/255, 1],
#           'lightblue': [86/255, 180/255, 233/255, 1],
#           'yellow': [240/255, 228/255, 66/255, 1],
#           }

# https://davidmathlogic.com/colorblind/#%23332288-%23117733-%2344AA99-%2388CCEE-%23CAAE22-%23CC6677-%23AA4499-%23882255-%23FFDEAD
from stellar_system_creator.visualization.drawing_tools import GradientColor

colors = {'purple': [51 / 255, 34 / 255, 136 / 255, 1],
          'darkgreen': [17 / 255, 119 / 255, 51 / 255, 1],
          'bluegreen': [68 / 255, 170 / 255, 153 / 255, 1],
          'lightblue': [138 / 255, 204 / 255, 238 / 255, 1],
          'yellowish': [201 / 255, 174 / 255, 34 / 255, 1],
          'lightred': [204 / 255, 102 / 255, 119 / 255, 1],
          'violetish': [170 / 255, 68 / 255, 153 / 255, 1],
          'darkviolet': [136 / 255, 34 / 255, 85 / 255, 1],
          'navajowhite': [1, 222 / 255, 173 / 255, 1],
          }


class SystemPlot:
    # TODO: change ImageSurface of base surface to SVGSurface. Do not change for planet images.
    def __init__(self, ssc_object: Union[PlanetarySystem, StellarSystem]):
        self.ssc_object = ssc_object
        self.scale = 6

        # drawing options - lines // areas
        self.want_orbit_limits = True
        self.want_habitable_zones_extended = True
        self.want_habitable_zones_conservative = True
        self.want_water_frost_line = True
        self.want_rock_line = True
        self.want_tidal_locking_radius = True
        self.want_orbit_lines = True
        self.orbit_line_width = 3

        # drawing options - labels
        self.want_orbit_limits_labels = True
        self.want_other_line_labels = True
        self.want_children_orbit_labels = True
        self.want_children_name_labels = True
        self.want_parent_name_labels = True

        self.orbit_distance_font_size = 10
        self.object_name_font_size = 10

        # drawing options - objects
        self.satellite_plot_y_step = None
        self.want_satellites = True
        self.want_trojans = True
        self.want_asteroid_belts = True
        self.want_children_objects = True
        self.want_parents = True

        self.plot_base_surface: Union[cairo.ImageSurface, None] = None
        self.plot_base_context: Union[cairo.Context, None] = None
        self._set_plot_limits()

    def save_image(self, filename):
        array = get_ndarray_from_cairo_image_surface(self.plot_base_surface)
        save_image_ndarray(array, filename)

    def transform_im_to_data(self, im_value, mode='x'):
        base_surface = self.plot_base_surface
        if mode == 'x':
            width = base_surface.get_width()
            a = width / np.log10(self.xlims[1] / self.xlims[0])
            b = - a * np.log10(self.xlims[0])
            data_value = 10 ** ((im_value - b) / a)
        elif mode == 'y':
            height = base_surface.get_height()
            b = self.ylims[0]
            a = (self.ylims[1] - self.ylims[0]) / height
            data_value = a * im_value + b
        else:
            data_value = np.nan

        return data_value

    def transform_data_to_im(self, data_value, mode='x'):
        base_surface = self.plot_base_surface
        if mode == 'x':
            width = base_surface.get_width()
            a = width / (np.log10(self.xlims[1] / self.xlims[0]))
            b = - a * np.log10(self.xlims[0])
            im_value = a * np.log10(data_value) + b
        elif mode == 'y':
            height = base_surface.get_height()
            b = -self.ylims[0] * height
            a = - height / (self.ylims[1] - self.ylims[0])
            im_value = a * data_value + b
        else:
            im_value = np.nan

        return im_value

    def _set_plot_limits(self):
        if isinstance(self.ssc_object, StellarSystem):
            self._set_relative_habitable_zone_type()
        orbit_distances = self.ssc_object.get_children_orbit_distances('au', self)
        self.xlims = (min(orbit_distances) / 3, max(orbit_distances) * 2)
        self.ylims = (-0.5, 0.5)
        if self.satellite_plot_y_step is None:
            self.satellite_plot_y_step = (self.ylims[1] - self.ylims[0]) / 10

    def update_plot_limits(self):
        self._set_plot_limits()

    def render_plot(self):
        self._render_plot()

    def delete_plot(self):
        self.plot_base_surface, self.plot_base_context = None, None

    def _render_plot(self):
        self.plot_base_surface, self.plot_base_context = create_base_surface_and_context(
            300 * self.scale, 1100 * self.scale)

        self.update_plot_limits()

        self.add_habitable_zones('extended')
        self.add_habitable_zones('conservative')
        self.add_water_frost_line()
        self.add_rock_line()
        self.add_tidal_locking_radius()

        self.add_orbit_limits()
        self.add_children_orbit()

        if self.want_parents:
            self.add_parent()
        if self.want_children_objects:
            self.add_children()
        if self.want_asteroid_belts:
            self.add_asteroid_belts()
        if self.want_satellites:
            self.add_satellites()
        if self.want_trojans:
            self.add_trojans()

        self.add_orbit_limits_labels()
        self.add_children_orbit_labels()
        self.add_other_line_labels()
        self.add_children_name_labels()
        self.add_parent_name_labels()

    def add_orbit_limits(self):
        ssc_object = self.ssc_object
        if isinstance(self.ssc_object, PlanetarySystem):
            orbit_limits = [ssc_object.parent.outer_orbit_limit]
        else:
            orbit_limits = [ssc_object.parent.inner_orbit_limit, ssc_object.parent.outer_orbit_limit]

        value = False
        for limit in orbit_limits:
            if self.want_orbit_limits:
                value = draw_orbit(self, colors['navajowhite'], limit.to('au').m)

        return value

    def add_orbit_limits_labels(self):
        ssc_object = self.ssc_object
        if isinstance(self.ssc_object, PlanetarySystem):
            orbit_limits = [ssc_object.parent.outer_orbit_limit]
        else:
            orbit_limits = [ssc_object.parent.inner_orbit_limit, ssc_object.parent.outer_orbit_limit]

        value = False
        for limit in orbit_limits:
            if self.want_orbit_limits_labels:
                value = draw_orbit_label(self, [1, 1, 1, 1], limit.to('au').m, 'bottom',
                                         font_size=self.orbit_distance_font_size) or value

        return value

    def add_children_orbit(self):
        ssc_object = self.ssc_object
        if isinstance(ssc_object, StellarSystem):
            target_objects: List[Planet] = [ps.parent for ps in ssc_object.planetary_systems]
        elif isinstance(ssc_object, PlanetarySystem):
            target_objects: List[Satellite] = ssc_object.satellite_list
        else:
            return False

        value = False
        for tobj in target_objects:
            if self.want_orbit_lines:
                value = draw_orbit(self, colors['darkviolet'], tobj.semi_major_axis.to('au').m,
                                   tobj.periapsis.to('au').m, tobj.apoapsis.to('au').m) or value

    def add_children_orbit_labels(self):
        ssc_object = self.ssc_object
        if isinstance(ssc_object, StellarSystem):
            target_objects: List[Planet] = [ps.parent for ps in ssc_object.planetary_systems]
            unit_label = 'A.U'
            normalization = 1
        elif isinstance(ssc_object, PlanetarySystem):
            target_objects: List[Satellite] = ssc_object.satellite_list
            unit_label = 'Rp'
            normalization = ssc_object.parent.radius.to('au').m
        else:
            return False

        value = False
        for tobj in target_objects:
            if self.want_children_orbit_labels:
                value = draw_orbit_label(self, [1, 1, 1, 1], tobj.semi_major_axis.to('au').m, 'top', unit_label,
                                         normalization, font_size=self.orbit_distance_font_size) or value

    def add_parent(self):
        ssc_object = self.ssc_object
        parent_drawing_orbit = self.xlims[0]

        value = False
        if isinstance(ssc_object.parent, StellarBody):
            with_inset = False
            if isinstance(ssc_object.parent, BlackHole):
                with_inset = True
            if isinstance(ssc_object.parent, Planet):
                value = draw_object(self, ssc_object.parent.radius.to('R_e').m,
                                    parent_drawing_orbit, ssc_object.parent.image_array,
                                    normalization_factor=2.5, flip_image_horizontally=True)
                if ssc_object.parent.has_ring:
                    ring = ssc_object.parent.ring
                    value = draw_parent_ring(self, ring_inner_radius=ring.inner_radius.to('au').m,
                                             ring_outer_radius=ring.outer_radius.to('au').m,
                                             forbidden_bands=ring.forbidden_bands.to('au').m,
                                             ring_color_list=ring.ring_radial_gradient_colors) or value
            else:
                value = draw_object(self, ssc_object.parent.radius.to('R_e').m,
                                    parent_drawing_orbit, ssc_object.parent.image_array, with_inset=with_inset)

        elif isinstance(ssc_object.parent, BinarySystem):
            with_inset = False
            if isinstance(ssc_object.parent.primary_body, BlackHole):
                with_inset = True
            value = draw_object(self, ssc_object.parent.primary_body.radius.to('R_e').m,
                                parent_drawing_orbit, ssc_object.parent.primary_body.image_array,
                                y0=0.2, with_inset=with_inset)

            with_inset = False
            if isinstance(ssc_object.parent.secondary_body, BlackHole):
                with_inset = True
            value = draw_object(self, ssc_object.parent.secondary_body.radius.to('R_e').m,
                                parent_drawing_orbit, ssc_object.parent.secondary_body.image_array,
                                y0=-0.2, with_inset=with_inset) or value

        return value

    def add_parent_name_labels(self):
        ssc_object = self.ssc_object
        parent_drawing_orbit = self.xlims[0] * 2

        value = False
        if isinstance(ssc_object.parent, StellarBody):
            if self.want_parent_name_labels:
                value = draw_object_label(self, ssc_object.parent.name, [1, 1, 1, 1], parent_drawing_orbit, y0=0,
                                          font_size=self.object_name_font_size) or value

        elif isinstance(ssc_object.parent, BinarySystem):
            if self.want_parent_name_labels:
                value = draw_object_label(self, ssc_object.parent.primary_body.name, [1, 1, 1, 1], parent_drawing_orbit,
                                          y0=-0.2, font_size=self.object_name_font_size) or value

                value = draw_object_label(self, ssc_object.parent.secondary_body.name, [1, 1, 1, 1],
                                          parent_drawing_orbit, y0=0.7, font_size=self.object_name_font_size) or value

        return value

    def add_children(self):
        ssc_object = self.ssc_object
        if isinstance(ssc_object, StellarSystem):
            target_objects: List[Planet] = [ps.parent for ps in ssc_object.planetary_systems]
            flip_image_horizontally = False
        elif isinstance(ssc_object, PlanetarySystem):
            target_objects: List[Satellite] = ssc_object.satellite_list
            flip_image_horizontally = True
        else:
            return False

        value = False
        for tobj in target_objects:
            if not tobj.has_ring:
                value = draw_object(self, tobj.radius.to('R_e').m,
                                    tobj.semi_major_axis.to('au').m, tobj.image_array,
                                    flip_image_horizontally=flip_image_horizontally) or value
            else:
                value = draw_object(self, tobj.radius.to('R_e').m,
                                    tobj.semi_major_axis.to('au').m, tobj.image_array,
                                    flip_image_horizontally=flip_image_horizontally,
                                    ring_inner_radius=tobj.ring.inner_radius.to('R_e').m,
                                    ring_outer_radius=tobj.ring.outer_radius.to('R_e').m,
                                    forbidden_bands=tobj.ring.forbidden_bands.to('R_e').m,
                                    ring_color_list=tobj.ring.ring_radial_gradient_colors) or value

        return value

    def add_children_name_labels(self):
        ssc_object = self.ssc_object
        if isinstance(ssc_object, StellarSystem):
            target_objects: List[Planet] = [ps.parent for ps in ssc_object.planetary_systems]
        elif isinstance(ssc_object, PlanetarySystem):
            target_objects: List[Satellite] = ssc_object.satellite_list
        else:
            return False

        value = False
        for tobj in target_objects:
            if self.want_children_name_labels:
                value = draw_object_label(self, tobj.name, [1, 1, 1, 1], tobj.semi_major_axis.to('au').m,
                                          font_size=self.object_name_font_size) or value

        return value

    def add_habitable_zones(self, limit='conservative'):
        ssc_object = self.ssc_object
        if limit == 'conservative' and not self.want_habitable_zones_conservative:
            return False
        if limit == 'extended' and not self.want_habitable_zones_extended:
            return False

        if isinstance(ssc_object, StellarSystem):
            if limit == 'extended':
                min_name = ssc_object.parent.insolation_model.relaxed_min_name
                max_name = ssc_object.parent.insolation_model.relaxed_max_name
                alpha = 0.4
            elif limit == 'conservative':
                min_name = ssc_object.parent.insolation_model.conservative_min_name
                max_name = ssc_object.parent.insolation_model.conservative_max_name
                alpha = 0.8
            else:
                return False

            self._set_relative_habitable_zone_type()
            value = draw_orbit(self, colors['darkgreen'][:-1] + [alpha], None,
                               ssc_object.parent.habitable_zone_limits[self.relevant_zone_type][min_name].to('au').m,
                               ssc_object.parent.habitable_zone_limits[self.relevant_zone_type][max_name].to('au').m)

            return value

        return False

    def _set_relative_habitable_zone_type(self):
        ssc_object = self.ssc_object
        habitable_zone_limit_keys = ssc_object.parent.habitable_zone_limits.keys()
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

        self.relevant_zone_type = relevant_zone_type

    def add_water_frost_line(self):
        ssc_object = self.ssc_object
        if isinstance(ssc_object, StellarSystem):
            value = False
            if self.want_water_frost_line:
                value = draw_orbit(self, colors['lightblue'], ssc_object.parent.water_frost_line.to('au').m)
            return value

        return False

    def add_rock_line(self):
        ssc_object = self.ssc_object
        if isinstance(ssc_object, StellarSystem):
            value = False
            if self.want_rock_line:
                value = draw_orbit(self, colors['bluegreen'], ssc_object.parent.rock_line.to('au').m)
            return value

        return False

    def add_tidal_locking_radius(self):
        ssc_object = self.ssc_object
        value = False
        if self.want_tidal_locking_radius:
            value = draw_orbit(self, colors['purple'], ssc_object.parent.tidal_locking_radius.to('au').m)

        return value

    def add_other_line_labels(self):
        ssc_object = self.ssc_object
        value = False
        if self.want_other_line_labels:
            if self.want_rock_line and isinstance(ssc_object, StellarSystem):
                value = draw_orbit_label(self, [1, 1, 1, 1], ssc_object.parent.rock_line.to('au').m, 'bottom',
                                         font_size=self.orbit_distance_font_size) or value
            if self.want_water_frost_line and isinstance(ssc_object, StellarSystem):
                value = draw_orbit_label(self, [1, 1, 1, 1], ssc_object.parent.water_frost_line.to('au').m, 'bottom',
                                         font_size=self.orbit_distance_font_size) or value
            if self.want_tidal_locking_radius:
                value = draw_orbit_label(self, [1, 1, 1, 1], ssc_object.parent.tidal_locking_radius.to('au').m,
                                         'bottom', font_size=self.orbit_distance_font_size) or value

        return value

    def add_satellites(self):
        ssc_object = self.ssc_object
        if isinstance(ssc_object, StellarSystem):
            value = False
            for ps in list(ssc_object.planetary_systems):
                target_objects = ps.satellite_list
                for i, tobj in enumerate(target_objects):
                    satellite_no = i + 1
                    if self.satellite_plot_y_step is None:
                        satellite_plot_y_step = (self.ylims[1] - self.ylims[0]) / 10
                    else:
                        satellite_plot_y_step = self.satellite_plot_y_step
                    if len(target_objects) % 2:
                        y0 = (-1) ** (satellite_no - 1) * (satellite_no // 2) * satellite_plot_y_step + 0j
                    else:
                        y0 = ((-1) ** (satellite_no - 1) * ((satellite_no + 1) // 2) - np.sign(
                            (-1) ** (satellite_no - 1)) / 2) * satellite_plot_y_step + 0j

                    value = draw_object(self, tobj.radius.to('R_e').m,
                                        0.87 * ps.parent.semi_major_axis.to('au').m, tobj.image_array, y0=np.real(y0)) \
                            or value
            return value

        return False

    def add_asteroid_belts(self):
        ssc_object = self.ssc_object
        if isinstance(ssc_object, StellarSystem):
            target_objects = ssc_object.asteroid_belts
        else:
            return False

        value = False
        for tobj in target_objects:
            y_distribution = np.linspace(self.ylims[0], self.ylims[1], tobj.relative_count)
            for i in range(tobj.relative_count):
                semi_major_axis = tobj.semi_major_axis_distribution[i].to('au').m
                asteroid_radius = tobj.radius_distribution[i].to('R_e').m
                y0 = y_distribution[i]
                value = draw_object(self, asteroid_radius,
                                    semi_major_axis, tobj.image_array[i % 3], y0=y0) or value

        return value

    def add_trojans(self):
        ssc_object = self.ssc_object
        if isinstance(ssc_object, StellarSystem):
            value = False
            for ps in ssc_object.planetary_systems:
                target_objects = ps.trojans_list
                for i, tobj in enumerate(target_objects):
                    if isinstance(tobj, TrojanSatellite):
                        y0 = tobj.lagrange_position * 3.5 / 5 * self.ylims[1]
                        value = draw_object(self, tobj.radius.to('R_e').m,
                                            ps.parent.semi_major_axis.to('au').m, tobj.image_array, y0=y0) or value
                    else:
                        y_distribution = np.linspace(2.5 / 5 * tobj.lagrange_position * self.ylims[1],
                                                     4.5 / 5 * tobj.lagrange_position * self.ylims[1],
                                                     tobj.relative_count)
                        for i in range(tobj.relative_count):
                            semi_major_axis = tobj.semi_major_axis_distribution[i].to('au').m

                            # smoothen out edges
                            if i < 0.2 * tobj.relative_count:
                                dsma = tobj.semi_major_axis.to('au').m - semi_major_axis
                                semi_major_axis = tobj.semi_major_axis.to('au').m + \
                                                  dsma * (20 * i / tobj.relative_count) ** 0.1
                            if i > 0.8 * tobj.relative_count:
                                dsma = tobj.semi_major_axis.to('au').m - semi_major_axis
                                semi_major_axis = tobj.semi_major_axis.to('au').m + \
                                                  dsma * (20 * (tobj.relative_count - i) / tobj.relative_count) ** 0.1

                            asteroid_radius = tobj.radius_distribution[i].to('R_e').m
                            y0 = y_distribution[i]
                            value = draw_object(self, asteroid_radius,
                                                semi_major_axis, tobj.image_array[i % 3], y0=y0) or value

                return value

        return False


class SystemMultiPlot:

    def __init__(self, ssc_object: MultiStellarSystemSType):
        self.ssc_object = ssc_object
        self.plot_base_surface: Union[cairo.ImageSurface, None] = None
        self.system_plots = [child.system_plot for child in self.ssc_object.children]

    def render_plot(self):
        self._render_plot()

    def _render_plot(self):
        for child in self.ssc_object.children:
            child.system_plot.render_plot()
        self.plot_base_surface = combine_system_plots_vertically(self.system_plots)

    def delete_plot(self):
        self.plot_base_surface = None
        for child in self.ssc_object.children:
            child.system_plot.delete_plot()

    def save_image(self, filename):
        array = get_ndarray_from_cairo_image_surface(self.plot_base_surface)
        save_image_ndarray(array, filename)


def get_cairo_image_surface_from_ndarray(data: np.ndarray, flip_horizontally=False) -> cairo.ImageSurface:
    if flip_horizontally:
        data = np.array(list(np.fliplr(data)))
    surface: cairo.ImageSurface = cairo.ImageSurface.create_for_data(data, cairo.FORMAT_ARGB32,
                                                                     *(reversed(data.shape[:2])))
    return surface


def get_ndarray_from_cairo_image_surface(surface: cairo.ImageSurface) -> np.ndarray:
    buffer = surface.get_data()
    data: np.ndarray = np.frombuffer(buffer, np.uint8)
    data.shape = (surface.get_height(), surface.get_width(), 4)
    return data


def get_image_ndarray(filename: str) -> np.ndarray:
    # noinspection PyTypeChecker
    return np.array(Image.open(filename))


def save_image_ndarray(data: np.ndarray, filename) -> bool:
    pil_image = Image.fromarray(data, 'RGBA')
    pil_image.save(filename)
    return True


def create_base_surface_and_context(height, width) -> Tuple[cairo.ImageSurface, cairo.Context]:
    surface: cairo.ImageSurface = cairo.ImageSurface(cairo.FORMAT_ARGB32, int(width), int(height))
    context = cairo.Context(surface)
    context.set_source_rgba(0, 0, 0, 1)
    context.paint()
    return surface, context


def get_object_x_y_radius_surface(system_plot, context, base_surface, planet_image_array,
                                  normalization_factor, planet_relative_radius, y0, planet_orbit_radius,
                                  flip_image_horizontally=False):
    # getting scale of base_surface
    base_surface_scale = base_surface.get_height() / 30

    # setting up scaling of planet
    normalization = planet_image_array.shape[0]
    scale_xy = normalization_factor / normalization * 2.5 ** np.log10(planet_relative_radius * 10) * base_surface_scale
    context.scale(scale_xy, scale_xy)  # scales down image size

    planet_image_surface = get_cairo_image_surface_from_ndarray(planet_image_array, flip_image_horizontally)
    planet_radius = planet_image_surface.get_width() / 2

    # getting x displacement dx due to vertical position
    orbit_radius = get_orbit_radius(base_surface)
    theta = np.arcsin((system_plot.transform_data_to_im(y0, 'y') - base_surface.get_height() / 2) / orbit_radius)
    dx = orbit_radius * (1 - np.cos(theta))

    # set center height of base surface minus radius of planet when scaled down
    planet_y_position = system_plot.transform_data_to_im(y0, 'y') - planet_radius * scale_xy
    planet_x_position = system_plot.transform_data_to_im(planet_orbit_radius, 'x') - planet_radius * scale_xy - dx
    # context.arc(x_edge - radius, y_edge, radius, -0.5 * np.pi, 0.5 * np.pi)
    planet_y_position /= scale_xy
    planet_x_position /= scale_xy

    return planet_x_position, planet_y_position, planet_radius, planet_image_surface, scale_xy


def draw_object(system_plot: SystemPlot, planet_relative_radius, planet_orbit_radius,
                planet_image_array, normalization_factor=1., y0=0., with_inset=False, flip_image_horizontally=False,
                ring_inner_radius=None, ring_outer_radius=None, forbidden_bands=None,
                ring_color_list=None) -> bool:
    context: cairo.Context = system_plot.plot_base_context
    base_surface: cairo.ImageSurface = system_plot.plot_base_surface

    context.save()

    if not with_inset:
        zoom_factor = 1
    elif planet_relative_radius < 0.0001:
        zoom_factor = 10E4
    elif planet_relative_radius < 0.001:
        zoom_factor = 10E3
    elif planet_relative_radius < 0.01:
        zoom_factor = 10E2
    elif planet_relative_radius < 0.1:
        zoom_factor = 10E1
    else:
        zoom_factor = 1
    planet_x_position, planet_y_position, planet_radius, planet_image_surface, scale_xy = \
        get_object_x_y_radius_surface(system_plot, context, base_surface, planet_image_array, normalization_factor,
                                      zoom_factor * planet_relative_radius, y0, planet_orbit_radius,
                                      flip_image_horizontally)

    planet_radius_scaling = planet_relative_radius / planet_radius

    if ring_inner_radius is not None and ring_outer_radius is not None:
        add_ring_path_part(context, planet_x_position + planet_radius, planet_y_position + planet_radius,
                           ring_inner_radius / planet_radius_scaling,
                           ring_outer_radius / planet_radius_scaling,
                           np.array(forbidden_bands) / planet_radius_scaling,
                           ring_color_list, 0, 5, 'back')

    context.set_source_surface(planet_image_surface, planet_x_position, planet_y_position)
    context.arc(planet_x_position + planet_radius, planet_y_position + planet_radius, planet_radius, 0., 2. * np.pi)
    context.fill()

    if with_inset:
        context.save()

        context.set_source_rgba(1, 1, 1, 1)
        spacing = 0.1
        context.set_line_width(system_plot.scale * system_plot.orbit_line_width / 2 / scale_xy)
        context.rectangle(planet_x_position - spacing * planet_radius, planet_y_position - spacing * planet_radius,
                          planet_radius * 2 * (1 + spacing), planet_radius * 2 * (1 + spacing))
        context.stroke()

        context.set_font_size(system_plot.scale * system_plot.orbit_distance_font_size / scale_xy)
        text = f"x{zoom_factor:.0g}"
        text_extents: cairo.TextExtents = context.text_extents(text)
        # text_extents.width - 2 * text_extents.x_bearing
        context.move_to(planet_x_position + planet_radius * 2 * (1 + spacing), planet_y_position - text_extents.height)

        context.text_path(text)
        context.fill()
        context.restore()

    if ring_inner_radius is not None and ring_outer_radius is not None:
        add_ring_path_part(context, planet_x_position + planet_radius, planet_y_position + planet_radius,
                           ring_inner_radius / planet_radius_scaling,
                           ring_outer_radius / planet_radius_scaling,
                           np.array(forbidden_bands) / planet_radius_scaling,
                           ring_color_list, 0, 5, 'front')

    context.restore()

    return True


def add_ring_path_part(context: cairo.Context, x, y, inner_radius, outer_radius, forbidden_bands: np.array,
                       color_list: List[GradientColor], side_plane_angle=0., off_plane_angle=45.,
                       placing_around_planet='back'):
    if placing_around_planet == 'back':
        min_an = 0.9999
        max_an = 2.0001
    elif placing_around_planet == 'front':
        min_an = -0.0001
        max_an = 1.0001
    elif placing_around_planet == 'all':
        min_an = 0.000
        max_an = 2
    else:
        return False

    context.save()
    context.push_group()

    context.translate(x, y)
    context.rotate(side_plane_angle / 180 * np.pi)
    context.scale(outer_radius, outer_radius * np.cos((90 - off_plane_angle) / 180 * np.pi))

    radial_gradient = cairo.RadialGradient(0., 0., inner_radius / outer_radius, 0., 0., 1.0)
    for color_set in color_list:
        radial_gradient.add_color_stop_rgba(*color_set.get_color())

    context.set_source(radial_gradient)
    context.arc(0.0, 0.0, 1.0, min_an * np.pi, max_an * np.pi)
    context.fill()

    forbidden_bands = list(forbidden_bands)
    forbidden_bands.reverse()
    for fb in forbidden_bands:
        context.arc(0.0, 0.0, fb[1] / outer_radius, min_an * np.pi, max_an * np.pi)
        context.set_source_rgba(0, 0, 0, 1)
        context.set_operator(cairo.OPERATOR_CLEAR)
        context.fill()

        context.arc(0.0, 0.0, fb[0] / outer_radius, min_an * np.pi, max_an * np.pi)
        context.set_source(radial_gradient)
        context.set_operator(cairo.OPERATOR_OVER)
        context.fill()

    context.arc(0.0, 0.0, inner_radius / outer_radius, 0.00 * np.pi, 2 * np.pi)
    context.set_source_rgba(0, 0, 0, 1)
    context.set_operator(cairo.OPERATOR_CLEAR)
    context.fill()

    context.pop_group_to_source()
    context.paint()

    context.restore()

    return True


def draw_parent_ring(system_plot: SystemPlot, ring_inner_radius=None, ring_outer_radius=None, forbidden_bands=None,
                     ring_color_list=None) -> bool:
    context: cairo.Context = system_plot.plot_base_context
    base_surface: cairo.ImageSurface = system_plot.plot_base_surface

    context.save()
    context.push_group()

    x_outer_edge = system_plot.transform_data_to_im(ring_outer_radius, 'x')
    x_inner_edge = system_plot.transform_data_to_im(ring_inner_radius, 'x')
    y_edge = base_surface.get_height() / 2
    radius = get_orbit_radius(base_surface)

    radial_gradient = cairo.RadialGradient(0., y_edge, x_inner_edge, 0., y_edge, x_outer_edge)
    for i, color_set in enumerate(ring_color_list):
        cs = color_set.get_color()
        cs[0] = cs[0] * x_outer_edge
        radial_gradient.add_color_stop_rgba(*cs)

    context.set_source(radial_gradient)
    context.arc(x_outer_edge - radius, y_edge, radius, -0.5 * np.pi, 0.5 * np.pi)
    context.fill()

    forbidden_bands = list(forbidden_bands)
    forbidden_bands.reverse()
    for fb in forbidden_bands:
        x_fb1_edge = system_plot.transform_data_to_im(fb[1], 'x')
        context.arc(x_fb1_edge - radius, y_edge, radius, -0.5 * np.pi, 0.5 * np.pi)
        context.set_source_rgba(0, 0, 0, 1)
        context.set_operator(cairo.OPERATOR_CLEAR)
        context.fill()

        x_fb0_edge = system_plot.transform_data_to_im(fb[0], 'x')
        context.arc(x_fb0_edge - radius, y_edge, radius, -0.5 * np.pi, 0.5 * np.pi)
        context.set_source(radial_gradient)
        context.set_operator(cairo.OPERATOR_OVER)
        context.fill()

    context.arc(x_inner_edge - radius, y_edge, radius, -0.5 * np.pi, 0.5 * np.pi)
    context.set_source_rgba(0, 0, 0, 1)
    context.set_operator(cairo.OPERATOR_CLEAR)
    context.fill()

    context.pop_group_to_source()
    context.paint()
    context.restore()

    return True


def get_orbit_radius(base_surface: cairo.ImageSurface):
    return base_surface.get_width()


def draw_orbit(system_plot: SystemPlot, color_rgba: list, mean_orbit_distance: [float, None],
               periapsis: [float, None] = None, apoapsis: [float, None] = None, line_width: float = 3) -> bool:
    context: cairo.Context = system_plot.plot_base_context
    base_surface: cairo.ImageSurface = system_plot.plot_base_surface

    # getting color
    color_gbr = list(color_rgba[:-1])
    color_gbr.reverse()
    color_gbra = color_gbr + [color_rgba[-1]]

    y_edge = base_surface.get_height() / 2
    radius = get_orbit_radius(base_surface)

    # draw line
    if mean_orbit_distance is not None:
        context.save()
        context.set_source_rgba(*color_gbra)
        context.set_line_width(line_width * system_plot.scale)
        x_edge = system_plot.transform_data_to_im(mean_orbit_distance, 'x')
        context.arc(x_edge - radius, y_edge, radius, -0.5 * np.pi, 0.5 * np.pi)
        context.stroke()
        context.restore()
        color_gbra = color_gbr + [color_rgba[-1] / 2]  # change color alpha if periapsis and apoaspis need to be drawn.

    if periapsis is not None and apoapsis is not None:
        context.save()
        context.set_source_rgba(*color_gbra)

        context.push_group()

        x_edge = system_plot.transform_data_to_im(apoapsis, 'x')
        context.arc(x_edge - radius, y_edge, radius, -0.5 * np.pi, 0.5 * np.pi)
        context.fill()

        x_edge = system_plot.transform_data_to_im(periapsis, 'x')
        context.set_source_rgba(0, 0, 0, 1)
        context.arc(x_edge - radius, y_edge, radius, -0.5 * np.pi, 0.5 * np.pi)
        context.set_operator(cairo.OPERATOR_CLEAR)
        context.fill()

        context.pop_group_to_source()
        context.paint()

        return True


def draw_orbit_label(system_plot: SystemPlot, color_rgba: list, mean_orbit_distance: [float, None],
                     text_position: str = 'top', text_units: str = 'A.U.',
                     numeral_normalization: float = 1, font_size: float = 10) -> bool:
    # TODO: Allow user to define font type and size with a drop down menu on the settings.
    context: cairo.Context = system_plot.plot_base_context
    base_surface: cairo.ImageSurface = system_plot.plot_base_surface

    context.save()
    context.set_font_size(font_size * system_plot.scale)
    mean_orbit_distance = 1.034 * mean_orbit_distance

    # getting color
    color_gbr = list(color_rgba[:-1])
    color_gbr.reverse()
    color_gbra = color_gbr + [color_rgba[-1]]
    context.set_source_rgba(*color_gbra)

    # set text
    text = f"{mean_orbit_distance / numeral_normalization:.2g} {text_units}"
    text_extents = context.text_extents(text)

    x_edge = system_plot.transform_data_to_im(mean_orbit_distance, 'x')
    if text_position == 'bottom':
        y_edge = base_surface.get_height() * 0.95 - text_extents.width - 2 * text_extents.x_bearing
    elif text_position == 'top':
        y_edge = base_surface.get_height() * 0.05
    else:
        return False

    context.move_to(x_edge, y_edge)
    context.rotate(np.pi / 2)

    context.text_path(text)
    context.fill()

    context.restore()

    return True


def draw_object_label(system_plot: SystemPlot, label_text: str, color_rgba: list, planet_orbit_radius, y0=0.,
                      font_size: float = 10) -> bool:
    # getting old context state before modifying it
    context: cairo.Context = system_plot.plot_base_context
    base_surface: cairo.ImageSurface = system_plot.plot_base_surface

    context.save()

    context.set_font_size(font_size * system_plot.scale)

    # getting color
    color_gbr = list(color_rgba[:-1])
    color_gbr.reverse()
    color_gbra = color_gbr + [color_rgba[-1]]
    context.set_source_rgba(*color_gbra)

    # set text
    text_extents = context.text_extents(label_text)

    x_edge = system_plot.transform_data_to_im(planet_orbit_radius, 'x') * 1.01
    y_edge = abs(0.7 + y0) * base_surface.get_height() / 2 - text_extents.height / 2 - text_extents.y_bearing

    context.move_to(x_edge, y_edge)

    context.text_path(label_text)
    context.fill()

    context.restore()

    return True


def combine_system_plots_vertically(system_plots: List[SystemPlot]) -> cairo.ImageSurface:
    total_height = sum([sp.plot_base_surface.get_height() for sp in system_plots])
    width = system_plots[0].plot_base_surface.get_width()
    surface, context = create_base_surface_and_context(total_height, width)

    for i, sp in enumerate(system_plots):
        context.save()
        context.translate(0, i * sp.plot_base_surface.get_height())
        context.set_source_surface(sp.plot_base_surface)
        context.paint()
        context.restore()

    return surface


# next steps:
# 1. test all systems and try to save them via draw in system
# 2. test gui in general.
# 3. change logo.
# 4. add screenshots of gui strengths in website.
# 5. add user pictures.
