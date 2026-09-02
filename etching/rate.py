import numpy as np
import matplotlib.pyplot as plt
import scipy.optimize

plt.rcParams["mathtext.fontset"] = "cm"
plt.rcParams["font.family"] = "STIXGeneral"
plt.rcParams["font.size"] = 17


def linear_fit(z, z_err):
    t = np.array([31.58, 45.82, 60.03])
    z_err = np.array([7.5896194348802055, 2.074269258363188, 3.2388620141653064])
    z = np.array([ 278.33428541524495, 288.3653204782002, 306.6049519873934 ])

    p_opt, p_cov = scipy.optimize.curve_fit(
        lambda x, m, b: m * x + b, t, z, sigma=z_err, absolute_sigma=True
    )

    p_err = np.sqrt(np.diag(p_cov))
    m, b = p_opt
    m_err, b_err = p_err

    # print(f"m = {m:.2e} +- {m_err:.2e}")
    # print(f"b = {b:.2e} +- {b_err:.2e}")

    plt.errorbar(t, z, yerr=z_err, fmt="o")
    plt.plot(t, m*t+b, color="black", label=
             "$z(t) = at + b$\n"
             fr"$a = ({m:.1f}\pm{m_err:.1f})$ nm/s"
             "\n"
             fr"$b = ({b:.1f}\pm{b_err:.1f})$ nm/s"
         )

    plt.legend()

    plt.xlabel("Tiempo [s]")
    plt.ylabel("Altura comida [nm]")
    plt.tight_layout()
    plt.show()
