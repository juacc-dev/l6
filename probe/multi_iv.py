import sys
from pathlib import Path

import matplotlib.pyplot as plt
import pylabo
import util

pylabo.defaults()
plt.rcParams["font.size"] = 10

if len(sys.argv) == 1:
    print("Missing path!")
    sys.exit()

DIR = Path(sys.argv[1])
title = r"Curvas $I$ vs $V$"

if len(sys.argv) == 3:
    title += f" ({sys.argv[2]})"

pairs = []  # Pares de contactos

# Import files
for file in DIR.rglob("*_0"):
    df = util.read_data(file)
    params = util.get_params(df, file.name)

    if params is None:
        continue

    pairs.append(params)


by_name = util.group_by(pairs, "nombre_incompleto")

axes = util.plot_grid(by_name, title=title, sharey=True)
nrows, ncols = axes.shape

# Por si hay más de una muestra
for i, grouped in enumerate(by_name.values()):
    row = i // ncols
    col = i % ncols

    muestra = grouped[0].nombre_incompleto
    temp = grouped[0].temp

    ax = axes[row, col]
    ax.set(
        title=rf"{muestra} @ {temp}$\degree$C",
    )
    if col == 0:
        ax.set(ylabel=r"Tensión [mV]")

    if row == ncols - 1:
        ax.set(xlabel=r"Corriente [$\mu$A]")

    util.plot_iv_curves(ax, muestra, temp, grouped)

plt.tight_layout()
plt.show()
