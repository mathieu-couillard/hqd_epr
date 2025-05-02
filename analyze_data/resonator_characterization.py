import csv
import os

import matplotlib.pyplot as plt
import numpy as np
import numpy.typing as npt
import pandas as pd
from scipy.constants import physical_constants
from scipy.optimize import curve_fit
from functools import partial

from utils import db_to_lin_amp, reflection_coef_2d, reflection_coef

# from dataclasses import dataclass
# # Make this class if
# @dataclass
# class resonatorSpinEnsembleParameters:
#     freq_cav: float
#     freq_spins: npt.NDArray
#     Q_ext: float
#     Q_int: float
#     g_ens: float
#     gamma: float
#     Delta: float


#####################
# USER COFIGURATION #
#####################

freq_cav = 4.5423412e9
freq_start_lim = 1
freq_stop_lim = -1


##############
# User input #
##############

GLOB = "4p5422GHz_-40dBm"
INITIAL_B_FIELD = 156

###############

FILENAME_BACKGROUND = f"Data/{GLOB}_{INITIAL_B_FIELD}p0mT.csv"
FILENAME_MAG_DATA = f"Data2D_mag_{GLOB}.csv"
FILENAME_PHASE_DATA = f"Data2D_phase_{GLOB}.csv"

################


def read_data(filename: str):
    """Alias to read_data_1d()."""
    return read_data_1d(filename)


def read_data_1d(filename: str):
    """Read 1 dimensional data from file.

    Read data from file consisting of one dependent variable and one
    independent variable.

    Args:
        filename (str): name of file from which Pandas will read from
    Returns:
      data (numpy.array): Dependent variable
      freq (numpy.array): Frequencies

    """
    df = pd.read_csv(filename)

    freq = np.array([f / 1e9 for f in df.iloc[:, 0]])
    data = np.array(df.iloc[:, 1])
    return data, freq


def read_data_2d(filename):
    """Read 2 dimensional data from file."""
    df = pd.read_csv(filename)
    data = df.drop(columns=["Unnamed: 0"]).to_numpy().T
    freqs_GHz = np.array([freq / 1e9 for freq in df["Unnamed: 0"]])
    fields = np.array([float(field) for field in df.columns[1:]])
    return data, freqs_GHz, fields


##################
# Calculate Background
##################


def calculate_background(freq, power, phase, lower_cutoff=100, upper_cutoff=100):
    """Calculate background offsets based on edges of the spectrum."""
    freq_fit = np.concatenate((freq[:lower_cutoff], freq[-1 * upper_cutoff :]))

    db_fit = np.concatenate((power[:lower_cutoff], power[-1 * upper_cutoff :]))
    coefs = np.polyfit(freq_fit, db_fit, 3, rcond=len(freq_fit) * 2e-26)
    power_bg = np.polyval(coefs, np.array(freq))

    phase_fit = np.concatenate((phase[:lower_cutoff], phase[-1 * upper_cutoff :]))
    coefs = np.polyfit(freq_fit, phase_fit, 1, rcond=len(freq_fit) * 2e-26)
    phase_bg = np.polyval(coefs, np.array(freq))
    return power_bg, phase_bg


################
# Remove background
################
# def remove_background(power_in, phase_in, b_fields, power_bg, phase_bg):
#     power_out = np.zeros_like(power_in)
#     phase_out = np.zeros_like(phase_in)
#     for ii, _ in enumerate(b_fields):
#         power_out = power_in[ii, :] - power_bg
#         phase_out = phase_in[ii, :] - phase_bg
#     return power_out, phase_out


################
# calculate 
################


def fit_resonator(
    freqs_GHz: npt.NDArray,
    amp_line_norm: npt.NDArray,  # 2D array
    Q_int: float = 160677,
    Q_ext: float = 9120,
) -> tuple[npt.NDArray, npt.NDArray]:
    omegas = freqs_GHz * (2 * np.pi) * 1e9
    omega_cav = freq_cav * (2 * np.pi)
    kappa_int = omega_cav / Q_int  # internal loss rate
    kappa_ext = omega_cav / Q_ext  # external loss rate reflected port

    p0 = [
        omega_cav,
        kappa_int,
        kappa_ext,
    ]

    return curve_fit(reflection_coef_2d, omegas, amp_line_norm, p0=p0, ftol=1e-30)


def plot(x, y):
    plt.plot(x, y)
    plt.grid(
        visible=True,
        which="major",
        color="gray",
        alpha=0.6,
        linestyle="dashdot",
        lw=1.5,
    )
    plt.minorticks_on()
    plt.grid(visible=True, which="minor", color="beige", alpha=0.8, ls="-", lw=1)
    # plt.show()


if __name__ == "__main__":
    #############
    # Read data #
    #############

    # Use the first frequency sweep to correct background slopes
    data_BG = pd.read_csv(FILENAME_BACKGROUND)

    # Read all data files and reshape the data
    power_db, freqs_GHz, b_fields = read_data_2d(FILENAME_MAG_DATA)
    phase_deg = read_data_2d(FILENAME_PHASE_DATA)[0]
    ########################
    # Calculate background #
    ########################
    # Calculate the background in dB scale to set the far detuned value to 0dB
    power_db_bg, phase_deg_bg = calculate_background(
        freqs_GHz, power_db[0], phase_deg[0]
    )
    #####################
    # Remove background #
    #####################
    power_db -= power_db_bg
    phase_deg -= phase_deg_bg
    # amp_norm, phasedeg = remove_background(
    #     power_db, phase_deg, b_fields, power_db, phase_deg_bg
    # )

    ##########################
    # dB to linear amplitude #
    ##########################
    amp = db_to_lin_amp(power_db)
    phase_rad = phase_deg * np.pi / 180

    # Characterize resonator (kappa, resonance freq, loaded and unloaded Q)
    popt, pcov = fit_resonator(
        freqs_GHz=freqs_GHz[freq_start_lim:freq_stop_lim],
        amp_line_norm=amp[:, freq_start_lim:freq_stop_lim],
    )

    print(popt / (2 * np.pi))
    # exit()
    # plot(freqs_GHz, amp[int(len(amp) / 2 - 1)])
    plot(freqs_GHz, amp[0])
    print(b_fields[0])
    plot(
        freqs_GHz, reflection_coef_2d((freqs_GHz * 2 * np.pi * 1e9, b_fields[0]), *popt)
    )
    plt.show()
    # Characterize spin system (Gamma, g_ens, Cooperativity)
