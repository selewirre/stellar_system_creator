from stellar_system_creator.astrothings.units import ureg
from stellar_system_creator.stellar_system_elements.binary_system import StellarBinary
from stellar_system_creator.stellar_system_elements.stellar_body import MainSequenceStar, Planet, Satellite, Trojan,\
    AsteroidBelt, BlackHole
from stellar_system_creator.stellar_system_elements.planetary_system import PlanetarySystem
from stellar_system_creator.stellar_system_elements.stellar_system import StellarSystem
from stellar_system_creator.filing import save

# creating the stars
croomsk_star = MainSequenceStar('Croomsk', 0.8 * ureg.M_s)
autshogu = BlackHole("Auts'hogu", 4.2 * ureg.M_s)

viyodzorax = StellarBinary('Viyodzorax', autshogu, croomsk_star,
                           mean_distance=1.2 * ureg.au, eccentricity=0.534)


# creating planets with earth's unit reference
planet1 = Planet('planet1',  0.67 * ureg.M_j, semi_major_axis=50 * ureg.au, parent=viyodzorax,
                 composition='Gasgiant')
planet6 = Planet('planet6', 100 * ureg.M_e, semi_major_axis=7 * ureg.au, parent=viyodzorax,
                 composition='Icegiant')
planet7 = Planet('planet7', 0.1 * ureg.M_e, semi_major_axis=12.7 * ureg.au, parent=viyodzorax,
                 composition='Waterworld100')
planet8 = Planet('planet8', 0.0086 * ureg.M_e, semi_major_axis=22.7 * ureg.au, parent=viyodzorax,
                 composition='Waterworld100')

# creating trojans around planet1
trojans1 = Trojan('trojans1', planet1, 1, relative_count=60, composition='Rockworld70')
trojans2 = Trojan('trojans2', planet1, -1, relative_count=60, composition='Rockworld70')

# creating six satellites for planet6
satelliteJ1 = Satellite('sat1', 0.000001 * ureg.M_e, parent=planet1, semi_major_axis=10E4 * ureg.km,
                        composition='Rockworld70')
satelliteJ2 = Satellite('sat2', 0.0001 * ureg.M_e, parent=planet1, semi_major_axis=17E4 * ureg.km,
                        composition='Rockworld70')
satelliteJ3 = Satellite('sat3', 0.0003 * ureg.M_e, parent=planet1, semi_major_axis=26E4 * ureg.km,
                        composition='Rockworld70')
satelliteJ4 = Satellite('sat4', 0.0000002 * ureg.M_e, parent=planet1, semi_major_axis=34E4 * ureg.km,
                        composition='Rockworld70')
satelliteJ5 = Satellite('sat5', 0.0007 * ureg.M_e, parent=planet1, semi_major_axis=110E4 * ureg.km,
                        composition='Rockworld70')
satelliteJ6 = Satellite('sat6', 0.000005 * ureg.M_e, parent=planet1, semi_major_axis=130E4 * ureg.km,
                        composition='Rockworld70')

# creating planetary systems for visualization
ps1 = PlanetarySystem('ps1', planet1, [satelliteJ1, satelliteJ2, satelliteJ3, satelliteJ4, satelliteJ5, satelliteJ6],
                      [trojans1, trojans2])
ps6 = PlanetarySystem('ps6', planet6)
ps7 = PlanetarySystem('ps7', planet7)
ps8 = PlanetarySystem('ps8', planet8)

# creating stellar system for visualization
ss = StellarSystem('Viyodzorax Stellar System', viyodzorax, [ps1, ps6, ps7, ps8])

save(ss, 'output_files/ViyodzoraxStellarSystem.ssc')

ss.system_plot.want_tidal_locking_radius = False
ss.system_plot.want_habitable_zones_conservative = False
ss.system_plot.want_habitable_zones_extended = False
ss.system_plot.want_rock_line = False
ss.system_plot.want_water_frost_line = False
ss.draw_stellar_system()
ss.system_plot.save_image('output_files/ViyodzoraxStellarSystem.png')
