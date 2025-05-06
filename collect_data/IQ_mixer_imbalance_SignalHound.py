# spa path
# from spa_N9010A import SPA_N9010A
from SignalHound_SA.SignalHound import SignalHound
# microwave generator path
from Config_debdip.logs import initlog
from Config_debdip.fileio import experiment
# QM 
from qm.qua import *
from qm import QuantumMachinesManager
from Quantum_Machine.qm_configs import *
# for QM
from qualang_tools.loops import from_array
from qualang_tools.results import progress_counter, fetching_tool
# numpy, matplotlib, pyvisa, scipy, time
import matplotlib.pyplot as plt
import pyvisa as visa
import numpy as np
from scipy import signal,optimize
import time
import pandas as pd


n_average = 5e6
with program() as IQ_Mixer_Calibration:
	n = declare(int)
	with while_(True):
		pause()
		play('spa', 'SPA')
		with for_(n, 0, n < n_average, n + 1):
			play('saturation','spin')

###################
#    Functions    #
###################
def calib_dc(dc_iq):
	while not job.is_paused():
		time.sleep(0.1)

	qm.set_output_dc_offset_by_element('spin', 'I', dc_iq[0])
	qm.set_output_dc_offset_by_element('spin', 'Q', dc_iq[1])

	while not job.is_paused():
		time.sleep(0.1)
	job.resume()
	spa.init_now()
	spa.operation_complete()
	valuemarker1 = spa.get_marker(marker=1)#getmarker(1, frequency=spin_LO)
	valuemarker2 = spa.get_marker(marker=2)#getmarker(2, frequency= (spin_IF + spin_LO))
	print(valuemarker1)
	print(valuemarker2)
	return 10**((valuemarker1-valuemarker2)/10)

def calib_gphi(gphi):
	while not job.is_paused():
		time.sleep(0.1)
	print(gphi[0])
	print(gphi[1])
	qm.set_mixer_correction('mixer_spin', int(spin_IF), int(spin_LO), IQ_imbalance(gphi[0], gphi[1]))

	while not job.is_paused():
		time.sleep(0.1)
	job.resume()
	spa.init_now()
	spa.operation_complete()
	valuemarker3 = spa.get_marker(marker=3)#getmarker(3, frequency=(spin_LO - spin_IF))
	valuemarker2 = spa.get_marker(marker=2)#getmarker(2, frequency= (spin_IF + spin_LO))
	print(valuemarker3)
	print(valuemarker2)
	return 10**((valuemarker3-valuemarker2)/10)

def set_calib_params(dc_I,dc_Q,g,phi):
	qm.set_mixer_correction('mixer_spin', int(spin_IF), int(spin_LO), IQ_imbalance(g, phi))
	qm.set_output_dc_offset_by_element('spin', 'I', dc_I)

	qm.set_output_dc_offset_by_element('spin', 'Q', dc_Q)

# for the trace collection get_trace

def get_newTrace():
	while not job.is_paused():
		time.sleep(0.1)
	job.resume()

	return spa.get_data()

############
#   Main   #
############
logger = initlog(type='Experiment').get_logger()
project_name = 'Impedance_Matching_with_DPPH'
experiment_name = 'IQ_Mixer_Calibration'
exp_path = experiment(project = project_name,exp_name=experiment_name).get_path()
logger.info('Experiment - IQ_Mixer_Calibration')
logger.info('Experiment path: {}'.format(exp_path))

# Load instruments
rm = visa.ResourceManager()
qmm = QuantumMachinesManager(host=host_ip)
qm = qmm.open_qm(config)
#Open SPA
spa = SignalHound()
#configure SPA
spa.freq_center(center=spin_LO)
spa.freq_span(span=5*spin_IF)
# spa.auto_raw_fft_BW(auto='on')
# spa.auto_video_fft_BW(auto='on')
spa.raw_fft_BW(resolution=30e3)
spa.video_fft_BW(resolution=30e3)
spa.freq_step(step = 1e6)
spa.ref_level(20)
spa.set_marker(freq=spin_LO, marker=1)
spa.set_marker(freq=spin_LO+spin_IF, marker=2)
spa.set_marker(freq=spin_LO-spin_IF, marker=3)
# Initaial Guesses and set the parameter
g = -0.02 
phi = 0.05 # these are initial values
dc_I = 0.02
dc_Q = -0.02

# mixer_gain = 0.06197836277633909
# minxer_phase = -0.024094506129622398
# dc_in_I = -0.02123538254514486
# dc_in_Q =  -0.02018161319622236


set_calib_params(dc_I,dc_Q,g,phi)
# Execute it on QM
job = qm.execute(IQ_Mixer_Calibration)
time.sleep(5)
metadata= get_newTrace()
before = get_newTrace()

# ## DC calibration
dc_res = optimize.minimize(calib_dc,[dc_I,dc_Q],method='Nelder-Mead', options={'fatol': 0.01})
logger.debug('dc_I_Q: {}'.format(dc_res))
dc_I = dc_res['x'][0]
dc_Q = dc_res['x'][1]
set_calib_params(dc_I,dc_Q,g,phi)
print('dc done')
logger.info('Finish DC calibration.')

# phase calibration
gPhi_res= optimize.minimize(calib_gphi,[g,phi],method='Nelder-Mead', options={'fatol': 0.01})
logger.debug('g_phi: {}'.format(gPhi_res))
g= gPhi_res['x'][0]
phi = gPhi_res['x'][1]
set_calib_params(dc_I,dc_Q,g,phi)
print('phase done')
print(dc_I)
print(dc_Q)
print(g)
print(phi)
logger.info('Finish g phi calibration.')

# ## DC calibration
dc_res = optimize.minimize(calib_dc,[dc_I,dc_Q],method='Nelder-Mead')
logger.debug('dc_I_Q: {}'.format(dc_res))
dc_I = dc_res['x'][0]
dc_Q = dc_res['x'][1]
set_calib_params(dc_I,dc_Q,g,phi)
print('dc done')
logger.info('Finish DC calibration.')

# # if needed do extra phase and dec calibration again
# # phase calibration
# gPhi_res= optimize.minimize(calib_gphi,[g,phi],method='Nelder-Mead', options={'fatol': 0.01})
# logger.debug('g_phi: {}'.format(gPhi_res))
# g= gPhi_res['x'][0]
# phi = gPhi_res['x'][1]
# set_calib_params(dc_I,dc_Q,g,phi)
# print('phase done')
# print(dc_I)
# print(dc_Q)
# print(g)
# print(phi)
# logger.info('Finish g phi calibration.')

# # ## DC calibration
# dc_res = optimize.minimize(calib_dc,[dc_I,dc_Q],method='Nelder-Mead')
# logger.debug('dc_I_Q: {}'.format(dc_res))
# dc_I = dc_res['x'][0]
# dc_Q = dc_res['x'][1]
# set_calib_params(dc_I,dc_Q,g,phi)
# print('dc done')
# logger.info('Finish DC calibration.')
print('dc_I_offset:',dc_I)
print('dc_Q_offset',dc_Q)
print('Mixer gain inbalance:',g)
print('Mixer phase inbalance:',phi)

IQ_mix_params = {
	'dc_I': dc_I,
	'dc_Q': dc_Q,
	'g': g,
	'phi': phi,
}
logger.debug(IQ_mix_params)
after = get_newTrace()
before.to_csv(r'{}/before_calibration.csv'.format(exp_path))
after.to_csv(r'{}/after_calibration.csv'.format(exp_path))


# for the final plot (read the data and plot)
data1 = pd.read_csv(r'{}/before_calibration.csv'.format(exp_path))
data2 = pd.read_csv(r'{}/after_calibration.csv'.format(exp_path))

# Plot the save data
fig, (ax1, ax2) = plt.subplots(2, figsize = (8,10))
ax1.plot(data1['frequency'], data1['power(dbm)'], label = 'Before Calibration')
ax1.set_title('Before Calibration')
ax1.set_xlabel('Frequency[GHz]')
ax1.set_ylabel('power(dBm)')
ax1.legend()
ax1.grid()

ax2.plot(data2['frequency'], data2['power(dbm)'], label = 'After Calibration')
ax2.set_title('After Calibration')
ax2.set_xlabel('Frequency[GHz]')
ax2.set_ylabel('power(dBm)')
ax2.legend()
ax2.grid()
plt.savefig('{}/Calibration.png'.format(exp_path))
plt.savefig('{}/Calibration.svg'.format(exp_path))
plt.show()
