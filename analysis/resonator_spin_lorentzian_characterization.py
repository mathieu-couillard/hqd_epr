import csv
import os

import matplotlib.pyplot as plt
import numpy as np
import numpy.typing as npt
import pandas as pd
from scipy.constants import physical_constants
from scipy.optimize import curve_fit
from functools import partial
from pathlib import Path

from utils import db_to_lin_amp, reflection_2d_resonator_spin


#####################
# USER COFIGURATION #
#####################

# mu_B = physical_constants["Bohr magneton in Hz/T"][0]
# g_e = physical_constants["electron g factor"][0]
# g_DPPH = 2.0037

freq_cav = 4.582152970046483e9
freq_start_lim = 1000
freq_stop_lim = -1000


##############
# User input #
##############
PATH = Path("/home/mathieu/phd/projects/quantum_memory/data/dpph/5k/strong_coupling/")
GLOB = "4p5818GHz_-10dBm"

###############

FILENAME_MAG_DATA = PATH / ("Data2D_mag_" + GLOB + ".csv")
FILENAME_PHASE_DATA = PATH / ("Data2D_phase_" + GLOB + ".csv")

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
# calculate Loaded and unloaded loss rate, cavity frequency, g_ens, Broadening
################


def fit_2d_data(
    freqs: npt.NDArray,
    b_fields: npt.NDArray,
    amp_line_norm: npt.NDArray,  # 2D array
    freq_cav: float,
    b_offset: float = 0,
    kappa_int: float = 0 * 2 * np.pi,
    kappa_ext: float = 4.423e6 * 2 * np.pi,
    g_ens: float = 5 * 2 * np.pi * 10e6,
    inhomo_broad: float = 18 * 2 * np.pi * 1e6,
):
    omegas = freqs * (2 * np.pi)
    omega_cav = freq_cav * (2 * np.pi)

    
    freq_grid, b_grid = np.meshgrid(omegas, b_fields)
    size = freq_grid.shape
    freq_1d = freq_grid.reshape((1, np.prod(size)))
    b_field_1d = b_grid.reshape((1, np.prod(size)))
    x_data = np.vstack((freq_1d, b_field_1d))
    y_data = amp_line_norm.reshape(np.prod(size))


    p0 = [omega_cav,
          b_offset,
          g_ens,
          inhomo_broad,
          # kappa_int,
          #kappa_ext,
          ]
    print("fitting")
    return curve_fit(reflection_2d_resonator_spin, x_data, y_data, p0=p0, ftol=1e-10000)



def plot(x, y, label=""):
    plt.plot(x, y, label=label)
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
    # data_BG = pd.read_csv(FILENAME_BACKGROUND)

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
    # phase_deg = (phase_deg + 360) % 360 #- 180
    # amp_norm, phasedeg = remove_background(
    #     power_db, phase_deg, b_fields, power_db, phase_deg_bg
    # )

    ##########################
    # dB to linear amplitude #
    ##########################
    amp = db_to_lin_amp(power_db)
    phase_rad = phase_deg * np.pi / 180
    
    # Characterize resonator (kappa, resonance freq, loaded and unloaded Q)
    popt, pcov = fit_2d_data(
        freqs=freqs_GHz[freq_start_lim: freq_stop_lim]*1e9,
        b_fields=b_fields,
        amp_line_norm=amp[:, freq_start_lim: freq_stop_lim],
        freq_cav=freq_cav,
    )
    print(popt)
    print(f"Resonance frequency: {popt[0]/(2*np.pi*1e9)} GHz")
    print(f"B-field offset: {popt[1]} mT")
    print(f"Ensemble Coupling: {popt[2]/(2*np.pi*1e6)} MHz")
    print(f"Inhomogenous Broadening: {popt[3]/(2*np.pi*1e6)} MHz")
    # print(f"Internal loss: {popt[4]/(2*np.pi*1e6)} MHz")
    # print(f"External loss: {popt[4]/(2*np.pi*1e6)} MHz")
    # exit()
    #plot(freqs_GHz, amp[int(len(amp) / 2 - 1)])
    c = 520
    plot(freqs_GHz,  amp[c], label="data")
    plot(freqs_GHz, reflection_2d_resonator_spin((freqs_GHz*2*np.pi*1e9, b_fields[c]), *popt), label="fit")
    plt.legend()
    plt.show()
    # Characterize spin system (Gamma, g_ens, Cooperativity)
