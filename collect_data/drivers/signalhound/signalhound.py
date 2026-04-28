import numpy as np
import pyvisa as visa
import pandas as pd
import os
# write the wait function for the sweep, and average before collcting data


class SignalHoundSA:

    def __init__(self, address, verbatim = False):
        self._inst = visa.ResourceManager().open_resource(address)
        self._inst.timeout = 3000000
        self._inst.read_termination = '\n'
        self._inst.write_termination = '\n'
        self.verbatim = verbatim
        # self.init_continuous(init='OFF')
        # self.trace_update(update='on')
        self.data_type(type='ascii')
      
        # self.auto_raw_fft_BW(auto='on')
        # self.auto_video_fft_BW(auto='on')
        # self.video_fft_shape(type='flattop')
        # self.measurement_mode(mode='sa')


    ##################################################
    # Display Settings
    ##################################################
    def hidedisplay(self, displayhide = '?'):
        displayhide = str(displayhide)
        options = {
            '?': '?',
            'Ture': ' 1',
            'False': ' 0',
            '1': ' 1',
            '0':  '0'
        }
        if displayhide in options:
            return self._com(':DISP:HIDE{}'.format(options[displayhide]))
        else:
            return Exception('InvalidDisplaySettingException')


    def title(self, title = '?'):
        if title =="?":
            return self._com(':DISP:ANN:TITL?')
        else:
            title = str(title)
            return self._com(':DISP:ANN:TITL {}'.format(title))
    
    def clear_title(self):
        return self._com(':DISP:ANN:CLE')
    




    ################################################
    # Initiation Commands
    ################################################

    def measurement_mode(self, mode = '?'):
        mode = str(mode).lower()
        options = {
            'sa': ' SA', 'rtsa': ' RTSA',
            'zs': ' ZS', 'harmonics': ' HARM',
            'na': ' NA', 'pnoise': ' PN',
            'ddemod': ' DDEM', 'emi': ' EMI',
            'ademod': ' ADEM', 'ih': ' IH',
            'semask': ' SEM', 'nfigure': ' NFIG',
            'wlan': ' WLAN', 'ble': ' BLE',
            'lte': ' LTE', '?': '?'
        }
        if mode in options:
            return self._com(':INST:SEL{}'.format(options[mode]))
        else:
            return Exception('InvalidMeasurementModeSelectionException')
    
    def recalibrate(self):
        return self._com(':INST:RECAL')
    
    def init_continuous(self, init = '?'):
        init = str(init)
        options = {
            'ON': ' ON',
            'OFF': ' OFF',
            '0': ' 0',
            '1': ' 1',
            'True': ' ON',
            'False': ' OFF',
            'On': ' ON',
            'Off': ' OFF',
            'on': ' ON',
            'off': ' OFF',
            '?': '?'
        }

        if init in options:
            return self._com(':INIT:CONT{}'.format(options[init]))
        else:
            return Exception('InvalidContinuousInitiateMothodException')

    def init_now(self):
        return self._com(':INIT:IMM')

    def sweep_time(self,time = '?'):
        """_summary_

        Args:
            time (str, optional): set sweep time in seconds unit. Defaults to '?'.

        Returns:
            str: sweep_time or resoponse due to time set.
        """
        time = str(time)
        if time == '?':
            return self._com(':SENS:SWE:TIME?')
        else:
            return self._com(':SENS:SWE:TIME {}'.format(time))


    ###############################################
    # Frequency Axis
    ###############################################
    def freq_center(self, center = '?'):
        center = str(center)
        if center =='?':
            return self._com(':SENS:FREQ:CENT?')
        else:
            return self._com(':SENS:FREQ:CENT {}'.format(center))
    
    def freq_span(self, span = '?'):
        span = str(span)
        if span == '?':
            return self._com(':SENS:FREQ:SPAN?')
        else:
            return self._com(':SENS:FREQ:SPAN {}'.format(span))

    def freq_start(self, start = '?'):
        start = str(start)
        if start =='?':
            return self._com(':SENS:FREQ:STAR?')
        else:
            return self._com(':SENS:FREQ:STAR {}'.format(start))
    
    def freq_stop(self, stop = '?'):
        stop = str(stop)
        if stop == '?':
            return self._com(':SENS:FREQ:STOP?')
        else:
            return self._com(':SENS:FREQ:STOP {}'.format(stop))
    
    def freq_step(self, step = '?'):
        step = str(step)
        if step == '?':
            return self._com(':SENS:FREQ:CENT:STEP?')
        else:
            return self._com(':SENS:FREQ:CENT:STEP {}'.format(step))
        

    ###############################################
    # power out axis
    ###############################################


    def ref_level(self, reference= '?', unit = 'DBM'):
        reference = str(reference)
        unit = str(unit)
        if reference =='?':
            return self._com(':SENS:POW:RF:RLEV?')+'dBm'
        else:
            return self._com('SENS:POW:RF:RLEV {}{}'.format(reference,unit))
        

    def ref_offset(self, offset = '?'):
        offset = str(offset)
        if offset == '?':
            return self._com(':SENS:POW:RF:RLEV:OFFS?')
        else:
            return self._com(':SENS:POW:RF:RLEV:OFFS {}'.format(offset))

    def ydivision(self, value = '?', unit = 'DBM'):
        value = str(value)
        unit = str(unit)
        if value == '?':
            return self._com(':SENS:POW:RF:PDIV?')+'dBm'
        else:
            return self._com(':SENS:POW:RF:PDIV {}{}'.format(value,unit))



    


    ##############################################
    # FFT settings
    ##############################################

    def raw_fft_BW(self, resolution = '?'):
        resolution = str(resolution)
        if resolution == '?':
            return self._com(':SENS:BAND:RES?')
        else:
            return self._com(':SENS:BAND:RES {}'.format(resolution))
        
    def auto_raw_fft_BW(self, auto = '?'):
        auto = str(auto)
        options = {
            'ON': ' ON',
            'OFF': ' OFF',
            '0': ' 0',
            '1': ' 1',
            'True': ' ON',
            'False': ' OFF',
            'On': ' ON',
            'Off': ' OFF',
            'on': ' ON',
            'off': ' OFF',
            '?': '?'
        }
        if auto in options:
            return self._com(':SENS:BAND:RES:AUTO{}'.format(options[auto]))
        else:
            return Exception('InvalidAutoSettingException')

    def video_fft_BW(self, resolution = '?'):
        resolution = str(resolution)
        if resolution == '?':
            return self._com(':SENS:BAND:VID?')
        else:
            return self._com(':SENS:BAND:VID {}'.format(resolution))
        
    def auto_video_fft_BW(self, auto = '?'):
        auto = str(auto)
        options = {
            'ON': ' ON',
            'OFF': ' OFF',
            '0': ' 0',
            '1': ' 1',
            'True': ' ON',
            'False': ' OFF',
            'On': ' ON',
            'Off': ' OFF',
            'on': ' ON',
            'off': ' OFF',
            '?': '?'
        }
        if auto in options:
            return self._com(':SENS:BAND:VID:AUTO{}'.format(options[auto]))
        else:
            return Exception('InvalidAutoSettingException')
    
    def video_fft_shape(self, type = '?'):
        type = str(type).lower()
        options = {
            'flattop': ' FLAT',
            'nuttall': ' NUTT',
            'gaussian': ' GAUS',
            '?': '?'
        }
        if type in options:
            return self._com(':SENS:BAND:SHAP{}'.format(options[type]))
        else:
            return Exception('InvalidFFTWindowTypeException')
    
    
    #############################################
    # Trace Selection
    ##############################################

    def active_trace(self, trace = '?'):
        trace = str(trace)
        if trace == '?' and type == '?':
            return self._com(':TRAC:SEL?')
        else:
            return self._com(':TRAC:SEL {}; UPD:STAT: ON'.format(trace))
        
    def trace_type(self, type = '?'):
        type = str(type).lower()
        options = {
            'off': ' OFF',
            'write': ' WRIT',
            'average': ' AVER',
            'maxhold': ' MAX',
            'minhold': ' MIN',
            'minmax': ' MINMAX',
            'min': ' MIN',
            'max': ' MAX',
            'avg': ' AVGR',
            '?': '?'
        }
        if type in options:
            return self._com(':TRAC: TYPE{}'.format(options[type]))
        else:
            return Exception('INvalidTraceTypeError')

    def average_count(self, average = '?'):
        type = self.trace_type()
        if type == 'average':
            average = str(average)
            if average =='?':
                return self._com(':TRAC:AVER:COUN?')
            else:
                return self._com(':TRAC:AVER:COUN {}'.format(average))
        else:
            return Exception('InvalidAverageTypeException. Trace_type: {}'.format(type))
    
    def trace_update(self, update ='?'):
        update = str(update).lower()
        options = {
            'ON': ' ON',
            'OFF': ' OFF',
            '0': ' 0',
            '1': ' 1',
            'True': ' ON',
            'False': ' OFF',
            'On': ' ON',
            'Off': ' OFF',
            'on': ' ON',
            'off': ' OFF',
            '?': '?'
        }
        if update in options:
            return self._com(':TRAC:UPD:STAT{}'.format(options[update]))
        else:
            return Exception('InvalidTraceUpdateTypeException')

    def clear_trace(self):
        return self._com(':TRAC:CLE')
    
    def clear_trace_all(self):
        return self._com(':TRAC:CLE:ALL')
    
    def sweep_start(self):
        return self._com(':TRAC:XSTAR?')
    
    def sweep_increment(self):
        return self._com(':TRAC:XINC?')
    
    def sweep_point(self):
        return self._com(':TRAC:POIN?')

    def sweep_freq_list(self):
        start_frequency = self.sweep_start()
        increment = self.sweep_increment()
        points = self.sweep_point()
        end_frequency = start_frequency + points*increment
        frequency_list = np.arange(start_frequency, end_frequency, increment)
        frequency_list = [str(i) for i in frequency_list]

        return frequency_list    


    ##########################################
    # Data
    ##########################################

    def get_data(self):
        xdata = self.sweep_freq_list()
        ytrace = self._com(':TRAC:DATA?')
        ydata = [str(x) for x in ytrace.split(',')]
        print(len(xdata))
        print(len(ydata))
        data = pd.DataFrame(
            {
                'frequency': xdata,
                'power(dbm)': ydata
            }
        )
        return data

    def data_type(self, type = '?'):
        type = str(type).lower()
        options = {
            'ascii': ' ASCII',
            'real': ' REAL',
            '?':'?'
        }
        if type in options:
            return self._com(':FORM:TRAC:DATA{}'.format(options[type]))
        else:
            return Exception('InvalidDataTypeRequestException')
        

    ################################################
    # Marker Commands
    ################################################


    def select_marker(self, marker_number = '?'):
        marker_number = str(marker_number)
        if marker_number == '?':
            return self._com(':CALC:MARK:SEL?')
        else:
            return self._com(':CALC:MARK:SEL {}'.format(marker_number))


    def markler_state(self, value = 'on'):
        value = str(value).lower()
        options = {
            '0': ' 0',
            '1': ' 1',
            'True': ' ON',
            'False': ' OFF',
            'on': ' ON',
            'off': ' OFF',
            '?': '?'
        }
        if value in options:
            return self._com(':CALC:MARK:STAT{}'.format(options[value]))
        else:
            return Exception('InvalidMarkerStateSelectedException')
    

    def selected_marker_place_trace(self, trace = '?'):
        trace = str(trace)
        if trace == '?':
            return self._com(':CALC:MARK:TRAC?')
        else:
            return self._com(':CLAC:MARK:TRAC {}'.format(trace))
    
    def marker_x(self, freq = '?'):
        freq = str(freq)
        if freq == '?':
            return self._com(':CALC:MARK:X?')
        else:
            return self._com(':CALC:MARK:X {}'.format(freq))


    def marker_y(self):
        return self._com(':CALC:MARK:Y?')

    def marker_mode(self, mode = '?'):
        mode = str(mode).lower()
        options = {
            'position': ' POS',
            'noise': ' NOISE',
            'chpower': ' CHP',
            'nbd': ' NBD',
            '?': '?'
        }

        if mode in options:
            return self._com(':CALC:MARK:MODE{}'.format(options[mode]))
        else:
            return Exception('InvalidMarkerModeTypeSelectionException')
        
    def set_marker(self,freq, marker = 1, marker_mode = 'position'):
        self.select_marker(marker_number=marker)
        self.marker_mode(mode=marker_mode)
        self.marker_x(freq=freq)
    
    def get_marker(self,marker = 1):
        self.select_marker(marker_number=marker)
        return self.marker_y()






    ####################################
    # General commands
    ####################################

    def identity(self):
        return self._com('*IDN?')
    
    def operation_complete(self):
        return self._com('*OPC?')
    

    






    def _com(self, cmd):
        """_summary_

        Args:
            cmd (str): SCPI commands in the string format

        Returns:
            str/float: returns query value or written SCPI command
        """
        if self.verbatim:
            print(cmd)
        if cmd[-1] == '?':
            
            value = self._inst.query(cmd)
            try:
                return float(value)
            except:
                return value
        else:
            self._inst.write(cmd)
            return "sent: " + cmd
        


if __name__ == "__main__":
    spa = SignalHound()
    spa.init_continuous(init='off')
    data = spa.get_data()
    print(data)





    
