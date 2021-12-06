import numpy as np

from stellar_system_creator.astrothings.units import ureg, Q_, gravitational_constant


def calculate_rough_inner_orbit_limit(mass: Q_) -> Q_:
    """
    The rough inner orbit limit is a rough estimate of how far away a child object can orbit around the parent object.
     It only depends on the mass of the parent.
    A better estimate of this limit is given by the Roche limit, which requires both the parent and the child physical
     characteristics.

    This equation was taken from artifexian's youtube channel "How to Create a Classical Planetary System"
     https://www.youtube.com/watch?v=J5xU-8Kb63Y&list=PLduA6tsl3gygXJbq_iQ_5h2yri4WL6zsS&index=12
     """
    return 0.1 * mass.to('solar_mass').magnitude * ureg.au


def calculate_rough_outer_orbit_limit(mass: Q_) -> Q_:
    """
    The rough outer orbit limit is a rough estimate of how far away a child object can orbit around the parent object.
     It only depends on the mass of the parent.
    A better estimate of this limit is given by the Hill Sphere, which requires both the parent and the child physical
     characteristics.

    This equation was taken from artifexian's youtube channel "How to Create a Classical Planetary System"
     https://www.youtube.com/watch?v=J5xU-8Kb63Y&list=PLduA6tsl3gygXJbq_iQ_5h2yri4WL6zsS&index=12
     """
    return 40 * mass.to('solar_mass').magnitude * ureg.au


def calculate_frost_line(luminosity: Q_) -> Q_:
    """
    The frost line is the distance at which volatile compounds (water, carbon oxide, ammonia, etc) condense enough to
     become solid ice. This distance depends on the luminosity these compounds receive, and on the type of compound.
     Here, we have an estimate of the water frost line for well developed solar systems (not during their birth).

    More information can be found on here: https://en.wikipedia.org/wiki/Frost_line_(astrophysics)

    This equation was taken from artifexian's youtube channel "How to Create a Classical Planetary System"
     https://www.youtube.com/watch?v=J5xU-8Kb63Y&list=PLduA6tsl3gygXJbq_iQ_5h2yri4WL6zsS&index=12
    """
    return 4.85 * np.sqrt(luminosity.to('solar_luminosity').magnitude) * ureg.au


def calculate_approximate_inner_orbit_limit(parent_radius: Q_) -> Q_:
    """
    In this approach we will use the roche limit and we will assume the worst case scenario, where the density of the
    parent is 10 times bigger than the density of the child to be.

    More info on: https://en.wikipedia.org/wiki/Roche_limit
    """
    parent_child_density_ratio = 10
    return (2.44 * parent_radius * parent_child_density_ratio ** (1 / 3)).to_reduced_units()


def calculate_roche_limit(child_stellar_body, parent_stellar_body) -> Q_:
    """
    Roche limit is the minimum distance a child object can orbit a parent object, before the child object breaks apart.

    More info on: https://en.wikipedia.org/wiki/Roche_limit
    """
    if "radius" in parent_stellar_body.__dict__.keys():
        parent_child_density_ratio = (parent_stellar_body.density / child_stellar_body.density).to_reduced_units().m
        return 2.44 * parent_stellar_body.radius * parent_child_density_ratio ** (1 / 3)
    else:
        parent_child_mass_ratio = (parent_stellar_body.mass / child_stellar_body.mass).to_reduced_units().m
        return 2.44 * child_stellar_body.radius * parent_child_mass_ratio ** (1 / 3)


def calculate_hill_sphere(child_stellar_body, parent_stellar_body) -> Q_:
    """
    Hill sphere is the maximum distance a child body can affect even smaller body, because of the presence of a bigger
     body around. For example the moon is within the hill sphere of earth, and the hill sphere of earth is determined
     by earth and the sun.

    More info on: https://en.wikipedia.org/wiki/Hill_sphere
    """
    child_parent_mass_ratio = (child_stellar_body.mass / parent_stellar_body.mass).to_reduced_units().m
    if 'semi_major_axis' in child_stellar_body.__dict__:
        return child_stellar_body.semi_major_axis * (1 - child_stellar_body.orbital_eccentricity) \
                                                  * (child_parent_mass_ratio / 3) ** (1 / 3)
    else:
        return child_stellar_body.parent.mean_distance * (1 - child_stellar_body.parent.eccentricity) \
               * (child_parent_mass_ratio / 3) ** (1 / 3)


def calculate_roche_lobe(stellar_mass, companion_mass, mean_distance: Q_) -> Q_:
    """
    Roche sphere (not to be confused with roche limit) is the region around a star in a binary system within which
     orbiting material is gravitationally bound to that star.

    More info on: https://en.wikipedia.org/wiki/Roche_lobe
    """
    q: Q_ = stellar_mass / companion_mass
    q = q.to_reduced_units().m
    numerator = 0.49 * q ** (2/3)
    denominator = 0.6 * q ** (2/3) + np.log(1 + q ** (1/3))
    return numerator / denominator * mean_distance


def calculate_three_body_lagrange_point_smallest_body_mass_limit(m1: Q_, m2: Q_) -> Q_:

    """https://hal.archives-ouvertes.fr/hal-00552502/document"""
    # TODO: get it right
    # probably wrong implementation
    # https://www.wolframalpha.com/input/?i=solve+%28m1+%2B+m2+%2B+m3%29**2%2F%28m1*m2%2Bm1*m3%2Bm2*m3%29+%3E27%2C+m1%3E0%2C+m2%3E0+m3
    element1 = 3 * np.sqrt(3) * np.sqrt(23 * m1 ** 2 + 50 * m1 * m2 + 23 * m2 ** 2)
    element2 = 25 * (m1 + m2)
    return (-element1 + element2).to_reduced_units() / 2


# def calculate_earth_equivalent_orbit(luminosity: Q_) -> Q_:
#     """
#     The habitable zone (HZ) is the stellar zone in which life is supported. This is a very complicated designation and.
#      there are still many questions around it. The most broadly used limits were give by Kasting et al., 1993,
#      https://doi.org/10.1006/icar.1993.1010. These CONSERVATIVE limits are only limited to water-based life.
#      Life based on other temperatures and volatile compounts (e.g. ammonia), will have a different (HZ)!
#
#     More info on: https://en.wikipedia.org/wiki/Circumstellar_habitable_zone.
#      """
#     return np.sqrt(luminosity.to('solar_luminosity').magnitude) * ureg.au


# def calculate_habitable_zone_min(luminosity: Q_) -> Q_:
#     """
#     The habitable zone (HZ) is the stellar zone in which life is supported. This is a very complicated designation and.
#      there are still many questions around it. The most broadly used limits were give by Kasting et al., 1993,
#      https://doi.org/10.1006/icar.1993.1010. These CONSERVATIVE limits are only limited to water-based life.
#      Life based on other temperatures and volatile compounts (e.g. ammonia), will have a different (HZ)!
#
#     More info on: https://en.wikipedia.org/wiki/Circumstellar_habitable_zone.
#      """
#     return 0.95 * np.sqrt(luminosity.to('solar_luminosity').magnitude) * ureg.au
#
#
# def calculate_habitable_zone_max(luminosity: Q_) -> Q_:
#     """
#     The habitable zone (HZ) is the stellar zone in which life is supported. This is a very complicated designation and.
#      there are still many questions around it. The most broadly used limits were give by Kasting et al., 1993,
#      https://doi.org/10.1006/icar.1993.1010. These CONSERVATIVE limits are only limited to water-based life.
#      Life based on other temperatures and volatile compounts (e.g. ammonia), will have a different (HZ)!
#
#     More info on: https://en.wikipedia.org/wiki/Circumstellar_habitable_zone.
#      """
#     return 1.37 * np.sqrt(luminosity.to('solar_luminosity').magnitude) * ureg.au

def calculate_elliptic_orbit_effect_for_mean_flux(eccentricity: float):
    """
    When trying to calculate the average incident flux, one needs to account for the eccentricity's effect on the orbit.
    source: https://arxiv.org/pdf/1702.07314.pdf, equation (17)
    """
    return (1 - eccentricity ** 2) ** 0.25


def calculate_elliptic_orbit_effect_for_mean_temperature(eccentricity: float):
    """
    When looking into the average equilibrium temperature, one needs to acount for a different effective orbit
    source: https://arxiv.org/pdf/1702.07314.pdf, equation (18, 19)
    """
    # return (2 * np.sqrt(1 + eccentricity) * ellipe(np.sqrt(2 * eccentricity / (1 + eccentricity))) / np.pi) ** (-2)
    # the above doesn't work. I suspect I used the wrong elliptic function, so I will use the aprox. instead
    return 1 + 0.125 * eccentricity ** 2 + 21 / 512 * eccentricity ** 4


def calculate_average_insolation_threshold(insolation_threshold: Q_, potential_orbit_eccentricity: float = 0) -> Q_:
    return insolation_threshold * calculate_elliptic_orbit_effect_for_mean_temperature(
        potential_orbit_eccentricity) ** 2


def calculate_spectrally_weighted_luminosity(luminosity: Q_, insolation_threshold: Q_,
                                             potential_orbit_eccentricity: float = 0) -> Q_:
    """
    The habitable zone (HZ) is the stellar zone in which life is supported. This is a very complicated designation and
     there are still many questions around it.
    Insolation threshold is in units of solar flux, and represents different limits of solar flux for specific effects
     on the planetary climate, i.e. runaway greenhouse effect, maximum greenhouse effect etc.
    Here we calculate HZ regions via insolation theresholds (Kopparapu et al. 2014).
    For the entire analysis of habitable zones, we use the reference "Handbook of Exoplanets (2018)", chapter 141,
     "Habitability of Planets in Binary Star Systems", written by Siegfried Eggl
    The average insolation is taken by Kopparapu 2013 E.q 4 (effective insolation over a slightly eliptic orbit)
    """
    average_insolation = calculate_average_insolation_threshold(insolation_threshold,
                                                                potential_orbit_eccentricity).to('solar_flux').m
    return luminosity.to('solar_luminosity').m / average_insolation * ureg.au**2


def calculate_binary_forbidden_zone_minimum(binary_minimum_distance: Q_) -> Q_:
    """
    This was taken by artifexian's youtube channel.
    It seems like it is a simplified version of the calculate_close_binary_critical_orbit function,
    where the mass is not significantly contributing for masses 0.6 to 1.4 solar masses, as artifexian suggests
    on his website.
    This value is remarkably close to what the actual function is.
    """
    return binary_minimum_distance / 3


def calculate_binary_forbidden_zone_maximum(binary_maximum_distance: Q_) -> Q_:
    """
    This was taken by artifexian's youtube channel.
    It seems like it is a simplified version of the calculate_wide_binary_critical_orbit function,
    where the mass is not significantly contributing for masses 0.6 to 1.4 solar masses, as artifexian suggests
    on his website.
    This value is remarkably close to what the actual function is.
    """
    return binary_maximum_distance * 3


def calculate_close_binary_critical_orbit(secondary_to_binary_mass_ratio: Q_, binary_mean_distance: Q_,
                                          binary_eccentricity: float) -> Q_:
    """
    More info on: https://iopscience.iop.org/article/10.1086/300695 (eq. 3)
    and https://arxiv.org/pdf/2108.07815.pdf
    """
    mu = secondary_to_binary_mass_ratio
    d = binary_mean_distance
    e = binary_eccentricity

    if mu > 0.5:
        mu = 1 - mu
        print('Secondary body has higher mass than primary, which it should not.')

    normalized_critical_distance = 1.6 + \
                                   5.1 * e - 2.22*e**2 + \
                                   4.12 * mu - 5.09*mu**2 + \
                                   4.61 * e**2 * mu**2 - 4.27*e*mu

    return normalized_critical_distance * d


def calculate_wide_binary_critical_orbit(star_to_binary_mass_ratio: float, binary_mean_distance: Q_,
                                         binary_eccentricity: float) -> Q_:
    """
    More info on: https://iopscience.iop.org/article/10.1086/300695 (eq. 1)
    and https://arxiv.org/pdf/2108.07815.pdf
    """
    mu = 1 - star_to_binary_mass_ratio  # we need the mass ratio of the companion star for this limit.
    d = binary_mean_distance
    e = binary_eccentricity

    normalized_critical_distance = 0.464 - 0.38*mu - 0.631*e + 0.586*mu*e + 0.15*e**2 - 0.198*mu*e**2

    return normalized_critical_distance * d


def calculate_forced_eccentricity_in_wide_binary(semimajor_axis: Q_, binary_mean_distance: Q_,
                                                 binary_eccentricity: float) -> float:
    """
    When a planet is orbiting a binary system, the gravitational forces are not symmetric in the planetary orbit.
    These forces push the planet to an oscillating elliptic orbit. Forced eccentricity is the eccentricity the binary
     favors, same way a single star "favors" circular orbits.
    Eq. 23, "Handbook of Exoplanets (2018)", chapter 141, "Habitability of Planets in Binary Star Systems",
     written by Siegfried Eggl
    """
    fecc: Q_ = 5 / 4 * semimajor_axis / binary_mean_distance * binary_eccentricity ** 2 / (1 - binary_eccentricity ** 2)
    return fecc.to_reduced_units().m


def calculate_forced_eccentricity_in_close_binary(semimajor_axis: Q_, binary_mean_distance: Q_,
                                                  binary_eccentricity: float,
                                                  secondary_star_mass_ratio: float) -> float:
    """
    When a planet is orbiting a binary system, the gravitational forces are not symmetric in the planetary orbit.
    These forces push the planet to an oscillating elliptic orbit. Forced eccentricity is the eccentricity the binary
     favors, same way a single star "favors" circular orbits.
    Eq. 28, "Handbook of Exoplanets (2018)", chapter 141, "Habitability of Planets in Binary Star Systems",
     written by Siegfried Eggl
    """
    if secondary_star_mass_ratio > 0.5:
        secondary_star_mass_ratio = 1 - secondary_star_mass_ratio  # should be given in terms of the less massive star.
    distance_term = 5 / 4 * binary_mean_distance / semimajor_axis * (1 - 2 * secondary_star_mass_ratio)
    becc_term = (4 * binary_eccentricity + 3 * binary_eccentricity ** 3)
    becc_term = becc_term/(4 + 6 * binary_eccentricity ** 2)
    fecc: Q_ = distance_term * becc_term
    return fecc.to_reduced_units().m


def calculate_eccentricity_oscillation_frequency_in_wide_binary(semimajor_axis: Q_, binary_mean_distance: Q_,
                                                                binary_eccentricity: float,
                                                                parent_mass: Q_, parent_companion_mass: Q_,
                                                                object_mass: Q_) -> float:
    """
    When a planet is orbiting a binary system, the gravitational forces are not symmetric in the planetary orbit.
    These forces push the planet to an oscillating elliptic orbit.
    Eq. 23, "Handbook of Exoplanets (2018)", chapter 141, "Habitability of Planets in Binary Star Systems",
     written by Siegfried Eggl
    """
    orbital_frequency = 1 / calculate_orbital_period(semimajor_axis, parent_mass, object_mass)
    mass_ratio = parent_companion_mass / parent_mass
    distance_ratio = semimajor_axis / binary_mean_distance
    g: Q_ = 3 / 4 * mass_ratio * distance_ratio ** 3 * orbital_frequency / (1 - binary_eccentricity ** 2) ** 1.5
    return g.to_reduced_units().m


def calculate_eccentricity_oscillation_frequency_in_close_binary(semimajor_axis: Q_, binary_mean_distance: Q_,
                                                                 binary_eccentricity: float,
                                                                 primary_mass: Q_, secondary_mass: Q_,
                                                                 object_mass: Q_) -> float:
    """
    When a planet is orbiting a binary system, the gravitational forces are not symmetric in the planetary orbit.
    These forces push the planet to an oscillating elliptic orbit.
    Eq. 28, "Handbook of Exoplanets (2018)", chapter 141, "Habitability of Planets in Binary Star Systems",
     written by Siegfried Eggl
    """
    total_mass = primary_mass + secondary_mass
    planetary_orbital_frequency = 1 / calculate_orbital_period(semimajor_axis, total_mass, object_mass)
    binary_orbital_frequency = 1 / calculate_orbital_period(binary_mean_distance, primary_mass, secondary_mass)
    secondary_mass_ratio = secondary_mass / total_mass
    primary_mass_ratio = primary_mass / total_mass

    orbital_period_term = binary_orbital_frequency ** 2 / planetary_orbital_frequency
    mass_ratio_term = primary_mass_ratio * secondary_mass_ratio
    distance_term = (binary_mean_distance / semimajor_axis) ** 5
    eccentricity_term = 1 + 1.5 * binary_eccentricity ** 2

    g: Q_ = 3 / 4 * orbital_period_term * distance_term * mass_ratio_term * eccentricity_term
    return g.to_reduced_units().m


def calculate_incident_flux(luminosity: Q_, orbital_distance: Q_, eccentricity: float = 0, ecc_correction='flux'):
    """
    More info on: http://www.astronomy.ohio-state.edu/~thompson/161/lecture_24_web.pdf
    """
    if ecc_correction == 'flux':
        ecc_cor_func = calculate_elliptic_orbit_effect_for_mean_flux
    else:
        ecc_cor_func = calculate_elliptic_orbit_effect_for_mean_temperature

    effective_orbital_distance = orbital_distance * ecc_cor_func(eccentricity)
    return luminosity / (4 * np.pi * effective_orbital_distance ** 2)


def calculate_part_incident_flux_in_close_binary(part_luminosity: Q_, part_to_binary_mass_ratio, orbital_distance: Q_,
                                                 binary_distance: Q_, eccentricity: float = 0,
                                                 binary_eccentricity: float = 0, ecc_correction='flux'):
    """
    More info on: http://www.astronomy.ohio-state.edu/~thompson/161/lecture_24_web.pdf
    """
    if ecc_correction == 'flux':
        ecc_cor_func = calculate_elliptic_orbit_effect_for_mean_flux
    else:
        ecc_cor_func = calculate_elliptic_orbit_effect_for_mean_temperature

    effective_orbital_distance = orbital_distance * ecc_cor_func(eccentricity)
    effective_binary_distance = part_to_binary_mass_ratio * binary_distance * ecc_cor_func(binary_eccentricity)
    effective_distance = np.sqrt(effective_orbital_distance ** 2 - effective_binary_distance ** 2)
    return part_luminosity / (4 * np.pi * effective_distance ** 2)


def calculate_companion_incident_flux_in_wide_binary(companion_luminosity: Q_, orbital_distance: Q_,
                                                     binary_distance: Q_, eccentricity: float = 0,
                                                     binary_eccentricity: float = 0, ecc_correction='flux'):
    """
    More info on: http://www.astronomy.ohio-state.edu/~thompson/161/lecture_24_web.pdf
    """
    if ecc_correction == 'flux':
        ecc_cor_func = calculate_elliptic_orbit_effect_for_mean_flux
    else:
        ecc_cor_func = calculate_elliptic_orbit_effect_for_mean_temperature

    effective_orbital_distance = orbital_distance * ecc_cor_func(eccentricity)
    effective_binary_distance = binary_distance * ecc_cor_func(binary_eccentricity)
    effective_distance = np.sqrt(effective_binary_distance ** 2 - effective_orbital_distance ** 2)
    return companion_luminosity / (4 * np.pi * effective_distance ** 2)


def calculate_semi_minor_axis(semi_major_axis: Q_, eccentricity) -> Q_:
    """
    Orbit is the gravitationally curved trajectory of an object, such as the trajectory of a planet around a star or
     a natural satellite (moon) around a planet. Usual stable orbits of planets and moons are circular or elliptic.
     They are described by the semi-major and semi-minor axes, the largest and smallest distance from the center of
     mass of two objects. In literature, we usually describe an object by its semi-major axis and eccentricity of the
     orbit. From these two we can calculate the semi-minor axis.

    More information on: https://en.wikipedia.org/wiki/Orbit, https://en.wikipedia.org/wiki/Orbital_mechanics,
     https://en.wikipedia.org/wiki/Semi-major_and_semi-minor_axes
    """
    return semi_major_axis * np.sqrt(1 - eccentricity ** 2)


def calculate_periapsis(semi_major_axis: Q_, eccentricity) -> Q_:
    """
    Periapsis is the largest distance between two objects in orbit with each other.

    More info on: https://en.wikipedia.org/wiki/Apsis
    """
    return semi_major_axis * (1 - eccentricity)


def calculate_apoapsis(semi_major_axis: Q_, eccentricity) -> Q_:
    """
    Periapsis is the smallest distance between two objects in orbit with each other.

    More info on: https://en.wikipedia.org/wiki/Apsis
    """
    return semi_major_axis * (1 + eccentricity)


def calculate_orbital_period(orbit_semi_major_axis: Q_, primary_mass: Q_, secondary_mass: Q_) -> Q_:
    """
    Orbital period is the amount of time it takes for one object to complete one full turn around another.

    More info on: https://en.wikipedia.org/wiki/Orbital_period
    """
    total_mass: Q_ = primary_mass + secondary_mass
    return np.sqrt(orbit_semi_major_axis.to('au').magnitude ** 3 / total_mass.to('solar_mass').magnitude) * ureg.years


def calculate_orbital_velocity(semi_major_axis: Q_, parent_mass: Q_) -> Q_:
    """
    Orbital speed is the speed at which a (child) object travels around the center of mass of the two objects
     (primary-secondary, or parent-child) In this case we assume that the primary body is much more massive than the
     secondary one.

    More info on: https://en.wikipedia.org/wiki/Orbital_speed
    """
    return np.sqrt(parent_mass.to('solar_mass').magnitude / semi_major_axis.to('au').magnitude) * ureg.vorb_e


def calculate_surface_gravity(object_mass: Q_, object_radius: Q_) -> Q_:
    """
    Surface gravity is the gravitational acceleration that a small object experiences at the surface of a massive object
    (e.g. a planet or a satellite).

    More info on: https://en.wikipedia.org/wiki/Surface_gravity
    """
    return object_mass.to('earth_mass').magnitude / object_radius.to('earth_radius').magnitude ** 2 * ureg.g_e


def calculate_planet_escape_velocity(object_mass: Q_, object_radius: Q_) -> Q_:
    """
    Escape velocity is the initial velocity required for an object, starting from the surface of a (e.g.) planet to
     escape its gravitational pull.

    More info on : https://en.wikipedia.org/wiki/Escape_velocity
    """
    return np.sqrt(object_mass.to('earth_mass').magnitude / object_radius.to('earth_radius').magnitude) * ureg.vesc_e


def calculate_surface_pressure(object_mass: Q_, object_radius: Q_) -> Q_:
    """
    Surface pressure is the pressure on the surface of the planet if the planet is a solid planet

    Source: Kopparapu et al. 2014, Eq. 2
    More info on: https://en.wikipedia.org/wiki/Atmospheric_pressure
    """
    return object_mass.to('earth_mass').magnitude ** 2 / object_radius.to('earth_radius').magnitude ** 4 * ureg.atm


def calculate_circumference(radius: Q_) -> Q_:
    """
    The length of a full turn around a sphere
    """
    return 2 * np.pi * radius


def calculate_surface_area(radius: Q_) -> Q_:
    """
    The surface area of a sphere
    """
    return 4 * np.pi * radius ** 2


def calculate_volume(radius: Q_) -> Q_:
    """
    The volume of a sphere
    """
    return 4 * np.pi * radius ** 3 / 3


def calculate_density(mass: Q_, volume: Q_) -> Q_:
    """
    The density of an object
    """
    return (mass / volume).to('g/cm^3')


def calculate_distance_to_barycenter(mass: Q_, total_distance: Q_, total_mass: Q_) -> Q_:
    """
    Barycenter is the center of mass between (in this case) two bodies. The barycenter is closer to the more massive
     object.

    More info on: https://en.wikipedia.org/wiki/Barycenter
    """
    return (total_distance * mass / total_mass).to_reduced_units()


def calculate_minimum_distance_to_barycenter(eccentricity: float, distance_to_barycenter: Q_) -> Q_:
    """
    Barycenter is the center of mass between (in this case) two bodies. When the bodies are in an elliptical orbit,
     their distance varies between them. We can easily calculate the minimum and maximum of the distance from the
     barycenter, using the eccentricity of each orbit.

    More info on: https://en.wikipedia.org/wiki/Barycenter
    """
    return (1 - eccentricity) * distance_to_barycenter


def calculate_maximum_distance_to_barycenter(eccentricity: float, distance_to_barycenter: Q_) -> Q_:
    """
    Barycenter is the center of mass between (in this case) two bodies. When the bodies are in an elliptical orbit,
     their distance varies between them. We can easily calculate the minimum and maximum of the distance from the
     barycenter, using the eccentricity of each orbit.

    More info on: https://en.wikipedia.org/wiki/Barycenter
    """
    return (1 + eccentricity) * distance_to_barycenter


def calculate_main_sequence_stellar_lifetime(mass: Q_, luminosity: Q_) -> Q_:
    """
    The life time of a star depends on many factors. For a main sequence star, we approximate the lifetime
     to be proportional to it's mass divided by its luminisity (while on main sequence).

    More info on: https://astronomy.swin.edu.au/cosmos/m/main+sequence+lifetime
    """
    return mass.to('solar_mass').magnitude / luminosity.to('solar_luminosity').magnitude * ureg.solar_lifetime


def calculate_temperature(luminosity: Q_, radius: Q_) -> Q_:
    """
    Stars can be thought as almost ideal black bodies that emit radiation and hence have a specific temperature
     associated with it.

     More info on: https://en.wikipedia.org/wiki/Black-body_radiation
    """
    return 5778 * (luminosity.to('solar_luminosity').m / radius.to('solar_radius').m ** 2) ** 0.25 * ureg.kelvin


def calculate_spectrum_peak_wavelength(temperature: Q_) -> Q_:
    """
    Stars can be thought as almost ideal black bodies that emit radiation and hence have a specific temperature
     associated with it. This temperature can be associated with a profile of emitted wavelengths, with 1 maximum.
    For our sun, the maximum is around 500 nm (green).

     More info on: https://en.wikipedia.org/wiki/Black-body_radiation
    """
    b = 2.897771955 * 10 ** 6 * ureg.nanometers * ureg.kelvin  # Wien displacement constant
    return (b / temperature).to_reduced_units()


def calculate_planetary_effective_surface_temperature(temp_avg_incident_flux: Q_, bond_albedo, normalized_greenhouse,
                                                      heat_distribution, emissivity) -> Q_:
    """
    source: https://arxiv.org/pdf/1702.07314.pdf, equation (6)
    Instead of using the incident luminosity from a single source, I added the fluxes as an average from all sources.
    """
    To = 278.5 * ureg.K  # Kelvin (earth's effective temperature with A=0)
    return To * (((1 - bond_albedo) * temp_avg_incident_flux.to('solar_flux').magnitude) / (
            heat_distribution * emissivity * (1 - normalized_greenhouse))) ** (1 / 4)


def calculate_tidal_locking_radius(parent_mass: Q_, age: Q_) -> Q_:
    """
    Tidal locking means that an orbiting object around a parent turns around itself at the same amount of time it turns
    around its parent.
    More info on: https://en.wikipedia.org/wiki/Tidal_locking#Timescale,
                  https://physics.stackexchange.com/questions/12541/tidal-lock-radius-in-habitable-zones
                  https://www.sciencedirect.com/science/article/abs/pii/S0019103583710109 -> Eq 10 in CGS units...
    """
    init_period = 13.5 * ureg.hours  # for sun
    locking_radius = 0.027 * (init_period.to('seconds') * age.to('seconds') / 100) ** (1 / 6) * \
        parent_mass.to('grams') ** (1 / 3) * ureg.cm / (ureg.gram * ureg.second) ** (1 / 3)
    return locking_radius.to('au')


def calculate_tide_height(companion_mass: Q_, target_mass: Q_, target_radius: Q_, distance: Q_) -> Q_:
    """
    When a celestial object rotates around another, they both exert forces on each other. When there is liquid mass
    on top of solid, the liquid rise and fall is give from equation 20 of reference.

    More info on: https://www.cambridge.org/resources/0521846560/7708_Tidal%20distortion.pdf
    """
    tide_height = 3 * target_radius ** 4 / distance ** 3 * companion_mass / target_mass
    return tide_height.to('meters')


def     calculate_angular_diameter(target_radius: Q_, distance: Q_) -> Q_:
    """
    Angular diameter is the size of a celestial body in the sky. The angular diameter of the sun and the moon are
    similar on earth, and approximatelly ~ 0.5 degrees

    More info on: https://en.wikipedia.org/wiki/Angular_diameter
    """
    angular_diameter = 2 * np.arcsin(target_radius/distance)
    return angular_diameter.to('degrees')


def calculate_distance_to_horizon(radius: Q_, height: Q_) -> Q_:
    """
    The distance to horizon is the furthest we can see from a certain height.

    More info on: https://en.wikipedia.org/wiki/Horizon
    """
    return np.sqrt(2 * radius * height + height ** 2)


def calculate_satellite_prograde_orbit_limit_factor(parent_eccentricity: float, child_ecentricity: float) -> float:
    """
    Within the Hill Sphere, satellites are even more limited on the maximum orbital distance they can be at.
    This is determined by the parent's eccentricity, their own eccentricity, and if the orbit is prograde or retrograde.

    More info on: https://www.aanda.org/articles/aa/pdf/2010/13/aa14955-10.pdf Eq. 3
    """
    return 0.4895 * (1 - 1.0305 * parent_eccentricity - 0.2738 * child_ecentricity)


def calculate_satellite_retrograde_orbit_limit_factor(parent_eccentricity: float, child_ecentricity: float) -> float:
    """
    Within the Hill Sphere, satellites are even more limited on the maximum orbital distance they can be at.
    This is determined by the parent's eccentricity, their own eccentricity, and if the orbit is prograde or retrograde.

    More info on: https://www.aanda.org/articles/aa/pdf/2010/13/aa14955-10.pdf Eq. 4
    """
    return 0.9309 * (1 - 1.0764 * parent_eccentricity - 0.9812 * child_ecentricity)


def calculate_max_satellite_mass(parent_mass: Q_, parent_radius: Q_, hill_sphere: Q_, orbit_type_limit_factor: float,
                                 satellite_lifetime: Q_) -> Q_:
    """
    Satellites around planets have a limited mass dependent on their parent.

    More info on: https://www.aanda.org/articles/aa/pdf/2010/13/aa14955-10.pdf Eq. 5
    """
    prefactor = 1000 / 0.51 / 39 / np.sqrt(gravitational_constant) * orbit_type_limit_factor ** 6.5

    upper_mass_limit = prefactor * hill_sphere.to('m') ** 6.5 \
        / satellite_lifetime.to('second') / parent_radius.to('m') ** 5 * np.sqrt(parent_mass.to('kg'))

    return upper_mass_limit.to(parent_mass.units)


def calculate_synodic_period(period1: Q_, periond2: Q_) -> Q_:
    """
    Synodic period is the period of time it takes for an object (sun) to appear at the same spot on another object's
    sky.

    More info on: https://en.wikipedia.org/wiki/Synodic_day
    """
    return abs(1 / (1 / period1 - 1 / periond2)).to('days')

