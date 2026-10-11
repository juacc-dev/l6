from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pylabo
import scipy.optimize
import util

pylabo.defaults()

plt.rcParams["font.size"] = 9

DIR = Path("./data/ETH viejo")


def plot_fit(ax, datasets, temp, dist, r, m, b, b_err):
    x = np.linspace(dist.min(), dist.max(), 2)
    y = m * x + b

    ax.set(
        xlabel=r"Distancia [$\mu$m]",
        ylabel=r"Resistencia [k$\Omega$]",
        title=f"Temperatura: {temp} C\n"
        + rf"$R_c$ = ({b / 2:.1e} $\pm$ {b_err / 2:.1e}) $\Omega$",
    )

    by_muestra = util.group_by(datasets, "nombre_completo")

    for muestra, grouped in by_muestra.items():
        dist, r, r_err = util.unpack(grouped)
        ax.errorbar(dist, r / 1000, yerr=r_err / 1000, fmt=".", label=muestra)

    ax.plot(x, y / 1000)
    ax.legend()


pairs = []  # Pares de contactos

# Import files
for file in DIR.rglob("*_0"):
    df = util.read_data(file)
    params = util.get_params(df, file.name)

    pairs.append(params)


# Diccionario agrupado por temperatura:
# by_temp = { 470: [pair1, pair2, ...], 480: [...], ... }
by_temp = util.group_by(pairs, "temp")

# Sort by temperature
by_temp = dict(sorted(by_temp.items()))

axes = util.plot_grid(by_temp)
nrows, ncols = axes.shape

for i, (temp, grouped) in enumerate(by_temp.items()):
    dist, r, r_err = util.unpack(grouped)

    # No se puede ajustar una recta con un solo punto
    if len(dist) <= 1:
        continue

    p_opt, p_cov = scipy.optimize.curve_fit(
        lambda x, m, b: m * x + b,
        dist,
        r,
        sigma=r_err,
        absolute_sigma=True,
    )

    m, b = p_opt
    m_err, b_err = np.sqrt(np.diag(p_cov))

    row = i // ncols
    col = i % ncols

    plot_fit(axes[row, col], grouped, temp, dist, r, m, b, b_err)

plt.tight_layout()
plt.show()
