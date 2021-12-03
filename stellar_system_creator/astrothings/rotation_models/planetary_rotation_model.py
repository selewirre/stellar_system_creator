import numpy as np
from stellar_system_creator.astrothings.units import ureg, Q_


def calculate_planetary_rotation_speed(mass: Q_) -> Q_:
    """
    Source: https://iopscience.iop.org/article/10.3847/1538-4357/aabfbe
    Source is shit about the units and the actual relation. I extracted it myself.
    Earth doesnt fit because it exchanged angular momentum with the moon.
    Mercury doesnt fit because it is tidally locked
    Venus doesnt fit because it was probably slowed down by the atmosphere.
    """
    a = 0.5
    b = 1.09848667
    x = np.log(mass.to('M_j').m)
    return np.exp(x * a + b) * ureg.km/ureg.second * 4.25


def calculate_rotation_period_from_speed(speed: Q_, radius: Q_) -> Q_:
    """
    https://en.wikipedia.org/wiki/Rotational_speed
    """
    return (2 * np.pi * radius / speed).to_reduced_units()


def calculate_planetary_rotation_period(mass: Q_, radius: Q_) -> Q_:
    speed = calculate_planetary_rotation_speed(mass)
    period = calculate_rotation_period_from_speed(speed, radius)
    return period.to_reduced_units().to('days')
