import numpy as np
import matplotlib.pyplot as plt
import scipy.optimize

from util import show_or_save

plt.rcParams["mathtext.fontset"] = "cm"
plt.rcParams["font.family"] = "STIXGeneral"
plt.rcParams["font.size"] = 17


def linear_fit(t, z, z_err, nofit=False, dataset=None):
    p_opt, p_cov = scipy.optimize.curve_fit(
        lambda x, a, b: a * x + b, t, z, sigma=z_err, absolute_sigma=True
    )

    p_err = np.sqrt(np.diag(p_cov))
    a, b = p_opt
    a_err, b_err = p_err

    plt.errorbar(t, z, yerr=z_err, fmt="o")

    if not nofit:
        plt.plot(
            t,
            a * t + b,
            color="black",
            label="$z(t) = at + b$\n"
            rf"$a = ({a:.1f}\pm{a_err:.1f})$ nm/s"
            "\n"
            rf"$b = ({b:.1f}\pm{b_err:.1f})$ nm/s",
        )

        plt.legend()

    if dataset:
        plt.title(", ".join(dataset))

    plt.xlabel("Tiempo [s]")
    plt.ylabel("Altura comida [nm]")
    plt.tight_layout()
    show_or_save()
