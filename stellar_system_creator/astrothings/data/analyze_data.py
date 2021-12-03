from matplotlib import pyplot as plt
import pandas as pd
from scipy.optimize import curve_fit


def lin(x, b):
    return x * 0.5 + b


vrot = pd.read_csv('v_rot_planets_and_brown_dwarfs.csv')
x = vrot['log(m/mj)']
y = vrot['log(vrot)']

popt, _ = curve_fit(lin, x, y)
print(popt)

plt.plot(x, y)
plt.plot(x, lin(x, *popt))

plt.show()

