import logging
import sys
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter
import numpy as np
import plot
import pylabo
import util
import rate

# https://en.wikipedia.org/wiki/Spectral_density
# https://en.wikipedia.org/wiki/Correlation_function

BIN_SIZE = "auto"

Z_MIN = 240
Z_MAX = 360

FILES = [Path("./data/2-2.csv"), Path("./data/3.csv"), Path("./data/4.csv")]
plt.rcParams["mathtext.fontset"] = "cm"
plt.rcParams["font.family"] = "STIXGeneral"
plt.rcParams["font.size"] = 17


time = {"2-2": 31.58, "3": 45.82, "4": 60.03}
err = {"2-2": 7.5896194348802055, "3": 2.074269258363188, "4": 3.2388620141653064}


def mode(x):
    hist, bins = np.histogram(x, bins=BIN_SIZE)
    m_idx = np.argmax(hist)

    return bins[m_idx]


def get_bottom(z_low):
    bottom = np.mean(z_low)
    err = np.std(z_low)

    return bottom, err


pylabo.defaults()
logger = logging.getLogger("main")


def high_region(z, name):
    plane = {
        "2-1": [305, 390, 250, 300],
        "2-2": [340, -1, 10, 340],
        "3": [300, -1, 0, 300],
        "4": [125, 300, 360, -1],
    }

    if name not in plane:
        return z

    r = plane[name]

    return z[r[0] : r[1], r[2] : r[3]]


def low_region(z, name):
    limits = {
        "2-1": [Z_MIN, Z_MAX],
        "2-2": [Z_MIN, 295],
        "3": [282, Z_MAX],
        "4": [Z_MIN, Z_MAX],
    }
    r = limits[name]
    z = z[~np.isnan(z)]

    return z[(z >= r[0]) & (z <= r[1])]


def filter_hist(z):
    z_hist = z[~np.isnan(z)]

    return z_hist


def preresult(filepath):
    z, _ = util.read_csv(filepath)

    z_plane = high_region(z, filepath.stem)

    params = util.fit(z_plane)

    z -= util.plane(z, params)

    z_high = high_region(z, filepath.stem)

    zero = np.average(z_high)
    z_high = -(z_high - zero)

    z -= zero
    z *= -1000
    z_low = low_region(z, filepath.stem)

    z_high = filter_hist(z_high)
    z_low = filter_hist(z_low)

    return z, z_high, z_low


def inspect_2D(filepath):
    z, _, _ = preresult(filepath)

    plot.colormap(-z)
    plt.tight_layout()
    plt.show()


def inspect_3D(filepath):
    z, _, _ = preresult(filepath)

    plot.surface(z)
    plt.tight_layout()
    plt.show()


def show_low(filepath):
    _, _, z_low = preresult(filepath)

    bottom, err = get_bottom(z_low)

    _, ax = plt.subplots(1, 1)
    prob, z, _ = plt.hist(z_low, bins=1000, label=f"{z_low.size} puntos")
    # ax.yaxis.set_major_formatter(PercentFormatter(xmax=1))

    bottom = z[np.argmax(prob)]
    idx = np.argmin(np.abs(prob - prob.max() // 2))

    err = np.abs(bottom - z[idx])

    ax.axvline(bottom, color="black")
    # ax.axhline(prob.max() / 2)
    ax.axhline(prob[idx])
    ax.axvline(bottom + err, color="black", alpha=0.7, zorder=0)
    ax.axvline(bottom - err, color="black", alpha=0.7, zorder=0)
    # ax.axvline(z[idx], color="black", alpha=0.7, zorder=0)
    # print(bottom)
    print(err)

    plt.xlabel("Profundidad [nm]")
    plt.legend()
    plt.tight_layout()
    plt.show()


def full_hist(filepath):
    z, _, _ = preresult(filepath)

    z_hist = filter_hist(z)

    plt.hist(z_hist, bins=1000, label=f"{z.size} puntos")
    plt.xlabel("Profundidad [nm]")
    plt.legend()
    plt.tight_layout()
    plt.show()


def result(filepath, no_plot=False, ax=None):
    _, z_high, z_low = preresult(filepath)

    bottom, err = get_bottom(z_low)

    if no_plot:
        return bottom, err

    if ax is None:
        print(f"{filepath}")
        print(f"z_high = {np.mean(z_high):.3e} +- {np.std(z_high):.3e} um")
        print(f"z_low = {bottom:.3e} +- {err:.3e} um")

        _, ax = plt.subplots(1, 2)

        ax[0].hist(z_high, bins=BIN_SIZE)
        ax[0].set(title=f"High ({z_high.size} puntos)", xlabel=r"Profundidad [nm]")

        axis = ax[1]

    else:
        axis = ax

    axis.hist(z_low, bins=BIN_SIZE, density=True)
    axis.yaxis.set_major_formatter(PercentFormatter(xmax=1))
    axis.axvline(bottom, color="black")

    axis.axvline(bottom + err, color="black", alpha=0.6)
    axis.axvline(bottom - err, color="black", alpha=0.6)

    axis.set(xlabel=r"Profundidad [nm]")

    plt.tight_layout()
    plt.show()


def analyze(command, filepath):
    match command:
        case "2d":
            inspect_2D(filepath)

        case "3d":
            inspect_3D(filepath)

        case "low":
            show_low(filepath)

        case "hist":
            full_hist(filepath)

        case "result":
            result(filepath)

        case _:
            logger.error(f"Invalid command '{command}'")


def find_params(files):
    z = []
    z_err = []

    for file in files:
        bottom, err = result(file, no_plot=True)
        z.append(bottom)
        z_err.append(err)

    return np.array(z), np.array(z_err)


def plot_hists(files):
    _, ax = plt.subplots(1, 1, tight_layout=True)

    for filepath in files:
        _, _, z_low = preresult(filepath)

        bottom, err = get_bottom(z_low)

        _, _, patches = ax.hist(
            z_low,
            bins=BIN_SIZE,
            density=True,
            zorder=1,
            label=f"Sumergido ${time[filepath.stem]}$ s",
            alpha=0.9,
        )
        ax.yaxis.set_major_formatter(PercentFormatter(xmax=1))

        color = patches[0].get_facecolor()

        ax.axvline(bottom, color=color, alpha=0.7)

    ax.legend()
    ax.set(xlabel=r"Profundidad [nm]", ylabel="Distribución")
    plt.show()


def do_all(command):
    match command:
        case "plot":
            for filepath in FILES:
                result(filepath)

        case "fit":
            z, z_err = find_params(FILES)
            rate.linear_fit(z, z_err)

        case "hist":
            plot_hists(FILES)

        case "low":
            for filepath in FILES:
                show_low(filepath)


def main():
    if len(sys.argv) != 3:
        logger.error(f"Usage: python {sys.argv[0]} <file> <command>")
        sys.exit(-1)

    command = sys.argv[2]

    if sys.argv[1] == "all":
        do_all(command)

    else:
        filepath = Path(sys.argv[1])
        analyze(command, filepath)


if __name__ == "__main__":
    main()
