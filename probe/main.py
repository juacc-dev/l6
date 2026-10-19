import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pylabo
import scipy.optimize
import scipy.stats
import util

pylabo.defaults()

plt.rcParams["mathtext.fontset"] = "cm"
plt.rcParams["figure.dpi"] = 100
plt.rcParams["axes.grid"] = True
plt.rcParams["font.family"] = "STIXGeneral"
# plt.rcParams["font.size"] = 14
plt.rcParams["font.size"] = 10
plt.rcParams["figure.figsize"] = (9, 7)
plt.rcParams["legend.loc"] = "best"

if len(sys.argv) == 1:
    print("Missing path!")
    sys.exit()

title1 = "Resistencia de contacto"
title2 = r"$R_c$ en función de $T$"

if len(sys.argv) == 3:
    title1 += f" ({sys.argv[2]})"
    title2 += f" ({sys.argv[2]})"


DIR = Path(sys.argv[1])

pairs = []  # Pares de contactos

# Import files
for file in DIR.rglob("*_0"):
    df = util.read_data(file)

    params = util.get_params(df, file.name)

    if params is None:
        continue

    pairs.append(params)


# Diccionario agrupado por nombre:
by_name = util.group_by(pairs, "nombre_incompleto")

axes = util.plot_grid(by_name, title=title1, sharex=True)
nrows, ncols = axes.shape

muestras = []
temps = []
contactos = []
contactos_err = []

for i, (nombre, grouped) in enumerate(by_name.items()):
    row = i // ncols
    col = i % ncols

    dist, _, r, r_err = util.unpack(grouped)
    temp = grouped[0].temp

    result = util.r_c_fit(grouped)

    if result is None:
        axes[row, col].set_visible(False)
        continue

    m = result.slope
    r_c = result.intercept
    r_c_err = result.intercept_stderr

    if r_c > 0 and r_c < 1e4:
        is_bad = False

        muestras.append(nombre)
        temps.append(temp)
        contactos.append(r_c)
        contactos_err.append(r_c_err)

    else:
        is_bad = True

    title = (
        rf"{nombre} @ $T$ = {temp}$\degree$C"
        + "\n"
        + rf"$R_c$ = ({r_c / 2:.1e} $\pm$ {r_c_err / 2:.1e}) $\Omega$"
    )
    ax = axes[row, col]

    ax.set(
        title=title,
    )
    if col == 0:
        ax.set(ylabel=r"Resistencia [k$\Omega$]")

    if row == ncols - 1:
        ax.set(xlabel=r"Distancia [$\mu$m]")

    util.plot_fit(
        ax=ax,
        datasets=grouped,
        title=title,
        dist=dist,
        r=r,
        m=m,
        b=r_c,
        is_bad=is_bad,
    )

plt.tight_layout()
plt.show()

temps = np.array(temps)
contactos = np.array(contactos)
contactos_err = np.array(contactos_err)

plt.rcParams["font.size"] = 16
plt.rcParams["figure.figsize"] = (8, 6)

plt.errorbar(temps, contactos / 1000, contactos_err / 1000, fmt="o")

for x, y, s in zip(temps, contactos / 1000, muestras):
    x_text = x + 1
    plt.text(x_text, y, s)

plt.title(title2, fontsize=18)
plt.xlabel(r"Temperatura [$\degree$C]")
plt.ylabel(r"Resistencia de contacto [k$\Omega$]")
plt.tight_layout()
plt.show()
