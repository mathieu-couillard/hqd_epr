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
experiment_name = 'MW_T2_HahnEcho_4K_DPPH'

chunk_size = 20//4
array_size = readout_length // (chunk_size*4)

T_n_10us = int(1) # in us
sat_n_10us = int(1) # in 10us 
tau_n_us = int(4) # in us
# cd_n_ms = int(1) # in ms cooldown
CPMG_n_pi = int(4) # number of pi pulses in CPMG sequence


with program() as CPMG_HahnEcho:
    qm_us = int(1e3//4)
    qm_ms = int(1e6//4)
    qm_10us = int(1e4//4)

    qm_n_tau = declare(int)
    qm_iteration = declare(int)
    qm_n_sat = declare(int)
    qm_n_T = declare(int)
    qm_n_cd = declare(int)
    qm_n_CPMG = declare(int)
    
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
    i_st = declare_stream()
    logger.info('--START_MEASUREMENT--')
    with for_(qm_iteration, 0, qm_iteration<n_avg, qm_iteration+1):
        align('spin','SPA', 'Digitizer','CryoSw')
        reset_frame('spin', 'Digitizer')
        reset_phase('Digitizer')
        reset_phase('spin')

        # saturation pulse
        with for_(qm_n_sat, 0,qm_n_sat<sat_n_10us, qm_n_sat+1):
            play('saturation','spin')
        
        # T_time_wait
        with for_(qm_n_T, 0, qm_n_T<T_n_10us, qm_n_T+1):
            wait(qm_10us, 'spin')


        # half-pi
        align('spin','SPA', 'Digitizer','CryoSw')
        play('spa', 'SPA')
        play('pi_half','spin')
        
        # tau
        with for_(qm_n_tau, 0, qm_n_tau < tau_n_us, qm_n_tau+1):
            wait(qm_us, 'spin')

        #pi CPMG
        frame_rotation(np.pi/2, 'spin')

        with for_(qm_n_CPMG, 0, qm_n_CPMG < CPMG_n_pi, qm_n_CPMG+1):
            play('pi','spin')

            with for_(qm_n_tau, 0, qm_n_tau < tau_n_us-1, qm_n_tau+1):
                wait(qm_us, 'spin')

            align('spin', 'Digitizer', 'CryoSw')

            play('cryosw', 'CryoSw')
            measure('readout','Digitizer', qm_adc_st, 
                    demod.sliced('cos',qm_I1, chunk_size, 'out1'),
                    demod.sliced('minus_sin',qm_Q1, chunk_size, 'out1'),
                    demod.sliced('cos',qm_Q2, chunk_size, 'out2'),
                    demod.sliced('sin',qm_I2, chunk_size, 'out2'))
            
            align('Digitizer','spin')
            with for_(qm_n_tau, 0, qm_n_tau < tau_n_us-1, qm_n_tau+1):
                wait(qm_us, 'spin')
            
            with for_(qm_j,0,qm_j<array_size,qm_j+1):
                assign(qm_I[qm_j], qm_I1[qm_j]+qm_I2[qm_j])
                assign(qm_Q[qm_j], qm_Q1[qm_j]+qm_Q2[qm_j])
                save(qm_I[qm_j], qm_I_st)
                save(qm_Q[qm_j], qm_Q_st)

            save(qm_n_CPMG, i_st)
        # cooldown
        
        # align('spin','SPA', 'Digitizer','CryoSw')
        # with for_(qm_n_cd, 0, qm_n_cd < cd_n_ms, qm_n_cd+1):
        #     wait(qm_ms, 'spin')
    save(qm_iteration, itr_st)    
    with stream_processing():
        qm_I_st.buffer(array_size).buffer(CPMG_n_pi).average().save('I')
        qm_Q_st.buffer(array_size).buffer(CPMG_n_pi).average().save('Q')
        itr_st.save('Iteration')
        i_st.save('i')

def initialize_experiment(project, exp_name):
    exp = experiment(project=project, exp_name=exp_name)
    exp_path = exp.get_path()
    logger = initlog(type='Experiment', basepath=exp_path).get_logger()
    logger.info('{}: {}'.format(project, exp_name))
    shutil.copy(__file__,r'{}/pulse_duration_HahnEcho.py'.format(exp_path))
    shutil.copy(config_path, r'{}/qm_configs.py'.format(exp_path))
    return logger, exp_path


rm = visa.ResourceManager()
qmm = QuantumMachinesManager(host=host_ip)



simulate = True
if simulate:
    simulation_time = 150000 //4 
    job = qmm.simulate(config, CPMG_HahnEcho, SimulationConfig(duration =simulation_time))
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
    job = qm.execute(CPMG_HahnEcho)
    res_handles  = fetching_tool(job, data_list=['Iteration', 'I', 'Q', 'i'], mode = 'live')
    
    
    while res_handles.is_processing():
        iteration, I , Q, i = res_handles.fetch_all()
        progress_counter(int(i), CPMG_n_pi,start_time=res_handles.get_start_time())
        progress_counter(int(iteration), int(n_avg),start_time=res_handles.get_start_time())
        print(I.shape, Q.shape)
    
    
    logger.debug(I.shape)
    logger.debug(Q.shape)
    t = np.linspace(0, readout_length-chunk_size*4, array_size)
    cpmg_n_list = np.arange(CPMG_n_pi)
    save_data_2d_echo(np.array(cpmg_n_list),t,I,Q,exp_path, 'N CPMG', experiment_name)
    sg.mwIsOn = False

    job.halt()





