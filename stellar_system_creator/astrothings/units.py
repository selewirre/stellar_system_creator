# for pint unit definition https://pint.readthedocs.io/en/stable/defining.html#defining

from pint import registry
import pint
import numpy as np

from stellar_system_creator.astrothings.constants import solar_luminosity, solar_mass, solar_radius, solar_surface_area, solar_volume, \
    solar_density, solar_lifetime, solar_flux, \
    earth_mass, earth_volumetric_radius, earth_surface_area, earth_volume, earth_density, \
    earth_gravitational_acceleration, earth_orbital_speed, earth_escape_velocity, \
    jup_mass, jup_volumetric_radius, jup_surface_area, jup_volume, jup_density, \
    stefan_boltzmann_constant, gravitational_constant, speed_of_light, plank_constant

ureg = registry.UnitRegistry()

# defining mass units
ureg.define(f'earth_mass = {earth_mass} * kg = M_e')
ureg.define(f'jup_mass = {jup_mass} * kg = M_j = jupiter_mass')
ureg.define(f'solar_mass = {solar_mass} * kg = M_s = sun_mass')

# defining length units
ureg.define(f'earth_radius = {earth_volumetric_radius} * meter = R_e')
ureg.define(f'jup_radius = {jup_volumetric_radius} * meter = R_j = jupiter_radius')
ureg.define(f'solar_radius = {solar_radius} * meter = R_s = sun_radius')

# defining area units
ureg.define(f'earth_surface_area = {earth_surface_area} * meter**2 = A_e')
ureg.define(f'jup_surface_area = {jup_surface_area} * meter**2 = A_j = jupiter_surface_area')
ureg.define(f'solar_surface_area = {solar_surface_area} * meter**2 = A_s = sun_surface_area')

# defining volume units
ureg.define(f'earth_volume = {earth_volume} * meter**3 = V_e')
ureg.define(f'jup_volume = {jup_volume} * meter**3 = V_j = jupiter_volume')
ureg.define(f'solar_volume = {solar_volume} * meter**3 = V_s = sun_volume')

# defining density units
ureg.define(f'earth_density = {earth_density} * kg/meter**3 =  rho_e')
ureg.define(f'jup_density = {jup_density} * kg/meter**3 = rho_j = jupiter_density')
ureg.define(f'solar_density = {solar_density} * kg/meter**3 = rho_s = sun_density')

# defining power (luminosity) units
ureg.define(f'solar_luminosity = {solar_luminosity} * watt = L_s = sun_luminosity')

# defining acceleration units
ureg.define(f'earth_gravitational_acceleration = {earth_gravitational_acceleration} * meter/second**2 = g_e')

# defining velocity/speed units
ureg.define(f'earth_orbital_speed = {earth_orbital_speed} * meter / second = vorb_e')
ureg.define(f'earth_escape_velocity = {earth_escape_velocity} * meter / second = vesc_e')

# defining time units
ureg.define(f'solar_lifetime = {solar_lifetime} * year = T_s = sun_lifetime')

# defining flux units
ureg.define(f'solar_flux = {solar_flux} * W / meter ** 2 = S_s = sun_flux')

pint.set_application_registry(ureg)
Q_ = ureg.Quantity

# setting constants with units
stefan_boltzmann_constant: Q_ = stefan_boltzmann_constant * ureg.watt / (ureg.kelvin ** 4 * ureg.meter ** 2)
gravitational_constant: Q_ = gravitational_constant * ureg.m ** 3 / (ureg.kg * ureg.second ** 2)
speed_of_light: Q_ = speed_of_light * ureg.m / ureg.s
plank_constant: Q_ = plank_constant * ureg.J * ureg.s
h_bar_constant: Q_ = plank_constant / (2 * np.pi)

# a = ureg.Quantity(1, 'M_s')
# b = ureg.Quantity(1, 'M_j')
# print(a+b)

# vescearth = 11.19
# # vorbearth =


# unit_families = {'Earth': {'mass': mearth, 'radius': rearth, 'radius2': rearth2, 'radius3': rearth3,
#                            'distance': AU, 'density': gcm3, 'luminosity': wm2},
#                  'Jupiter': {'mass': mjupiter, 'radius': rjupiter, 'radius2': rjupiter2, 'radius3': rjupiter3,
#                              'distance': AU, 'density': gcm3, 'luminosity': wm2},
#                  'Sol': {'mass': msol, 'radius': rsun, 'radius2': rsun2, 'radius3': rsun3,
#                          'distance': AU, 'density': gcm3, 'luminosity': lsol}
#                  }
