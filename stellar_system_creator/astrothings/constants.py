import numpy as np
from astropy.constants import L_sun, M_earth, M_jup, M_sun, R_earth, R_jup, R_sun, au, c, h, g0, sigma_sb, G


def arithmetic_mean_radius(nominal_equatorial_radius, nominal_polar_radius):
    a = nominal_equatorial_radius
    b = nominal_polar_radius
    r1 = (2 * a + b) / 3
    return r1


def authalic_radius(nominal_equatorial_radius, nominal_polar_radius):
    """Authalic radius (meaning "equal area") is the radius of a hypothetical perfect sphere that has the same surface
     area as the reference ellipsoid."""
    a = nominal_equatorial_radius
    b = nominal_polar_radius
    e = 1 - (b / a) ** 2
    logpart = np.log((1 + e) / (b / a))
    r2 = np.sqrt((a ** 2 + b ** 2 / e * logpart) / 2)
    return r2


def volumetric_radius(nominal_equatorial_radius, nominal_polar_radius):
    """Volumetric radius is the radius of a sphere of volume equal to the ellipsoid"""
    a = nominal_equatorial_radius
    b = nominal_polar_radius
    r3 = (a ** 2 * b) ** (1 / 3)
    return r3


# define solar constants
solar_luminosity = L_sun.value  # W
solar_mass = M_sun.value  # kg
solar_radius = R_sun.value  # meters  # sun is almost a perfect sphere, no need for different radii
solar_lifetime = 10e9  # years
solar_flux = 1361  # W/m^2
solar_surface_area = 4 * np.pi * solar_radius ** 2
solar_volume = 4 * np.pi * solar_radius ** 3 / 3
solar_density = solar_mass / solar_volume

# define jovian constants
jup_mass = M_jup.value  # kg
jup_nominal_equatorial_radius = 71492000  # meters
jup_nominal_polar_radius = 66854000  # meters

jup_mean_radius = arithmetic_mean_radius(jup_nominal_equatorial_radius, jup_nominal_polar_radius)
jup_authalic_radius = authalic_radius(jup_nominal_equatorial_radius, jup_nominal_polar_radius)
jup_volumetric_radius = volumetric_radius(jup_nominal_equatorial_radius, jup_nominal_polar_radius)

jup_surface_area = 4 * np.pi * jup_volumetric_radius ** 2  # not exact, since the authalic radius is much different
jup_volume = 4 * np.pi * jup_volumetric_radius ** 3 / 3
jup_density = jup_mass / jup_volume


# define terran constants
earth_mass = M_earth.value  # kg
earth_nominal_equatorial_radius = 6378137.0  # meters
earth_nominal_polar_radius = 6356752.3  # meters
earth_gravitational_acceleration = g0.value  # meters/second^2
earth_orbital_speed = 29800  # meters/second
earth_escape_velocity = 11186  # meters/second

earth_mean_radius = arithmetic_mean_radius(earth_nominal_equatorial_radius, earth_nominal_polar_radius)
earth_authalic_radius = authalic_radius(earth_nominal_equatorial_radius, earth_nominal_polar_radius)
earth_volumetric_radius = volumetric_radius(earth_nominal_equatorial_radius, earth_nominal_polar_radius)

earth_surface_area = 4 * np.pi * earth_volumetric_radius ** 2
earth_volume = 4 * np.pi * earth_volumetric_radius ** 3 / 3
earth_density = earth_mass / earth_volume  # kg / meters^3


# define others
astronomical_unit = au.value  # meters
speed_of_light = c.value  # m/s
plank_constant = h.value  # J*s
stefan_boltzmann_constant = sigma_sb.value  # W/(K^4 m^2)
gravitational_constant = G.value  # m^3/(kg s^2)

