import matplotlib.pyplot as plt
import numpy as np
import scipy.stats
import pylabo

pylabo.defaults()

dist = np.array([100, 150, 200, 500])
r = np.array([26.7, 66.7, 80, 166.6]) * 1e3

result = scipy.stats.linregress(dist, r)
m = result.slope
b = result.intercept

y = m * dist + b

label = rf"$R_c = {b} \Omega$"

plt.plot(dist, r, "o")
plt.plot(dist, y, color="black", label=label)
plt.legend()
plt.show()
