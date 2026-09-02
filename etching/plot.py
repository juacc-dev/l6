import matplotlib.pyplot as plt
import numpy as np
from util import meshgrid


def surface(z, pixel_size=1, ax=None, **kwargs):
    x, y = meshgrid(z)
    fig = None

    if ax is None:
        fig = plt.figure()
        ax = fig.add_subplot(111, projection="3d")

    surf = ax.plot_surface(x, y, z, cmap="viridis", **kwargs)

    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_zlabel("Z")

    if fig is not None:
        fig.colorbar(surf, ax=ax, label="Z")

    return ax


def colormap(z, pixel_size=1):
    x = np.arange(0, z.shape[1], pixel_size)
    y = np.arange(0, z.shape[0], pixel_size)

    plt.imshow(
        z,
        cmap="viridis",
        origin="lower",
        extent=[x.min(), x.max(), y.min(), y.max()],
        aspect="auto",
    )

    plt.colorbar(label="Z")


def histogram(z, ax=None):
    if ax is None:
        ax = plt.subplots(1, 1)

    ax.hist(z)

    return ax
