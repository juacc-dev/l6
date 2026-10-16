from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import scipy.optimize
import scipy.stats
import util

plt.rcParams["mathtext.fontset"] = "cm"
plt.rcParams["figure.dpi"] = 100
plt.rcParams["axes.grid"] = True
plt.rcParams["font.family"] = "STIXGeneral"
# plt.rcParams["font.size"] = 14
plt.rcParams["font.size"] = 9
plt.rcParams["figure.figsize"] = (9, 7)
plt.rcParams["legend.loc"] = "best"

DIR = Path("./data/data/ETH/")


def plot_fit(ax, datasets, title, dist, r, m, b, is_bad):
    ax.set(
        xlabel=r"Distancia [$\mu$m]",
        ylabel=r"Resistencia [k$\Omega$]",
        title=title,
    )

    if is_bad:
        ax.title.set_color("red")

    by_muestra = util.group_by(datasets, "nombre_completo")

    for muestra, grouped in by_muestra.items():
        dist, r, r_err = util.unpack(grouped)
        ax.errorbar(dist, r / 1000, yerr=r_err / 1000, fmt=".", label=muestra)

    fit = m * dist + b

    ax.plot(dist, fit / 1000)

    if len(by_muestra) > 1:
        ax.legend()


pairs = []  # Pares de contactos

# Import files
for file in DIR.rglob("*_0"):
    df = util.read_data(file)
    params = util.get_params(df, file.name)

    pairs.append(params)


# Diccionario agrupado por nombre:
by_name = util.group_by(pairs, "nombre_incompleto")

# Sort by temperature
by_name = dict(sorted(by_name.items()))

axes = util.plot_grid(by_name)
nrows, ncols = axes.shape

muestras = []
temps = []
contactos = []
contactos_err = []

for i, (nombre, grouped) in enumerate(by_name.items()):
    row = i // ncols
    col = i % ncols

    dist, r, r_err = util.unpack(grouped)
    temp = grouped[0].temp

    # No se puede ajustar una recta con un solo punto
    if len(dist) <= 1:
        axes[row, col].set_visible(False)
        continue

    result = scipy.stats.linregress(dist, r)
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
        rf"Muestra {nombre} @ $T$ = {temp}$\degree$C"
        + "\n"
        + rf"$R_c$ = ({r_c / 2:.1e} $\pm$ {r_c_err / 2:.1e}) $\Omega$"
    )

    plot_fit(
        ax=axes[row, col],
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

plt.rcParams["font.size"] = 14
plt.rcParams["figure.figsize"] = (5, 4)

plt.errorbar(temps, contactos / 1000, contactos_err / 1000, fmt="o")
plt.xlabel(r"Temperatura [$\degree$C]")
plt.ylabel(r"Resistencia de contacto [k$\Omega$]")

plt.show()
