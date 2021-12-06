"""
Sources: 1a. https://arxiv.org/pdf/0707.2895.pdf
         1b. https://iopscience.iop.org/article/10.1086/521346 (same paper, better organized)
         2. https://lweb.cfa.harvard.edu/~lzeng/planetmodels.html (not used yet)
"""

import numpy as np

from .hot_gasgiant_radius_model import gasgiant_radius_modification
from stellar_system_creator.astrothings.units import ureg, Q_

planet_compositions = {'Rockworld70': {'m1': 6.41, 'r1': 3.19}, 'Rockworld100': {'m1': 10.55, 'r1': 3.90},
                       'Ironworld67': {'m1': 6.41, 'r1': 2.84}, 'Ironworld100': {'m1': 5.8, 'r1': 2.52},
                       'Waterworld25': {'m1': 6.41, 'r1': 3.63}, 'Waterworld45': {'m1': 6.88, 'r1': 4.02},
                       'Waterworld75': {'m1': 7.63, 'r1': 4.42}, 'Waterworld100': {'m1': 5.52, 'r1': 4.43},
                       'Icegiant': {'m1': 2.12331414, 'r1': 4.75266068, 'k3': 0.34468561,
                                    'm_min': 1 * ureg.M_e, 'm_max': 30 * ureg.M_e},
                       'Gasgiant': {'m1': 3.18600277, 'r1': 8.83406481, 'k3': 0.30311577,
                                    'm_min': 30 * ureg.M_e, 'm_max': 13 * ureg.M_j},
                       }

planet_chemical_abundance_ratios = {'Rockworld70': {'Fe': 0.3, 'MgSiO3': 0.7, 'H2O': 0.,
                                                    'H2': 0., 'He': 0., 'CH4': 0.},
                                    'Rockworld100': {'Fe': 0., 'MgSiO3': 1., 'H2O': 0.,
                                                    'H2': 0., 'He': 0., 'CH4': 0.},
                                    'Ironworld67': {'Fe': 0.675, 'MgSiO3': 0.325, 'H2O': 0.,
                                                    'H2': 0., 'He': 0., 'CH4': 0.},
                                    'Ironworld100': {'Fe': 1., 'MgSiO3': 0., 'H2O': 0.,
                                                    'H2': 0., 'He': 0., 'CH4': 0.},
                                    'Waterworld25': {'Fe': 0.225, 'MgSiO3': 0.525, 'H2O': 0.25,
                                                    'H2': 0., 'He': 0., 'CH4': 0.},
                                    'Waterworld45': {'Fe': 0.065, 'MgSiO3': 0.485, 'H2O': 0.45,
                                                    'H2': 0., 'He': 0., 'CH4': 0.},
                                    'Waterworld75': {'Fe': 0.03, 'MgSiO3': 0.22, 'H2O': 0.75,
                                                    'H2': 0., 'He': 0., 'CH4': 0.},
                                    'Waterworld100': {'Fe': 0., 'MgSiO3': 0., 'H2O': 1.,
                                                    'H2': 0., 'He': 0., 'CH4': 0.},
                                    'Icegiant': {'Fe': 0., 'MgSiO3': 0., 'H2O': 0.,
                                                 'H2': 0.81, 'He': 0.17, 'CH4': .02},
                                    'Gasgiant': {'Fe': 0., 'MgSiO3': 0., 'H2O': 0.,
                                                 'H2': .937, 'He': 0.06, 'CH4': 0.003},
                                    }


image_composition_dict = {'Rockworld70': 'rockyworld', 'Rockworld100': 'rockyworld',
                          'Ironworld67': 'ironworld', 'Ironworld100': 'ironworld',
                          'Waterworld25': 'waterworld', 'Waterworld45': 'waterworld',
                          'Waterworld75': 'waterworld', 'Waterworld100': 'waterworld',
                          'Icegiant': 'icegiant', 'Gasgiant': 'gasgiant'}


def calculate_planet_radius(planet_mass: Q_, planet_composition,
                            solar_radiation_incident_flux: Q_ = None) -> Q_:

    k1 = -0.20945
    k2 = 0.0804
    if 'k3' not in planet_compositions[planet_composition]:
        k3 = 0.394
    else:
        k3 = planet_compositions[planet_composition]['k3']

    m1 = planet_compositions[planet_composition]['m1']
    r1 = planet_compositions[planet_composition]['r1']

    scaled_mass = planet_mass.to('M_e').magnitude / m1

    log10_radius = k1 + 1 / 3 * np.log10(scaled_mass) - k2 * scaled_mass ** k3
    radius = 10 ** log10_radius * r1

    if planet_composition == 'Gasgiant' and solar_radiation_incident_flux is not None:
        from .hot_gasgiant_radius_model import get_hot_gas_giant_mass_class
        radius = radius * gasgiant_radius_modification(np.log10(solar_radiation_incident_flux.to('watt/m^2').magnitude),
                                                       get_hot_gas_giant_mass_class(planet_mass))

    radius = radius * ureg.R_e
    if radius >= 0.7 * ureg.R_j:
        radius.to('R_j')
    return radius
