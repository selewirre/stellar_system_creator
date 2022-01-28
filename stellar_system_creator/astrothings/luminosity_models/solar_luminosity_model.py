import numpy as np

from stellar_system_creator.astrothings.units import Q_, h_bar_constant, speed_of_light, gravitational_constant, ureg


def calculate_main_sequence_luminosity(mass: Q_) -> Q_:
    mass = mass.to('solar_mass').magnitude
    if 55 < mass <= 150:
        luminosity = 32000 * mass
    elif mass > 2:
        luminosity = 1.4 * mass ** 3.5
    elif mass > 0.43:
        luminosity = mass ** 4
    elif mass > 0.08:
        luminosity = 0.23 * mass ** 2.3
    else:
        luminosity = 0

    return Q_(luminosity, 'solar_luminosity')


def calculate_blackhole_luminosity(mass: Q_) -> Q_:
    """
    More info on: https://www.vttoth.com/CMS/physics-notes/311-hawking-radiation-calculator
    """
    luminosity = h_bar_constant * speed_of_light ** 6 / (15360 * np.pi * gravitational_constant ** 2 * mass ** 2)
    return 1.6232 * luminosity.to_reduced_units().to('W')  # the 1.6232 accounts for the excess photon emission rate.
