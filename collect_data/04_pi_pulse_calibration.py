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

from qualang_tools.loops import from_array
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

CHUNCK_SIZE = 4 // 4



TAU_I = 20
TAU_F = 1000
TAU_STEP = 1
TAUS = np.arange(TAU_I, TAU_F+0.5*TAU_STEP, TAU_STEP)

with program() as rt_switch_calibration:
    qm_us = int(1e3 // 4)
    qm_ms = int(1e6 // 4)

    n = declare(int)
    tau = declare(int)

    I = declare(fixed)
    Q = declare(fixed)


    I_st = declare_stream()
    Q_st = declare_stream()
    n_st = declare_stream()

    with for_(n, 0, n < n_avg, n + 1):
        with for_(*from_array(tau, TAUS)):
            align()
            reset_phase('spin')
            reset_phase('digitizer')
            reset_frame('spin')
            play('spa',"SPA")

            play("x90", "spin", duration=tau)
            wait(2000//4, "spin")
            frame_rotation_2pi(0.5, "spin")
            play("x180", "spin", duration=tau)
            wait(1400//4, 'spin')
            
            align("spin","digitizer", "CryoSw")

            wait(400//4, "digitizer")

            play('cryosw', "CryoSw")
            measure(
                "readout",
                "digitizer",
                None,
                dual_demod.full("cos", "out1", "sin", "out2", I),
                dual_demod.full("minus_sin", "out1", "cos", "out2", Q),
            )
            save(I, I_st)
            save(Q, Q_st)
            wait(1_500_000//4)

        save(n, n_st)
    with stream_processing():
        I_st.buffer(len(TAUS)).average().save("I")
        Q_st.buffer(len(TAUS)).average().save("Q")
        n_st.save("Iteration")


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
    mw_source.freqInHz = MWConfig.spin_lo_freq #- qm_config.SPIN_IF    
    mw_source.power_dBm = MWConfig.spin_lo_power

    # Set up spectrum analyzer
    spa = KeysightN9010A(InstAddr.spa)
    spa.centerFreqInHz = MWConfig.spin_freq

    spa.spanInHz = 0
    spa.resBWInHz = 5e6

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

    save_data_1d_echo(
        TAUS,
        u.demod2volts(I, qm_config.READOUT_LENGTH),
        u.demod2volts(Q, qm_config.READOUT_LENGTH),
        path,
        "tau [ns]",
    )
    # sg.mwIsOn = False

    job.halt()
