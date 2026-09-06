import logging
import sys

import config
import matplotlib.pyplot as plt
import numpy as np
import scipy.signal
from scipy.ndimage import gaussian_filter

logger = logging.getLogger("main")

Z_MIN = 50e-9
Z_MAX = 430e-9

STEP_NM = 0.5e-9


def read_csv_old(filepath):
    with open(filepath, "r") as file:
        lines = file.readlines()

    for i, line in enumerate(lines):
        if line.startswith("RAW_DATA"):
            start = i + 1

        elif line.startswith("Intensity"):
            end = i
            break

        elif line.startswith("Pixel_size"):
            pixel_size = float(line.split()[-1])

    z = np.genfromtxt(
        lines[start + 1 : end],
        delimiter="\t",
        missing_values="Bad",
        filling_values=np.nan,
    )[:, :-1]

    z *= 1e-6  # nanometros

    return z, pixel_size


def read_csv_gwyddion(filepath):
    with open(filepath, "r") as file:
        lines = file.readlines()

    for i, line in enumerate(lines):
        if not line.startswith("#"):
            start = i
            break

        elif line.startswith("# Width:"):
            width = float(line.split()[-2]) * 1e-6  # units: um

        elif line.startswith("# Height:"):
            height = float(line.split()[-2]) * 1e-6  # units: um

    z = np.genfromtxt(
        lines[start:],
        delimiter="\t",
        missing_values="Bad",
        filling_values=np.nan,
    )

    x_size = z[0, :].size
    z = z.T[:, ::-1]

    pixel_size = width / x_size

    return z, pixel_size


def read_csv_simple(filepath):
    with open(filepath, "r") as file:
        lines = file.readlines()

    for i, line in enumerate(lines):
        if not line.startswith("#"):
            start = i
            break

        elif line.startswith("# Pixel_size:"):
            pixel_size = float(line.split()[-1])  # * 1e3

    z = np.genfromtxt(lines[start:], delimiter=",")  # * 1e9

    return z, pixel_size


def read_csv(filepath):
    if filepath.stem.endswith(".old"):
        return read_csv_old(filepath)

    if filepath.stem.endswith(".gwyd"):
        return read_csv_gwyddion(filepath)

    return read_csv_simple(filepath)


def meshgrid(z, pixel_size=1):
    x = np.arange(z.shape[1]) * pixel_size
    y = np.arange(z.shape[0]) * pixel_size

    X, Y = np.meshgrid(x, y)

    return X, Y


def estimate_high_region(z, pixel_size):
    z_filter = gaussian_filter(z, sigma=20)

    x = np.arange(z.shape[1]) * pixel_size
    y = np.arange(z.shape[0]) * pixel_size
    X, Y = np.meshgrid(x, y)

    dz_dy, dz_dx = np.gradient(z_filter, y, x)

    bins = np.arange(-1e-6, 1e-6, 2e-9)

    dz_dy_hist, b1 = np.histogram(dz_dy, bins=bins)
    dz_dx_hist, b2 = np.histogram(dz_dx, bins=bins)

    a_est = b1[np.argmax(dz_dx_hist)]
    b_est = b2[np.argmax(dz_dy_hist)]

    plane_estimated = a_est * X + b_est * Y

    z_plane = z - plane_estimated
    z_hist = filter_nan(z_plane)

    heights = np.arange(z_hist.min(), z_hist.max(), 0.5e-9)
    hist, heights = np.histogram(z_hist, bins=heights)

    idx = find_highest_peaks(heights, hist, 2, separation=50e-9)
    idx = np.max(idx)
    most_common = heights[idx]
    delta = 3e-9

    mask = (
        (z_plane >= most_common - delta)
        & (z_plane <= most_common + delta)
        & np.isfinite(z_plane)
    )

    # z_masked = np.where(mask, z, np.nan)
    # fig = plt.figure(tight_layout=True)
    # ax = fig.add_subplot(111, projection="3d")
    # ax.plot_surface(X, Y, z - plane_estimated, cmap="viridis")
    # plt.show()

    return mask


def fit(z, mask, pixel_size=1):
    x, y = meshgrid(z, pixel_size)

    A = np.column_stack((x[mask], y[mask], np.ones(np.sum(mask))))

    params = np.linalg.lstsq(A, z[mask], rcond=None)[0]

    return params


def plane(z, params, pixel_size=1):
    x, y = meshgrid(z, pixel_size)
    a, b, c = params

    z_fit = a * x + b * y + c

    return z_fit


def get_bottom(z_low, density=True):
    bins = np.arange(Z_MIN, Z_MAX, STEP_NM) * 1e9
    hist, bins = np.histogram(z_low * 1e9, bins=bins, density=density)

    i0 = np.argmax(hist)

    bottom = bins[i0]

    # bottom +- err is where hist crosses half its maximum

    half = hist[i0] / 2
    crossings = np.where(np.diff(np.sign(hist - half)) != 0)[0]
    i = crossings[np.argmin(np.abs(crossings - i0))]

    err_exp = np.abs(bottom - bins[i])
    err_instr = STEP_NM * 1e9 / 2

    err = np.linalg.norm([err_exp, err_instr])

    return bottom, err, hist, bins


def high_region(z, name, pixel_size):
    if "plane" not in config.config[name]:
        return None

    r = config.config[name]["plane"]

    # r = [int(x // pixel_size) if x != -1 else -1 for x in r]
    r = [x if x != -1 else -1 for x in r]

    z_high = z[r[0] : r[1], r[2] : r[3]]
    mask = np.isfinite(z_high)

    return z_high, mask


def low_region(z, name):
    z = z[~np.isnan(z)]

    r = config.config[name].get("limits", None)

    if r is None:
        r = [Z_MIN, Z_MAX]

    return z[(z >= r[0]) & (z <= r[1])]


def filter_nan(z):
    z_hist = z[~np.isnan(z)]

    return z_hist


def get_z(file):
    z, pixel_size = read_csv(file)

    # z2fit, mask = high_region(z, file.stem, pixel_size)

    mask = estimate_high_region(z, pixel_size)
    z2fit = z

    # if z2fit is None:
    #     return -1 * z, None, pixel_size

    params = fit(z2fit, mask, pixel_size)

    z -= plane(z, params, pixel_size)

    # a, b, _ = params
    # print(a, b)
    # normal = np.array([-a, -b, 1])
    # height_factor = 1 / np.linalg.norm(normal)
    # z *= height_factor

    # z_high = high_region(z, file.stem, pixel_size)

    # zero = np.average(z_high)
    # z_high = -(z_high - zero)
    #
    # z -= zero
    z *= -1

    z_low = low_region(z, file.stem)

    return z, z_low, pixel_size


def show_or_save():

    if config.SAVE_PLOT:
        config.PLOT_DIR.mkdir(exist_ok=True, parents=True)

        file = None
        if config.FILE:
            file = config.FILE.name

        name = file or config.DATASET

        path = config.PLOT_DIR / f"{name}-{config.COMMAND}.png"
        print(f"Saving plot into {path}")

        plt.savefig(path)

    else:
        plt.show()


def find_highest_peaks(x, y, n, /, *, separation=0):
    distance = separation / (x[1] - x[0])

    peaks, properties = scipy.signal.find_peaks(y, distance=distance)

    if peaks.size <= n:
        order = np.argsort(-y[peaks])
        return peaks[order]

    heights = y[peaks]

    top_n = np.argpartition(-heights, n - 1)[:n]
    top_n_sorted = top_n[np.argsort(-heights[top_n])]

    highest_peaks = peaks[top_n_sorted]

    return highest_peaks
