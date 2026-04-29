import csv
import os

import matplotlib.pyplot as plt
import numpy as np
import numpy.typing as npt
import pandas as pd
from pathlib import Path
from scipy.constants import physical_constants
from scipy.optimize import curve_fit
from functools import partial

from utils import db_to_lin_amp, reflection_resonator_phase

#####################
# USER COFIGURATION #
#####################

freq_cav = 4.581229600e9
freq_start_lim = 0
freq_stop_lim = -1


##############
# User input #
##############
Data_DIR = Path(
    "~/phd/projects/quantum_memory/data/dpph/5k/vna_b-field_scan_various_gradient/200MHz_scan_2/"
    + f"rutile_cavity_freq_and_Bfield_DPPH_gradient0p0mA_09-32-43/data"
)
FILENAME = Data_DIR / "4p5809095GHz_-30dBm_157p780mT.csv"


################


def read_data(filename: Path):
    """Read 1 dimensional data from file.

    Read data from file consisting of one dependent variable and one
    independent variable.

    Args:
        filename (Path): name of file from which Pandas will read from
    Returns:
      data (numpy.array): Dependent variable
      freq (numpy.array): Frequencies

    """
    df = pd.read_csv(filename)

    freq = np.array([f / 1e9 for f in df.iloc[:, 0]])
    log_mag = np.array(df.iloc[:, 1])
    phase = np.array(df.iloc[:, 2])

    print(f"number of data points: {len(freq)}")
    return freq, log_mag, -phase


##################
# Calculate Background
##################


def calbirate_phase(freq, phase) -> npt.NDArray:
    """Calibrate the phase to be compatible with reflection_resonator_phase().

    Set phase to zero far off resonance and flip if phase is cycling the
    wrong direction.

    """
    # Remove the offset. Far off resonance, phase needs to be zero to average.
    if np.abs(phase[-1] - phase[0]) > np.pi:
        print("shifting")
        phase = (phase + 2 * np.pi) % (2 * np.pi) - np.pi
    phase -= np.average([phase[0], phase[-1]])
    # Shift phase offset to be compatible with reflection_resonator_phase().
    phase = (phase + 2 * np.pi) % (2 * np.pi) - np.pi
    # The VNA data usually subtracts the phase from the LO.
    # if np.argmax(phase) < np.argmin(phase):
        # phase *= -1
    return phase


################
# calculate
################


def fit_resonator(
    freqs_GHz: npt.NDArray,
    amp_line_norm: npt.NDArray,  # 2D array
    phase: npt.NDArray,
    Q_int: float = 1e5,
    Q_ext: float = 1000,
    offset: float = 0,
    delay: float = 0,
) -> tuple[npt.NDArray, npt.NDArray]:
    omegas = freqs_GHz * (2 * np.pi) * 1e9
    omega_cav = freq_cav * (2 * np.pi)
    kappa_int = omega_cav / Q_int  # internal loss rate
    kappa_ext = omega_cav / Q_ext  # external loss rate reflected port

    p0 = [
        omega_cav,
        kappa_int,
        kappa_ext,
        offset,
        delay,
    ]

    return curve_fit(reflection_resonator_phase, omegas, phase, p0=p0, ftol=1e-100000)


def remove_background(freq, phase):
    freq_bkg_subset = np.concatenate(
        (freq[: int(32000 / 3)], freq[int(32000 * 2 / 3) : -1])
    )
    phase_bkg_subset = np.concatenate(
        (phase[: int(32000 / 3)], phase[int(32000 * 2 / 3) : -1])
    )
    coef = np.polyfit(freq_bkg_subset, phase_bkg_subset, 5)
    p = np.poly1d(coef)
    phase_bkg_fit = p(freq)
    phase -= phase_bkg_fit
    return phase


def plot(x, y, label=""):
    plt.plot(x, y, label=label)
    # plt.grid(
    #     visible=True,
    #     which="major",
    #     color="gray",
    #     alpha=0.6,
    #     linestyle="dashdot",
    #     lw=1.5,
    # )
    plt.legend()
    plt.xlabel("Frequency (GHz)")
    plt.ylabel("Phase (rad)")
    # plt.minorticks_on()
    # plt.grid(visible=True, which="minor", color="beige", alpha=0.8, ls="-", lw=1)
    # plt.show()


if __name__ == "__main__":
    #############
    # Read data #
    #############


    # Read all data files and reshape the data
    freq_GHz, power_db, phase_rad = read_data(FILENAME)
    phase_rad = remove_background(freq_GHz, phase_rad)

    freq_GHz = freq_GHz[32000 // 3 : 32000 * 2 // 3]
    phase_rad = phase_rad[32000 // 3 : 32000 * 2 // 3]

    phase_rad = calbirate_phase(freq_GHz, phase_rad)

    ##########################
    # dB to linear amplitude #
    ##########################
    amp = db_to_lin_amp(power_db)
    # Gamma = 1*np.exp(1j*phase_rad)
    # Z_in = 50*(1+Gamma)/(1-Gamma)
    # plt.plot(freq_GHz, Z_in)
    # plt.show()
    
    # Characterize resonator (kappa, resonance freq, loaded and unloaded Q)
    popt, pcov = fit_resonator(
        freqs_GHz=freq_GHz[freq_start_lim:freq_stop_lim],
        amp_line_norm=amp[freq_start_lim:freq_stop_lim],
        phase=phase_rad[freq_start_lim:freq_stop_lim],
    )
    
    print(f"resonance freq: {popt[0] / (2 * np.pi * 1e6)} MHz")
    print(f"kappa internal: {popt[1] / (2 * np.pi * 1e6)} MHz")
    print(f"kappa external: {popt[2] / (2 * np.pi * 1e6)} MHz")
    print(f"Phase offset: {popt[3]} rad")
    print(f"Delay: {popt[4]} s")
    
    plot(freq_GHz, phase_rad, label="data")
    plot(
        freq_GHz,
        reflection_resonator_phase((freq_GHz * 2 * np.pi * 1e9), *popt),
        label="fit",
    )
    # plot(
    #     freq_GHz, reflection_resonator_phase((freq_GHz * 2 * np.pi * 1e9), *popt), label='fit'
    # )
    plt.legend()
    output_filename = FILENAME.parent / "phase_fit"
    # plt.savefig(output_filename)
    plt.show()

    # Characterize spin system (Gamma, g_ens, Cooperativity)
