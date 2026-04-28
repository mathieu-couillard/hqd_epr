import shutil
import time
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pyvisa as visa
from drivers import KeysightE8247C, AMI430Vector, YokogawaGS200
from qm import LoopbackInterface, SimulationConfig
from qm.qua import *
from qm import QuantumMachinesManager

from qualang_tools.loops import from_array
from qualang_tools.plot import interrupt_on_close
from qualang_tools.results import (
    fetching_tool,
    progress_counter,
)
from qualang_tools.results.data_handler import DataHandler
from qualang_tools.units import unit

from config import qm_config
from config import InstrumentAddresses as InstAddr
from config.experiment_config import FreeInductionDecay as FIDconf
from config.experiment_config import MagConfig, EXPERIMENT_BASE_PATH, n_avg, QMConfig
from config.experiment_config import __file__ as EXPPERIMENT_CONFIG_PATH

from utils import generate_path
from utils import save_data_1d_echo, source_ramp
from utils import get_iq_full_demod

from qm import generate_qua_script

###############
# Experiment config TODO: this should be in experiment config
###############
project_name = "impedance_matching_dpph"
experiment_name = "echo_sequence_func_of_broadening"

base_amp = QMConfig.spin_if_amp

chunck_size = 20 // 4
time_array_size = qm_config.READOUT_LENGTH // (chunck_size * 4)

scale_min = 0
scale_max = 1
scale_step = 0.005

scale_list = np.arange(scale_min, scale_max + scale_step / 2, scale_step)
n_scale = len(scale_list)

with program() as pi_pulse_calibration:
    qm_us = int(1e3 // 4)
    qm_ms = int(1e6 // 4)

    n = declare(int)

    scale = declare(fixed)
    scale_st = declare_stream()

    I = declare(fixed)
    Q = declare(fixed)

    I_st = declare_stream()
    Q_st = declare_stream()

    with for_(*from_array(scale, scale_list)):
        with for_(n, 0, n < n_avg, n + 1):
            align()
            reset_if_phase("spin")
            reset_if_phase("digitizer")
            reset_frame("spin")
            # wait(600//4, "spin") # compensate for time of flight
            play("x90" * amp(scale), "spin")
            frame_rotation_2pi(0.25, "spin")
            wait(3000 // 4, "spin")
            play("x180" * amp(scale), "spin")
            wait(2250 // 4, "spin")

            align("spin", "CryoSw", "digitizer")

            play("cryosw", "CryoSw")
            # wait(448//4, "digitizer")

            I, Q, I_st, Q_st = get_iq_full_demod(I=I, Q=Q, I_st=I_st, Q_st=Q_st)

            wait(15_000_000 // 4)
        save(scale, scale_st)

    with stream_processing():
        I_st.buffer(n_avg).map(FUNCTIONS.average()).save_all("I")
        Q_st.buffer(n_avg).map(FUNCTIONS.average()).save_all("Q")
        scale_st.save("scale")


# TODO: This should be in the utils
def create_directories(project, exp_name):
    path, data_path, fig_path = generate_path(
        project=project, exp_name=exp_name, basepath=EXPERIMENT_BASE_PATH
    )
    config_path = qm_config.__file__
    shutil.copy(__file__, f"{str(path / Path(__file__).name)}")
    shutil.copy(config_path, f"{str(path / Path(config_path).name)}")
    shutil.copy(
        EXPPERIMENT_CONFIG_PATH, f"{str(path / Path(EXPPERIMENT_CONFIG_PATH).name)}"
    )
    return path, data_path, fig_path


rm = visa.ResourceManager()
qmm = QuantumMachinesManager(host=InstAddr.qm)


simulate = False

if simulate:
    simulation_time = 12000 // 4
    job = qmm.simulate(
        config,
        pi_pulse_calibration,
        SimulationConfig(duration=simulation_time),
    )
    results = job.get_simulated_samples()
    plt.figure()
    results.con1.plot()
    plt.show()

else:
    # Setup magnets
    mag_addr = (InstAddr.mag_x, InstAddr.mag_y, InstAddr.mag_z)
    magnets = AMI430Vector(mag_addr)
    magnets.ramp_spherical(
        field=MagConfig.field,
        thetaDeg=MagConfig.theta,
        phiDeg=MagConfig.phi,
        ramp_rate=MagConfig.ramp_rate,
    )

    # Set up microwave
    mw_source = KeysightE8247C(InstAddr.mw_source)
    mw_source.freqInHz = FIDconf.spin_lo_freq  # - 2 * qm_config.SPIN_IF
    mw_source.power_dBm = FIDconf.spin_lo_power

    qm = qmm.open_qm(qm_config.config)
    path, data_path, fig_path = create_directories(project_name, experiment_name)
    print(path)

    sourceFile = open((path / "debug.py"), "w")
    print(
        generate_qua_script(pi_pulse_calibration, qm_config.config),
        file=sourceFile,
    )
    sourceFile.close()

    u = unit()
    job = qm.execute(pi_pulse_calibration)
    time.sleep(1)
    # Get results from QUA program and initialize live plotting
    fig = plt.figure()
    interrupt_on_close(fig, job)
    
    results = fetching_tool(job, data_list=["I", "Q", "scale"], mode="live")
    while results.is_processing():
        # Set current
        time.sleep(1)
        # Fetch the data from the last OPX run corresponding to the current slow axis iteration
        I, Q, scale = results.fetch_all()
        # Convert results into Volts
        S = u.demod2volts(I + 1j * Q, qm_config.READOUT_LENGTH, single_demod=True)
        amp = np.abs(S) # Amplitude
        phase = np.angle(S) # Phase
        print(f"Amplitude: {amp}")
        print(f"Phase: {phase}")

        progress_counter(len(I), n_scale, start_time=results.get_start_time())
        # Plot results
        plt.suptitle(r"Hahn ehcho sequence for different $\Gamma$")
        plt.subplot(211)
        plt.cla()
        plt.plot(scale_list[: len(amp)] * base_amp, amp*1e3)
        plt.xlabel("Pulse Amp [V]")
        plt.ylabel(r"Echo Amp [mV]")
        plt.subplot(212)
        plt.cla()
        plt.plot(scale_list[: len(phase)] * base_amp, phase)
        plt.xlabel("Pulse Amp [V]")
        plt.ylabel("Echo Phase [rad]")
        plt.tight_layout()
        plt.savefig((fig_path / f"Amplitude{scale * base_amp*1e3:06.2f}mv".replace(".", "p")))
        plt.pause(0.1)

    # Save results
    df_I = pd.DataFrame(I, index=scale_list)
    df_I.to_csv((data_path / "I.csv"))
    df_Q = pd.DataFrame(Q, index=scale_list)
    df_Q.to_csv((data_path / "Q.csv"))
    print("Experiment completed")

    plt.show()
    job.halt()
