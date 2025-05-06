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

# magnet Contact
    magnet = AMI430xyz()
    logger.info("Magnet connected")
    

# vna measurement configuration
    vna.traces_number(num = 2)
    vna.active_trace(trace = 1)
    vna.Spar(Spar = 'S21')
    vna.format_trace(trace_format = 'mlog')
    vna.active_trace(trace = 2)
    vna.Spar(Spar = 'S21')
    vna.format_trace(trace_format = 'phase')
    vna.sweep_type(sweep_type = 'linear')

# Magnet related variables
    # Magnetic field list
    modmagf_start = 0 # mT
    modmagf_stop = 100 # mT
    modmagf_step = 1 # mT
    modmagf_list = np.arange(modmagf_start, modmagf_stop, modmagf_step)
    # for direction of the magnetic field
    mag_theta = 0 # degree
    mag_phi = 0 # degree
    modmagfield = 50 # mT for fixed magnetic field
    # Field ramp rate
    ramp_rate = 0.5 # mT/s

# VNA related variables
    measurement_temperature = 0.012 # Kelvin
    room_amplifire = 19
    input_att = 40
    output_att = 6
    # Frequency, offset, delay, span, point list
    frequency_list = [7.4211, 12.1915, 13.772, 14.808] # GHz
    phase_offset_list = [44.71, 44.71, 44.71, 44.71] # degree
    electrical_delay_list = [48.2, 48.2, 48.2, 48.2]  # nano second
    span_list = [200, 300, 1000, 200] # MHz
    point_list = [4001,4001,4001,4001,4001,4001,4001,4001] # required points in a span
    #power
    measurement_power = -20 # vna start power
    #average
    number_of_average = 40 # vna measurement averaging
    # band width
    band_width = 500
    # input power to the device
    _input_power = measurement_power + room_amplifire - input_att
# Experiment Initialization
    # Create a folder for the experiment
    project_name = 'Tunable_Coupler'
    experiment_name = 'Resonator Response with external magnetic field along x-axis'
    exp = experiment(project_name, experiment_name, new = True)
    logger.info("Experiment folder created")
    logger.info("Experiment path: {}".format(exp.get_path()))
    device_name = '1400_100nm_D300um'
    device_path = exp.create_folder(base_path = exp.get_path(),_folder = device_name)
    # initialize vna
    vna.power(measurement_power)
    vna.bandwidth(band_width)
    vna.trigger_initiate('off')
    vna.trigger_source('bus')
    vna.average_state(state='on')
    vna.trigger_averaging('off')
    t0 = time()
    count = 0
    for freq, span, points, phase_offset, delay in zip(frequency_list, span_list, point_list, phase_offset_list, electrical_delay_list):
        vna.freq_center(freq)
        vna.delay(delay/1e9)
        vna.phase_offset(phase_offset)
        vna.freq_span(span/1000)
        vna.points(points)
        vna.average_count(number_of_average)
        
        cfreq = int(vna.freq_center()/1e6) # in MHz
        save_data_path = exp.create_folder(basepath = device_path, _folder = str(cfreq)+'MHz')
        
        data2D = np.zeros((len(modmagf_list), points))
        mag_count = 0
        for modmagf in modmagf_list:
            magnet.rampXYZ(fieldMod = modmagf, thetaDeg = mag_theta, phiDeg = mag_phi, rampRate = ramp_rate)    
            sleep(1)
            vna.trigger_initiate('on')
            vna.trigger_now()
        # collect data
            data = vna.read_all_traces()
            data = pd.DataFrame(data).T
            data.rename(columns = {'0': 'Frequency', '1': 'S21', '2': 'S21-Q', '3': 'S21-Phase','4': 'S21-Phase-Q'}, inplace = True)
            data.to_csv(r'{}/{}MHz_{}dBm_{}mT.csv'.format(save_data_path,cfreq, _input_power, modmagf), index=False)
            data2D[mag_count] = data['S21']
            vna.trigger_initiate('off')
            mag_count += 1
        
        data2D.to_csv(r'{}/{}MHz_{}dBm_2D_magnetic_field.csv'.format(save_data_path,cfreq, _input_power), index=False)
        count += 1
        
        print(datetime.timedelta(seconds=int(time() - t0)))
        magnet.ramp_zero()
        
        # angles = magnet.rotateInPlane(fieldMod = modmagfield, initThetaDeg = mag_theta, initPhiDeg = mag_phi, axisThetaDeg = 0, axisPhiDeg = 0, rotStep=1, rotRange=180)
        # data2d = np.zeros((len(angles)+2, len(points)+2))
        # i = 0
        # for [theta, phi] in angles:
        #     magnet.rampXYZ(fieldMod = modmagf, thetaDeg = theta, phiDeg = phi, rampRate = ramp_rate)    
        #     sleep(1)
        #     vna.trigger_initiate('on')
        #     vna.trigger_now()
        # # collect data
        #     data = vna.read_all_traces()
        #     data = pd.DataFrame(data).T
        #     data.rename(columns = {'0': 'Frequency', '1': 'S21', '2': 'S21-Q', '3': 'S21-Phase','4': 'S21-Phase-Q'}, inplace = True)
        #     data.to_csv(r'{}/{}MHz_{}dBm_{}mT_{}.csv'.format(save_data_path,cfreq, _input_power, modmagf,i), index=False)
        #     data2d[i+1] = data['S21']
        #     vna.trigger_initiate('off')
        #     data2d[0] = data['Frequency']
        #     i += 1
        # data2d.to_csv(r'{}/{}MHz_{}dBm_{}mT_inPlaneRotate_2D.csv'.format(save_data_path,cfreq, _input_power, modmagf), index=False)
        # print(datetime.timedelta(seconds=int(time() - t0)))
        # count += 1
        # magnet.ramp_zero()
    
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
        'output_att',
        'modmagf_start',
        'modmagf_stop',
        'modmagf_step',
        'mag_theta',
        'mag_phi',
        'ramp_rate',
        'modmagf_list'
    }

    with open(r'{}/variables.txt'.format(device_path), 'w') as f:
        local_vars = locals()
        for var_name in selected_vars:
            f.write(f"{var_name}: {local_vars[var_name]}\n")
            logger.info("Experiment variables")
            logger.info(f"{var_name}: {local_vars[var_name]}")
        logger.info('Experiment variables saved')
    logger.info("Experiment completed")
    vna.close()

        


    

    
