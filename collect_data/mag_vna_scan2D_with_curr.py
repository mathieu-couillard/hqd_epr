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
from americanMagneticsInc430.AMIxyz_control import AMI430xyz
from Yokogawa_GS200.yokogawa_gs200 import gs200
import mag_vna_scan2D
# anti Heltmoltz 
# curr_center = 114e-3
# curr_span = 

curr_start = 100e-3
curr_stop = 130e-3
curr_step = 0.5e-3

curr_list = np.arange(curr_start, curr_stop+0.5*curr_step, curr_step)
print(np.flip(curr_list))

def source_ramp(source, target_level, rate=1e-3 ,step_size=1e-5):
    # units of amp and seconds
    level = float(source.level())
    while level != target_level:
        if target_level>level:
            direction = 1
        else:
            direction = -1
        level = float(source.level())
        level += direction*step_size
        source.level(level)
        if(step_size/rate>0.004):
            time.sleep(step_size/rate)
        if abs(target_level-level) < step_size:
            source.level(target_level)
            break



if __name__ == '__main__':
    mag_grad_source = gs200(visa_backend='@py', address=yokogawa_gs200_address_2)

    mag_grad_source.function(function='current')
    mag_grad_source.source_range(source_range='0.2')
    #source_ramp(mag_grad_source, 0)
    mag_grad_source.output(True)
    mag_grad_source.operation_complete()
    for curr in curr_list:
        source_ramp(mag_grad_source, curr)
        mag_grad_source.operation_complete()
        # print('curr: ', source_curr.level('?'))
        mag_vna_scan2D.main(curr)
    source_ramp(mag_grad_source, 0)










