import shutil
import time
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pyvisa as visa
from drivers import KeysightE8247C, AMI430Vector, YokogawaGS200
from qm import SimulationConfig
from qm.qua import *
from qm import QuantumMachinesManager

from qualang_tools.plot import interrupt_on_close
from qualang_tools.results import (
    fetching_tool,
    progress_counter,
)
from qualang_tools.units import unit

from config import qm_config
from config import InstrumentAddresses as InstAddr
from config.experiment_config import FreeInductionDecay as FIDconf
from config.experiment_config import MagConfig, EXPERIMENT_BASE_PATH, n_avg, MWConfig
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

print(f"averaging {n_avg}")

chunck_size = 20 // 4
time_array_size = qm_config.READOUT_LENGTH // (chunck_size * 4)

curr_min = 0e-3
curr_max = 150e-3
curr_step = 5e-3

curr_list = np.arange(curr_min, curr_max + curr_step / 2, curr_step)
n_curr = len(curr_list)
print(f"current list length {n_curr}")

freq_center = MWConfig.spin_freq  # 4.5808095e9
freq_span = 25e6
freq_step = 250e3

freq_min = freq_center - 0.5 * freq_span
freq_max = freq_center + 0.5 * freq_span

freq_list = np.arange(freq_min, freq_max + freq_step / 2, freq_step)
n_freq = len(freq_list)
print(f"Frequency list length: {n_freq}")
# print(f"Frequency list: {freq_list}")

with program() as hahn_echo_2d_freq_gradient_scan:
    qm_us = int(1e3 // 4)
    qm_ms = int(1e6 // 4)

    n = declare(int)

    curr_i = declare(int)
    curr_st = declare_stream()

    freq_i = declare(int)
    freq_st = declare_stream()

    I = declare(fixed)
    Q = declare(fixed)
    I_st = declare_stream()
    Q_st = declare_stream()

    with for_(curr_i, 0, curr_i < len(curr_list) + 1, curr_i + 1):
        with for_(freq_i, 0, freq_i < len(freq_list) + 1, freq_i + 1):
            pause()
            with for_(n, 0, n < n_avg, n + 1):
                align()
                reset_if_phase("spin")
                reset_if_phase("digitizer")
                reset_frame("spin")
                # wait(600//4, "spin") # compensate for time of flight
                play("x90", "spin")
                frame_rotation_2pi(0.25, "spin")
                wait(3000 // 4, "spin")
                play("x180", "spin")
                wait(2250 // 4, "spin")

                align("spin", "CryoSw", "digitizer")

                play("cryosw", "CryoSw")
                # wait(448//4, "digitizer")

                I, Q, I_st, Q_st = get_iq_full_demod(I=I, Q=Q, I_st=I_st, Q_st=Q_st)
                wait(20_000_000 // 4)
                save(curr_i, curr_st)
                save(freq_i, freq_st)

    with stream_processing():
        I_st.buffer(n_freq).buffer(n_avg).map(FUNCTIONS.average()).save_all("I")
        Q_st.buffer(n_freq).buffer(n_avg).map(FUNCTIONS.average()).save_all("Q")
        curr_st.save("curr_i")
        freq_st.save("freq_i")


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
        hahn_echo_2d_freq_gradient_scan,
        SimulationConfig(duration=simulation_time),
    )
    results = job.get_simulated_samples()
    plt.figure()
    results.con1.plot()
    plt.show()

else:

    def wait_for_next_data(current_job):
        """
        Resumes and waits until the OPX FPGA reaches the next pause statement.
        Used when the OPX sequence needs to be synchronized with an external parameter sweep.

        :param current_job: the job object.
        """
        print(f"Is pause: {current_job.is_paused()}")
        print(f"Is job running: {current_job._is_job_running()}")
        current_job.resume()
        time.sleep(1)
        while not current_job.is_paused():
            time.sleep(1)
            print("In loop")
            if not current_job._is_job_running():
                print(current_job.execution_report())
                break
        # print("Out of loop")
        time.sleep(1)
        return True

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
    mw_source.power_dBm = MWConfig.spin_lo_power

    grad_source = YokogawaGS200(address=InstAddr.gs200_2, visa_backend="@py")

    qm = qmm.open_qm(qm_config.config)
    path, data_path, fig_path = create_directories(project_name, experiment_name)
    print(path)

    sourceFile = open((path / "debug.py"), "w")
    print(
        generate_qua_script(hahn_echo_2d_freq_gradient_scan, qm_config.config),
        file=sourceFile,
    )
    sourceFile.close()

    time.sleep(1)
    u = unit()
    job = qm.execute(hahn_echo_2d_freq_gradient_scan)
    # Get results from QUA program and initialize live plotting
    fig = plt.figure()
    interrupt_on_close(fig, job)

    for i, curr in enumerate(curr_list):
        for j, freq in enumerate(freq_list):
            print(f"current index: {i}")
            print(f"frequency index: {j}")
            mw_source.freqInHz = freq - qm_config.SPIN_IF
            source_ramp(
                grad_source,
                curr,
            )
            grad_source.operation_complete()
            mw_source.opc()

            time.sleep(1)
            print("resuming")

            wait_for_next_data(job)
            print("paused")
            # Fetch the data from the last OPX run corresponding to the current slow axis iteration
            print(n_curr)
            # if j == n_freq - 1:
        if i == 0:
            start_time = time.time()
            results = fetching_tool(
                job, data_list=["I", "Q", "curr_i", "freq_i"], mode="live"
            )
        I, Q, curr_i, freq_i = results.fetch_all()
        # Convert results into Volts
        S = u.demod2volts(
            I + 1j * Q, qm_config.READOUT_LENGTH, single_demod=True
        )
        amp = np.abs(S)  # Amplitude
        phase = np.angle(S)  # Phase

        progress_counter(freq_i, n_freq, start_time=start_time)
        print(len(freq_list * 1e-9))
        print(amp)
        # Plot results
        plt.suptitle(r"Hahn ehcho for varying frequency and $\Gamma$")
        plt.subplot(211)
        plt.cla()
        plt.plot(freq_list * 1e-9, amp[i,:])
        plt.xlabel("Frequency  [GHz]")
        plt.ylabel(r"Amplitude [V]")
        plt.subplot(212)
        plt.cla()
        plt.plot(freq_list * 1e-9, phase[i,:])
        plt.xlabel("Frequency [GHz]")
        plt.ylabel("Phase [rad]")
        plt.tight_layout()
        plt.savefig((fig_path / f"{(curr * 1e3):06.2f}mA".replace(".", "p")))
        plt.pause(0.1)

        # Save results

        df_I = pd.DataFrame(I, index=curr_list[:i+1], columns=freq_list)
        df_I.to_csv((data_path / "I.csv"))
        df_Q = pd.DataFrame(Q, index=curr_list[:i+1], columns=freq_list)
        df_Q.to_csv((data_path / "Q.csv"))

    job.halt()
