import csv
import os
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.optimize import curve_fit
import scipy.special
from matplotlib import colors as mcolors
import colorsys


max_rho = 1.2235e7
currents = [0, 50, 100, 150, 200]


times = {0: "14-05-15", 50: "14-32-43", 100: "15-00-12", 150: "15-27-34", 200: "15-54-56"}


theta_list_dict = {
    0: [
        1.09,
        1.082625,
        1.07525,
        1.067875,
        1.0605,
        1.053125,
        1.05575,
        1.048375,
        1.041,
        1.033625,
        1.02125,
        1.008875,
        0.9985,
        0.987625,
        0.99675,
        0.973375,
        0.958,
        0.945625,
        0.93225,
        0.909875,
        0.8825,
        0.865125,
        0.84275,
        0.823375,
        0.803,
    ],
    50: [
        1.09,
        1.082625,
        1.07525,
        1.067875,
        1.0705,
        1.076125,
        1.05375,
        1.045375,
        1.041,
        1.033625,
        1.01625,
        1.003875,
        0.9955,
        0.991625,
        0.98825,
        0.981175,
        0.969,
        0.946625,
        0.92925,
        0.911875,
        0.8875,
        0.870125,
        0.85275,
        0.835375,
        0.818,
    ],
    100: [
        1.09,
        1.082625,
        1.07525,
        1.067875,
        1.0605,
        1.053125,
        1.04575,
        1.038375,
        1.025,
        1.017625,
        1.00625,
        0.994875,
        0.994,
        0.987625,
        0.99075,
        0.984375,
        0.982,
        0.973625,
        0.95225,
        0.929875,
        0.9025,
        0.885125,
        0.86775,
        0.850375,
        0.833,
    ],
    150: [
        1.09,
        1.082625,
        1.07525,
        1.067875,
        1.0605,
        1.053125,
        1.04075,
        1.028375,
        1.016,
        1.003625,
        0.99725,
        0.992875,
        0.993875,
        0.9905,
        0.99075,
        0.987375,
        0.986,
        0.982625,
        0.97725,
        0.959875,
        0.9275,
        0.902125,
        0.85775,
        0.833375,
        0.798,
    ],
    200: [
        1.09,
        1.082625,
        1.07525,
        1.067875,
        1.0605,
        1.035125,
        1.02775,
        1.010375,
        1.0,
        0.992625,
        0.99425,
        0.987875,
        0.9905,
        0.987125,
        0.98785,
        0.984375,
        0.985,
        0.981625,
        0.98025,
        0.974875,
        0.9645,
        0.940125,
        0.91275,
        0.890375,
        0.863,
    ],
}


def read_spectrum(filename, freq_col=0, amp_col=1, phase_col=2):
    data = pd.read_csv(filename)
    data = data.to_numpy().T
    return data[freq_col], data[amp_col], data[phase_col]


def plot2_top_bottom(
    freqs, data_top, data_bottom, y_label_top="Amp [dB]", y_label_bottom="Phase [rad]"
):
    fig = plt.figure(figsize=(10, 8))
    ax1 = fig.add_subplot(2, 1, 1)
    for i, val in enumerate(data_top):
        ax1.plot(freqs[i] * 1e-9, val)
    ax1.set_xlabel("Frequency [GHz]")
    ax1.set_ylabel(y_label_top)
    plt.grid()
    ax2 = fig.add_subplot(2, 1, 2)
    for i, val in enumerate(data_bottom):
        ax2.plot(freqs[i] * 1e-9, val)
    ax2.set_xlabel("Frequency [GHz]")
    ax2.set_ylabel(y_label_bottom)
    plt.grid()


def remove_background(freq, pow_log, pow_log_bkg, phase, phase_bkg):
    pow_log -= pow_log_bkg
    amp = 10 ** (pow_log / 20)

    frac = 1 / 5

    freq_bkg_subset = np.concatenate(
        (freq[: int(32000 * frac)], freq[int(32000 * (1 - frac)) : -1])
    )
    phase_bkg_subset = np.concatenate(
        (phase_bkg[: int(32000 * frac)], phase_bkg[int(32000 * (1 - frac)) : -1])
    )

    coef = np.polyfit(freq_bkg_subset, phase_bkg_subset, 3)
    p = np.poly1d(coef)
    # print(coef)
    phase_bkg_fit = p(freq)
    phase -= phase_bkg_fit
    # plot2_top_bottom([freq, freq], [pow_log, pow_log_bkg], [phase, phase_bkg])
    # plt.show()
    return amp, phase


def estimate_kernel(omega, r, omega_res, kappa_int, kappa_ext):
    return omega - omega_res + 1j / 2 * (kappa_int + (r - 1) / (r + 1) * kappa_ext)


def gaussian(x, x0, A, sigma, D):
    return A * (np.exp(-((x - x0) ** 2) / 2 / sigma / sigma)) + D


def lorentzian(x, x0, A, HWHM, D):
    return A * (HWHM**2 / ((x - x0) ** 2 + HWHM**2)) + D


def ellipse(x, x0, r, g_ens2):
    arg = ((x - x0) / r) ** 2
    if arg.any() < 1:
        print((x - x0) / r)
        print(r)
    # return g_ens2 * np.sqrt(np.maximum(0,1 - ((x - x0) / r) ** 2))
    return 2 * g_ens2 / (np.pi * r) * np.sqrt(np.maximum(0, 1 - ((x - x0) / r) ** 2))


# Helper function to adjust color lightness
def adjust_color_lightness(color_hex, factor):
    """Adjusts the lightness of a color (e.g., 1.5 for lighter)."""
    rgb = mcolors.to_rgb(color_hex)
    h, l, s = colorsys.rgb_to_hls(*rgb)
    l = max(0, min(1, l * factor))
    new_rgb = colorsys.hls_to_rgb(h, l, s)
    return mcolors.to_hex(new_rgb)


color_iterator = iter(plt.rcParams["axes.prop_cycle"])


def main(current):
    Data_DIR = Path(
        "~/phd/projects/quantum_memory/data/dpph/5k/vna_b-field_scan_various_gradient/200MHz_scan_3_extra_wide_bfield"
        + f"/rutile_cavity_freq_and_Bfield_DPPH_gradient{current}p0mA_{times[current]}/data"
    )

    CAVITY_PATH = Data_DIR / "4p5809095GHz_-30dBm_156p780mT.csv"

    bfield_list = np.arange(161.78, 166.78, 0.2)

    freq_res = 4.5812296e9
    kappa_ext = 4.423e6
    kappa_int = 47e3

    theta_i = 1.029
    theta_f = 0.967
    theta = 0.99
    x = 0.1

    # theta_list = np.linspace(theta_i, theta_f, len(bfield_list))
    # theta_list = np.array(
    #     [
    #         1.09,  # 1 blue
    #         1.082625,  # 2 orange
    #         1.07525,  # 3 green
    #         1.067875,  # 4 red
    #         1.0605 - 0.0,  # 5 purple
    #         1.053125 - 0.0,  # 6 brown
    #         1.04575 - 0.005,  # 7 pink
    #         1.038375 - 0.01,  # 8 gray
    #         1.031 - 0.015,  # 9 yellow
    #         1.023625 - 0.02,  # 10 turquoise
    #         1.01625 - 0.019,  # 11 blue
    #         1.008875 - 0.016,  # 12 orange
    #         0.993875 - 0.0,  # 13 green
    #         0.9945 - 0.004,  # 14 red
    #         0.99175 - 0.001,  # 15 purple
    #         0.987375 + 0.00,  # 16 brown
    #         0.986 + 0.0,  # 17 pink
    #         00.982625 + 0.0,  # 18 gray
    #         00.97725 + 0.0,  # 19 yellow
    #         0.949875 + 0.01,  # 20 turquoise
    #         0.9675 - 0.04,  # 21 blue
    #         0.962125 - 0.06,  # 22 orange
    #         0.95775 - 0.1,  # 23 green
    #         0.953375 - 0.12,  # 24 red
    #         0.948 - 0.15,  # 25 purple
    #     ]
    # )

    theta_list = theta_list_dict[current]

    freq_bkg, pow_log_bkg, phase_bkg_rad = read_spectrum(CAVITY_PATH)
    phase_bkg_rad = ((phase_bkg_rad + np.pi) % (2 * np.pi)) - np.pi
    # print(bfield_list[1] - bfield_list[0])
    freq_window = 28.027e6 * (bfield_list[1] - bfield_list[0])
    freq_step = (freq_bkg[-1] - freq_bkg[0]) / (len(freq_bkg) - 1)
    points_per_spectrum = int(freq_window / freq_step)

    freq_full = []
    rho_full = []
    for i, bfield in enumerate(bfield_list):
        POLARITONS_PATH = Data_DIR / (
            f"4p5809095GHz_-30dBm_{bfield:07.3f}mT".replace(".", "p") + ".csv"
        )

        freq, pow_log, phase_rad = read_spectrum(POLARITONS_PATH)

        phase_rad = ((phase_rad + np.pi) % (2 * np.pi)) - np.pi
        amp, phase = remove_background(freq, pow_log, pow_log_bkg, phase_rad, phase_bkg_rad)

        # We need to rotate it to ensure rho -k.imag has the correct phase.
        r = np.array(amp) * np.exp(-1j * (phase + np.pi * (theta_list[i])))
        k = estimate_kernel(
            freq * 2 * np.pi,
            r,
            freq_res * 2 * np.pi,
            kappa_int * 2 * np.pi,
            kappa_ext * 2 * np.pi,
        )
        rho_i_full = -k.imag / np.pi
        freq_i = np.arange((-freq_window / 2), (freq_window / 2), freq_step) - freq_window * (
            i - len(bfield_list) // 2
        )
        rho_i = rho_i_full[
            (len(rho_i_full) - len(freq_i)) // 2 + 1 : (len(rho_i_full) + len(freq_i)) // 2 + 1
        ]
        # plt.plot(freq_i * 1e-9, rho_i, label="Data")

        freq_full.append(freq_i)
        rho_full.append(rho_i)

    # 1. Manually get the next color property from the iterator
    prop_dict = next(color_iterator)
    data_color_hex = prop_dict["color"]
    # 2. Calculate the lighter color for the fit
    fit_color_hex = adjust_color_lightness(data_color_hex, factor=1.5)

    freq_full = np.concatenate((freq_full[::-1]), axis=0) + 9e6
    rho_full = np.concatenate(rho_full[::-1], axis=0)

    plt.plot(
        freq_full*1e-6 , rho_full / max_rho, label=f"Current: {current} mA", color=data_color_hex
    )
    integral = (freq_full[1] - freq_full[0]) * np.sum(rho_full)
    # print(f"Area: {integral}")

    #############
    # get subset of rho needed for ellipse fitting
    #############
    if current >= 50:
        ellipse_width = 34e6 * current / 200
        bool_mask = np.abs(freq_full) < ellipse_width
        freq_fit = freq_full[bool_mask]
        rho_fit = rho_full[bool_mask]
        # plt.plot(freq_fit * 1e-6, rho_fit / max_rho, color=data_color_hex)

        # fit to ellipse using curve_fit to get spectral radius
        # print("fitting")
        popt, pcov = curve_fit(
            ellipse, freq_fit, rho_fit, p0=[0, ellipse_width, max_rho], maxfev=int(1e8)
        )
        # print(f"popt: {popt}")
        freq_fit = freq_full[np.abs(freq_full) < popt[1]]
        plt.plot(
            (freq_fit + popt[0]) * 1e-6,
            ellipse(freq_fit, 0, popt[1], popt[2]) / max_rho,
            color=fit_color_hex,
        )
    if current == 0:
        freq_range = 30e6
        bool_mask = np.abs(freq_full) < freq_range
        freq_fit = freq_full[bool_mask]
        rho_fit = rho_full[bool_mask]
        # print(freq_fit)
        # plt.plot(freq_fit * 1e-6, rho_fit / max_rho, color=data_color_hex)

        # fit to ellipse using curve_fit to get spectral radius
        popt, pcov = curve_fit(lorentzian, freq_fit, rho_fit, p0=[0, max_rho, 5e6, 0])
        # print(popt)
        freq_fit = freq_full[np.abs(freq_full) < freq_range]
        plt.plot(
            (freq_fit + popt[0]) * 1e-6,
            lorentzian(freq_fit, 0, popt[1], popt[2], popt[3]) / max_rho,
            color=fit_color_hex,
        )


if __name__ == "__main__":
    for current in currents:
        main(current)
    plt.xlim(-50, 50)
    plt.ylim(-0.05, 1.05)
    plt.xlabel("Frequency GHz")
    plt.ylabel("Spin Density [Arb. Units]")
    plt.legend()
    # plt.legend()
    plt.grid()
    plt.savefig("spin_spectral_density.png", transparent=True)
    plt.show()
