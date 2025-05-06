# For log and save data
import sys
sys.path.append(r'D:\Instrument_Program\Config_debdip')
sys.path.append(r'D:\Instrument_Program\keysight_E5071C')

import os 
from datetime import datetime
from my_config import *
from logs import initlog
from fileio import experiment

# For measurement
from VNA_Keysight_E5071C.VNA_keysight_E5071C import E5071C
# from AMIxyz_control import AMI430xyz
import pandas as pd
from time import sleep, time
import numpy as np
import pyvisa as visa
import matplotlib.pyplot as plt


def plot_data(freqs, amps, phases, title, fig_folder):
    figs, ax2 = plt.subplots()
    ax2.plot(freqs, amps,color = 'blue', label = 'S11-Amplitude')
    ax2.set_xlabel('Frequency [Hz]')
    ax2.set_ylabel('Amplitude [dBm]')
    ax3 = ax2.twinx()
    ax3.plot(freqs, phases, color = 'red', label='S11-Phase')
    ax3.set_ylabel('Phase [degree]')
    ax2.set_title(title)
    plt.savefig(r'{}/{}.png'.format(fig_folder, title))
    plt.clf()
    plt.close(figs)


if __name__ == "__main__":
    logger = initlog(type='Experiment').get_logger()
    logger.info("Experiment started")
# vna Contact
    # rm = visa.ResourceManager()
    vna = E5071C(VNA_address)
    vna.timeout = 600000
    logger.info("VNA connected")
    logger.info("VNA address: {}".format(VNA_address))

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
    room_amplifire = 18
    line_att = 16

    # Frequency, offset, delay, span, point list
    frequency_list = [4.156, 4.23281, 4.32558, 4.36838, 4.442, 4.4680, 4.5532, 4.35] # GHz
    # phase_offset_list = [44.71, 44.71, 44.71, 44.71] # degree
    # electrical_delay_list = [48.2, 48.2, 48.2, 48.2]  # nano second
    span_list = [200, 40, 40, 40,40,40,100,300] # MHz
    point_list = [4001,4001,4001,4001,4001,4001,4001,4001,10001] # required points in a span
    #power
    start_power = -40 # vna start power 
    stop_power = -20 # vna stop power 
    power_step = 2 # vna power step
    #average
    number_of_average = 20 # vna measurement averaging
    number_of_average_high_power = 10 # vna measurement averaging
    
    high_power_start = -10 # when program will consider power as high
    #bandwidth
    band_width = 500
    band_width_high_power = 500
    #power list
    power_list = np.arange(start_power, stop_power+1, power_step) # makes the power list
    power_list = [f'{num:+03d}' for num in power_list.astype(int)] # modifies the power list
    print(power_list)
    

# Experiment initiation


    project_name = 'Dephasing_VS_Nitrogen_Concentration'
    experiment_name = 'Resonator_Response'
    exp = experiment(project_name, experiment_name, new = True)
    logger.info("Experiment initiated")
    logger.info("Experiment path: {}".format(exp.get_path()))
    device_name = 'L1400_D150_100nm_{}K'.format(measurement_temperature)
    device_path = exp.create_folder(base_path = exp.get_path(),_folder = device_name)
    logger.info("power list: {}".format(power_list))

    # Initial vna
    vna.trigger_initiate('off')
    vna.average_state(state='on')
    vna.set_trigger(source='bus', averaging='on', initiate=True)


    # t0= time()
    count = 0
# Frequency dependent measurement loop
    for freq, span, points in zip(frequency_list, span_list, point_list):    
        vna.freq_center(freq)
        # vna.delay(delay/1e9)
        # vna.phase_offset(phase_offset)
        vna.freq_span(span/1000)
        vna.points(points)
        vna.average_count(count=number_of_average)
        vna.bandwidth(bandwidth=band_width)

        
        
        cfreq = int(vna.freq_center()/1e6) #give in integer MHz frequency
        save_data_path = exp.create_folder(base_path=device_path, _folder = str(cfreq)+'MHz')
        logger.info("Data directory created")
        logger.info("Data directory path: {}".format(save_data_path))

        vna.trigger_initiate('on')
        count = count + 1

    # Power dependent measurement loop
        for power in power_list:
            vna.power(int(power))
            print(power)

        # write your power dependent measurement conditions here
            if int(power) >= high_power_start:
                vna.average_count(number_of_average_high_power)
                vna.bandwidth(band_width_high_power)
                vna.trigger_initiate('off')
                sleep(20)
                vna.trigger_initiate('on')
                vna.trigger_now()
                    
            else:
                vna.average_count(number_of_average)
                vna.bandwidth(band_width)
                vna.trigger_initiate('off')
                sleep(10)
                vna.trigger_initiate('on')
                vna.trigger_now()
                

        # Collect data

            data = vna.read_all_traces()
            data = pd.DataFrame(data).T
            data.rename(columns={0: 'Frequency', 1: 'S21', 2: 'S21-Q', 3: 'S21-Phase',4: 'S21-Phase-Q'}, inplace=True)
            print('Saving Data')
            data.to_csv(r'{}/{}MHz_{}dBm.csv'.format(save_data_path,cfreq, power), index=False)
            print('Data Saved')
            plot_data(data['Frequency'], data['S21'], data['S21-Phase'], title=r'{}MHz_{}dBm'.format(cfreq, power), fig_folder=save_data_path)

            # print(datetime.timedelta(seconds=int(time() - t0)))
    
        vna.trigger_initiate('off')
        vna.power(start_power)
        sleep(120)
    
    selected_vars = {
        'measurement_temperature',
        'frequency_list',
        # 'phase_offset_list',
        # 'electrical_delay_list',
        'span_list',
        'point_list',
        'start_power',
        'stop_power',
        'power_step',
        'number_of_average',
        'device_name',
        'power_list',
        'number_of_average',
        'number_of_average_high_power',
        'high_power_start',
        'band_width',
        'band_width_high_power',
        # 'room_amplifire',
        # 'line_att'
    }
    # Open the file in write mode
    with open(r'{}/variables.txt'.format(device_path), 'w') as file:
        local_vars = locals()
        for var_name in selected_vars:
            file.write(f"{var_name}: {local_vars[var_name]}\n")
            logger.info("Experiment variables")
            logger.info(f"{var_name}: {local_vars[var_name]}")
        logger.info("Experiment variables saved")
    
    logger.info("Experiment completed")

    # vna.close()
    # print('closed')
    # rm.close()



    # freq = data[0]
    # trace1 = data[1]
    # trace2 = data[3]
    # plt.plot(freq, trace1,label = 'S21')
    # plt.plot(freq,trace2, label = 'S21-Phase')
    # plt.legend(framealpha = 1)
    # plt.xlabel("frequency")
    # plt.ylabel("S21")
    # plt.show()




    
