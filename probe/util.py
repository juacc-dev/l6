import math
import re
from collections import defaultdict
from dataclasses import dataclass

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import props
import scipy.optimize
import scipy.stats

pattern = re.compile(r"([\w#\d]+)\s-\s(\d+)um\s-\scontactos\s(\dy\d)\s*([\s\w]*)_0")


@dataclass
class ContactPair:
    # Una medición de un par de contactos
    muestra: str
    nombre_completo: str
    ancho: float
    contactos: str
    dist: float
    temp: float
    r: float
    r_err: float
    intercept: float
    int_err: float


def linear_fit(df):
    result = scipy.stats.linregress(df["Corriente"], df["Tensión"])
    m = result.slope
    m_err = result.stderr
    b = result.intercept
    b_err = result.intercept_stderr

    return m, b, m_err, b_err


def get_params(df, filename):
    match = pattern.search(filename)

    if match is None:
        return None

    muestra = match.group(1)
    ancho_canal = match.group(2)
    pares = match.group(3)
    comment = match.group(4)

    temp = props.temp[muestra]
    dist = props.dist_entre_contactos[pares]

    m, b, m_err, b_err = linear_fit(df)

    nombre = f"{muestra}-{ancho_canal}"

    if comment != "":
        nombre += f" ({comment})"

    params = ContactPair(
        muestra=muestra,
        nombre_completo=nombre,
        ancho=ancho_canal,
        contactos=pares,
        dist=dist,
        temp=temp,
        r=m,
        r_err=m_err,
        intercept=b,
        int_err=b_err,
    )

    return params


def read_data(file):
    df = pd.read_csv(
        file,
        sep=r"\s+",
        skiprows=2,
        names=["Tensión", "Corriente"],
        encoding="latin1",
    )

    return df


def group_by(array, prop):
    by_prop = defaultdict(list)
    for obj in array:
        by_prop[getattr(obj, prop)].append(obj)

    return by_prop


def unpack(pairs):
    dist = []
    r = []
    r_err = []

    for pair in pairs:
        dist.append(pair.dist)
        r.append(pair.r)
        r_err.append(pair.r_err)

    idx_sort = np.argsort(dist)

    return np.array(dist)[idx_sort], np.array(r)[idx_sort], np.array(r_err)[idx_sort]


def optimal_rectangle(n):
    ncols = math.ceil(math.sqrt(n))
    nrows = math.ceil(n / ncols)

    return nrows, ncols


def plot_grid(datasets):
    # optimal rectangle of plots
    nrows, ncols = optimal_rectangle(len(datasets))

    _, axes = plt.subplots(
        nrows,
        ncols,
        figsize=(4 * ncols, 3 * nrows),
        squeeze=False,
    )

    # hide unused plots
    for i in range(len(datasets), nrows * ncols):
        row = i // ncols
        col = i % ncols
    axes[row, col].set_visible(False)

    return axes
