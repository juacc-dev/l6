import logging

import matplotlib.pyplot as plt
import numpy as np
import config

logger = logging.getLogger("main")

Z_MIN = 150
Z_MAX = 430

STEP_NM = 0.5


def read_csv(filepath):
    with open(filepath, "r") as file:
        lines = file.readlines()

    for i, line in enumerate(lines):
        if line.startswith("RAW_DATA"):
            start = i

        elif line.startswith("Intensity"):
            end = i

        elif line.startswith("Pixel_size"):
            pixel_size = float(line.split()[-1]) * 1e3

    z = np.genfromtxt(
        lines[start + 1 : end],
        delimiter="\t",
        missing_values="Bad",
        filling_values=np.nan,
    )[:, :-1]

    z *= 1e3  # nanometros

    return z, pixel_size


def meshgrid(z):
    x, y = np.meshgrid(np.arange(z.shape[1]), np.arange(z.shape[0]))

    return x, y


def fit(z):
    x, y = meshgrid(z)

    mask = np.isfinite(z)

    domain = np.column_stack((x[mask], y[mask], np.ones(np.sum(mask))))

    params = np.linalg.lstsq(domain, z[mask], rcond=None)[0]

    return params


def plane(z, params):
    x, y = meshgrid(z)
    a, b, c = params

    z_fit = a * x + b * y + c

    return z_fit


def get_bottom(z_low, density=True):
    bins = np.arange(Z_MIN, Z_MAX, STEP_NM)
    hist, bins = np.histogram(z_low, bins=bins, density=density)

    i0 = np.argmax(hist)

    bottom = bins[i0]

    # bottom +- err is where hist crosses half its maximum

    half = hist[i0] / 2
    crossings = np.where(np.diff(np.sign(hist - half)) != 0)[0]
    i = crossings[np.argmin(np.abs(crossings - i0))]

    err_exp = np.abs(bottom - bins[i])
    err_instr = STEP_NM / 2

    err = np.linalg.norm([err_exp, err_instr])

    return bottom, err, hist, bins


def high_region(z, name, pixel_size):
    if "plane" not in config.config[name]:
        return None

    r = config.config[name]["plane"]

    r = [int(x // pixel_size) if x != -1 else -1 for x in r]

    return z[r[0] : r[1], r[2] : r[3]]


def low_region(z, name):
    r = config.config[name]["limits"]
    z = z[~np.isnan(z)]

    if r is None:
        r = [Z_MIN, Z_MAX]

    return z[(z >= r[0]) & (z <= r[1])]


def filter_nan(z):
    z_hist = z[~np.isnan(z)]

    return z_hist


def get_z(file):
    z, pixel_size = read_csv(file)

    z_plane = high_region(z, file.stem, pixel_size)

    if z_plane is None:
        return -1 * z, None, None, pixel_size

    params = fit(z_plane)

    z -= plane(z, params)

    a, b, _ = params
    normal = np.array([-a, -b, 1])
    height_factor = np.linalg.norm(normal)
    z *= height_factor

    z_high = high_region(z, file.stem, pixel_size)

    zero = np.average(z_high)
    z_high = -(z_high - zero)

    z -= zero
    z *= -1

    z_low = low_region(z, file.stem)

    z_high = filter_nan(z_high)
    z_low = filter_nan(z_low)

    return z, z_low, pixel_size


def show_or_save():

    if config.SAVE_PLOT:
        config.PLOT_DIR.mkdir(exist_ok=True, parents=True)
        name = config.FILE or config.DATASET

        plt.savefig(config.PLOT_DIR / f"{name}-{config.COMMAND}.png")

    else:
        plt.show()
