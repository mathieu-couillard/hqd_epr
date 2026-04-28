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
from utils import get_iq_slice_demod

from qm import generate_qua_script

###############
# Experiment config TODO: this should be in experiment config
###############
project_name = "impedance_matching_dpph"
experiment_name = "echo_sequence_func_of_broadening"

base_amp = QMConfig.spin_if_amp

chunck_size = 20 // 4
time_array_size = qm_config.READOUT_LENGTH // (chunck_size * 4)

duration_min = 16 // 4
duration_max = 32 // 4
duration_step = 4 // 4

duration_list = np.arange(duration_min, duration_max + duration_step / 2, duration_step)
n_duration = len(duration_list)

with program() as pi_pulse_calibration:
    qm_us = int(1e3 // 4)
    qm_ms = int(1e6 // 4)

    n = declare(int)

    duration = declare(int)
    duration_st = declare_stream()

    I = declare(fixed, size=time_array_size)
    Q = declare(fixed, size=time_array_size)

    I_st = declare_stream()
    Q_st = declare_stream()

    with for_(*from_array(duration, duration_list)):
        with for_(n, 0, n < n_avg, n + 1):
            align()
            reset_if_phase("spin")
            reset_if_phase("digitizer")
            reset_frame("spin")
            # wait(600//4, "spin") # compensate for time of flight
            play("x90", "spin", duration=duration)
            frame_rotation_2pi(0.25, "spin")
            wait(3000 // 4, "spin")
            play("x180", "spin", duration=duration)
            wait(2250 // 4, "spin")
            align("spin", "CryoSw", "digitizer")
            play("cryosw", "CryoSw")
            I, Q, I_st, Q_st = get_iq_slice_demod(
                time_array_size, chunck_size, I=I, Q=Q, I_st=I_st, Q_st=Q_st
            )

            wait(15_000_000 // 4)
        save(duration, duration_st)
        pause()

    with stream_processing():
        I_st.buffer(time_array_size).buffer(n_avg).map(FUNCTIONS.average()).save_all("I")
        Q_st.buffer(time_array_size).buffer(n_avg).map(FUNCTIONS.average()).save_all("Q")
        duration_st.save("duration")


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
        field=MagConfig.set_field,
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
    t = np.round(
        np.linspace(0, qm_config.READOUT_LENGTH - chunck_size * 4, time_array_size)
    )
    results = fetching_tool(job, data_list=["I", "Q", "duration"], mode="live")
    start_time = time.time()
    while results.is_processing():
        # Set current
        wait_for_next_data(job)
        # Fetch the data from the last OPX run corresponding to the current slow axis iteration
        I, Q, duration = results.fetch_all()
        # Convert results into Volts
        S = u.demod2volts(I + 1j * Q, qm_config.READOUT_LENGTH, single_demod=True)
        amp = np.abs(S)  # Amplitude
        phase = np.angle(S)  # Phase
        print(f"Amplitude: {amp}")
        print(f"Phase: {phase}")

        progress_counter(len(I), n_duration, start_time=start_time)
        # Plot results
        plt.suptitle(f"Hahn echo for {duration*4} ns pulses.")
        plt.subplot(211)
        plt.cla()
        plt.plot(t, amp[-1] * 1e3)
        plt.xlabel("Time [ns]")
        plt.ylabel(r"Echo amp [mV]")
        plt.subplot(212)
        plt.cla()
        plt.plot(t, phase[-1])
        plt.xlabel("Time [ns]")
        plt.ylabel("Echo Phase [rad]")
        plt.ylim(-np.pi, np.pi)
        plt.tight_layout()
        plt.savefig(
            (fig_path / f"pulse_duraiton_{duration * 4: 04d}ns".replace(".", "p"))
        )
        plt.pause(0.1)

        # Save results
        df_I = pd.DataFrame(I, index=duration_list[:len(I)], columns=t).T
        df_I.to_csv((data_path / "I.csv"))
        df_Q = pd.DataFrame(Q, index=duration_list[:len(Q)], columns=t).T
        df_Q.to_csv((data_path / "Q.csv"))
        df_amp = pd.DataFrame(amp, index=duration_list[:len(amp)], columns=t).T
        df_amp.to_csv((data_path / "amp.csv"))
        df_phase = pd.DataFrame(phase, index=duration_list[:len(phase)], columns=t).T
        df_phase.to_csv((data_path / "phase.csv"))
        if duration == duration_list[-1]:
            print("Experiment completed")
            break

    plt.show()
    job.halt()
