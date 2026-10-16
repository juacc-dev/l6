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
    df: pd.DataFrame
    muestra: str
    nombre_incompleto: str
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
    nombre_comentario = nombre

    if comment != "":
        nombre_comentario += f" ({comment})"

    params = ContactPair(
        df=df,
        muestra=muestra,
        nombre_incompleto=nombre,
        nombre_completo=nombre_comentario,
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


def plot_fit(ax, datasets, title, dist, r, m, b, is_bad):
    ax.set(
        xlabel=r"Distancia [$\mu$m]",
        ylabel=r"Resistencia [k$\Omega$]",
        title=title,
    )

    if is_bad:
        ax.title.set_color("red")

    by_muestra = group_by(datasets, "nombre_completo")

    for muestra, grouped in by_muestra.items():
        dist, r, r_err = unpack(grouped)
        ax.errorbar(dist, r / 1000, yerr=r_err / 1000, fmt=".", label=muestra)

    fit = m * dist + b

    ax.plot(dist, fit / 1000)

    if len(by_muestra) > 1:
        ax.legend()
