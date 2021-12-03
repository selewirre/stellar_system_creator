from stellar_system_creator.solar_system_elements.stellar_body import StellarBody
from stellar_system_creator.astrothings.units import ureg

# titan = Planet('Titan', 0.055*ureg.M_e, composition='Rockworld70')
#
# print(titan.density, titan.mass)
# titan.__dict__['mass'] = 1*ureg.M_e
# print(titan.density, titan.mass)
# titan.__post_init__()
# print(titan.density, titan.mass)
# print(titan.density)
# print(titan.surface_pressure.to('kPa'))

a = StellarBody('patata', 1 * ureg.M_s)
print(a)

# xx = np.array([0, 1, 2])
# yy = np.array([0, 1, 0])
# x = [0, 1, 2]
# y1 = 1
# y2 = 2
# # path = Path(np.array([xx, yy]).transpose())
# # patch = PathPatch(path, facecolor='none')
# # plt.gca().add_patch(patch)
#
# tt = xx
# xx = yy
# yy = xx
#
# plt.fill_between(x, y1, y2, cmap=plt.cm.Reds)
#
# # im = plt.imshow(yy.reshape(xx.size, 1), cmap=plt.cm.Reds, interpolation="bicubic",
# #                 origin='lower', extent=[xx.min(), xx.max(), yy.min(), yy.max()], aspect="auto", clip_path=patch,
# #                 clip_on=True)
# # im.set_clip_path(patch)
#
# plt.ylim([-1, 2])
# plt.show()
