import re
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import props
import pylabo
import scipy.optimize
import scipy.stats
import util


def get_t(pairs):
    t = []
    r = []
    r_err = []

    for pair in pairs:
        t.append(pair.extra["tiempo"])
        r.append(pair.r)
        r_err.append(pair.r_err)

    idx_sort = np.argsort(t)

    return np.array(t)[idx_sort], np.array(r)[idx_sort], np.array(r_err)[idx_sort]


def plot_tiempo(pairs):
    t, r, r_err = get_t(pairs)

    plt.errorbar(1000 * t, r, yerr=r_err, fmt=".")
    plt.title(f"{pairs[0].nombre_incompleto} @ {pairs[0].temp}")
    plt.xlabel("Tiempo de paso [ms]")
    plt.ylabel(r"Resistencia [$\Omega$]")
    plt.tight_layout()
    plt.show()


pattern = re.compile(r".*t=(0\.\d{2})s_0")

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
    match = pattern.search(file.name)
    tiempo = match.group(1)
    params.extra["tiempo"] = float(tiempo)

    pairs.append(params)


plot_tiempo(pairs)
