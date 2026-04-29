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
experiment_name = (
    f"fid_{QMConfig.pi_pulse_length}ns_{MagConfig.gradient_current:05.3f}A".replace(
        ".", "p"
    )
)


chunck_size = 4 // 4
time_array_size = qm_config.READOUT_LENGTH // (chunck_size * 4)

curr_min = 0e-3
curr_max = 1e-3
curr_step = 1e-3

curr_list = np.round(np.arange(curr_min, curr_max + 0.5 * curr_step, curr_step), 3)
print(curr_list)
# curr_list = [200e-3]

# print(amplitude_list)

with program() as pi_pulse_calibration_amplitude:
    qm_us = int(1e3 // 4)
    qm_ms = int(1e6 // 4)

    n = declare(int)

    curr = declare(fixed)
    curr_st = declare_stream()

    j = declare(int)
    I1 = declare(fixed, size=time_array_size)
    Q1 = declare(fixed, size=time_array_size)
    I2 = declare(fixed, size=time_array_size)
    Q2 = declare(fixed, size=time_array_size)

    I = declare(fixed, size=time_array_size)
    Q = declare(fixed, size=time_array_size)

    I_st = declare_stream()
    Q_st = declare_stream()

    with for_(*from_array(curr, curr_list)):
        with for_(n, 0, n < n_avg, n + 1):
            
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
            wait(15_000_000 // 4)
            with for_(j, 0, j < time_array_size, j + 1):
                assign(I[j], I1[j] + I2[j])
                assign(Q[j], Q1[j] - Q2[j])
                save(I[j], I_st)
                save(Q[j], Q_st)

        save(curr, curr_st)
        pause()

    with stream_processing():
        I_st.buffer(time_array_size).buffer(n_avg).map(FUNCTIONS.average()).save_all(
            "I"
        )
        Q_st.buffer(time_array_size).buffer(n_avg).map(FUNCTIONS.average()).save_all(
            "Q"
        )
        curr_st.save("current")


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


def main():
    if simulate:
        simulation_time = 12000 // 4
        job = qmm.simulate(
            config,
            pi_pulse_calibration_amplitude,
            SimulationConfig(duration=simulation_time),
        )
        results = job.get_simulated_samples()
        plt.figure()
        results.con1.plot()
        plt.show()

    else:
        mag_grad_source1 = YokogawaGS200(visa_backend="@py", address=InstAddr.gs200_1)
        mag_grad_source1.function(function="current")
        mag_grad_source1.source_range(source_range="0.2")
        if not mag_grad_source1.output():
            source_ramp(mag_grad_source1, 0)
            mag_grad_source1.output(True)
        mag_grad_source1.operation_complete()
        source_ramp(mag_grad_source1, 0.5 * curr_list[0])

        mag_grad_source2 = YokogawaGS200(visa_backend="@py", address=InstAddr.gs200_2)
        mag_grad_source2.function(function="current")
        mag_grad_source2.source_range(source_range="0.2")
        if not mag_grad_source2.output():
            source_ramp(mag_grad_source2, 0)
            mag_grad_source2.output(True)
        mag_grad_source2.operation_complete()
        source_ramp(mag_grad_source2, 0.5 * curr_list[0])


        # Setup magnets
        mag_addr = (InstAddr.mag_x, InstAddr.mag_y, InstAddr.mag_z)
        magnets = AMI430Vector(mag_addr)
        magnets.ramp_spherical(
            field=MagConfig._field + MagConfig.gradient_offset_coef * curr_list[0],
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

        sourceFile = open((path / "debug.py"), "w")
        print(
            generate_qua_script(pi_pulse_calibration_amplitude, qm_config.config),
            file=sourceFile,
        )
        sourceFile.close()

        u = unit()
        job = qm.execute(pi_pulse_calibration_amplitude)
        time.sleep(1)
        # Get results from QUA program and initialize live plotting
        fig = plt.figure()
        interrupt_on_close(fig, job)
        t = np.round(
            np.linspace(0, qm_config.READOUT_LENGTH - chunck_size * 4, time_array_size)
        )
        results = fetching_tool(job, data_list=["I", "Q", "current"], mode="live")
        start_time = time.time()
        while results.is_processing():
            # Fetch the data from the last OPX run corresponding to the current slow axis iteration
            I, Q, current = results.fetch_all()
            # Convert results into Volts
            S = u.demod2volts(I + 1j * Q, qm_config.READOUT_LENGTH, single_demod=False)
            amp = np.abs(S)  # Amplitude
            phase = np.angle(S)  # Phase
            progress_counter(len(I) - 1, len(curr_list), start_time=start_time)

            # Plot results
            plt.suptitle(f"Hahn echo for {round(current * 1e3)} mA current.")
            plt.subplot(211)
            plt.cla()
            plt.plot(t, amp[-1] * 1e3)
            plt.xlabel("Time [ns]")
            plt.ylabel("amplitude [mV]")
            plt.subplot(212)
            plt.cla()
            plt.plot(t, phase[-1])
            plt.xlabel("Time [ns]")
            plt.ylabel("Phase [rad]")
            plt.ylim(-np.pi, np.pi)
            plt.tight_layout()
            plt.savefig(
                (
                    fig_path
                    / f"pulse_amplitude_{round(current * 1e3)} mA".replace(
                        ".", "p"
                    )
                )
            )
            plt.pause(0.1)

            # Save results
            df_I = pd.DataFrame(I, index=curr_list[: len(I)], columns=t).T
            df_I.to_csv((data_path / "I.csv"))
            df_Q = pd.DataFrame(Q, index=curr_list[: len(Q)], columns=t).T
            df_Q.to_csv((data_path / "Q.csv"))
            df_amp = pd.DataFrame(amp, index=curr_list[: len(amp)], columns=t).T
            df_amp.to_csv((data_path / "amp.csv"))
            df_phase = pd.DataFrame(phase, index=curr_list[: len(phase)], columns=t).T
            df_phase.to_csv((data_path / "phase.csv"))
            print("\n")
            if round(current, 3) == curr_list[-1]:
                print("Experiment completed")
                break
            # Set current
            next_curr = curr_list[np.where(curr_list == round(current, 3))[0][0] + 1]

            source_ramp(mag_grad_source1, 0.5 * next_curr)
            source_ramp(mag_grad_source2, 0.5 * next_curr)
            magnets.ramp_spherical(
                field=(MagConfig._field + MagConfig.gradient_offset_coef * next_curr),
                thetaDeg=MagConfig.theta,
                phiDeg=MagConfig.phi,
                ramp_rate=MagConfig.ramp_rate,
            )

            wait_for_next_data(job)

        source_ramp(mag_grad_source1, 0)
        source_ramp(mag_grad_source2, 0)
        # magnets.ramp_spherical(
        #     field=(MagConfig._field),
        #     thetaDeg=MagConfig.theta,
        #     phiDeg=MagConfig.phi,
        #     ramp_rate=MagConfig.ramp_rate,
        # )

        job.halt()
        plt.show()


if __name__ == "__main__":
    main()
