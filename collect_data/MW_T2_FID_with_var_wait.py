import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pyvisa as visa
import time
import shutil

from Config_debdip.fileio import experiment
from Config_debdip.logs import initlog
from Config_debdip.my_config import *
from Quantum_Machine.qm_configs import *
from Config_debdip.hqd_util import *

from PSG import psg_keysight

from qm import SimulationConfig, LoopbackInterface
from qm.qua import *
from qm.QuantumMachinesManager import QuantumMachinesManager
from qualang_tools.loops import from_array
from qualang_tools.results import fetching_tool, progress_counter

project_name = 'Impedance_Matching_DPPH'
experiment_name = 'MW_T2_FID_4K_DPPH'

chunk_size = 20//4
array_size = readout_length // (chunk_size*4)

# n_us = int(4) # in us
# n_10us = int(1) # in 10us 
cd_n_ms = int(20) # in ms cooldown


with program() as Pulse_Duration_calib:
    qm_us = int(1e3//4)
    qm_ms = int(1e6//4)
    # qm_10us = int(1e4//4)

    # qm_n_tau = declare(int)
    # qm_tau = declare(int)
    qm_iteration = declare(int)
    qm_n_cd = declare(int)
    
    qm_j = declare(int)
    qm_I = declare(fixed, size = array_size)
    qm_Q = declare(fixed, size = array_size)
    qm_I1 = declare(fixed, size = array_size)
    qm_I2 = declare(fixed, size = array_size)
    qm_Q1 = declare(fixed, size = array_size)
    qm_Q2 = declare(fixed, size = array_size)
    

    qm_I_st = declare_stream()
    qm_Q_st = declare_stream()
    qm_adc_st = declare_stream(adc_trace = True)
    itr_st = declare_stream()
    logger.info('--START_MEASUREMENT--')
    with for_(qm_iteration, 0, qm_iteration<n_avg, qm_iteration+1):
        align('spin', 'Digitizer','CryoSw')
        reset_frame('spin', 'Digitizer')
        reset_phase('Digitizer')
        reset_phase('spin')


        # half-pi
        align('spin', 'Digitizer','CryoSw')
        play('spa', 'SPA')
        play('pi_half','spin')

        wait(500//4, 'spin')
        align('spin', 'Digitizer', 'CryoSw')

        #measurement
        play('cryosw', 'CryoSw')
        measure('readout','Digitizer', qm_adc_st, 
                demod.sliced('cos',qm_I1, chunk_size, 'out1'),
                demod.sliced('minus_sin',qm_Q1, chunk_size, 'out1'),
                demod.sliced('cos',qm_Q2, chunk_size, 'out2'),
                demod.sliced('sin',qm_I2, chunk_size, 'out2'))
        
        # cooldown
        
        align('Digitizer','CryoSw', 'spin')
        with for_(qm_n_cd, 0, qm_n_cd<cd_n_ms, qm_n_cd+1):
            wait(qm_ms, 'spin')

        with for_(qm_j,0,qm_j<array_size,qm_j+1):
            assign(qm_I[qm_j], qm_I1[qm_j]+qm_I2[qm_j])
            assign(qm_Q[qm_j], qm_Q1[qm_j]+qm_Q2[qm_j])
            save(qm_I[qm_j], qm_I_st)
            save(qm_Q[qm_j], qm_Q_st)

        save(qm_iteration, itr_st)    
    with stream_processing():
        qm_I_st.buffer(array_size).average().save('I')
        qm_Q_st.buffer(array_size).average().save('Q')
        itr_st.save('Iteration')

def initialize_experiment(project, exp_name):
    exp = experiment(project=project, exp_name=exp_name)
    exp_path = exp.get_path()
    logger = initlog(type='Experiment', basepath=exp_path).get_logger()
    logger.info('{}: {}'.format(project, exp_name))
    shutil.copy(__file__,r'{}/MW_T2_FID_with_var_wait.py'.format(exp_path))
    shutil.copy(config_path, r'{}/qm_configs.py'.format(exp_path))
    return logger, exp_path


rm = visa.ResourceManager()
qmm = QuantumMachinesManager(host=host_ip)



simulate = True
if simulate:
    simulation_time = 20000 //4 
    job = qmm.simulate(config, Pulse_Duration_calib, SimulationConfig(duration =simulation_time))
    results = job.get_simulated_samples()
    plt.figure()
    results.con1.plot()
    plt.show()

else:
    qm = qmm.open_qm(config)
    logger, exp_path = initialize_experiment(project_name, experiment_name)
    sg = psg_keysight.Instrument()
    logger.debug('PSG Connected')
    sg.freqInGHz = 5.437
    sg.mwIsOn = True
    time.sleep(10)

    logger.debug('____START_EXPERIMENT____')
    job = qm.execute(Pulse_Duration_calib)
    res_handles  = fetching_tool(job, data_list=['Iteration', 'I', 'Q'], mode = 'live')
    
    
    while res_handles.is_processing():
        iteration, I , Q = res_handles.fetch_all()
        progress_counter(int(iteration), int(n_avg),start_time=res_handles.get_start_time())
        print(I.shape, Q.shape)
    
    
    logger.debug(I.shape)
    logger.debug(Q.shape)
    t = np.linspace(0, readout_length-chunk_size*4, array_size)
    save_data_1d_echo(t,I,Q,exp_path,'t [ns]')
    sg.mwIsOn = False

    job.halt()





