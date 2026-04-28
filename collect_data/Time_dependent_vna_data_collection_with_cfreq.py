# For log and save data 
import sys
sys.path.append(r'D:\Instrument_Program\Config_debdip')
sys.path.append(r'D:\Instrument_Program\keysight_E5071C')
sys.path.append(r'D:\Instrument_Program\americanMagneticsInc430')

import os 
from datetime import datetime
from my_config import *
from logs import initlog
from fileio import experiment

# For measurement
from VNA_keysight_E5071C import E5071C
from AMIxyz_control import AMI430xyz
import pandas as pd
from time import sleep, time
import numpy as np
import pyvisa as visa
import matplotlib.pyplot as plt


if __name__ == "__main__":
    logger = initlog(type='Experiment').get_logger()
    logger.info("Experiment started")

# vna Contact
    vna = E5071C(VNA_address)
    vna.timeout = 600000
    logger.info("VNA connected")
    logger.info("VNA address: {}".format(VNA_address))

# # magnet Contact
#     magnet = AMI430xyz()
#     logger.info("Magnet connected")
    

# vna measurement configuration
    # vna.traces_number(num = 2)
    # vna.active_trace(trace = 1)
    # vna.Spar(Spar = 'S21')
    # vna.format_trace(trace_format = 'mlog')
    # vna.active_trace(trace = 2)
    # vna.Spar(Spar = 'S21')
    # vna.format_trace(trace_format = 'phase')
    # vna.sweep_type(sweep_type = 'linear')

#variables
    measurement_temperature = 0.012 # Kelvin

    room_amplifire = 19
    input_att = 40
    output_att = 6

    # Frequency, offset, delay, span, point list
    frequency_list = [4.25] # GHz
    phase_offset_list = [0] # degree
    electrical_delay_list = [48.567]  # nano second
    span_list = [500] # MHz
    point_list = [5001] # required points in a span
    
    #power
    measurement_power = -30 # vna start power

    #average
    number_of_average = 5 # vna measurement averaging
    
    # band width
    band_width = 1000

    # input power to the device

    _input_power = measurement_power + room_amplifire - input_att

# Experiment Initialization

    # Create a folder for the experiment
    project_name = 'Dephasing_VS_Nitrogen_Concentration'
    experiment_name = 'Temperature_Dependence'
    exp = experiment(project_name, experiment_name, new = True)
    logger.info("Experiment folder created")
    logger.info("Experiment path: {}".format(exp.get_path()))
    device_name = '1400_200nm_D300um'
    device_path = exp.create_folder(base_path = exp.get_path(),_folder = device_name)

    # initialize vna
    vna.power(measurement_power)
    vna.bandwidth(band_width)
    vna.trigger_initiate('off')
    vna.trigger_source('bus')
    vna.average_state(state='on')
    vna.trigger_averaging('on')

    t0 = time()
    count = 0
   
    for i in range(30):

        for freq, span, points, phase_offset, delay in zip(frequency_list, span_list, point_list, phase_offset_list, electrical_delay_list):
            vna.freq_center(freq)
            vna.delay(delay/1e9)
            vna.phase_offset(phase_offset)
            vna.freq_span(span/1e3)
            vna.average_count(number_of_average)
            vna.points(points)
            
            cfreq = int(vna.freq_center()/1e6) # in MHz
            save_data_path = exp.create_folder(base_path = device_path, _folder = str(cfreq)+'MHz')
            vna.trigger_initiate('on')
            vna.trigger_now()

        # collect data

            data = vna.read_all_traces()
            data = pd.DataFrame(data).T
            data.rename(columns = {'0': 'Frequency', '1': 'S21', '2': 'S21-Q', '3': 'S21-Phase','4': 'S21-Phase-Q'}, inplace = True)
            data.to_csv(r'{}/{}MHz_{}dBm_{}.csv'.format(save_data_path,cfreq, _input_power, count), index=False)
            # print(datetime.timedelta(seconds=int(time() - t0)))
            count += 1
        vna.trigger_initiate('off')
        sleep(300)

    
    
    selected_vars = {
        'measurement_temperature',
        'frequency_list',
        'phase_offset_list',
        'electrical_delay_list',
        'span_list',
        'point_list',
        'measurement_power',
        'number_of_average',
        'device_name',
        'experiment_name',
        'project_name',
        'band_width',
        'room_amplifire',
        'input_att',
        'output_att'
    }

    with open(r'{}/variables.txt'.format(device_path), 'w') as f:
        local_vars = locals()
        for var_name in selected_vars:
            f.write(f"{var_name}: {local_vars[var_name]}\n")
            logger.info("Experiment variables")
            logger.info(f"{var_name}: {local_vars[var_name]}")
        logger.info('Experiment variables saved')
    logger.info("Experiment completed")
    # vna.close()

        


    

    
