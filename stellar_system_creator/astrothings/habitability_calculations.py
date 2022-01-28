import numpy as np
from stellar_system_creator.astrothings.units import ureg, Q_, gravitational_constant
from stellar_system_creator.astrothings.astromechanical_calculations import calculate_forced_eccentricity_in_wide_binary, \
    calculate_forced_eccentricity_in_close_binary

"""
The habitable zone (HZ) is the stellar zone in which life is supported. This is a very complicated designation and
 there are still many questions around it.
 Here we calculate HZ regions via insolation theresholds (Kopparapu et al. 2014).
Insolation threshold is in units of solar flux, and represents different limits of solar flux for specific effects
 on the planetary climate, i.e. runaway greenhouse effect, maximum greenhouse effect etc.
For the all the calculations of habitable zones, we use the reference "Handbook of Exoplanets (2018)", chapter 141,
 "Habitability of Planets in Binary Star Systems", written by Siegfried Eggl
Here, we provide functions to calculate Single Star HZ, Radiative HZ in binaries, Permanent HZ in binaries, Average HZ 
 in binaries. For trinary systems, replace the swl of the sub-binary to the limit from the binary ** 2.
 
Another type of habitability that needs to be taken into account is tectonic activity. 
The tectonic activity is dominated by radioactive abundance, primordial heating and tidal heating.
Here we calculate all three. Some rough boundaries is that the total heating flux should be between 0.04 W/m2 to 2 W/m2.
These are rough estimates and should not be taken too seriously if you are barely outside the limits.
"""


def sqrt(x: Q_):
    if x.m < 0:
        return np.sqrt(np.nan * x)
    else:
        return np.sqrt(x)


def calculate_single_star_habitable_orbital_threshold(spectrally_weighted_luminosity: Q_) -> Q_:
    """
    Single Star Habitable zone is the simplest kind of habitable zone. It is determined solely by the star's luminosity.
    Equations 3 and 6 from Handbook of Exoplanets, Chapter 141
    """
    return sqrt(spectrally_weighted_luminosity)


def calculate_stype_radiative_habitable_limit(star_swl: Q_, star_companion_swl: Q_,
                                              binary_mean_distance: Q_, threshold_type: str) -> Q_:
    """
    Radiative habitability zone is the largest spherical shell to fit into the isophote-based habitability zone.
    In isophote-based habitability zone borders are determined by insolation contours only.
    Equations 9 from Handbook of Exoplanets, Chapter 141
    """
    d = binary_mean_distance
    Ls = star_swl
    Lsc = star_companion_swl

    srLs = sqrt(Ls)

    if threshold_type == 'Inner':
        denominator = (d - srLs) ** 2
        rhl = srLs * (1 + Lsc / denominator)
    elif threshold_type == 'Outer':
        denominator = (d + srLs) ** 2
        rhl = srLs * (1 + Lsc / denominator)
    else:
        denominator = (d - srLs) ** 2
        rhl_inner = srLs * (1 + Lsc / denominator)
        denominator = (d + srLs) ** 2
        rhl_outer = srLs * (1 + Lsc / denominator)
        rhl = (rhl_inner + rhl_outer) / 2

    return rhl


def calculate_ptype_radiative_habitable_limit(primary_swl: Q_, secondary_swl: Q_,
                                              binary_mean_distance: Q_, threshold_type: str) -> Q_:
    """
    Radiative habitability zone is the largest spherical shell to fit into the isophote-based habitability zone.
    In isophote-based habitability zone borders are determined by insolation contours only.
    Equations 12, 13 from Handbook of Exoplanets, Chapter 141
    Valid for binary_mean_distance << RHL_inner
    """
    b = binary_mean_distance/2
    Lpp = primary_swl
    Lsp = secondary_swl

    srLtotp = sqrt(Lpp + Lsp) + b
    srLtotm = sqrt(Lpp + Lsp) - b

    if threshold_type == 'Inner':
        term1 = Lpp * srLtotp / srLtotm
        term2 = Lsp * srLtotm / srLtotp

        rhl = sqrt(term1 + term2 - b ** 2)
    elif threshold_type == 'Outer':
        term1 = Lpp * srLtotm / srLtotp
        term2 = Lsp * srLtotp / srLtotm
        rhl = sqrt(term1 + term2 - b ** 2)
    else:
        term1 = Lpp * srLtotp / srLtotm
        term2 = Lsp * srLtotm / srLtotp
        rhl_inner = sqrt(term1 + term2 - b ** 2)
        term1 = Lpp * srLtotm / srLtotp
        term2 = Lsp * srLtotp / srLtotm
        rhl_outer = sqrt(term1 + term2 - b ** 2)
        rhl = (rhl_inner + rhl_outer) / 2

    return rhl


def calculate_stype_permanent_habitable_limit(star_swl: Q_, star_companion_swl: Q_, binary_mean_distance: Q_,
                                              binary_eccentricity: float, threshold_type: str,
                                              planetary_semimajor_axis: Q_ = None,
                                              max_planetary_eccentricity: Q_ = None) -> Q_:
    """
    Permanent habitability zone is the zone where long-term planetary insolation average must not exceed habitable
     limits, no climate inertia. It depends on the dynamically oscillating eccentricity over the course of many years,
     due to the binary systems non-spherical gravitational pull. No climate inertia means that the climate of the
     planet responds to the eccentricity changes immediately.
    Equations 29 from Handbook of Exoplanets, Chapter 141
    """
    Ls = star_swl
    Lsc = star_companion_swl
    qb = binary_mean_distance * (1 - binary_eccentricity)
    Qb = binary_mean_distance * (1 + binary_eccentricity)

    if planetary_semimajor_axis is None or max_planetary_eccentricity is None:
        planetary_semimajor_axis = calculate_single_star_habitable_orbital_threshold(Ls)
        max_planetary_eccentricity = calculate_forced_eccentricity_in_wide_binary(
            planetary_semimajor_axis, binary_mean_distance, binary_eccentricity)

    if max_planetary_eccentricity >= 1:
        return np.nan * planetary_semimajor_axis.units

    qp = planetary_semimajor_axis * (1 - max_planetary_eccentricity)
    Qp = planetary_semimajor_axis * (1 + max_planetary_eccentricity)

    if threshold_type == 'Inner':
        if Lsc < (qb - sqrt(Ls)) ** 2:
            first_term = Ls / qp / (1 - max_planetary_eccentricity)
            second_term = sqrt(Ls) * Lsc / (qp - qb) ** 2
        else:
            first_term = Ls / Qp / (1 + max_planetary_eccentricity)
            second_term = sqrt(Ls) * Lsc / (Qp - qb) ** 2
        phl = first_term + second_term
    elif threshold_type == 'Outer':
        first_term = Ls / Qp / (1 + max_planetary_eccentricity)
        second_term = sqrt(Ls) * Lsc / (Qp - Qb) ** 2
        phl = first_term + second_term
    else:
        if Lsc < (qb - sqrt(Ls)) ** 2:
            first_term = Ls / qp / (1 - max_planetary_eccentricity)
            second_term = sqrt(Ls) * Lsc / (qp - qb) ** 2
        else:
            first_term = Ls / Qp / (1 + max_planetary_eccentricity)
            second_term = sqrt(Ls) * Lsc / (Qp - qb) ** 2
        phl_inner = first_term + second_term

        first_term = Ls / Qp / (1 + max_planetary_eccentricity)
        second_term = sqrt(Ls) * Lsc / (Qp - Qb) ** 2
        phl_outer = first_term + second_term

        phl = (phl_inner + phl_outer) / 2

    return phl


def calculate_ptype_permanent_habitable_limit(primary_swl: Q_, secondary_swl: Q_, binary_mean_distance: Q_,
                                              binary_eccentricity: float, secondary_star_mass_ratio: float,
                                              threshold_type: str,
                                              planetary_semimajor_axis: Q_ = None,
                                              max_planetary_eccentricity: Q_ = None) -> Q_:
    """
    Permanent habitability zone is the zone where long-term planetary insolation average must not exceed habitable
     limits, no climate inertia. It depends on the dynamically oscillating eccentricity over the course of many years,
     due to the binary systems non-spherical gravitational pull. No climate inertia means that the climate of the
     planet responds to the eccentricity changes immediately.
    Equations 36 from Handbook of Exoplanets, Chapter 141
    """
    Lpp = primary_swl
    Lsp = secondary_swl
    Ltotp = Lpp + Lsp
    Qb = binary_mean_distance * (1 + binary_eccentricity)
    mu = secondary_star_mass_ratio

    if planetary_semimajor_axis is None or max_planetary_eccentricity is None:
        planetary_semimajor_axis = calculate_single_star_habitable_orbital_threshold(Ltotp)
        max_planetary_eccentricity = calculate_forced_eccentricity_in_close_binary(
            planetary_semimajor_axis, binary_mean_distance, binary_eccentricity, mu)

    if max_planetary_eccentricity >= 1:
        return np.nan * planetary_semimajor_axis.units

    qp = planetary_semimajor_axis * (1 - max_planetary_eccentricity)
    Qp = planetary_semimajor_axis * (1 + max_planetary_eccentricity)

    if threshold_type == 'Inner':
        first_term = Lpp / (qp - mu * Qb) ** 2
        second_term = Lsp / (qp + (1 - mu) * Qb) ** 2
        phl = (first_term + second_term) * sqrt(Ltotp)
    elif threshold_type == 'Outer':
        first_term = Lpp / (Qp + mu * Qb) ** 2
        second_term = Lsp / (Qp - (1 - mu) * Qb) ** 2
        phl = (first_term + second_term) * sqrt(Ltotp)
    else:
        first_term = Lpp / (qp - mu * Qb) ** 2
        second_term = Lsp / (qp + (1 - mu) * Qb) ** 2
        phl_inner = (first_term + second_term) * sqrt(Ltotp)

        first_term = Lpp / (Qp + mu * Qb) ** 2
        second_term = Lsp / (Qp - (1 - mu) * Qb) ** 2
        phl_outer = (first_term + second_term) * sqrt(Ltotp)

        phl = (phl_inner + phl_outer) / 2

    return phl


def calculate_stype_average_habitable_limit(star_swl: Q_, star_companion_swl: Q_, binary_mean_distance: Q_,
                                            binary_eccentricity: float,
                                            planetary_semimajor_axis: Q_ = None,
                                            max_planetary_eccentricity: Q_ = None) -> Q_:
    """
    Average habitability zone is the zone where long-term planetary insolation average must not exceed habitable limits,
     high climate inertia. It depends on the dynamically oscillating eccentricity over the course of many years, due to
     the binary systems non-spherical graviational pull. High climate inertia means that the climate of the planet takes
     a long time to reflect the eccentricity changes to its average temperature etc.
    Equations 33 from Handbook of Exoplanets, Chapter 141
    """
    Ls = star_swl
    Lsc = star_companion_swl
    rbmean = binary_mean_distance * (1 - binary_eccentricity ** 2) ** 0.25

    if planetary_semimajor_axis is None or max_planetary_eccentricity is None:
        planetary_semimajor_axis = calculate_single_star_habitable_orbital_threshold(Ls)
        max_planetary_eccentricity = calculate_forced_eccentricity_in_wide_binary(
            planetary_semimajor_axis, binary_mean_distance, binary_eccentricity)

    if max_planetary_eccentricity >= 1:
        return np.nan * planetary_semimajor_axis.units
    epmean2 = max_planetary_eccentricity ** 2

    rpmean = planetary_semimajor_axis * (1 - epmean2) ** 0.25

    first_term = Ls / (rpmean * (1 - epmean2) ** 0.25)
    second_term = sqrt(Ls) * Lsc / (rbmean ** 2 - rpmean ** 2)

    ahl = first_term + second_term
    return ahl


def calculate_ptype_average_habitable_limit(primary_swl: Q_, secondary_swl: Q_, binary_mean_distance: Q_,
                                            binary_eccentricity: float, secondary_star_mass_ratio: float,
                                            planetary_semimajor_axis: Q_ = None,
                                            max_planetary_eccentricity: Q_ = None) -> Q_:
    """
    Average habitability zone is the zone where long-term planetary insolation average must not exceed habitable limits,
     high climate inertia. It depends on the dynamically oscillating eccentricity over the course of many years, due to
     the binary systems non-spherical graviational pull. High climate inertia means that the climate of the planet takes
     a long time to reflect the eccentricity changes to its average temperature etc.
    Equations 39 from Handbook of Exoplanets, Chapter 141
    """
    Lpp = primary_swl
    Lsp = secondary_swl
    Ltotp = Lpp + Lsp
    mu = secondary_star_mass_ratio
    if Lpp < Lsp:
        Lpp = secondary_swl
        Lsp = primary_swl
        mu = 1 - secondary_star_mass_ratio

    rbmean = binary_mean_distance * (1 - binary_eccentricity ** 2) ** 0.25
    rbmeanprimary = mu * rbmean
    rbmeansecondary = (1 - mu) * rbmean

    if planetary_semimajor_axis is None or max_planetary_eccentricity is None:
        planetary_semimajor_axis = calculate_single_star_habitable_orbital_threshold(Ltotp)
        max_planetary_eccentricity = calculate_forced_eccentricity_in_close_binary(
            planetary_semimajor_axis, binary_mean_distance, binary_eccentricity, mu)

    if max_planetary_eccentricity >= 1:
        return np.nan * planetary_semimajor_axis.units
    epmean2 = max_planetary_eccentricity ** 2
    rpmean = planetary_semimajor_axis * (1 - epmean2) ** 0.25

    first_term = Lpp / (rpmean ** 2 - rbmeanprimary ** 2)
    second_term = Lsp / (rpmean ** 2 - rbmeansecondary ** 2)

    ahl = (first_term + second_term) * sqrt(Ltotp)
    return ahl


def calculate_tidal_heating(parent_mass: Q_, distance: Q_, eccentricity: float, radius: Q_) -> Q_:
    """
    Tidal heating occures from the oscillation of the shape of an object due to its elliptic orbit around its parent.

    More info on: https://academic.oup.com/mnras/article/391/1/237/1121115
                  https://www.liebertpub.com/doi/10.1089/ast.2015.1325
    To get modulating Qp, find https://iopscience.iop.org/article/10.1088/0004-637X/789/1/30/pdf, table 2, pg. 22
    """
    Qp = 500
    tidal_heating_flux = 63 / 16 / np.pi * gravitational_constant ** 1.5 * parent_mass.to('kg') ** 2.5 * \
        radius.to('m') ** 3 * eccentricity ** 2 / Qp / distance.to('m') ** 7.5

    return tidal_heating_flux.to('watt/m**2')


def calculate_primordial_heating_rocky_planets(age: Q_, mass: Q_, surface_area: Q_) -> Q_:
    """
    Primordial heating is heating due to initial formation. It is stored in the planet as an internal heating source
    that slowly (or quickly) escapes, depending on the planet materials.

    More info on: https://www.sciencedirect.com/science/article/abs/pii/S003206331300161X (Eq. 2.1) * mass / surf_area
    """
    Ho = 1.2E-11 * ureg.watt / ureg.kg  # we changed from 2 to 1.2, to match earth's total  heating
    decay = 0.3391 / ureg.gigayear
    primordial_heating_flux = np.exp(- age * decay) * Ho * mass / surface_area
    return primordial_heating_flux.to('watt/m**2')


def calculate_radiogenic_heating(age: Q_, mass: Q_, surface_area: Q_, chemical_composition: dict,
                                 radiogenic_abundance: float = 1) -> Q_:

    """
    Radiogenic heating is the heating produced by slowly radiative isotopes in a planets mantle.
    Since we only care for the mantle, we take into account the planetary composition (we assume that only the rocky
    part of the planet is contributing to radiogenic heating).
    This model assumes the same percentages of radioactive isotopes as earth.

    More info on: https://www.sciencedirect.com/science/article/abs/pii/S0019103514004473?via%3Dihub#b0415%20
                  table 1 for heat production and half-times, table 2 for relative abundance
                  They have a discussion on age of galaxy and isotope abuntance, but I did not account for that.
    """

    heat_production_k40 = 2.92E-5 * ureg.watt / ureg.kg
    abundance_k40 = 4.64E-7
    lifetime_k40 = 1.25 / np.log(2) * ureg.gigayear
    k40_heating = heat_production_k40 * abundance_k40 * np.exp(- age / lifetime_k40)

    heat_production_Th232 = 2.64E-5 * ureg.watt / ureg.kg
    abundance_Th232 = 1.55E-7
    lifetime_Th232 = 14 / np.log(2) * ureg.gigayear
    Th232_heating = heat_production_Th232 * abundance_Th232 * np.exp(- age / lifetime_Th232)

    heat_production_U235 = 5.69E-4 * ureg.watt / ureg.kg
    abundance_U235 = 1.64E-8
    lifetime_U235 = 0.704 / np.log(2) * ureg.gigayear
    U235_heating = heat_production_U235 * abundance_U235 * np.exp(- age / lifetime_U235)

    heat_production_U238 = 9.46E-5 * ureg.watt / ureg.kg
    abundance_U238 = 6.24E-8
    lifetime_U238 = 4.47 / np.log(2) * ureg.gigayear
    U238_heating = heat_production_U238 * abundance_U238 * np.exp(- age / lifetime_U238)

    total_heating = (k40_heating + Th232_heating + U235_heating + U238_heating) * radiogenic_abundance
    rocky_mantle_fraction = chemical_composition['MgSiO3']
    radiogenic_heating_flux = mass * rocky_mantle_fraction * total_heating / surface_area

    return radiogenic_heating_flux.to('watt/m**2')

