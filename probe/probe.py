import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import props
import scipy.optimize
import scipy.stats
import util
import pylabo


if len(sys.argv) != 2:
    print("Missing path!")
    sys.exit()


pylabo.defaults()


DIR = Path(sys.argv[1])

files = DIR.rglob("*_0")

pairs = []  # Pares de contactos

# Import files
for file in files:
    df = util.read_data(file)
    params = util.get_params(df, file.name)

    pairs.append(params)


by_name = util.group_by(pairs, "nombre_incompleto")

if len(by_name) > 1:
    print("ERROR: Debe haber una sola muestra.")


result = util.r_c_fit(pairs)

muestra = pairs[0].nombre_incompleto
temp = pairs[0].temp
_, ax = plt.subplots(1, 2, figsize=(16, 8))

util.plot_iv_curves(ax[0], muestra, temp, pairs)

util.plot_r_c_fit(ax[1], pairs, result)

plt.tight_layout()
plt.show()
