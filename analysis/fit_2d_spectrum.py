from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.optimize import curve_fit

# --- Physical Constants for DPPH ---
GYRO_RATIO = 28.042 * 1e-3  # GHz/mT
GAMMA_E_RAD = 28.042 * 2 * np.pi * 1e6  # rad/(s*mT)

# --- Configuration ---
CSV_STRONG = Path("./Data2D_mag_4p5809095GHz_-10dBm_strong.csv")
CSV_WEAK = Path("./Data2D_mag_4p5809095GHz_-10dBm_weak.csv")
CALIBRATION_COLUMN = "158.6"


def k_lorentzian(omega, omega_spins, g_ens, gamma_fwhm):
    return g_ens**2 / (omega - omega_spins + 0.5j * gamma_fwhm)


def reflection_model_db(coords, omega_res, b_offset, g_ens, gamma_fwhm, kappa_ext_fwhm):
    omega, b_field = coords
    kappa_int_fwhm = 5000 * 2 * np.pi
    omega_spins = GAMMA_E_RAD * (b_field - b_offset)
    k_func = k_lorentzian(omega, omega_spins, g_ens, gamma_fwhm)
    numerator = 1j * kappa_ext_fwhm
    denominator = (omega - omega_res) + 0.5j * (kappa_ext_fwhm + kappa_int_fwhm) - k_func
    r_linear = numerator / denominator - 1
    return 20 * np.log10(np.abs(r_linear) + 1e-12)


def get_reflection_minima_traces_dissipative(b_axis, f_cav, b_off, g_ens, gamma, k_total):
    """
    Analytical traces using Dissipative Coupled Mode Theory.
    Units: Consistent (GHz or MHz).
    f_cav, gamma, k_total are FWHM.
    """
    f_spins = GYRO_RATIO * (b_axis - b_off)

    # Define complex components (using HWHM for the complex plane calculation)
    # wc = f_cav - i * (kappa/2)
    # ws = f_spins - i * (gamma/2)

    avg_real = (f_cav + f_spins) / 2
    avg_imag = -1j * (k_total + gamma) / 4

    diff_real = (f_cav - f_spins) / 2
    diff_imag = -1j * (k_total - gamma) / 4

    # The term under the square root includes the difference in decay rates
    term = np.sqrt((g_ens) ** 2 + (diff_real + diff_imag) ** 2)

    z_plus = (avg_real + avg_imag) + term
    z_minus = (avg_real + avg_imag) - term

    # Return the real parts (the observable branch frequencies)
    return np.real(z_plus), np.real(z_minus)


def print_results(label, popt, perr):
    f_res_ghz = popt[0] / (2 * np.pi * 1e9)
    f_err_ghz = perr[0] / (2 * np.pi * 1e9)

    b_offset = popt[1]
    b_err = perr[1]

    g_mhz = popt[2] / (2 * np.pi * 1e6)
    g_err = perr[2] / (2 * np.pi * 1e6)

    gamma_mhz = popt[3] / (2 * np.pi * 1e6)
    gamma_err = perr[3] / (2 * np.pi * 1e6)

    kappa_e_mhz = popt[4] / (2 * np.pi * 1e6)
    kappa_e_err = perr[4] / (2 * np.pi * 1e6)

    k_total_rad = popt[4] + (5000 * 2 * np.pi)
    coop = (4 * popt[2] ** 2) / (k_total_rad * popt[3])

    print(f"\n--- {label} Results (DPPH g=2.0036) ---")
    print(f"Resonator Frequency: {f_res_ghz:.6f} ± {f_err_ghz:.6f} GHz")
    print(f"Calculated B-Offset: {b_offset:.4f} ± {b_err:.4f} mT")
    print(f"Coupling (g):        {g_mhz:.3f} ± {g_err:.3f} MHz")
    print(f"Spin Broadening (y): {gamma_mhz:.3f} ± {gamma_err:.3f} MHz")
    print(f"Kappa_ext:           {kappa_e_mhz:.3f} ± {kappa_e_err:.3f} MHz")
    print(f"Cooperativity (C):   {coop:.3f}")


def fit_strong(csv_path):
    df = pd.read_csv(csv_path, header=0, index_col=0)
    df_fit = (
        df.sub(df[CALIBRATION_COLUMN], axis=0).drop(columns=[CALIBRATION_COLUMN])
        if CALIBRATION_COLUMN in df.columns
        else df
    )
    freq = df_fit.index.astype(float).values
    b_vec = df_fit.columns.astype(float).values
    B_mesh, Omega_mesh = np.meshgrid(b_vec, freq * 2 * np.pi)

    m_rad = 1e6 * 2 * np.pi
    p0 = [freq.mean() * 2 * np.pi, 1.0, 5 * m_rad, 2 * m_rad, 4 * m_rad]
    lower = [freq.min() * 2 * np.pi, -5.0, m_rad, m_rad, m_rad]
    upper = [freq.max() * 2 * np.pi, 5.0, 10 * m_rad, 100 * m_rad, 10 * m_rad]

    popt, pcov = curve_fit(
        reflection_model_db,
        (Omega_mesh.ravel(), B_mesh.ravel()),
        df_fit.values.ravel(),
        p0=p0,
        bounds=(lower, upper),
    )
    perr = np.sqrt(np.diag(pcov))

    fit_vals = reflection_model_db((Omega_mesh.ravel(), B_mesh.ravel()), *popt).reshape(
        df_fit.shape
    )
    return df_fit, fit_vals, b_vec, freq, popt, perr


def fit_weak_fixed(csv_path, g_fixed, kappa_fixed):
    df = pd.read_csv(csv_path, header=0, index_col=0)
    df_fit = (
        df.sub(df[CALIBRATION_COLUMN], axis=0).drop(columns=[CALIBRATION_COLUMN])
        if CALIBRATION_COLUMN in df.columns
        else df
    )
    freq = df_fit.index.astype(float).values
    b_vec = df_fit.columns.astype(float).values
    B_mesh, Omega_mesh = np.meshgrid(b_vec, freq * 2 * np.pi)

    def model_fixed(coords, omega_res, b_offset, gamma_fwhm):
        return reflection_model_db(coords, omega_res, b_offset, g_fixed, gamma_fwhm, kappa_fixed)

    m_rad = 1e6 * 2 * np.pi
    p0 = [freq.mean() * 2 * np.pi, 1.0, 2 * m_rad]
    lower = [freq.min() * 2 * np.pi, -5.0, m_rad]
    upper = [freq.max() * 2 * np.pi, 5.0, 100 * m_rad]

    popt_weak, pcov_weak = curve_fit(
        model_fixed,
        (Omega_mesh.ravel(), B_mesh.ravel()),
        df_fit.values.ravel(),
        p0=p0,
        bounds=(lower, upper),
    )
    perr_weak = np.sqrt(np.diag(pcov_weak))

    popt_full = [popt_weak[0], popt_weak[1], g_fixed, popt_weak[2], kappa_fixed]
    perr_full = [perr_weak[0], perr_weak[1], 0.0, perr_weak[2], 0.0]

    fit_vals = reflection_model_db((Omega_mesh.ravel(), B_mesh.ravel()), *popt_full).reshape(
        df_fit.shape
    )
    return df_fit, fit_vals, b_vec, freq, popt_full, perr_full


# --- Execution ---
res_s = fit_strong(CSV_STRONG)
print_results("Strong Coupling", res_s[4], res_s[5])

g_fix, k_fix = res_s[4][2], res_s[4][4]
res_w = fit_weak_fixed(CSV_WEAK, g_fix, k_fix)
print_results("Weak Coupling (Fixed g, ke)", res_w[4], res_w[5])

# --- Plotting ---
fig, axes = plt.subplots(2, 2, figsize=(16, 12), sharex="col", sharey="row")
results = [res_s, res_w]

for i, res in enumerate(results):
    df_data, fit_vals, b_vec, freq, popt, perr = res
    b_phys = b_vec - popt[1]
    extent = [b_phys.min(), b_phys.max(), freq.min() / 1e9, freq.max() / 1e9]
    label = "Strong" if i == 0 else "Weak (Fixed g, ke)"

    # --- NEW: High-resolution axis for traces only ---
    b_fine = np.linspace(b_vec.min(), b_vec.max(), len(b_vec) * 10)
    b_phys_fine = b_fine - popt[1]

    f_cav_ghz = popt[0] / (2 * np.pi * 1e9)
    g_ghz = popt[2] / (2 * np.pi * 1e9)
    gamma_ghz = popt[3] / (2 * np.pi * 1e9)
    k_total_ghz = (popt[4] + (5000 * 2 * np.pi)) / (2 * np.pi * 1e9)

    # Use the new Dissipative function here
    a = 0.9
    b = 0.85
    z_p, z_m = get_reflection_minima_traces_dissipative(
        b_fine, f_cav_ghz, popt[1], g_ghz * a, gamma_ghz * a / b, k_total_ghz * b
    )

    for row, img_data in enumerate([df_data.values, fit_vals]):
        ax = axes[row, i]
        im = ax.imshow(img_data, extent=extent, aspect="auto", origin="lower", cmap="RdBu_r")

        # Plot using the fine-grained data
        ax.plot(b_phys_fine, z_p, "k--", alpha=0.8, lw=1.5)
        ax.plot(b_phys_fine, z_m, "k--", alpha=0.8, lw=1.5)


axes[0, 0].set_ylabel("Frequency (GHz)")
axes[1, 0].set_ylabel("Frequency (GHz)")
plt.tight_layout()
plt.show()
