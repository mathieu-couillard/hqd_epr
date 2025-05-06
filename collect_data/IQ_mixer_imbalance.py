import sys
sys.path.append(r'D:\Instrument_Program\Config_debdip')
sys.path.append(r'D:\Instrument_Program\Quantum_Machine')
sys.path.append(r'D:\Instrument_Program\SPA')
# spa path
from spa_N9010A import SPA_N9010A
# microwave generator path
from logs import initlog
from fileio import experiment
# QM 
from qm.qua import *
from qm import QuantumMachinesManager
from qm_configs import *
from qm import SimulationConfig
from qm import LoopbackInterface
# for QM
from qualang_tools.loops import from_array
from qualang_tools.results import progress_counter, fetching_tool
# numpy, matplotlib, pyvisa, scipy, time
import matplotlib.pyplot as plt
import pyvisa as visa
import numpy as np
from scipy import signal,optimize
import time

# import SignalHound
# from ..SignalHound_SA import SignalHound

n_average = 1e4
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
	qm.set_output_dc_offset_by_element('spin', 'I', dc_iq[0])
	qm.set_output_dc_offset_by_element('spin', 'Q', dc_iq[1])

	while not job.is_paused():
		time.sleep(0.1)
	job.resume()
	# time.sleep(0.1)
	
	return 10**((spa.valueAtMarker1-spa.valueAtMarker2))

# def calib_dc(dc_iq):
# 	while not job.is_paused():
# 		time.sleep(0.1)

# 	qm.set_output_dc_offset_by_element('spin', 'I', dc_iq[0])
# 	qm.set_output_dc_offset_by_element('spin', 'Q', dc_iq[1])

# 	while not job.is_paused():
# 		time.sleep(0.1)
# 	job.resume()
# 	time.sleep(1)
# 	spa.init_now()
	
# 	time.sleep(1)
# 	valuemarker1 = getmarker(1, frequency=spin_LO)
# 	valuemarker2 = getmarker(2, frequency= (spin_IF + spin_LO))
# 	print(valuemarker1)
# 	print(valuemarker2)
# 	return 10**((valuemarker1-valuemarker2))

def calib_gphi(gphi):
	qm.set_mixer_correction('mixer_spin', int(spin_IF), int(SPIN_LO), IQ_imbalance(gphi[0],gphi[1]))
	while not job.is_paused():
		time.sleep(0.1)
	job.resume()
	# time.sleep(0.1)
	return 10**(spa.valueAtMarker3-spa.valueAtMarker2)**100

# def calib_gphi(gphi):
# 	while not job.is_paused():
# 		time.sleep(0.1)
# 	print(gphi[0])
# 	print(gphi[1])
# 	qm.set_mixer_correction('mixer_spin', int(spin_IF), int(spin_LO), IQ_imbalance(gphi[0], gphi[1]))

# 	while not job.is_paused():
# 		time.sleep(0.1)
# 	job.resume()
# 	time.sleep(0.1)
# 	spa.init_now()
# 	time.sleep(5)
# 	valuemarker3 = getmarker(3, frequency=(spin_LO - spin_IF))
# 	valuemarker2 = getmarker(2, frequency= (spin_IF + spin_LO))
# 	print(valuemarker3)
# 	print(valuemarker2)
# 	return 10**((valuemarker3-valuemarker2))*100


def set_calib_params(dc_I,dc_Q,g,phi):
	qm.set_mixer_correction('mixer_spin', int(spin_IF), int(SPIN_LO), IQ_imbalance(g, phi))
	qm.set_output_dc_offset_by_element('spin', 'I', dc_I)
	qm.set_output_dc_offset_by_element('spin', 'Q', dc_Q)
# ##################################

# do the marker definition for activation, set at x position and measure y
# def getmarker(marker, frequency):
# 	spa.select_marker(marker_number=marker)
# 	spa.marker_mode(mode='position')
# 	spa.markler_state(value='on')
# 	spa.marker_x(freq= frequency)
# 	value = spa.marker_y()
# 	return float(value)



# for the trace collection get_trace

def get_newTrace():
	while not job.is_paused():
		time.sleep(0.1)
	job.resume()
	time.sleep(0.1)

	x,y = spa.getTrace()

	return x,y

# def get_newTrace():
# 	while not job.is_paused():
# 		time.sleep(0.1)
# 	job.resume()
# 	time.sleep(0.1)

# 	data = spa.get_data()

# 	return data

############
#   Main   #
############
logger = initlog(type='Experiment').get_logger()
project_name = 'Tunable_Resonator'
experiment_name = 'IQ_Mixer_Calibration'
exp_path = experiment(project = project_name,exp_name=experiment_name).get_path()
logger.info('Experiment - IQ_Mixer_Calibration')
logger.info('Experiment path: {}'.format(exp_path))
# Load instruments
rm = visa.ResourceManager()
qmm = QuantumMachinesManager(host=host_ip)
qm = qmm.open_qm(config)

# spa = SignalHound.SignalHound()
spa = SPA_N9010A()
spa.refLevel_dBm = 20


# spa.freq_center(spin_LO)
# spa.freq_span((4*ensemble_IF))
# spa.auto_raw_fft_BW(auto='on')
# spa.auto_video_fft_BW(auto='on')
# spa.freq_step(step = 1e6)
# spa.ref_level(0)
spa.centerFreqInGHz = SPIN_LO/1e9
spa.spanInGHz = 0.5
spa.x_Marker1 = SPIN_LO
spa.x_Marker2 = SPIN_LO + spin_IF
spa.x_Marker3 = SPIN_LO - spin_IF

g = 0.02
phi = -0.02
dc_I = -0.02
dc_Q = 0.02
set_calib_params(dc_I,dc_Q,g,phi)
job = qm.execute(IQ_Mixer_Calibration)
# metadata= get_newTrace()
# time.sleep(2)
x, before = get_newTrace()
# ## DC calibration
dc_res = optimize.minimize(calib_dc,[dc_I,dc_Q],method='Nelder-Mead')
logger.debug('dc_I_Q'.format(dc_res))
dc_I = dc_res['x'][0]
dc_Q = dc_res['x'][1]
set_calib_params(dc_I,dc_Q,g,phi)
print('dc done')
logger.info('Finish DC calibration.')
# phase calibration
# gPhi_res= optimize.minimize(calib_gphi,[g,phi],method='Nelder-Mead')
gPhi_res= optimize.minimize(calib_gphi,[g,phi],method='Nelder-Mead',options={'fatol':0.01})
logger.debug('g_phi'.format(gPhi_res))
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
logger.debug('dc_I_Q'.format(dc_res))
dc_I = dc_res['x'][0]
dc_Q = dc_res['x'][1]
set_calib_params(dc_I,dc_Q,g,phi)
print('dc done')
print(dc_I)
print(dc_Q)
print(g)
print(phi)
logger.info('Finish DC calibration.')
IQ_mix_params = {
	'dc_I': dc_I,
	'dc_Q': dc_Q,
	'g': g,
	'phi': phi,
}
logger.debug(IQ_mix_params)
x, after = get_newTrace()

fig, (ax1, ax2) = plt.subplots(ncols = 2, nrows = 1, figsize=(8, 6), layout = 'constrained')
ax1.plot(x,before, label = 'Before Calibration')
ax1.set_title('Before Calibration')
ax1.set_xlabel('Frequency (Hz)')
ax1.set_ylabel('Amplitude (dBm)')
ax2.plot(x,after, label = 'After Calibration')
ax2.set_title('After Calibration')
ax2.set_xlabel('Frequency (Hz)')
ax2.set_ylabel('Amplitude (dBm)')
ax1.legend()
ax2.legend()
plt.savefig(exp_path + r'/IQ_Mixer_Calibration.svg', dpi = 300)
plt.show()
