import shutil
import time
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pyvisa as visa
from drivers import KeysightE8247C, AMI430Vector, KeysightN9010A
from qm import LoopbackInterface, SimulationConfig
from qm.qua import *
from qm.QuantumMachinesManager import QuantumMachinesManager

from qualang_tools.loops import from_array:
from qualang_tools.results import fetching_tool, progress_counter
from qualang_tools.units import unit

from config import qm_config
from config import InstrumentAddresses as InstAddr
from config.experiment_config import FreeInductionDecay as FIDconf
from config.experiment_config import MagConfig, EXPERIMENT_BASE_PATH, n_avg
from config.experiment_config import __file__ as EXPPERIMENT_CONFIG_PATH

from utils import generate_path
from utils import save_data_1d_echo

# TODO: this should be in experiment config
PROJECT_NAME = "impedance_matching_dpph"
EXPERIMENT_NAME = "rt_switch_calibration"

CHUNCK_SIZE = 4 // 4
ARRAY_SIZE = qm_config.READOUT_LENGTH // (CHUNCK_SIZE * 4)

pulse_length_min = 40//4
pulse_length_max = 1000//4
pulse_length_step = 16 //4
pulse_lengths = np.arange(pulse_length_min, pulse_length_max+0.5*pulse_length_step, pulse_length_step)


with program() as rt_switch_calibration:
    qm_us = int(1e3 // 4)
    qm_ms = int(1e6 // 4)

    qm_iteration = declare(int)
    pulse_length = declare(int)

    qm_j = declare(int)
    qm_I = declare(fixed, size=ARRAY_SIZE)
    qm_Q = declare(fixed, size=ARRAY_SIZE)
    qm_I1 = declare(fixed, size=ARRAY_SIZE)
    qm_I2 = declare(fixed, size=ARRAY_SIZE)
    qm_Q1 = declare(fixed, size=ARRAY_SIZE)
    qm_Q2 = declare(fixed, size=ARRAY_SIZE)

    qm_I_st = declare_stream()
    qm_Q_st = declare_stream()
    qm_adc_st = declare_stream(adc_trace=True)
    itr_st = declare_stream()
    with for_(qm_iteration, 0, qm_iteration < n_avg, qm_iteration + 1):
        with for_(*from_array(pulse_length, pulse_lengths)):
            reset_phase('spin')
            reset_phase('digitizer')
            reset_frame('spin')
            measure(
                "readout",
                "digitizer",
                qm_adc_st,
                demod.sliced("cos", qm_I1, CHUNCK_SIZE, "out1"),
                demod.sliced("sin", qm_Q1, CHUNCK_SIZE, "out1"),
                demod.sliced("cos", qm_Q2, CHUNCK_SIZE, "out2"),
                demod.sliced("sin", qm_I2, CHUNCK_SIZE, "out2"),
            )

            wait(100//4, "spin") # compensate for time of flight
            play("x90", "spin", duration=pulse_length)
            wait(2000//4, "spin")
            frame_rotation_2pi(0.5, "spin")
            play("x180", "spin", duration=pulse_length)
            wait(1000//4, 'spin')
            align("spin", "CryoSw")

            play('cryosw', "CryoSw")
            with for_(qm_j, 0, qm_j < ARRAY_SIZE, qm_j + 1):
                assign(qm_I[qm_j], qm_I1[qm_j] + qm_I2[qm_j])
                assign(qm_Q[qm_j], qm_Q1[qm_j] - qm_Q2[qm_j])
                save(qm_I[qm_j], qm_I_st)
                save(qm_Q[qm_j], qm_Q_st)

            save(qm_iteration, itr_st)

    with stream_processing():
        qm_I_st.buffer(ARRAY_SIZE).average().save("I")
        qm_Q_st.buffer(ARRAY_SIZE).average().save("Q")
        itr_st.save("Iteration")


# TODO: This should be in the utils
def create_directories(project, exp_name):
    path = generate_path(project=project, exp_name=exp_name, basepath=EXPERIMENT_BASE_PATH)
    config_path = qm_config.__file__
    shutil.copy(__file__, f"{str(path / Path(__file__).name)}")
    shutil.copy(config_path, f"{str(path / Path(config_path).name)}")
    shutil.copy(EXPPERIMENT_CONFIG_PATH, f"{str(path / Path(EXPPERIMENT_CONFIG_PATH).name)}")
    return path


rm = visa.ResourceManager()
qmm = QuantumMachinesManager(host=InstAddr.qm)


simulate = False
if simulate:
    simulation_time = 12000 // 4
    job = qmm.simulate(
        config, rt_switch_calibration, SimulationConfig(duration=simulation_time)
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
        theta=MagConfig.theta,
        phi=MagConfig.phi,
        ramp_rate=MagConfig.ramp_rate,
    )

    # Set up microwave
    mw_source = KeysightE8247C(InstAddr.mw_source)
    mw_source.freqInHz = FIDconf.spin_lo_freq #- qm_config.SPIN_IF    
    mw_source.power_dBm = FIDconf.spin_lo_power

    # Set up spectrum analyzer
    spa = KeysightN9010A(InstAddr.spa)
    spa.centerFreqInHz = qm_config.SPIN_LO + qm_config.SPIN_IF

    spa.spanInHz = 5e6
    spa.resBWInHz = 0.01e6

    qm = qmm.open_qm(qm_config.config)
    path = create_directories(PROJECT_NAME, EXPERIMENT_NAME)
    
    time.sleep(10)
    u = unit()
    job = qm.execute(rt_switch_calibration)
    res_handles = fetching_tool(job, data_list=["Iteration", "I", "Q"], mode="live")

    while res_handles.is_processing():
        iteration, I, Q = res_handles.fetch_all()
        progress_counter(
            int(iteration), int(n_avg), start_time=res_handles.get_start_time()
        )
        #print(I.shape, Q.shape)

    t = np.linspace(0, qm_config.READOUT_LENGTH-CHUNCK_SIZE * 4, ARRAY_SIZE)
    save_data_1d_echo(
        t,
        u.demod2volts(data=I, duration=CHUNCK_SIZE),
        u.demod2volts(data=Q, duration=CHUNCK_SIZE),
        path,
        "t [ns]",
    )
    # sg.mwIsOn = False

    job.halt()
