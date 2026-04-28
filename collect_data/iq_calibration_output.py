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
    wait_until_job_is_paused,
)
from qualang_tools.results.data_handler import DataHandler
from qualang_tools.units import unit

from config import qm_config
from config import InstrumentAddresses as InstAddr
from config.experiment_config import FreeInductionDecay as FIDconf
from config.experiment_config import MagConfig, EXPERIMENT_BASE_PATH, n_avg
from config.experiment_config import __file__ as EXPPERIMENT_CONFIG_PATH

from utils import generate_path
from utils import save_data_1d_echo, source_ramp
from utils import get_iq_full_demod, get_iq_slice_demod

from qm import generate_qua_script

###############
# Experiment config TODO: this should be in experiment config
###############
project_name = "impedance_matching_dpph"
experiment_name = "iq_inbalance_measurement_output.py"


chunck_size = 20 // 4
time_array_size = qm_config.READOUT_LENGTH // (chunck_size * 4)

with program() as iq_calibration_output:
    qm_us = int(1e3 // 4)
    qm_ms = int(1e6 // 4)

    n = declare(int)

    I = declare(fixed, size=time_array_size)
    Q = declare(fixed, size=time_array_size)

    I_st = declare_stream()
    Q_st = declare_stream()

    with for_(n, 0, n < n_avg, n + 1):
        align()
        reset_if_phase("spin")
        reset_if_phase("digitizer")
        reset_frame("spin")

        play("x90" * amp(0.01), "spin")
        frame_rotation_2pi(0.25, "spin")
        play("x90" * amp(0.01), "spin")
        frame_rotation_2pi(0.25, "spin")
        play("x90" * amp(0.01), "spin")
        frame_rotation_2pi(0.25, "spin")
        play("x90" * amp(0.01), "spin")

        I, Q, I_st, Q_st = get_iq_slice_demod(
            time_array_size, chunck_size, I=I, Q=Q, I_st=I_st, Q_st=Q_st
        )
        wait(15_000_000 // 4)

    with stream_processing():
        I_st.buffer(time_array_size).buffer(n_avg).map(FUNCTIONS.average()).save_all(
            "I"
        )
        Q_st.buffer(time_array_size).buffer(n_avg).map(FUNCTIONS.average()).save_all(
            "Q"
        )


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
        iq_calibration_output,
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
        field=MagConfig.field-2,
        thetaDeg=MagConfig.theta,
        phiDeg=MagConfig.phi,
        ramp_rate=MagConfig.ramp_rate,
    )

    # Set up microwave
    mw_source = KeysightE8247C(InstAddr.mw_source)
    mw_source.freqInHz = FIDconf.spin_lo_freq - qm_config.SPIN_IF
    mw_source.power_dBm = FIDconf.spin_lo_power

    qm = qmm.open_qm(qm_config.config)
    path, data_path, fig_path = create_directories(project_name, experiment_name)
    print(path)

    sourceFile = open((path / "debug.py"), "w")
    print(
        generate_qua_script(iq_calibration_output, qm_config.config),
        file=sourceFile,
    )
    sourceFile.close()

    time.sleep(1)
    u = unit()
    job = qm.execute(iq_calibration_output)
    # Get results from QUA program and initialize live plotting
    fig = plt.figure()
    interrupt_on_close(fig, job)
    t = np.round(
        np.linspace(0, qm_config.READOUT_LENGTH - chunck_size * 4, time_array_size)
    )

    results = fetching_tool(job, data_list=["I", "Q"], mode="live")
    start_time = time.time()
    while results.is_processing():
        magnets.amiz.operation_complete()
        time.sleep(1)
        # Fetch the data from the last OPX run corresponding to the current slow axis iteration
        I, Q  = results.fetch_all()
        # Convert results into Volts
        S = u.demod2volts(I + 1j * Q, qm_config.READOUT_LENGTH, single_demod=True)[0]
        amp = np.abs(S)
        phase = np.angle(S)
        I = S.real
        Q = S.imag
        print(t)
        print(amp)
        print(phase)

        # Plot results
        plt.suptitle(r"Hahn ehcho sequence for different $\Gamma$")
        plt.subplot(211)
        plt.cla()
        plt.plot(t, I)
        plt.xlabel("Time [ns]")
        plt.ylabel(r"I [V]")
        plt.subplot(212)
        plt.cla()
        plt.plot(t, Q)
        plt.xlabel("Time [ns]")
        plt.ylabel("Q [V]")
        plt.tight_layout()
        plt.savefig((fig_path / "pulses_90_degree_phase_chage"))
        plt.pause(0.1)

        # Save results
        df = pd.DataFrame([I, Q, amp, phase], columns=t, index=["I","Q","amp", "phase"])
        df.to_csv((data_path / "data.csv"))

    print("Experiment completed")
    plt.show()
    job.halt()
