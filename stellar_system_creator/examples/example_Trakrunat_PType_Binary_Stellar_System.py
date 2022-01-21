
from stellar_system_creator.filing import save
from stellar_system_creator.stellar_system_elements.planetary_system import PlanetarySystem
from stellar_system_creator.stellar_system_elements.stellar_body import MainSequenceStar, Planet, AsteroidBelt, Trojan, \
    Satellite, TrojanSatellite, Ring
from stellar_system_creator.stellar_system_elements.binary_system import StellarBinary
from stellar_system_creator.astrothings.units import ureg
from stellar_system_creator.stellar_system_elements.stellar_system import StellarSystem, MultiStellarSystemSType

bhasdha_star = MainSequenceStar('Bhasdha', 1.04 * ureg.M_s, radius=0.964 * ureg.R_s,
                                luminosity=0.84 * ureg.L_s)
duheb_star = MainSequenceStar('Duheb', 0.362 * ureg.M_s, radius=0.351 * ureg.R_s,
                              luminosity=0.014 * ureg.L_s)

trakrunat_binaryP = StellarBinary('Trakrunat', bhasdha_star, duheb_star,
                                 mean_distance=0.0836 * ureg.au, eccentricity=0.0234)

planet1 = Planet('Ironball',  0.09 * ureg.M_e, semi_major_axis=0.29 * ureg.au, parent=trakrunat_binaryP,
                 composition='Ironworld67', orbital_eccentricity=0.013, albedo=0.09,
                 heat_distribution=0.5)
planet2 = Planet('Fireball', 0.32 * ureg.M_e, semi_major_axis=0.59 * ureg.au, parent=trakrunat_binaryP,
                 composition='Rockworld70', orbital_eccentricity=0.023, albedo=0.13,
                 normalized_greenhouse=0.9)
planet3 = Planet('Bacon Giant', 2.34 * ureg.M_j, semi_major_axis=0.93 * ureg.au, parent=trakrunat_binaryP,
                 composition='Gasgiant', albedo=0.57, normalized_greenhouse=0.2,
                 image_filename='../visualization/more_images/bacon-world.png')
planet4 = Planet('Waterball', 3.8 * ureg.M_e, semi_major_axis=1.58 * ureg.au, parent=trakrunat_binaryP,
                 composition='Waterworld25', albedo=0.32, normalized_greenhouse=0.2,
                 orbital_eccentricity=0.0113)
planet5 = Planet('Iceball', 19 * ureg.M_e, semi_major_axis=6.4 * ureg.au, parent=trakrunat_binaryP,
                 composition='Icegiant', orbital_eccentricity=0.006, albedo=0.31,
                 normalized_greenhouse=0.14, has_ring=True)
planet6 = Planet('Golden Strip', 35 * ureg.M_e, semi_major_axis=11.4 * ureg.au, parent=trakrunat_binaryP,
                 composition='Icegiant', orbital_eccentricity=0.004, albedo=0.36,
                 normalized_greenhouse=0.17,
                 image_filename='../visualization/more_images/gold-speckle-ice-giant.png')
planet7 = Planet('Gas Baby', 0.06 * ureg.M_e, semi_major_axis=23 * ureg.au, parent=trakrunat_binaryP,
                 composition='Waterworld45', orbital_eccentricity=0.22, albedo=0.43,
                 normalized_greenhouse=0.25,
                 image_filename='../visualization/more_images/dinosaur-egg-world.png')

# creating asteroid belts
asteroid_belt1 = AsteroidBelt('Floating potatoes', semi_major_axis=3.6 * ureg.au, parent=trakrunat_binaryP,
                              extend=1.4 * ureg.au, relative_count=1000)
asteroid_belt2 = AsteroidBelt('Whipped cream cloud', semi_major_axis=50 * ureg.au, parent=trakrunat_binaryP,
                              extend=20 * ureg.au, relative_count=1000)

# creating trojans around planet6
trojans61 = Trojan('Chased', planet6, 1, relative_count=300, mass=0.0001 * ureg.M_e)
trojans62 = TrojanSatellite('HunterRat', planet6, -1, 0.01 * ureg.M_e, composition='Waterworld75',
                            albedo=0.29, normalized_greenhouse=0.27)

# creating satellite for planet3
satellite31 = Satellite('Earth-2', 1.7 * ureg.M_e, parent=planet3, semi_major_axis=137 * ureg.R_j,
                        orbital_eccentricity=0.05, albedo=0.27, normalized_greenhouse=0.33,
                        composition='Rockworld70', orbit_type='Retrograde')
planet3.__post_init__()
satellite31.__post_init__()
# satellite2 = Satellite('moon2', 0.001 * ureg.M_e, parent=planet3, semi_major_axis=37E3 * ureg.km)
# satellite3 = Satellite('moon3', 0.00007 * ureg.M_e, parent=planet3, semi_major_axis=530E3 * ureg.km)


# creating satellite for planet4
satellite41 = Satellite('Dark Moon', 0.01 * ureg.M_e, parent=planet4, semi_major_axis=172 * ureg.R_e,
                        orbital_eccentricity=0.06, albedo=0.12,
                        composition='Waterworld25', image_filename='../visualization/more_images/dark-moon.png')

# creating satellite for planet5
satellite51 = Satellite('sat1', 0.000001 * ureg.M_e, parent=planet5, semi_major_axis=10E4 * ureg.km)
satellite52 = Satellite('sat2', 0.0001 * ureg.M_e, parent=planet5, semi_major_axis=17E4 * ureg.km)
satellite53 = Satellite('sat3', 0.0003 * ureg.M_e, parent=planet5, semi_major_axis=26E4 * ureg.km)
satellite54 = Satellite('sat4', 0.0000002 * ureg.M_e, parent=planet5, semi_major_axis=34E4 * ureg.km)
satellite55 = Satellite('sat5', 0.0007 * ureg.M_e, parent=planet5, semi_major_axis=110E4 * ureg.km)
satellite56 = Satellite('sat6', 0.000005 * ureg.M_e, parent=planet5, semi_major_axis=130E4 * ureg.km)

# modifyi planet5 ring colors
planet5.ring.change_ring_radial_gradient_colors([[0, 200/255, 220.5/255, 1, 0.8],
                                                [1, 100/255, 220.5/255, 1, 0]])

# creating planetary systems for visualization
ps1 = PlanetarySystem('Ironball System', planet1)
ps2 = PlanetarySystem('Fireball System', planet2)
ps3 = PlanetarySystem('Bacon Giant System', planet3, [satellite31])
ps4 = PlanetarySystem('Waterball System', planet4, [satellite41])
ps5 = PlanetarySystem('Iceball System', planet5, [satellite51, satellite52, satellite53, satellite54,
                                                  satellite55, satellite56])
ps6 = PlanetarySystem('Golden Strip System', planet6, [], [trojans61, trojans62])
ps7 = PlanetarySystem('Gas Baby System', planet7)

# creating stellar system for visualization
ss = StellarSystem('Trakrunat Stellar System', trakrunat_binaryP, [ps1, ps2, ps3, ps4, ps5, ps6, ps7],
                   [asteroid_belt1, asteroid_belt2])

save(ss, 'output_files/TrakrunatStellarSystem.ssc')
save(ps5, 'output_files/IceballSystem.ssc')

ss.draw_stellar_system()
ps5.draw_planetary_system()
ss.system_plot.save_image('output_files/TrakrunatStellarSystem.png')
ps5.system_plot.save_image('output_files/IceballPlanetarySystem.png')
