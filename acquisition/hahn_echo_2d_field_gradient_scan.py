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
curr_max = 2e-3
curr_step = 1e-3

curr_list = np.arange(curr_min, curr_max + curr_step / 2, curr_step)
n_curr = len(curr_list)
print(f"current list length {n_curr}")

b_field_min = 164.54
b_field_max = 165
b_field_step = 2

b_field_list = np.arange(b_field_min, b_field_max+b_field_step/2, b_field_step)
n_b_field = len(b_field_list)
print(f"B field list length {n_b_field}")

with program() as hahn_echo_amplitude_vary_gamma:
    qm_us = int(1e3 // 4)
    qm_ms = int(1e6 // 4)

    n = declare(int)

    curr_i = declare(int)
    curr_st = declare_stream()

    # b_field_i = declare(int)
    # b_field_st = declare_stream()

    j = declare(int)
    I1 = declare(fixed, size=time_array_size)
    Q1 = declare(fixed, size=time_array_size)
    I2 = declare(fixed, size=time_array_size)
    Q2 = declare(fixed, size=time_array_size)

    
    I = declare(fixed, size=time_array_size)
    Q = declare(fixed, size=time_array_size)
    I_st = declare_stream()
    Q_st = declare_stream()

    # with for_(b_field_i, 0, b_field_i<len(b_field_list)+1, b_field_i+1):
    with for_(curr_i, 0, curr_i<len(curr_list)+1, curr_i+1):
        pause()
        with for_(n, 0, n < n_avg, n+1):
            align()
            reset_if_phase("spin")
            reset_if_phase("digitizer")
            reset_frame("spin")

            wait(400 // 4, "spin")  # compensate for time of flight
            measure(
                "readout",
                "digitizer",
                demod.sliced("cos", I1, chunck_size, "out1"),
                demod.sliced("sin", Q1, chunck_size, "out1"),
                demod.sliced("cos", Q2, chunck_size, "out2"),
                demod.sliced("sin", I2, chunck_size, "out2"),
            )

            play("x90", "spin")
            frame_rotation_2pi(0.25, "spin")
            wait(3000 // 4, "spin")
            play("x180", "spin")
            wait(2250 // 4, "spin")

            align("spin", "CryoSw")
            play("cryosw", "CryoSw")
            wait(15_000_000 // 4)
            with for_(j, 0, j < time_array_size, j + 1):
                assign(I[j], I1[j] + I2[j])
                assign(Q[j], Q1[j] - Q2[j])
                save(I[j], I_st)
                save(Q[j], Q_st)


    with stream_processing():
        I_st.buffer(time_array_size).buffer(n_avg).map(FUNCTIONS.average()).save_all(
            "I"
        )
        Q_st.buffer(time_array_size).buffer(n_avg).map(FUNCTIONS.average()).save_all(
            "Q"
        )
        curr_st.save("curr_i")
        # b_field_st.save("b_field_i")


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
        hahn_echo_amplitude_vary_gamma,
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
        field=MagConfig.set_field,
        thetaDeg=MagConfig.theta,
        phiDeg=MagConfig.phi,
        ramp_rate=MagConfig.ramp_rate
    )

    # Set up microwave
    mw_source = KeysightE8247C(InstAddr.mw_source)
    mw_source.freqInHz = FIDconf.spin_lo_freq  # - qm_config.SPIN_IF
    mw_source.power_dBm = FIDconf.spin_lo_power

    grad_source = YokogawaGS200(address=InstAddr.gs200_2, visa_backend="@py")

    # # Set up spectrum analyzer
    # spa = KeysightN9010A(InstAddr.spa)
    # spa.centerFreqInHz = qm_config.SPIN_LO + qm_config.SPIN_IF

    # spa.spanInHz = 5e6
    # spa.resBWInHz = 0.01e6

    qm = qmm.open_qm(qm_config.config)
    path, data_path, fig_path = create_directories(project_name, experiment_name)
    print(path)

    sourceFile = open((path / "debug.py"), "w")
    print(
        generate_qua_script(hahn_echo_amplitude_vary_gamma, qm_config.config),
        file=sourceFile,
    )
    sourceFile.close()
    t = np.round(
        np.linspace(0, qm_config.READOUT_LENGTH - chunck_size * 4, time_array_size)
    )

    time.sleep(1)
    u = unit()
    job = qm.execute(hahn_echo_amplitude_vary_gamma)
    # Get results from QUA program and initialize live plotting
    fig = plt.figure()
    interrupt_on_close(fig, job)
    
    for j, b_field in enumerate(b_field_list):
        for i, curr in enumerate(curr_list): 
            # Set current
            magnets.ramp_spherical(
                field=(b_field + MagConfig.gradient_offset_coef * curr),
                ramp_rate=MagConfig.ramp_rate
            )
            source_ramp(
                grad_source,
                curr,
            )
            grad_source.operation_complete()
            magnets.amiz.operation_complete()
            
            time.sleep(1)
            print("resuming")
            
            wait_for_next_data(job)
            print("paused")
            # Fetch the data from the last OPX run corresponding to the current slow axis iteration
            print(i)
            print(n_curr)
            if i == n_curr-1:
                if j==0:
                    start_time = time.time()
                    results = fetching_tool(job, data_list=["I", "Q", "curr_i", "b_field_i"], mode="live")
                I, Q, curr_i, b_field_i = results.fetch_all()
                # Convert results into Volts
                S = u.demod2volts(I + 1j * Q, qm_config.READOUT_LENGTH, single_demod=True)
                amp = np.abs(S)  # Amplitude
                phase = np.angle(S)  # Phase

                progress_counter(b_field_i, n_b_field, start_time=start_time)
                # Plot results
                plt.suptitle(r"Hahn ehcho for varying $\Gamma$")
                plt.subplot(211)
                plt.cla()
                plt.plot(t, amp[i])
                plt.xlabel("Anti-Helmholtz Coil Current [mA]")
                plt.ylabel(r"Amplitude [V]")
                plt.subplot(212)
                plt.cla()
                plt.plot(t, phase[i])
                plt.xlabel("Anti-Helmholtz Coil Current [mA]")
                plt.ylabel("Phase [rad]")
                plt.tight_layout()
                plt.savefig((fig_path / f"{b_field:07.3f}mT".replace(".", "p")))
                plt.pause(0.1)

    # Save results

    df_I = pd.DataFrame(I, index=b_field_list, columns=curr_list).T
    df_I.to_csv((data_path / "I.csv"))
    df_Q = pd.DataFrame(Q, index=b_field_list, columns=curr_list).T
    df_Q.to_csv((data_path / "Q.csv"))
    plt.show()
    job.halt()
