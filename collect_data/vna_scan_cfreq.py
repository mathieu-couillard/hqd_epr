# General imports

from Config_debdip.my_config import *
from Config_debdip.fileio import experiment
from Config_debdip.logs import initlog
import numpy as np
import matplotlib.pyplot as plt
import time
from datetime import datetime
import pandas as pd
import shutil

# instrument imports

from VNA_Keysight_E5071C.VNA_keysight_E5071C import E5071C
from Yokogawa_GS200.yokogawa_gs200 import gs200

project_name = 'Impedance_Matching_with_DPPH'
experiment_name = 'room_temp_bare_cavity_kappa11MHz'

cfreq = 5.209344 # GHz
span = 0.120 #GHz
data_points = 4001
elec_delay = 56.669e-9 #sec
phase_offset = -42.35

exp_power = 0 # dbm
n_avg = 5
avg_state = 'off' # off
bandwidth = 1000 # Hz

sw_voltage = 3.3 # volt


if __name__ == '__main__':
    logger = initlog(type='Experiment').get_logger()
    exp_path = experiment(project=project_name, exp_name=experiment_name).get_path()

    vna = E5071C()
    logger.debug('VNA-conneted: {}: {}'.format(VNA_address,vna.identify()))
    # source = gs200(visa_backend='@py')
    # logger.debug('DC-Sourc-connected: {}: {}'.format(yokogawa_gs200_address,source.identify()))

    # # vna measuremnt configuration

    # vna.sweep_type(sweep_type='linear')
    # vna.traces_number(num=2)
    # vna.active_trace(trace=1)
    # vna.Spar(Spar='S21', trace=1)
    # vna.format_trace(trace_format='mlog')
    # time.sleep(0.5)
    # vna.active_trace(trace=2)
    # vna.Spar(Spar='S21', trace=2)
    # vna.format_trace(trace_format='phase')
    # time.sleep(0.5)

    # vna.power(exp_power)
    # vna.bandwidth(bandwidth)
    # vna.trigger_initiate('off')
    # vna.trigger_source('bus')
    # vna.average_state(state=avg_state)
    # vna.trigger_averaging('on')

    # vna.freq_center(cfreq)
    # vna.delay(elec_delay)
    # vna.phase_offset(phase_offset)
    # vna.freq_span(span)
    # vna.average_count(n_avg)
    # vna.points(data_points)

    # Source Configuration

    # source.function(function='voltage')
    # source.source_range(source_range='10')
    # source.level(3.3)

    # # Experiment Triggers
    # source.output(True)
    # time.sleep(1)    
    # vna.trigger_initiate('on')
    # vna.trigger_now()

    data = vna.read_all_traces()
    data = pd.DataFrame(data).T
    data.rename(columns = {'0': 'Frequency', '1': 'S11', '2': 'S11-Q', '3': 'S11-Phase','4': 'S11-Phase-Q'}, inplace = True)
    data.to_csv(r'{}/{}Hz_{}dBm.csv'.format(exp_path,cfreq,exp_power), index=False)
    shutil.copy(__file__,r'{}/vna_scan_cfreq.py'.format(exp_path))
    # power output off
    vna.trigger_initiate('off')
    # source.output(False)  









