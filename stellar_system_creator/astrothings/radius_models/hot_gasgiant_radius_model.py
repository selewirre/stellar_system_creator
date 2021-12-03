"""
Source: https://arxiv.org/pdf/1804.03075.pdf
Modified it a bit, to adhere to the composition model as well.
For internal temp: https://www.aanda.org/articles/aa/pdf/2021/01/aa38361-20.pdf
"""
from stellar_system_creator.astrothings.units import Q_

hot_gas_giant_classes = {'very low mass': {'upper mass limit': 0.37, 'a': -0.33, 'log10_fs': 6.1},
                         'low mass': {'upper mass limit': 0.98, 'a': 0.7, 'log10_fs': 5.52},
                         'medium mass': {'upper mass limit': 2.5, 'a': 0.52, 'log10_fs': 5.82},
                         'high mass': {'upper mass limit': 15, 'a': 0.22, 'log10_fs': 5.2}}


def get_hot_gas_giant_mass_class(mass: Q_):
    mass = mass.to('jupiter_mass').magnitude
    for key in hot_gas_giant_classes:
        if mass < hot_gas_giant_classes[key]['upper mass limit']:
            return key
    return None


def is_gasgiant_hot(log10_flux, hot_gas_giant_mass_class) -> bool:

    if log10_flux > 100:
        print('This is a warning. In function "is_gasgiant_hot" you may have provided '
              'a flux without log10 applied on it.')

    log10_fs = hot_gas_giant_classes[hot_gas_giant_mass_class]['log10_fs']

    if 10 ** log10_flux < 10 ** log10_fs:
        return False
    else:
        return True


def gasgiant_radius_modification(log10_flux, hot_gas_giant_mass_class) -> float:

    if is_gasgiant_hot(log10_flux, hot_gas_giant_mass_class):
        a = hot_gas_giant_classes[hot_gas_giant_mass_class]['a']
        log10_fs = hot_gas_giant_classes[hot_gas_giant_mass_class]['log10_fs']
        return 1 + a * (log10_flux - log10_fs)
    else:
        return 1
