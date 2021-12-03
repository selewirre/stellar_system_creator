import numpy as np

from stellar_system_creator.astrothings.luminosity_models.solar_luminosity_model import calculate_main_sequence_luminosity
from stellar_system_creator.astrothings.units import ureg, Q_, stefan_boltzmann_constant


def calculate_main_sequence_radius_from_polynomial(mass: Q_) -> Q_:
    """
    Source: https://en.wikipedia.org/wiki/Main_sequence#Sample_parameters
    and fitted with a 5 degree polynomial with numpy poly1d and weights 1/mass
    """
    mass = mass.to('solar_mass').magnitude
    mass_to_radius_poly_pars = [9.33374663e-07, -1.49811271e-04, 6.67440028e-03, -1.11931342e-01, 1.04271954e+00,
                                2.21613832e-02]
    radius = np.poly1d(mass_to_radius_poly_pars)(mass)
    return Q_(radius, 'solar_radius')


def calculate_main_sequence_radius(mass: Q_) -> Q_:
    """
        Source: https://academic.oup.com/mnras/article/479/4/5491/5056185, pg.5502, table 5.
        I changed the jumping point to make it smoother (from 1.5 Ms to 1.45 Ms)
        """
    mass = mass.to('solar_mass').magnitude
    if mass < 1.45:
        radius = (0.438098 * mass ** 2 + 0.479180 * mass + 0.075479) * ureg.R_s
    else:
        log_mass = np.log10(mass)
        log_temperature = -0.170026 * log_mass ** 2 + 0.888037 * log_mass + 3.671010
        temperature = 10 ** log_temperature * ureg.K
        luminosity = calculate_main_sequence_luminosity(mass * ureg.M_s)

        radius2: Q_ = luminosity.to('watt') / (4 * np.pi * stefan_boltzmann_constant * temperature ** 4)
        radius = radius2 ** 0.5

    return radius.to('R_s')


