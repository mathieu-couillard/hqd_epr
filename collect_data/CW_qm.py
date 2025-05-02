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

print(saturation_wf_amp)

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

job = qm.execute(IQ_Mixer_Calibration)


for i in range(2):
	while not job.is_paused():
		time.sleep(0.1)
	job.resume()

job.halt()


