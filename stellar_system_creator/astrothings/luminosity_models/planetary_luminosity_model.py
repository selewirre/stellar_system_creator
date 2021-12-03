from stellar_system_creator.astrothings.units import Q_, stefan_boltzmann_constant

"""For not very cold Juvian planets?: source: https://www.google.com/url?sa=t&rct=j&q=&esrc=s&source=web&cd=&cad=rja&uact=8&ved=2ahUKEwj-y8vmwLfyAhXyNX0KHWrwDOMQFnoECAMQAQ&url=https%3A%2F%2Facademic.oup.com%2Fmnras%2Farticle-pdf%2F325%2F4%2F1497%2F3038268%2F325-4-1497.pdf&usg=AOvVaw2U-eVzTKbde6MtsPOmaOGf """
"""For rocky planets?: https://arxiv.org/pdf/1702.07314.pdf or
 https://iopscience.iop.org/article/10.3847/2041-8213/aa5f13 (same)"""
"""For albedo estimates: https://en.wikipedia.org/wiki/Albedo 
and https://www.ncbi.nlm.nih.gov/pmc/articles/PMC7580787/
Source: http://www.mit.edu/~iancross/8901_2019A/lec033.pdf,
    http://www.mit.edu/~iancross/8901_2019A/astrophysics_lecture_notes_2019_Crossfield.pdf
    https://scioly.org/wiki/index.php/Astronomy/Exoplanets
    """


def calculate_planetary_luminosity(surface_temperature: Q_, temp_avg_incident_flux: Q_, albedo: float,
                                   surface_area: Q_) -> Q_:
    """
    https://www.acs.org/content/acs/en/climatescience/atmosphericwarming/singlelayermodel.html
    https://en.wikipedia.org/wiki/Planetary_equilibrium_temperature

    """
    surface_temp_luminosity = stefan_boltzmann_constant * surface_area * surface_temperature ** 4
    reflected_luminosity = albedo * temp_avg_incident_flux * surface_area / 4

    total_luminosity: Q_ = surface_temp_luminosity.to_reduced_units() + reflected_luminosity.to_reduced_units()
    return total_luminosity.to('watt')
