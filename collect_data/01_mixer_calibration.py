import time
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pyvisa as visa
# microwave generator path
from qm import QuantumMachinesManager
from qm.qua import *
from qualang_tools.loops import from_array
from qualang_tools.results import fetching_tool, progress_counter
from scipy import optimize, signal
from SignalHound_SA.SignalHound import SignalHound

from config import inst_addresses, qm_config
from config.qm_configs import *
from utils.path_generator import generate_path

n_average = 5e6
with program() as Mixer_Calibration:
    n = declare(int)
    with while_(True):
        pause()
        play("spa", "SPA")
        with for_(n, 0, n < n_average, n + 1):
            play("saturation", "spin")


###################
#    Functions    #
###################
def calib_dc(dc_iq):
    while not job.is_paused():
        time.sleep(0.1)

    qm.set_output_dc_offset_by_element("spin", "I", dc_iq[0])
    qm.set_output_dc_offset_by_element("spin", "Q", dc_iq[1])

    while not job.is_paused():
        time.sleep(0.1)
    job.resume()
    spa.init_now()
    spa.operation_complete()
    valuemarker1 = spa.get_marker(marker=1)  # getmarker(1, frequency=spin_LO)
    valuemarker2 = spa.get_marker(
        marker=2
    )  # getmarker(2, frequency= (spin_IF + spin_LO))
    print(valuemarker1)
    print(valuemarker2)
    return 10 ** ((valuemarker1 - valuemarker2) / 10)


def calc_g_and_phi(g_phi):
    while not job.is_paused():
        time.sleep(0.1)
    qm.set_mixer_correction(
        "mixer_spin1", int(SPIN_IF), int(SPIN_LO), IQ_imbalance(g_phi[0], g_phi[1])
    )

    while not job.is_paused():
        time.sleep(0.1)
    job.resume()
    spa.init_now()
    spa.operation_complete()
    valuemarker3 = spa.get_marker(
        marker=3
    )  # getmarker(3, frequency=(spin_LO - spin_IF))
    valuemarker2 = spa.get_marker(
        marker=2
    )  # getmarker(2, frequency= (spin_IF + spin_LO))
    print(valuemarker3)
    print(valuemarker2)
    return 10 ** ((valuemarker3 - valuemarker2) / 10)


def set_calib_params(mixer: str, dc_I: int, dc_Q: int, g: int, phi: int):
    qm.set_mixer_correction(mixer, int(SPIN_IF), int(SPIN_LO), IQ_imbalance(g, phi))
    qm.set_output_dc_offset_by_element("spin", "I", dc_I)

    qm.set_output_dc_offset_by_element("spin", "Q", dc_Q)


# for the trace collection get_trace


def get_spa_trace():
    while not job.is_paused():
        time.sleep(0.1)
    job.resume()

    return spa.get_data()


############
#   Main   #
############
project_name = "impedance_matching_dpph"
experiment_name = "mixer_calibration"
exp_path = generate_path(project=project_name, exp_name=experiment_name)

# Load instruments
rm = visa.ResourceManager()
qmm = QuantumMachinesManager(host=host_ip)
qm = qmm.open_qm(config)
# Open SPA
spa = SignalHound()
# configure SPA
spa.freq_center(center=spin_LO)
spa.freq_span(span=5 * spin_IF)
# spa.auto_raw_fft_BW(auto='on')
# spa.auto_video_fft_BW(auto='on')
spa.raw_fft_BW(resolution=30e3)
spa.video_fft_BW(resolution=30e3)
spa.freq_step(step=1e6)
spa.ref_level(20)
spa.set_marker(freq=spin_LO, marker=1)
spa.set_marker(freq=spin_LO + spin_IF, marker=2)
spa.set_marker(freq=spin_LO - spin_IF, marker=3)


mixer_name = "mixer_spin1"
# Initaial Guesses and set the parameter
g = -0.02
phi = 0.05  # these are initial values
dc_I = 0.02
dc_Q = -0.02


set_calib_params(mixer, dc_I, dc_Q, g, phi)
job = qm.execute(Mixer_Calibration)
time.sleep(5)

# ## DC calibration 1
dc_res = optimize.minimize(
    calib_dc, [dc_I, dc_Q], method="Nelder-Mead", options={"fatol": 0.01}
)
dc_I = dc_res["x"][0]
dc_Q = dc_res["x"][1]
set_calib_params(mixer, dc_I, dc_Q, g, phi)
print("dc offset calibrated")

# gain and phase calibration 1
g_phi_optimized = optimize.minimize(
    calc_g_and_phi, [g, phi], method="Nelder-Mead", options={"fatol": 0.01}
)
g = g_phi_optimized["x"][0]
phi = g_phi_optimized["x"][1]
set_calib_params(mixer_name, dc_I, dc_Q, g, phi)

# ## DC calibration 2
dc_res = optimize.minimize(calib_dc, [dc_I, dc_Q], method="Nelder-Mead")
dc_I = dc_res["x"][0]
dc_Q = dc_res["x"][1]
set_calib_params(mixer_name, dc_I, dc_Q, g, phi)
print("dc done")

print("dc_I_offset: ", dc_I)
print("dc_Q_offset: ", dc_Q)
print("Mixer gain inbalance: ", g)
print("Mixer phase inbalance: ", phi)

IQ_mix_params = {
    "dc_I": dc_I,
    "dc_Q": dc_Q,
    "g": g,
    "phi": phi,
}
data = get_spa_trace()
path = Path(f"{exp_path}/calibrated_iq_mixer_data.csv")
data.to_csv(path)
# Test this. It might be a useless line assuming the data
# is formated properly.
data = pd.read_csv(path)

# Plot the save data
plt.plot(data["frequency"], data["power(dbm)"], label="After Calibration")
plt.title("After Calibration")
plt.xlabel("Frequency[GHz]")
plt.ylabel("power(dBm)")
plt.legend()
plt.grid()
plt.savefig((exp_path / "Calibration.png"))
plt.savefig((exp_path / "Calibration.svg"))
plt.show()
