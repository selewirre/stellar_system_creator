from stellar_system_creator.astrothings.units import Q_


def get_star_mass_class(mass: Q_) -> str:
    mass = mass.to('solar_mass').magnitude
    if mass >= 150:
        mass_class = ''
    elif mass >= 16:
        mass_class = 'O'
    elif mass >= 2.1:
        mass_class = 'B'
    elif mass >= 1.4:
        mass_class = 'A'
    elif mass >= 1.04:
        mass_class = 'F'
    elif mass >= 0.8:
        mass_class = 'G'
    elif mass >= 0.45:
        mass_class = 'K'
    elif mass >= 0.08:
        mass_class = 'M'
    else:
        mass_class = ''

    return mass_class


def get_star_appearance_frequency(star_mass_class) -> float:
    frequency = 0
    if star_mass_class == 'O':
        frequency = 0.0000003
    elif star_mass_class == 'B':
        frequency = 0.0013
    elif star_mass_class == 'A':
        frequency = 0.006
    elif star_mass_class == 'F':
        frequency = 0.03
    elif star_mass_class == 'G':
        frequency = 0.076
    elif star_mass_class == 'K':
        frequency = 0.121
    elif star_mass_class == 'M':
        frequency = 0.7645

    return frequency


def get_planetary_mass_class(mass: Q_) -> str:
    """
    Source: https://www.space.com/36935-planet-classification.html
    Deviated on the higher masses, with my own naming
    """

    if mass.to('earth_mass').magnitude <= 0.00001:
        mass_class = 'Asteroidan'
    elif mass.to('earth_mass').magnitude <= 0.1:
        mass_class = 'Mercurian'
    elif mass.to('earth_mass').magnitude <= 0.5:
        mass_class = 'Subterran'
    elif mass.to('earth_mass').magnitude <= 2:
        mass_class = 'Terran'
    elif mass.to('earth_mass').magnitude <= 10:
        mass_class = 'Superterran'
    elif mass.to('earth_mass').magnitude <= 30:
        mass_class = 'Neptunian'
    elif mass.to('jupiter_mass').magnitude <= 0.5:  # ~160 earth mass
        mass_class = 'Subjuvian'
    elif mass.to('jupiter_mass').magnitude <= 2:  # ~640 earth mass
        mass_class = 'Juvian'
    elif mass.to('jupiter_mass').magnitude <= 13:  # ~4100 earth mass
        mass_class = 'Superjuvian'
    elif mass.to('jupiter_mass').magnitude <= 80:
        mass_class = 'Brown dwarf'
    else:
        mass_class = 'Not a planet'

    return mass_class
