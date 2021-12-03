from stellar_system_creator.astrothings.units import Q_


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
