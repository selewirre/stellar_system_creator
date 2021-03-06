
from stellar_system_creator.filing import save_as_ssc_light, load_ssc_light
from stellar_system_creator.stellar_system_elements.planetary_system import PlanetarySystem
from stellar_system_creator.stellar_system_elements.stellar_body import MainSequenceStar, Planet, AsteroidBelt, Trojan, \
    Satellite, TrojanSatellite, Ring
from stellar_system_creator.stellar_system_elements.binary_system import StellarBinary
from stellar_system_creator.astrothings.units import ureg
from stellar_system_creator.stellar_system_elements.stellar_system import StellarSystem, MultiStellarSystemSType

viyodzorax_system: StellarSystem = load_ssc_light('output_files/ViyodzoraxStellarSystem.sscl')
trakrunat_system: StellarSystem = load_ssc_light('output_files/TrakrunatStellarSystem.sscl')

quezuliferh = StellarBinary('Quezuliferh', viyodzorax_system.parent, trakrunat_system.parent,
                            700 * ureg.au, 0.472)

quezuliferh.primary_body.__post_init__()
quezuliferh.secondary_body.__post_init__()
for child in quezuliferh.primary_body.children:
    child.__post_init__()
    for second_child in child.children:
        second_child.__post_init__()

for child in quezuliferh.secondary_body.children:
    child.__post_init__()
    for second_child in child.children:
        second_child.__post_init__()

quezuliferh_system = MultiStellarSystemSType('Quezuliferh Wide Binary System', quezuliferh,
                                             [viyodzorax_system, trakrunat_system])

save_as_ssc_light(quezuliferh_system, 'output_files/QuezuliferhWideBinarySystem.sscl')

# quezuliferh_system.system_plot.system_plots[0].system_rendering_preferences['want_tidal_locking_radius'] = False
# quezuliferh_system.system_plot.system_plots[1].system_rendering_preferences['want_habitable_zones_extended'] = True
# quezuliferh_system.system_plot.system_plots[1].system_rendering_preferences['want_habitable_zones_conservative'] = True
quezuliferh_system.draw_multi_stellar_system()
quezuliferh_system.system_plot.save_image('output_files/QuezuliferhWideBinarySystem.png')
