import matplotlib.pyplot as plt
import numpy as np
import pylabo

anchos = [25]
dist = []

pylabo.defaults()
plt.rcParams["font.size"] = 10
plt.rcParams["figure.figsize"] = (9, 7)


class Foto:
    def __init__(self, ancho_um, ancho_px, dist_px, err_px):
        self.ancho_um = float(ancho_um)
        self.ancho_px = float(ancho_px)
        self.dist_px = np.array(dist_px, dtype=float)
        self.err_px = err_px

        self.dist = self.ancho_um * self.dist_px / self.ancho_px
        self.dist_err = (
            self.dist * err_px * np.sqrt(self.dist_px**-2 + self.ancho_px**-2)
        )


def promedio(fotos: list[Foto]):
    dists = np.array([foto.dist for foto in fotos])
    dists_err = np.array([foto.dist_err for foto in fotos])

    dist = np.average(dists, axis=0, weights=1 / dists_err)
    variance = np.average((dists - dist) ** 2, axis=0, weights=1 / dists_err)

    return dist, np.sqrt(variance)


fotos = {
    "ETH#7-100": Foto(ancho_um=100, ancho_px=25, dist_px=[19, 44, 57, 125], err_px=2),
    "M9#1-100": Foto(ancho_um=100, ancho_px=25, dist_px=[19, 47, 60, 130], err_px=4),
    "TEST#5-100": Foto(ancho_um=100, ancho_px=33, dist_px=[26, 59, 76, 161], err_px=1),
}

print(promedio(fotos.values()))
