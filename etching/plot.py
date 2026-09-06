import matplotlib.pyplot as plt
import numpy as np
from util import meshgrid


def surface(z, pixel_size=1, ax=None, title=None, **kwargs):
    x, y = meshgrid(z, pixel_size)
    fig = None

    if ax is None:
        fig = plt.figure(tight_layout=True)
        ax = fig.add_subplot(111, projection="3d")

    surf = ax.plot_surface(x, y, z, cmap="viridis", **kwargs)

    ax.set_xlabel(r"X [$\mu$m]")
    ax.set_ylabel(r"Y [$\mu$m]")
    ax.set_zlabel("Z [nm]")
    ax.set_title(title)

    # if fig is not None:
    #     fig.colorbar(surf, ax=ax, label="Z")

    return ax


def colormap(z, pixel_size=1, title=None):
    x = np.arange(0, z.shape[1]) * pixel_size
    y = np.arange(0, z.shape[0]) * pixel_size

    plt.imshow(
        z,
        cmap="viridis",
        origin="lower",
        extent=[x.min(), x.max(), y.min(), y.max()],
        aspect="auto",
    )
    plt.xlabel(r"X [$\mu$m]")
    plt.ylabel(r"Y [$\mu$m]")
    plt.title(title)

    plt.colorbar(label="Z [nm]")


def histogram(z, ax=None):
    if ax is None:
        ax = plt.subplots(1, 1)

    ax.hist(z)

    return ax
