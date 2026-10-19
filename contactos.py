import numpy as np
import matplotlib.pyplot as plt
import scipy.optimize
import scipy.stats

pixels_sust = np.array([185, 84, 63, 25])
pixels_cont = np.array([175, 73, 53, 14])
pixels_true = np.array([190, 87, 68, 29])
pixels_midl = np.array([263, 159, 139, 101])

px_err = 2

dist = np.array([500, 200, 150, 100])


def fit_func(x, y):
    p, p_cov = scipy.optimize.curve_fit(lambda x, m, b: m * x + b, y, x)

    return p, np.sqrt(np.diag(p_cov))


def fit_func2(x, y):
    r = scipy.stats.linregress(y, x)

    return (r.slope, r.intercept), (r.stderr, r.intercept_stderr)


def plot(pixels, label, id_max=3):
    p1, err1 = fit_func(dist[:id_max], pixels[:id_max])
    p2, err2 = fit_func2(dist[:id_max], pixels[:id_max])
    plt.errorbar(dist, pixels, yerr=px_err, fmt="o", label=label)
    plt.plot(p1[0] * pixels + p1[1], pixels, color="red", alpha=0.7)
    plt.plot(p2[0] * pixels + p2[1], pixels, color="blue", alpha=0.7)
    print(f"m = {p1[0]}, b = {p1[1]}")
    print(f"m = {p2[0]}, b = {p2[1]}")


# plot(pixels_sust, label="Sustrato")
# plot(pixels_cont, label="Contactos")
plot(pixels_true, label="True")
# plot(pixels_midl, label="Middle")


plt.xlabel(r"Distancia nominal [$\mu$m]")
plt.ylabel(r"Pixeles")
plt.grid()
# plt.legend()
plt.tight_layout()
plt.show()
