import logging
import sys
from pathlib import Path

import config
import matplotlib.pyplot as plt
import numpy as np
import pylabo
from commands import (
    all_hists,
    find_params,
    full_hist,
    hist,
    inspect_cut,
    print_bottom,
    raw,
    show_2D,
    show_3D,
)
from util import estimate_high_region
from rate import linear_fit

# https://en.wikipedia.org/wiki/Spectral_density
# https://en.wikipedia.org/wiki/Correlation_function

pylabo.defaults()

# plt.rcParams["mathtext.fontset"] = "cm"
# plt.rcParams["font.family"] = "STIXGeneral"
plt.rcParams["font.size"] = 15
# plt.rcParams["figure.dpi"] = 100

logger = logging.getLogger("main")


def do_file(command, file):
    match command:
        case "raw":
            raw(file)

        case "cut":
            inspect_cut(file)

        case "2d":
            show_2D(file)

        case "3d":
            show_3D(file)

        case "z":
            print_bottom(file)

        case "hist":
            hist(file)

        case "fullhist":
            full_hist(file)

        case "test":
            estimate_high_region(file)

        case _:
            logger.error(f"Invalid command '{command}'")


def do_dataset(command, dataset):
    dset = config.datasets[dataset]

    files = [config.DATA_DIR / f"{name}.csv" for name in dset]

    match command:
        case "hists":
            all_hists(files)

        case "fit":
            z, z_err = find_params(files)
            t = np.array([config.config[name]["time"] for name in dset])

            linear_fit(t, z, z_err, dataset=dset)

        case _:
            for file in files:
                do_file(command, file)


def sync(var1, var2):
    var1 = var1 or var2
    var2 = var2 or var1

    return var1, var2


def main(
    command=None,
    dataset=None,
    file=None,
):
    command, config.COMMAND = sync(command, config.COMMAND)

    if dataset:
        dataset, config.DATASET = sync(dataset, config.DATASET)
        do_dataset(command, dataset)

    elif file:
        file = Path(file)
        file, config.FILE = sync(file, config.FILE)
        do_file(command, file)

    else:
        logger.error("Pass either dataset of file, but not both.")
        sys.exit(-1)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("command")
    parser.add_argument("-s", "--dataset")
    parser.add_argument("-f", "--file")
    parser.add_argument("--data")
    parser.add_argument("--saveplot", action='store_true')

    args = parser.parse_args()

    if args.data:
        config.DATA_DIR = Path(args.data)

    if args.saveplot:
        config.SAVE_PLOT = True

    main(
        command=args.command,
        dataset=args.dataset,
        file=args.file,
    )
