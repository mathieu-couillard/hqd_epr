# General imports

from config.inst_addresses import InstrumentAddresses as instAddr
import numpy as np
# import matplotlib.pyplot as plt
import time
# from datetime import datetime
# import pandas as pd

# instrument imports

# from VNA_Keysight_E5071C.VNA_keysight_E5071C import E5071C
# from americanMagneticsInc430.AMIxyz_control import AMI430xyz
from drivers import YokogawaGS200
import mag_vna_scan2D
from utils import source_ramp

curr_start = 50e-3
curr_stop = 200e-3
curr_step = 50e-3

curr_list = np.arange(curr_start, curr_stop+0.5*curr_step, curr_step)
print(np.flip(curr_list))

# def source_ramp(source, target_level, rate=1e-3 ,step_size=1e-5):
#     # units of amp and seconds
#     level = float(source.level())
#     while level != target_level:
#         if target_level>level:
#             direction = 1
#         else:
#             direction = -1
#         level = float(source.level())
#         level += direction*step_size
#         source.level(level)
#         if(step_size/rate>0.004):
#             time.sleep(step_size/rate)
#         if abs(target_level-level) < step_size:
#             source.level(target_level)
#             break



if __name__ == '__main__':
    mag_grad_source = YokogawaGS200(visa_backend='@py', address=instAddr.gs200_2)

    mag_grad_source.function(function='current')
    mag_grad_source.source_range(source_range='0.2')
    if not mag_grad_source.output():
        source_ramp(mag_grad_source, 0)
        mag_grad_source.output(True)
    mag_grad_source.operation_complete()
    for curr in curr_list:
        source_ramp(mag_grad_source, curr)
        mag_grad_source.operation_complete()
        # print('curr: ', source_curr.level('?'))
        mag_vna_scan2D.main(curr)
    source_ramp(mag_grad_source, 0)










