import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import props
import scipy.optimize
import scipy.stats
import util

if len(sys.argv) != 2:
    print("Missing path!")
    sys.exit()

DIR = Path(sys.argv[1])

pairs = []  # Pares de contactos

# Import files
for file in DIR.glob("*_0"):
    df = util.read_data(file)
    params = util.get_params(df, file.name)

    pairs.append(params)


by_name = util.group_by(pairs, "nombre_incompleto")

axes = util.plot_grid(by_name)
nrows, ncols = axes.shape

# Por si hay más de una muestra
for i, grouped in enumerate(by_name.values()):
    row = i // ncols
    col = i % ncols

    muestra = grouped[0].nombre_incompleto
    temp = grouped[0].temp

    util.plot_iv_curves(axes[row, col], muestra, temp, grouped)


plt.tight_layout()
plt.show()
