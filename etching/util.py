import numpy as np
import scipy.optimize
import logging
import sys

logger = logging.getLogger("main")


def read_csv(filepath):
    valid_region = {
        "2-1": [0, -1, 0, 460],
    }

    with open(filepath, "r") as file:
        lines = file.readlines()

    start = next(i for i, line in enumerate(lines) if line.startswith("RAW_DATA"))
    end = next(i for i, line in enumerate(lines) if line.startswith("Intensity"))

    pixel_size = 1.0

    z = np.genfromtxt(
        lines[start + 1 : end],
        delimiter="\t",
        missing_values="Bad",
        filling_values=np.nan,
    )[:, :-1]

    if filepath.stem in valid_region:
        r = valid_region[filepath.stem]
        z = z[r[0] : r[1], r[2] : r[3]]

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
