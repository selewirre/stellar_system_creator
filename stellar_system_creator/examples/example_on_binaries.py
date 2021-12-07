from matplotlib import pyplot as plt

from stellar_system_creator.stellar_system_elements.stellar_body import MainSequenceStar
from stellar_system_creator.stellar_system_elements.binary_system import StellarBinary
from stellar_system_creator.astrothings.units import ureg
from stellar_system_creator.stellar_system_elements.stellar_system import StellarSystem, MultiStellarSystemSType

# creating 4 different stars that will be parts of binary systems
andra_star = MainSequenceStar('AndraStar', 1.4 * ureg.M_s, luminosity=4 * ureg.L_s)
bhasdha_star = MainSequenceStar('BhasdhaStar', 1.0 * ureg.M_s, radius=1 * ureg.R_s)
croomsk_star = MainSequenceStar('CroomskStar', 0.8 * ureg.M_s)
duheb_star = MainSequenceStar('DuhebStar', 0.6 * ureg.M_s)

# andra_star.save_as_csv('output_files/AndraStar.csv')

# creating a P binary system (due to small input distance). The eccentricity given is for the quaternary system creation
shugravu_binary = StellarBinary('ShugravuBinary', andra_star, croomsk_star,
                                mean_distance=0.5 * ureg.au, eccentricity=0.5)
# print(shugravu_binary)
# for key in shugravu_binary.habitable_zone_limits:
#     print(key, shugravu_binary.habitable_zone_limits[key])
# shugravu_binary.primary_body.save_as_csv('output_files/AndraStar_in_ShugravuBinary.csv')
# shugravu_binary.save_as_csv('output_files/ShugravuBinary.csv')

# creating a S binary system (due to large input distance). The eccentricity given is for the quaternary system creation
# trakruna_binaryS = StellarBinary('TrakrunaBinaryS', bhasdha_star, duheb_star,
#                                  mean_distance=300 * ureg.au, eccentricity=0.6)
# print(trakruna_binaryS)
# for key in trakruna_binaryS.habitable_zone_limits:
#     print(key, trakruna_binaryS.habitable_zone_limits[key])
# for key in bhasdha_star.habitable_zone_limits:
#     print(key, bhasdha_star.habitable_zone_limits[key])
# trakruna_binaryS.primary_body.save_as_csv('output_files/BhasdhaStar_in_TrakrunaBinaryS.csv')
# trakruna_binaryS.save_as_csv('output_files/TrakrunaBinaryS.csv')

# trakruna_binaryP = StellarBinary('TrakrunaBinaryP', bhasdha_star, duheb_star,
#                                  mean_distance=1.1 * ureg.au, eccentricity=0.44)

# print(trakruna_binaryP)
# for key in trakruna_binaryP.habitable_zone_limits:
#     print(key, trakruna_binaryP.habitable_zone_limits[key])

# trakruna_binaryP.primary_body.save_as_csv('output_files/BhasdhaStar_in_TrakrunaBinaryP.csv')
# trakruna_binaryP.save_as_csv('output_files/TrakrunaBinaryP.csv')

# quezuliferh_quaternary = StellarBinary('QuezuliferhQuaternary', shugravu_binary, trakruna_binaryP,
#                                        mean_distance=100 * ureg.au, eccentricity=0.7)
# print(quezuliferh_quaternary)
# for key in quezuliferh_quaternary.habitable_zone_limits:
#     print(key, quezuliferh_quaternary.habitable_zone_limits[key])
# for key in trakruna_binaryP.habitable_zone_limits:
#     print(key, trakruna_binaryP.habitable_zone_limits[key])
# for key in shugravu_binary.habitable_zone_limits:
#     print(key, shugravu_binary.habitable_zone_limits[key])

# quezuliferh_quaternary.primary_body.save_as_csv('output_files/ShugravuBinary_in_QuezuliferhQuaternary.csv')
# quezuliferh_quaternary.save_as_csv('output_files/QuezuliferhQuaternary.csv')

# shugravu_system = StellarSystem('Shugravu System', shugravu_binary)
# trakrunaP_system = StellarSystem('TrakrunaP System', trakruna_binaryP)
# quezuliferh_system = MultiStellarSystemSType('TrakrunaP System', quezuliferh_quaternary,
#                                            [shugravu_system, trakrunaP_system])

# shugravu_system.draw_stellar_system()
# trakrunaP_system.draw_stellar_system()
# quezuliferh_system.draw_multi_stellar_system()

# plt.show()





















