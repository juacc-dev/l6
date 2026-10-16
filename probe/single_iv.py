import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import props
import scipy.optimize
import scipy.stats
import util
import pylabo

pylabo.defaults()

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

if len(by_name) > 1:
    print("ERROR: Debe haber una sola muestra.")


muestra = pairs[0].muestra
_, ax = plt.subplots(1, 1)

util.plot_iv_curves(ax, muestra, pairs)


plt.tight_layout()
plt.show()
