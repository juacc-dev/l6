import matplotlib.pyplot as plt
import numpy as np
import plot
from config import config
from matplotlib.ticker import PercentFormatter
from util import (
    filter_nan,
    get_bottom,
    get_z,
    read_csv,
    show_or_save,
)


def raw(file):
    z, _ = read_csv(file)

    plot.colormap(z, 1, title=file.stem, units="pixels")
    plt.tight_layout()
    show_or_save()


def inspect_cut(file):
    z, pixel_size = read_csv(file)
    cut = config[file.stem]["cut"]

    if cut[0] is None:
        x0 = int(cut[1] // pixel_size)

        z_cut = z[:, x0]
        plt.xlabel(rf"Y [$\mu$m] ($X_0 = {cut[1]}$)")

    elif cut[1] is None:
        y0 = int(cut[0] // pixel_size)

        z_cut = z[y0, :]
        plt.xlabel(rf"X [$\mu$m] ($Y_0 = {cut[0]}$)")

    x_or_y = np.arange(z_cut.size) * pixel_size
    plt.plot(x_or_y, z_cut)
    plt.title(file.stem)
    show_or_save()


def show_2D(file):
    z, _, pixel_size = get_z(file)

    plot.colormap(-z * 1e9, pixel_size)
    plt.title(file)
    plt.tight_layout()
    show_or_save()


def show_3D(file):
    z, _, pixel_size = get_z(file)

    plot.surface(-z * 1e9, pixel_size=pixel_size, title=f"Muestra {file.stem}")
    plt.tight_layout()
    show_or_save()


def hist(file):
    _, z_low, _ = get_z(file)

    bottom, err, hist, bins = get_bottom(z_low)

    _, ax = plt.subplots(1, 1)

    ax.stairs(hist, bins, fill=True, label=rf"$z = ({bottom:.1f}\pm{err:.1f})$ nm")
    ax.yaxis.set_major_formatter(PercentFormatter(xmax=1))

    ax.axvline(bottom, color="black")
    ax.axvline(bottom + err, color="black", alpha=0.7, zorder=0)
    ax.axvline(bottom - err, color="black", alpha=0.7, zorder=0)

    ax.set(xlabel="Profundidad [nm]", title=file.stem)
    ax.legend()
    plt.tight_layout()
    show_or_save()

    return bottom, err


def full_hist(file):
    # z, _, _ = get_z(file)
    z, _ = read_csv(file)

    z_hist = filter_nan(z)

    _, ax = plt.subplots(1, 1)
    ax.hist(z_hist * 1e9, bins=1000, density=True)
    ax.yaxis.set_major_formatter(PercentFormatter(xmax=1))
    ax.set(
        xlabel="Profundidad [nm]",
        ylabel="Distribución",
        title=file.stem,
    )
    plt.tight_layout()
    show_or_save()


def find_params(files):
    z = []
    z_err = []

    for file in files:
        _, z_low, _ = get_z(file)

        bottom, err, _, _ = get_bottom(z_low)

        z.append(bottom)
        z_err.append(err)

    return np.array(z), np.array(z_err)


def all_hists(files):
    _, ax = plt.subplots(1, 1, tight_layout=True)

    for file in files:
        _, z_low, _ = get_z(file)

        bottom, err, hist, bins = get_bottom(z_low, density=True)

        patches = ax.stairs(
            hist,
            bins,
            label=f"{file.stem}: $t={config[file.stem]['time']}$ s,\n"
            rf"$z = ({bottom:.1f}\pm{err:.1f})$ nm",
            alpha=0.9,
            fill=True,
        )
        ax.yaxis.set_major_formatter(PercentFormatter(xmax=1))

        color = patches.get_facecolor()

        ax.axvline(bottom, color=color, alpha=0.7)
        # ax.axvline(bottom + err, color=color, alpha=0.7, zorder=0)
        # ax.axvline(bottom - err, color=color, alpha=0.7, zorder=0)

    ax.legend()
    ax.set(
        xlabel=r"Profundidad [nm]",
        ylabel="Distribución",
        title=",".join([file.stem for file in files]),
    )
    show_or_save()


def print_bottom(file):
    _, z_low, _ = get_z(file)

    bottom, err, _, _ = get_bottom(z_low)

    print(f"{file.stem}: z = {bottom:.1f} +- {err:.1f}")
