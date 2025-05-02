'''
Script looks at the raw ADC data, this allows checking that the ADC is not saturated
'''

from Config_debdip.fileio import experiment
from Config_debdip.logs import initlog
from Config_debdip.my_config import *
from qm import SimulationConfig, LoopbackInterface
from qm.QuantumMachinesManager import QuantumMachinesManager
from qm.qua import *
from qualang_tools.loops import from_array
from Quantum_Machine.qm_configs import *
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import shutil

#############
# QUA Program
#############

n_list = np.arange(n_avg)
phi_list = np.linspace(0, np.pi,101)

chunk_size = 4//4
array_size = readout_length// (chunk_size*4)

with program() as adc_calibrations:
    n = declare(int)
    j = declare(int)
    phi = declare(fixed)
    qm_ms = int(1e6//4)
    adc_st = declare_stream(adc_trace = True)
    
    with for_ (n, 0, n<100, n+1):
        # align('spin', 'Digitizer','CryoSw')
        reset_frame('spin', 'Digitizer')
        reset_phase('Digitizer')
        reset_phase('spin')
        
        #measurement


        # half-pi
        # align('spin', 'Digitizer','CryoSw')
        play('spa', 'SPA')

        play('pi_half', 'spin')
        wait(2000//4, 'spin')
        #pi
        frame_rotation(np.pi/2, 'spin')
        play('pi', 'spin')
        wait(2000//4,'spin')
        # align('spin', 'Digitizer', 'CryoSw')
        # play('cryosw', 'CryoSw')
        measure('readout', 'Digitizer',adc_st)

        # 
        
        
        wait(qm_ms*20)


    with stream_processing():
        adc_st.input1().average().save('adc1')
        adc_st.input2().average().save('adc2')

        adc_st.input1().save('adc1_single_run')
        adc_st.input2().save('adc2_single_run')
        


######################################
# Executions
######################################

def initialize_experiment(project, exp_name):
    logger = initlog(type='Experiment').get_logger()
    exp = experiment(project=project, exp_name=exp_name)
    exp_path = exp.get_path()
    data_folder = exp.create_folder(base_path=exp_path, _folder = 'Data')
    fig_folder = exp.create_folder(base_path=exp_path, _folder = 'fig')
    shutil.copy(__file__,r'{}/adc_calibrations.py'.format(exp_path))
    shutil.copy(config_path, r'{}/qm_configs.py'.format(exp_path))
    return logger, exp_path, data_folder, fig_folder


project_name = 'Impedance_Matching_DPPH'
experiment_name = 'ADC Calibrations'

qmm = QuantumMachinesManager(host=host_ip)

simulate = False

if simulate:
    simulation_time = 16000 //4 
    job = qmm.simulate(config
                       , adc_calibrations, SimulationConfig(duration=simulation_time))
    samples = job.get_simulated_samples()
    plt.figure()
    samples.con1.plot()
    plt.show()
else:

    logger, exp_path, data_folder, fig_folder = initialize_experiment(project=project_name, exp_name=experiment_name)

    logger.debug('ADC Calibration Started')
    logger.info('path: {}'.format(exp_path))
    qm = qmm.open_qm(config)
    job = qm.execute(adc_calibrations)
    res_handeles = job.result_handles
    res_handeles.wait_for_all_values()
    adc1 = res_handeles.get('adc1').fetch_all()
    adc2 = res_handeles.get('adc2').fetch_all()
    adc1_single_run = res_handeles.get('adc1_single_run').fetch_all()
    adc2_single_run = res_handeles.get('adc2_single_run').fetch_all()

    params = {
	'out1': np.average(adc1[:-100])/2**12,
	'out2': np.average(adc2[:-100])/2**12,
	}
    print(params)

    plt.figure()
    plt.title('Single run (Check ADCs saturation)')
    plt.plot(adc1_single_run/2**12)
    plt.plot(adc2_single_run/2**12)
    plt.ylabel('Voltage [a.u]')
    plt.xlabel('Readout Time [ns]')
    plt.savefig(r'{}\{}.png'.format(fig_folder, 'ADC_Single_Run'))
    plt.figure()
    plt.title('Averaged run (Check DC Offset)')
    plt.plot(adc1/2**12)
    plt.plot(adc2/2**12)
    plt.ylabel('Voltage [a.u]')
    plt.xlabel('Readout Time [ns]')
    plt.savefig(r'{}\{}.png'.format(fig_folder, 'ADC_Data'))
    plt.show()




