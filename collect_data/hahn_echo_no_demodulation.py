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
from qm import QuantumMachinesManager

from qualang_tools.results import fetching_tool, progress_counter
from qualang_tools.units import unit

from config import qm_config
from config import InstrumentAddresses as InstAddr
from config.experiment_config import FreeInductionDecay as FIDconf
from config.experiment_config import MagConfig, MWConfig, EXPERIMENT_BASE_PATH, n_avg
from config.experiment_config import __file__ as EXPPERIMENT_CONFIG_PATH

from utils import generate_path
from utils import save_data_1d_echo

# TODO: this should be in experiment config
PROJECT_NAME = "impedance_matching_dpph"
EXPERIMENT_NAME = "rt_switch_calibration"

ARRAY_SIZE = qm_config.READOUT_LENGTH 

with program() as hahn_echo:
    qm_us = int(1e3 // 4)
    qm_ms = int(1e6 // 4)

    qm_iteration = declare(int)

    qm_adc_st = declare_stream(adc_trace=True)
    itr_st = declare_stream()
    with for_(qm_iteration, 0, qm_iteration < n_avg, qm_iteration + 1):
        align()
        reset_if_phase('spin')
        reset_if_phase('digitizer')
        reset_frame('spin')

        measure("readout", "digitizer", adc_stream = qm_adc_st)        

        play('spa',"SPA")
        # wait(600//4, "spin") # compensate for time of flight
        play("x90", "spin")
        wait(1500//4, "spin")
        frame_rotation_2pi(0.25, "spin")
        play("x180", "spin")
        wait(400//4, 'spin')
        align("spin", "CryoSw")

        play('cryosw', "CryoSw")
        wait(15_000_000//4, "CryoSw")

        save(qm_iteration, itr_st)
    with stream_processing():
        qm_adc_st.input1().save("I")
        qm_adc_st.input2().save("Q")
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
        config, hahn_echo, SimulationConfig(duration=simulation_time)
    )
    results = job.get_simulated_samples()
    plt.figure()
    results.con1.plot()
    plt.show()

else:
    # Setup magnets
    # mag_addr = (InstAddr.mag_x, InstAddr.mag_y, InstAddr.mag_z)
    # magnets = AMI430Vector(mag_addr)
    # magnets.ramp_spherical(
    #     field=MagConfig.field,
    #     theta=MagConfig.theta,
    #     phi=MagConfig.phi,
    #     ramp_rate=MagConfig.ramp_rate,
    # )

    # Set up microwave
    mw_source = KeysightE8247C(InstAddr.mw_source)
    mw_source.freqInHz = MWConfig.spin_lo_freq    
    mw_source.power_dBm = MWConfig.spin_lo_power

    # # Set up spectrum analyzer
    # spa = KeysightN9010A(InstAddr.spa)
    # spa.centerFreqInHz = MWConfig.spin_freq

    # spa.spanInHz = 125e6
    # spa.resBWInHz = 0.01e6

    qm = qmm.open_qm(qm_config.config)
    path = create_directories(PROJECT_NAME, EXPERIMENT_NAME)
    
    time.sleep(10)
    u = unit()
    job = qm.execute(hahn_echo)
    res_handles = fetching_tool(job, data_list=["Iteration", "I", "Q"], mode="live")

    while res_handles.is_processing():
        iteration, I, Q = res_handles.fetch_all()
        progress_counter(
            int(iteration), int(n_avg), start_time=res_handles.get_start_time()
        )
        #print(I.shape, Q.shape)

    t = np.linspace(0, qm_config.READOUT_LENGTH, ARRAY_SIZE)

    save_data_1d_echo(
        t,
        u.raw2volts(data=I),
        u.raw2volts(data=Q),
        path,
        "t [ns]",
    )
    # sg.mwIsOn = False
    from qm import generate_qua_script

    sourceFile = open('debug_raw_adc.py', 'w')
    print(generate_qua_script(hahn_echo, qm_config.config), file=sourceFile) 
    sourceFile.close()

    job.halt()
    exit()
