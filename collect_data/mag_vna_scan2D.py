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
from tqdm import tqdm

# instrument imports

from VNA_Keysight_E5071C.VNA_keysight_E5071C import E5071C
from americanMagneticsInc430.AMIxyz_control import AMI430xyz
from Yokogawa_GS200.yokogawa_gs200 import gs200


current = 0.11506

# VNA parameter
cfreq = 4.5818 # GHz
span = 0.1 #GHz
data_points = 10001
elec_delay = 59.811e-9 #sec
phase_offset = 34.61


exp_power = 0 # dbm
n_avg = 1
avg_state = 'off' # off
bandwidth = 1e6 # Hz

# Power supply parameter
# sw_voltage = 3.3 # volt

# magnet parameter
Bmag_start = 165.15 - 0.5
Bmag_end = 165.15 + 0.5
Bmag_step = 0.005
Bmag_list = np.arange(Bmag_start, Bmag_end+0.5*Bmag_step, Bmag_step)
ramp_rate = 0.05
cooldown_time = 0

# magnetic field direction
theta= 0 
phi = 0

def plot_data(freqs, amps, phases, title, fig_folder):
    figs, ax2 = plt.subplots()
    ax2.plot(freqs, amps, label = 'S11-Amplitude')
    ax2.set_xlabel('Frequency [Hz]')
    ax2.set_ylabel('Amplitude [dBm]')
    ax3 = ax2.twinx()
    ax3.plot(freqs, phases,color= 'red', label='S11-Phase')
    ax3.set_ylabel('Phase [degree]')
    ax2.set_title(title)
    plt.savefig(r'{}/{}.png'.format(fig_folder, title))
    plt.clf()
    plt.close(figs)

def initialize_experiment(project, exp_name):
    logger = initlog(type='Experiment').get_logger()
    exp = experiment(project=project, exp_name=exp_name)
    exp_path = exp.get_path()
    data_folder = exp.create_folder(base_path=exp_path, _folder = 'Data')
    fig_folder = exp.create_folder(base_path=exp_path, _folder = 'fig')
    shutil.copy(__file__,r'{}/mag_vna_scan2D.py'.format(exp_path))
    return logger, exp_path, data_folder, fig_folder


def main(current: float):
    current = round(current*1e3, 3)
    current_str = str(current).split('.')
    if len(current_str)<2:
        current_str.append('0')
    project_name = 'Impedance_Matching_DPPH'
    print(current_str)
    experiment_name = 'rutile_cavity_freq_and_Bfield_DPPH_strong_coupling_gradient{}p{}mA'.format(current_str[0], current_str[1])
    
    logger, exp_path, data_folder, fig_folder = initialize_experiment(project=project_name, exp_name = experiment_name)

    vna = E5071C()
    logger.debug('VNA-conneted: {}: {}'.format(VNA_address,vna.identify()))
    # source = gs200(visa_backend='@py')
    # logger.debug('DC-Sourc-connected: {}: {}'.format(yokogawa_gs200_address,source.identify()))
    magnet = AMI430xyz()
    logger.debug('Magnet_Config: {}'.format(magnet.get_config()))




    vna.power(exp_power)
    vna.bandwidth(bandwidth)
    vna.trigger_initiate('off')
    vna.trigger_source('bus')
    vna.average_state(state=avg_state)
    vna.trigger_averaging('off')

    vna.freq_center(cfreq)
    vna.delay(elec_delay)
    vna.phase_offset(phase_offset)
    vna.freq_span(span)
    vna.average_count(n_avg)
    vna.points(data_points)


    # data structure set-up and running plot
    frequencies = vna.read_freq()
    data2D_mag = np.zeros((len(frequencies), len(Bmag_list)))
    data2D_phase = np.zeros((len(frequencies), len(Bmag_list)))
    fig, ax = plt.subplots()
    image = ax.imshow(data2D_mag, aspect='auto', extent = [Bmag_start, Bmag_end, frequencies[0], frequencies[-1]], origin='lower')
    ax.set_xlabel('Magnetic Field [mT]')
    ax.set_ylabel('Frequency [Hz]')
    ax.set_title('Magnetic Field Sweep Accross Resonance: 114.06mA')
    plt.ion()

    # Magnet_preparation and experiment start
    magnet.rampXYZ(fieldMod=Bmag_start-1, thetaDeg=theta, phiDeg=phi, rampRate=0.5)
    time.sleep(cooldown_time)
    ami_Blist = []

    # Experiment Triggers
    for i,mag in enumerate(tqdm(Bmag_list)):
        magnet.rampXYZ(fieldMod=mag, thetaDeg=theta, phiDeg=phi, rampRate=ramp_rate)
        magxyz = list(magnet.magnetic_field())
        ami_Blist.append([mag, magxyz[0], magxyz[1], magxyz[2]])
        time.sleep(cooldown_time)
        # source.output(True)
        # source.operation_complete() 
        vna.trigger_initiate('on')
        vna.trigger_now()

        data = vna.read_all_traces()
        data = pd.DataFrame(data).T.rename(columns = {0: 'Frequency', 1: 'S11', 2: 'S11-Q', 3: 'S11-Phase',4: 'S11-Phase-Q'})
        data.to_csv(r'{}/{}GHz_{}dBm_{}mT'.format(data_folder,cfreq,exp_power, mag).replace('.','p')+'.csv', index=False)
        data2D_mag[:,i] = data['S11']
        data2D_phase[:,i] = data['S11-Phase']

        plot_data(data['Frequency'], data['S11'], data['S11-Phase'], 'S11_{}GHz_{}dBm_{}mT'.format(cfreq,exp_power, mag).replace('.','p'), fig_folder)
        image.set_array(data2D_mag)
        image.autoscale()
        plt.pause(2)

        # power output off
        vna.trigger_initiate('off')
        # print('Progress:{}/{}'.format(i+1, len(Bmag_list)))
        # source.output(False)

    # magnet.ramp_zero()
    plt.ioff()
    # magnet.ramp_zero()
    Data2D_mag = pd.DataFrame(data2D_mag, columns=Bmag_list, index=frequencies)
    Data2D_mag.to_csv(r'{}/Data2D_mag_{}GHz_{}dBm'.format(exp_path,cfreq,exp_power).replace('.','p')+'.csv')
    Data2D_phase = pd.DataFrame(data2D_phase, columns=Bmag_list, index=frequencies)
    Data2D_phase.to_csv(r'{}/Data2D_phase_{}GHz_{}dBm'.format(exp_path,cfreq,exp_power).replace('.','p')+'.csv')
    plt.savefig(r'{}/VNA_2D_scan_with_magnet.png'.format(exp_path))
    plt.close()
    #plt.show() 
    with open(r'{}/Bfield_list.txt'.format(exp_path), 'w') as f:
        f.write(str(ami_Blist))
     





if __name__=='__main__':
    main(current=current)



