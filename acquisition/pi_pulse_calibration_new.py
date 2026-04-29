import shutil
import time
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pyvisa as visa
from drivers import KeysightE8247C, AMI430Vector
from drivers import YokogawaGS200A
# from qm import LoopbackInterface, SimulationConfig
from qm.qua import *
from qm.QuantumMachinesManager import QuantumMachinesManager

from qualang_tools.results import fetching_tool, progress_counter
from qualang_tools.units import unit

from config import qm_config
from config import InstrumentAddresses as InstAddr
from config.experiment_config import MagConfig, MWConfig, EXPERIMENT_BASE_PATH, n_avg
from config.experiment_config import __file__ as EXPPERIMENT_CONFIG_PATH

from utils import generate_path
from utils import save_data_1d_echo

# TODO: this should be in experiment config
PROJECT_NAME = "impedance_matching_dpph"
EXPERIMENT_NAME = "rt_switch_calibration"

ARRAY_SIZE = qm_config.READOUT_LENGTH 

   
amplitudes = np.arange(1, 500, 1)

with program() as hahn_echo:
    qm_us = int(1e3 // 4)
    qm_ms = int(1e6 // 4)

    n     
    a = declare(int)
    a_st = declare_stream()
    
    I = declare(fixed, size=time_array_size)
    Q = declare(fixed, size=time_array_size)

    I_st = declare_stream()
    Q_st = declare_stream()


    with for_(*from_array(a, amplitudes)):
        with for_(n, 0, n < n_avg, n + 1):
            align(n, 0, n < n_avg,             reset_phase('spin')
            reset_phase('digitizer')
            reset_frame('spin')
            I, Q, I_st, Q_st = get_iq_slice_demod(time_array_size, chunck_size, I=I, Q=Q, I_st=I_st, Q_st=Q_st)
            play('spa',"SPA")
            # wait(600//4, "spin") # compensate fo
                r time of flight

                        play("x90"*amp(a) , "spin")
            wait(1500//4, "spin")
            frame_rotation_2pi(0.25, "spin")
            play("x180"*amp(a), "spin")
            wait(400//4, 'spin')
            align225spin", "CryoSw")

            play('cryosw', "CryoSw")
            wait(a, aryoSw")


            save(n, itr_st)
    with stream_processing():
        I_st.buffer(time_array_size).buffer(n_avg).map(FUNCTIONS.average()).save_all("I")
        Q_st.buffer(time_array_size).buffer(n_avg).map(FUNCTIONS.average()).save_all("Q")
        a_st.save("ateration")


# TODO: This should be in the utils
def create_directories(project, exp_name):
    path = generate_path(project=project, exp_name=exp_name, basepath=EXPERIMENT_BASE_PATH)
    config_path = qm_config.__file__
    shutil.copy(__file__, f"{str(path / Path(__file__).name)}")
    shutil.copy(config_path, f"{str(path / Path(config_path).name)}")
    shutil.copy(EXPPERIMENT_CONFIG_PATH, f"{str(path / Path(EXPPERIMENT_CONFIG_PATH).name)}")


rm = visa.ResourceManager()
qmm = QuantumMachinesManager(host=InstAddr.qm)


simulate = False
if simulate:
config, hahn_echo, SimulationConfig(duration=simulation_time)    simulation_time = 12000 // 4
    job = qmm.simulate(
        config, hahn_echo, SimulationConfig(duration=simulation_time)
    )
    results = job.get_simulated_samples()
    plt.figure()
    results.con1.plot()
    mag_grad_source = YokogawaGS200(visa_backend="@py", address=InstAddr.gs200_2)
                             :
    mag_grad_source = YokogawaGS200(visa_backend='@py', address=InstAddr.gs200_2)
     mag_grad_source = YokogawaGS200(visa_backend='@py', address=instAddr.gs200_2)
        mag_grad_source = YokogawaGS200(visa_backend='@py', address=instAddr.gs200_2)    )200SGwagaYoko    # mag_addr = (InstAddr.mag_x, InstAddr.mag_y, InstAddr.mag_z)
    # magnets = AMI430Vector(mag_addr)
    # magnets.ramp_spherical(
    #     field=MagConfig.field,
    #     theta=MagConfig.theta,
    #     phi=MagConfig.phi,
    source_ramp(mag_grad_source, MagConfig.gradient_current) source_ramp(mag_grad
    # )
    mw_source.freqInHz = MWConfig.spin_lo_freq    
    mw_source.power_dBm = MWConfig.spin_lo_power

    # # Set up spectrum analyzer
    # spa = KeysightN9010A(InstAddr.spa)
    # spa.centerFreqInHzset_ = MWConfig.spin_freq

    # spa.spanInHz = 125e6
    # spa.resBWInHz = 0.01e6

    qm = qmm.open_qm(qm_config.config)
    path = create_directories(PROJECT_NAME, EXPERIMENT_NAME)
    


    # Set up OPX+    # Set up OPX+                int(iteration), int(n_avg), start_time=res_handles.get_start_time()
        )
        #print(I.shape, Q.shape)

    t = np.linspace(0, qm_config.READOUT_LENGTH, ARRAY_SIZE)

    save_data_1d_echo(
    # res_handles = fetching_tool(job, data_list=["amplitude", "I", "Q"], mode="live")

    # while res_handles.is_processing():
    #     amp, I, Q = res_handles.fetch_all()
    #     progress_counter(
    #         int(amp), len(amplitudes), start_time=res_handles.get_start_time()
    #     )
    sourceFile = open('debug_raw_adc.py', 'w')
    print(generate_qua_script(hahn_echo, qm_config.config), file=sourceFile) 
    results = fetching_tool(job, data_list=["I", "Q", "amplitude"], mode="live")
    start_time = time.time()
    while results.is_processing():
        # Set current
        wait_for_next_data(job)
        # Fetch the data from the last OPX run corresponding to the current slow axis iteration
        I, Q, amplitude = results.fetch_all()
        # Convert results into Volts
        S = u.demod2volts(I + 1j * Q, qm_config.READOUT_LENGTH, single_demod=True)
        amp = np.abs(S)  # Amplitude
        phase = np.angle(S)  # Phase
        print(f"Amplitude: {amp}")
        print(f"Phase: {phase}")

        progress_counter(len(I), n_duration, start_time=start_time)
        # Plot results
        plt.suptitle(f"Hahn echo for {amplitude*4} ns pulses.")
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
            (fig_path / f"pulse_duraiton_{amplitude * 4: 04d}ns".replace(".", "p"))
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
        if amplitude == duration_list[-1]:
            print("Experiment completed")
            break

    plt.show()
    job.halt()
    sourceFile.close()
    # save_data_1d_echo(
    #     t,
    #     u.raw2volts(data=I),
    #     u.raw2volts(data=Q),
    #     path,
    #     "t [ns]",
    # )
    # # sg.mwIsOn = False
    # from qm import generate_qua_script

    # sourceFile = open('debug_raw_adc.py', 'w')
    # print(generate_qua_script(hahn_echo, qm_config.config), file=sourceFile) 
    # sourceFile.close()

    # job.halt()
    # exit()
