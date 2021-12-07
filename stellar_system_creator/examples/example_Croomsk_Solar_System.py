from stellar_system_creator.astrothings.units import ureg
from stellar_system_creator.stellar_system_elements.stellar_body import MainSequenceStar, Planet, Satellite, Trojan, AsteroidBelt
from stellar_system_creator.stellar_system_elements.planetary_system import PlanetarySystem
from stellar_system_creator.stellar_system_elements.stellar_system import StellarSystem
from stellar_system_creator.filing import save
import timeit

# creating the star
croomsk_star = MainSequenceStar('CroomskStar', 0.8 * ureg.M_s)

# creating planets with earth's unit reference
planet1 = Planet('planet1',  0.67 * ureg.M_j, semi_major_axis=0.28 * ureg.au, parent=croomsk_star,
                 composition='Gasgiant')
planet2 = Planet('planet2', 0.038 * ureg.M_e, semi_major_axis=0.45 * ureg.au, parent=croomsk_star,
                 composition='Ironworld67')
planet3 = Planet('planet3', 1.32 * ureg.M_e, semi_major_axis=0.69 * ureg.au, parent=croomsk_star,
                 composition='Rockworld70')
planet4 = Planet('planet4', 2.24 * ureg.M_e, semi_major_axis=1.2 * ureg.au, parent=croomsk_star,
                 composition='Waterworld25')
planet5 = Planet('planet5', 30 * ureg.M_e, semi_major_axis=3.8 * ureg.au, parent=croomsk_star,
                 composition='Icegiant')
planet6 = Planet('planet6', 100 * ureg.M_e, semi_major_axis=7 * ureg.au, parent=croomsk_star,
                 composition='Icegiant')
planet7 = Planet('planet7', 0.1 * ureg.M_e, semi_major_axis=12.7 * ureg.au, parent=croomsk_star,
                 composition='Waterworld100')
planet8 = Planet('planet8', 0.0086 * ureg.M_e, semi_major_axis=22.7 * ureg.au, parent=croomsk_star,
                 composition='Waterworld100')

# creating asteroid belt at 7.8 AU
asteroid_belt = AsteroidBelt('asteroids1', semi_major_axis=2.15 * ureg.au, parent=croomsk_star, extend=1/3 * ureg.au)

# creating trojans around planet1
trojans1 = Trojan('trojans1', planet1, 1, relative_count=30, composition='Rockworld70')
trojans2 = Trojan('trojans2', planet1, -1, relative_count=30, composition='Rockworld70')

# creating three satelites for planet3
satellite1 = Satellite('moon1', 0.032 * ureg.M_e, parent=planet3, semi_major_axis=210E3 * ureg.km)
satellite2 = Satellite('moon2', 0.001 * ureg.M_e, parent=planet3, semi_major_axis=37E3 * ureg.km)
satellite3 = Satellite('moon3', 0.00007 * ureg.M_e, parent=planet3, semi_major_axis=530E3 * ureg.km)


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
ps2 = PlanetarySystem('ps2', planet2)
ps3 = PlanetarySystem('ps3', planet3, [satellite1, satellite2, satellite3])
ps4 = PlanetarySystem('ps4', planet4)
ps5 = PlanetarySystem('ps5', planet5)
ps6 = PlanetarySystem('ps6', planet6)
ps7 = PlanetarySystem('ps7', planet7)
ps8 = PlanetarySystem('ps8', planet8)

# creating stellar system for visualization
ss = StellarSystem('ss1', croomsk_star, [ps1, ps2, ps3, ps4, ps5, ps6, ps7, ps8], [asteroid_belt])

# visualizing planetary systems with satellites
# ps1.want_orbit_label = False
# ps1.want_draw_satellite_orbits = False
# ps1.want_draw_planetary_system_limits = False
# ps1.draw_planetary_system(save_fig=False)

# ps3.draw_planetary_system(save_fig=False)
#
# # visualizing Croomsk stellar system
# ss.want_draw_orbit_lines = False
# ss.want_draw_frost_line = False
# ss.draw_detailed_asteroid_belt = False
# ss.draw_detailed_trojans = False
# ss.want_draw_stellar_system_limits = False
# ss.want_draw_extended_habitable_zone = False
# ss.want_draw_conservative_habitable_zone = False

# ss.draw_stellar_system(save_fig=False)
# for sat in ps1.satellite_list:
#     print(sat.orbital_stability)
# planet3.save_as_csv('output_files/planet1.csv')
# croomsk_star.save_as_csv('output_files/CroomskStar.csv')
# num = 2
# a = timeit.timeit(lambda: save(ss, 'output_files/CroomskSystem.ssc'), number=num)
# print(a/num)
save(ss, 'output_files/CroomskSystem.ssc')
save(ps1, 'output_files/Planet1System.ssc')
# plt.show()
