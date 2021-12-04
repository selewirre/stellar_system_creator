import numpy as np

from matplotlib import pyplot as plt
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from matplotlib.path import Path
from matplotlib.patches import PathPatch


def draw_orbit(orbit, ax, min_draw_orbit, color, ploting=True, orbit_label=True, text_top=True, text_color='white',
               text_units='AU'):
    percentage = 1 / 1.1
    y_max = np.sqrt(min_draw_orbit ** 2 - (min_draw_orbit * percentage) ** 2)
    x_min = np.sqrt(min_draw_orbit ** 2 - y_max ** 2) / min_draw_orbit * orbit
    x_max = orbit
    x = np.logspace(np.log10(x_min), np.log10(x_max), 100) + 0j
    y = np.sqrt(orbit ** 2 - x ** 2) / orbit
    x = x.real
    y = y.real

    if ploting:
        if orbit_label:
            if text_top:
                y_text = 0.8 * y.max()
            else:
                y_text = - 0.8 * y.max()
            plt.text(orbit, y_text, f"{orbit:.2g} {text_units}", rotation=-90, verticalalignment='center',
                     color=text_color)
            # plt.text(orbit, y_text*1.25*1.1, f"{orbit:.2g} AU", rotation=-0, verticalalignment='center',
            #          horizontalalignment='right', color=text_color)
        ax.plot(x, y, color=color)
        ax.plot(x, -y, color=color)
        ax.set_ylim(-y.max(), y.max())
        if ax.get_xlim()[1] < x.max() * 1.1:
            ax.set_xlim(ax.get_xlim()[0], x.max() * 1.1)
        if ax.get_xlim()[0] > min_draw_orbit * percentage:
            ax.set_xlim(min_draw_orbit * percentage, ax.get_xlim()[1])
    return x, y


def draw_filled_orbit(orbit_min, orbit_max, ax, min_draw_orbit, color, plotting=True, alpha=1., with_gradient=False,
                      height_min=0, height_max=0.5):
    x_orbit_min, y_orbit_min = draw_orbit(orbit_min, ax, min_draw_orbit, color, ploting=False)
    x_orbit_max, y_orbit_max = draw_orbit(orbit_max, ax, min_draw_orbit, color, ploting=False)

    if plotting:
        if with_gradient:
            pass
            # add_fill_gradient_patch()
        else:
            condition1 = y_orbit_min >= height_min
            condition2 = height_max >= y_orbit_min
            condition = [c1 and c2 for (c1, c2) in zip(condition1, condition2)]
            ax.fill_betweenx(y_orbit_min[condition], x_orbit_min[condition], x_orbit_max[condition], color=color, alpha=alpha, linewidth=0.)
            ax.fill_betweenx(-y_orbit_min[condition], x_orbit_min[condition], x_orbit_max[condition], color=color, alpha=alpha, linewidth=0.)

    return x_orbit_min, y_orbit_min, x_orbit_max, y_orbit_max


def draw_planet(planet_relative_radius, planet_orbit_radius, planet_image, main_axis, normalization_factor=10, y0=0.):
    normalization = planet_image.shape[0]
    relative_zoom = normalization_factor / normalization * 2.5 ** np.log10(planet_relative_radius * 10)
    offset_image = OffsetImage(planet_image, zoom=relative_zoom)
    main_axis.scatter(planet_orbit_radius, y0, alpha=0)
    ab = AnnotationBbox(offset_image, (planet_orbit_radius, y0), frameon=False)
    main_axis.add_artist(ab)
    return None


def draw_satellite(satellite_relative_radius, satellite_parent_orbit_radius, satellite_image, main_axis, normalization_factor=10,
                   total_satellites_around_parent=1, satellite_no=1):
    satellite_plotting_orbit_radius = satellite_parent_orbit_radius*0.85
    x_orbit, y_orbit = draw_orbit(satellite_plotting_orbit_radius, main_axis, main_axis.get_xlim()[0], 'grey', ploting=False)
    satellite_plot_y_step = max(y_orbit)/5
    if total_satellites_around_parent % 2:
        y0 = (-1) ** (satellite_no - 1) * (satellite_no // 2) * satellite_plot_y_step + 0j
    else:
        y0 = ((-1) ** (satellite_no-1) * ((satellite_no+1)//2) - np.sign((-1) ** (satellite_no-1))/2) * satellite_plot_y_step + 0j

    x = np.sqrt(1 - y0 ** 2) * satellite_plotting_orbit_radius
    return draw_planet(satellite_relative_radius, x.real, satellite_image, main_axis, normalization_factor, y0.real)


def draw_asteroids(relative_count, orbit_radius, main_axis, min_drawing_orbit, belt_extend, radius_distribution,
                   image_arrays, lagrange_position=0):
    asteroid_relative_count = relative_count
    x_orbit, y_orbit = draw_orbit(orbit_radius, main_axis, min_drawing_orbit, 'grey', ploting=False)
    if not lagrange_position:
        y = np.random.uniform(-y_orbit.max(), y_orbit.max(), size=asteroid_relative_count)
    else:
        if asteroid_relative_count > 1:
            y = np.random.uniform(3*lagrange_position*y_orbit.max()/5, 5*lagrange_position*y_orbit.max()/5,
                                  size=asteroid_relative_count)
        else:
            y = 4*lagrange_position*y_orbit.max()/5
            r = orbit_radius
            x = np.sqrt(1 - y ** 2) * r
            draw_planet(radius_distribution, x, image_arrays, main_axis, normalization_factor=10, y0=y)
            return

    r = np.random.normal(loc=orbit_radius, scale=belt_extend / 2, size=asteroid_relative_count)
    x = np.sqrt(1 - y ** 2) * r

    for j, radius in enumerate(radius_distribution):
        draw_planet(radius, x[j], image_arrays[j % 3], main_axis, normalization_factor=10, y0=y[j])


def draw_trojan_satellite(radius, orbit_radius, image_array, main_axis, min_drawing_orbit, lagrange_position=0):
    x_orbit, y_orbit = draw_orbit(orbit_radius, main_axis, min_drawing_orbit, 'grey', ploting=False)
    y = 4*lagrange_position*y_orbit.max()/5
    r = orbit_radius
    x = np.sqrt(1 - y ** 2) * r
    draw_planet(radius, x, image_array, main_axis, normalization_factor=10, y0=y)
    return


def add_fill_gradient_patch(x, y, axis):
    path = Path(np.array([x, y]).transpose())
    patch = PathPatch(path, facecolor='none')
    axis.add_patch(patch)

    im = axis.imshow(x.reshape(y.size, 1), cmap=plt.cm.Reds, interpolation="bicubic",
                    origin='lower', extent=[0, 10, -0.0, 0.40], aspect="auto", clip_path=patch, clip_on=True)
    return im
