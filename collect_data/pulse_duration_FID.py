import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pyvisa as visa
import time
import shutil
from tqdm import tqdm

from Config_debdip.fileio import experiment
from Config_debdip.logs import initlog
from Config_debdip.my_config import *
from Quantum_Machine.qm_configs import *
from Config_debdip.hqd_util import *

# from PSG.psg_keysight import Keysight_PSG

from qm import SimulationConfig, LoopbackInterface
from qm.qua import *
from qm.QuantumMachinesManager import QuantumMachinesManager
from qualang_tools.loops import from_array
from qualang_tools.results import fetching_tool, progress_counter
from qualang_tools.units import unit

project_name = 'Impedance_Matching_DPPH'
experiment_name = 'Pulse_Calib_FID_4K_DPPH'



chunk_size = 4//4
array_size = readout_length // (chunk_size*4)

duration_min = 16//4
duration_max = 4000//4
dduration = 16//4
durations = np.arange(duration_min, duration_max+dduration*0.1, dduration)

durations = [int(d) for d in durations]
n_wait_us = 4
n_ms_cd = 10

with program() as Pulse_Duration_calib:
    qm_duration = declare(int)
    qm_us = int(1e3//4)
    qm_10us = int(10e3//4)
    qm_ms = int(1e6//4)

    
    qm_j = declare(int)
    # qm_n_tau = declare(int)
    qm_n_cd = declare(int)
    n = declare(int)
    qm_I = declare(fixed, size = array_size)
    qm_Q = declare(fixed, size = array_size)
    qm_I1 = declare(fixed, size = array_size)
    qm_I2 = declare(fixed, size = array_size)
    qm_Q1 = declare(fixed, size = array_size)
    qm_Q2 = declare(fixed, size = array_size)

    qm_I_st = declare_stream()
    qm_Q_st = declare_stream()
    qm_adc_st = declare_stream(adc_trace = True)
    st_itr = declare_stream()
    
    with for_(n,0,n<n_avg, n+1):
        
        with for_each_(qm_duration, durations):
            align('spin', 'Digitizer','CryoSw')
            reset_frame('spin', 'Digitizer')
            reset_phase('Digitizer')
            reset_phase('spin')
            
            #measurement


            # half-pi
            align('spin', 'Digitizer','CryoSw')
            play('spa', 'SPA')

            play('saturation', 'spin', duration=qm_duration)

            align('spin', 'Digitizer', 'CryoSw')
            play('cryosw', 'CryoSw')
            measure('readout','Digitizer', qm_adc_st, 
                    demod.sliced('cos',qm_I1, chunk_size, 'out1'),
                    demod.sliced('sin',qm_Q1, chunk_size, 'out1'),
                    demod.sliced('cos',qm_I2, chunk_size, 'out2'),
                    demod.sliced('sin',qm_Q2, chunk_size, 'out2'))


            # cooldown
            
            align('Digitizer','CryoSw','spin')
            with for_(qm_n_cd, 0, qm_n_cd < n_ms_cd, qm_n_cd+1):
                wait(qm_ms, 'spin')

            with for_(qm_j,0,qm_j<array_size,qm_j+1):
                assign(qm_I[qm_j], qm_I1[qm_j]+qm_Q2[qm_j])
                assign(qm_Q[qm_j], qm_I2[qm_j]-qm_Q1[qm_j])
                save(qm_I[qm_j], qm_I_st)
                save(qm_Q[qm_j], qm_Q_st)
            
            logger.info('duration: {}'.format(qm_duration*4))
        save(n, st_itr)
    with stream_processing():
        qm_I_st.buffer(array_size).buffer(len(durations)).average().save('I')
        qm_Q_st.buffer(array_size).buffer(len(durations)).average().save('Q')
        st_itr.save('Iteration')

def initialize_experiment(project, exp_name):
    logger = initlog(type='Experiment').get_logger()
    exp = experiment(project=project, exp_name=exp_name)
    logger.info('{}: {}'.format(project, exp_name))
    exp_path = exp.get_path()
    shutil.copy(__file__,r'{}/pulse_duration_FID.py'.format(exp_path))
    shutil.copy(config_path, r'{}/qm_configs.py'.format(exp_path))
    return logger, exp_path


rm = visa.ResourceManager()
# sg = Keysight_PSG()
qmm = QuantumMachinesManager(host=host_ip)



simulate = False
if simulate:
    simulation_time = 16000 //4 
    job = qmm.simulate(config, Pulse_Duration_calib, SimulationConfig(duration =simulation_time))
    results = job.get_simulated_samples()
    plt.figure()
    results.con1.plot()
    plt.show()

else:
    qm = qmm.open_qm(config)
    # sg.mwIsOn = True
    logger, exp_path = initialize_experiment(project_name, experiment_name)
    # rm = visa.ResourceManager()
    # sg = psg_keysight.Instrument()
    # logger.debug('PSG Connected')
    # sg.freqInGHz = 5.437
    # sg.mwIsOn = True
    time.sleep(10)
    u = unit()
    logger.debug('____START_EXPERIMENT____')
    job = qm.execute(Pulse_Duration_calib)
    res_handles  = job.result_handles
    res_handles.wait_for_all_values()
    
    
    I = res_handles.get('I').fetch_all()
    Q = res_handles.get('Q').fetch_all()
    logger.debug(I.shape)
    logger.debug(Q.shape)
    t = np.linspace(0, readout_length-chunk_size*4, array_size)

    save_data_2d_echo(np.array(durations)*4,t,u.demod2volts(I, chunk_size),u.demod2volts(Q, chunk_size),exp_path, 'Pulse Length [ns]', experiment_name)
    # sg.mwIsOn = False
    logger.debug('____END_EXPERIMENT____')

    job.halt()





