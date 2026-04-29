import numpy as np
import pyvisa as visa
from time import sleep

class KeysightE5071C:
    def __init__(self, address, configs="", verbatim=False):
        self._inst = visa.ResourceManager('@py').open_resource(address)
        self._active_chan = 1
        self._active_trace = 1
        self.verbatim = verbatim  # Print every command before sending
        
        self._inst.read_termination = '\n'
        self._inst.timeout = 30000
        

    ########################################
    # Selecting channel and trace
    ########################################
    def traces_number(self, num='?', chan=""):
        if chan == "":
            chan = self._active_chan
        if num != '?':
            num = " " + str(num)
        return self._com(":CALC{}:PAR:COUN{}".format(chan, num))

    def displayed_channels(self, chans='?'):
        chans = str(chans)
        options = {'1': ' D1',
                   '12': ' D1_2',
                   '13': ' D1_3',
                   '123': ' D1_2_3',
                   '1234': ' D1_2_3_4',
                   '123456': ' D1_2_3_4_5_6',
                   '?': '?'
                   }
        if chans in options:
            return self._com(":DISP:SPL{}".format(options[chans]))
        else:
            raise Exception("InvalidDisplaySettingException")

    def active_chan(self, chan):
        return self._com(":DISP:WIND{}:ACT".format(chan))

    def active_trace(self, trace="?", chan=""):
        if chan == "":
            chan = self._active_chan
        else:
            self._active_chan = chan
        if trace == '?':
            return self._com(":SERV:CHAN{}:TRAC:ACT?".format(chan))

        return self._com(':CALC{}:PAR{}:SEL'.format(chan, trace))

    ########################################
    # Averaging
    ########################################

    def average_reset(self, chan=""):
        if chan == "":
            chan = self._active_chan
        return self._com(":SENS{}:AVER:CLE".format(chan))

    def average_count(self, count='?', chan=""):
        if chan == "":
            chan = self._active_chan
        if count != '?':
            count = " " + str(count)
        return self._com(":SENS{}:AVER:COUN{}".format(chan, count))

    def average_state(self, state="?", chan=""):
        options = {'on': " on", '1': ' 1', 'true': ' on',
                  'off': ' off', '0': ' 0', 'false': ' 0',
                  '?': '?'
                  }
        if chan == "":
            chan = self._active_chan
        state = str(state).lower()
        if state in options:
            return self._com(":SENS{}:AVER:STAT{}".format(chan, options[state]))
        else:
            Exception('InvalidStateError: valid states are {}'.format(options.keys()))
    ########################################
    # Frequency axis
    ########################################
    def freq_start(self, freq='?', chan=""):
        if chan == "":
            chan = self._active_chan
        if type(freq) != str:
            freq = " " + str(freq*1e9)
        return self._com(":SENS{}:FREQ:STAR{}".format(chan, freq))

    def freq_stop(self, freq='?', chan=""):
        if chan == "":
            chan = self._active_chan
        if type(freq) != str:
            freq = " " + str(freq*1e9)
        return self._com(":SENS{}:FREQ:STOP{}".format(chan, freq))

    def freq_center(self, freq='?', chan=""):
        if chan == "":
            chan = self._active_chan
        if type(freq) != str:
            freq = " " + str(freq*1e9)
        return self._com(":SENS{}:FREQ:CENT{}".format(chan, freq))

    def freq_span(self, freq='?', chan=""):
        if chan == "":
            chan = self._active_chan
        if type(freq) != str:
            freq = " " + str(freq*1e9)
        return self._com(":SENS{}:FREQ:SPAN{}".format(chan, freq))

    def points(self, points='?', chan=""):
        if chan == "":
            chan = self._active_chan
        if type(points) != str:
            points = " " + str(points)
        return self._com(":SENS{}:SWE:POIN{}".format(chan, points))

    def IFBW(self, bandwidth='?', chan=""):
        if chan == "":
            chan = self._active_chan
        if type(bandwidth) != str:
            bandwidth = " " + str(bandwidth)
        return self._com(":SENS{}:BAND:RES{}".format(chan, bandwidth))

    def bandwidth(self, bandwidth='?', chan=""):
        return self.IFBW(bandwidth, chan)

    ########################################
    # Response
    ########################################

    def format_trace(self, trace_format='?', chan=""):
        if chan == "":
            chan = self._active_chan
        trace_formats = {'mlog': ' MLOG',
                   'phase': ' PHAS',
                   'lin_mag': ' MLIN',
                   'real': ' REAL',
                   'imag': " IMAG",
                   'extend_phase': ' UPH',
                   'uph': ' uph',
                   'positive_phase': ' PPH',
                   'pph': ' PHH',
                   'polar_linear': ' PLIN',
                   'plin': ' PLIN',
                   'polar_log': ' PLOG',
                   'plog': ' PLOG',
                   'real_imag': ' POL',
                   '?': '?'}
        trace_format = trace_format.lower()
        if trace_format in trace_formats:
            return self._com(':CALC{}:SEL:FORM{}'.format(chan, trace_formats[trace_format]))
        else:
            raise Exception("InvalidFormatError. valid strings are {}".format(trace_formats.keys()))

    ########################################
    # Output
    ########################################

    def delay(self, delay="?", chan=""):
        if delay != '?':
            delay = " " + str(delay)
        if chan == "":
            chan = self._active_chan
        return self._com(":CALC{}:CORR:EDEL:TIME{}".format(chan, delay))

    def phase_offset(self, phase="?", chan=""):
        if phase != "?":
            phase = " " + str(phase)
        if chan == "":
            chan = self._active_chan
        return self._com(":CALC{}:CORR:OFFS:PHAS{}".format(chan, phase))

    def power(self, power='?', source=""):
        if source != "":
            source = self._active_chan
        if power != '?':
            power = " " + str(power)
        return self._com(':SOUR{}:POW:LEV:IMM:AMPL{}'.format(source, power))

    def output(self, out='?'):
        options = {'true': ' 1',
                   'on': ' 1',
                   '1': ' 1',
                   'false': ' 0',
                   'off': ' 0',
                   '0': ' 0',
                   '?': '?'
                   }
        if str(out).lower() in options:
            return self._com(":OUTP{}".format(options[str(out).lower()]))
        else:
            raise Exception('InvalideOutputOption')

    def sweep_type(self, sweep_type='?', chan=""):
        sweep_types = {'linear': ' LIN',
                       'lin': ' LIN',
                       'log': ' LOG',
                       'segmented': ' SEG',
                       'power': ' POW',
                       '?': ' ?'
                       }
        if chan == "":
            chan = self._active_chan

        sweep_type = sweep_type.lower()
        if sweep_type in sweep_types:
            return self._com(':SENS{}:SWE:TYPE{}'.format(chan, sweep_types[sweep_type]))
        else:
            raise Exception("InvalidSweepType: Valid sweep types are {}".format(sweep_types.keys()))

    def Spar(self, Spar='?', trace="", chan=""):
        Spar = Spar.upper()
        if trace == "":
            trace = self._active_trace
        if chan == "":
            chan = self._active_chan
        options = {'S11': ' S11', 'S12': ' S12', 'S13': ' S13', 'S14': ' S14',
                   'S21': ' S21', 'S22': ' S22', 'S23': ' S23', 'S24': ' S24',
                   'S31': ' S31', 'S32': ' S32', 'S33': ' S33', 'S34': ' S34',
                   'S41': ' S41', 'S42': ' S42', 'S43': ' S43', 'S44': ' S44',
                   '?': '?'
                   }
        if Spar in options:
            return self._com(':CALC{}:PAR{}:DEF{}'.format(chan, trace, options[Spar]))

    ########################################
    # Trigger
    ########################################
    def trigger_source(self, source='?'):
        sources = {"internal": " INT",
                   "external": " EXT",
                   "manual": " MAN",
                   "bus": " BUS",
                   "?": "?"
                   }
        source = source.lower()
        if source in sources:
            return self._com(":TRIG:SOUR{}".format(sources[source]))
        else:
            raise Exception("InvalideTriggerSourceException")

    def trigger_initiate(self, state='?', chan=""):
        options = {"on": " ON", "1": " 1", "true": " 1",
                   "off": " OFF", "0": " 0", "false": " 0",
                   "?": "?"
                   }
        if chan == "":
            chan = self._active_chan
        state = str(state).lower()
        if state in options:
            return self._com('INIT{}:CONT{}'.format(chan, options[state]))
        else:
            Exception('InvalidTriggerStateException')

    def trigger_now(self):
        if self.average_state() == 1:
            average_count = self.average_count()
        else:
            average_count = 1
        self._com(":TRIG:SING")
        sweep_time = self.get_sweep_time()
        sleep(int(average_count*sweep_time))
        # print("Collecting data...")
        return 'Sent: :TRIG:SING \nMeasuremet complete {}'.format(self.operation_complete())

    def trigger_averaging(self, averaging='?'):
        options = {"on": " ON", "1": " 1", "true": " 1",
                   "off": " OFF", "0": " 0", "false": " 0",
                   "?": "?"
                   }
        averaging = str(averaging).lower()
        if averaging in options:
            return self._com(":TRIG:SEQ:AVER{}".format(options[averaging]))
        else:
            raise Exception("InvalidTriggerAveragingArgument")


    ########################################
    # reading data
    ########################################

    def format_data(self, form='?'):
        formats = {'ascii': ' ASC',
                   'asc': ' ASC',
                   'real': ' REAL',
                   'real32': ' REAL32',
                   '?': '?'
                   }
        form = form.lower()
        return self._com(':FORMat:DATA{}'.format(formats[form]))

    def read_freq(self):
        self.format_data('real')
        data = self._com_binary(':CALC:SEL:DATA:XAXis?')
        self.format_data('ascii')
        return data

    def read_single_trace(self, trace):
        self.format_data('real')
        data = self._com_binary(':CALC:TRACe{}:DATA:FDATa?'.format(trace))
        self.format_data('ascii')

        return data[0::2], data[1::2]

    def read_all_traces(self):
        # read the x axis and all traces of the active channel
        traces = int(self.traces_number())
        points = int(self.points())

        data = np.empty((2*traces+1, points))

        self.format_data('real')
        data[0] = self._com_binary(':CALC:SEL:DATA:XAXis?')
        for trace in range(traces):
            raw_data = self._com_binary(':CALC:TRACe{}:DATA:FDATa?'.format(trace+1))
            data[2*trace + 1] = raw_data[0::2]
            data[2*trace + 2] = raw_data[1::2]
        self.format_data('ascii')

        return data

    #def close(self):
    #    self._inst.close()

    def identify(self):
        return self._com("*IDN?")

    def idn(self):
        return self._com("*IDN?")

    def operation_complete(self):
        return self._com("*OPC?")

    def get_sweep_time(self):
        return self._com("SENS:SWE:TIME?")

    ########################################
    # parameters
    ########################################
    def set_trigger(self, source='bus', averaging=0, initiate=True):
        self.trigger_source(source)
        self.trigger_averaging(averaging)
        self.trigger_initiate(initiate)

    def set_averaging(self, state='off', count=0):
        self.average_state(state)
        self.average_count(count)

    def set_freq_axis(self, start="", stop="", center="", span="", point=1000, bandwidth=1000, sweep_type='lin'):
        if type(start) != str:
            self.freq_start(start)
        if type(stop) != str:
            self.freq_stop(stop)
        if type(center) != str:
            self.freq_center(center)
        if type(span) != str:
            self.freq_span(span)

        self.points(point)
        self.bandwidth(bandwidth)
        self.sweep_type(sweep_type)

    def set_response_axes(self, trace_formats, delay, phase_offset, Spar='S12'):
        if type(trace_formats) == str:
            trace_formats = [trace_formats]
        if Spar == str:
            Spar = [Spar] * len(trace_formats)
        self.delay(delay)
        self.phase_offset(phase_offset)
        self.traces_number(len(trace_formats))
        for i, trace_format in enumerate(trace_formats):
            self.active_trace(i+1)
            self.Spar(Spar)
            self.Format(trace_format)


    def get_parameters(self, chan=""):
        # TODO: test this and use this function to save to config
        # if chan == "":
        #     chan = self._active_chan
        # else:
        #     self.active_chan(chan)

        # total_traces = self.traces_number(chan)

        freq_start = self.freq_start()
        freq_stop = self.freq_stop()
        freq_center = (freq_stop + freq_start) / 2
        freq_span = freq_stop - freq_start
        points = self.points()
        bandwidth = self.IFBW()
        # Spar = self.Spar()
        # Format = self.format_trace()
        power = self.power()
        average_count = self.average_count()
        average_state = self.average_state()
        delay = self.delay()
        phase_offset = self.phase_offset()

        parameters = {'VNA E5071 freq_start': freq_start,
                      'VNA E5071 freq_stop': freq_stop,
                      'VNA E5071 freq_center': freq_center,
                      'VNA E5071 freq_span': freq_span,
                      'VNA E5071 points': points,
                      'VNA E5071 IFBW': bandwidth,
                      #'Format': Format,  # get this for each channel
                      #'Spar': Spar, # get this for each channel
                      'VNA E5071 power': power,
                      'VNA E5071 average_count': average_count,
                      'VNA E5071 average_state': average_state,
                      'VNA E5071 delay': delay,
                      'VNA E5071 phase_offset': phase_offset
                      }
        return parameters

    def set_parameters(self, chan="", **kwargs):
        # TODO: test this and read get **kwargs from a config file
        if chan == "":
            chan = self._active_chan
        parameters = {'VNA E5071 freq_start': self.freq_start,
                      'VNA E5071 freq_stop': self.freq_stop,
                      'VNA E5071 freq_center': self.freq_center,
                      'VNA E5071 freq_span': self.freq_span,
                      'VNA E5071 points': self.points,
                      'VNA E5071 IFBW': self.bandwidth,
                    #   'VNA E5071 Format': self.format_trace,  # set this for each channel
                    #   'VNA E5071 Spar': self.Spar,  # set this for each channel
                      'VNA E5071 power': self.power,
                      'VNA E5071 average_count': self.average_count,
                      'VNA E5071 average_state': self.average_state,
                      'VNA E5071 delay': self.delay,
                      'VNA E5071 phase_offset': self.phase_offset
                      }

        # need to figure out how to format the trace specific parameters like format
        for i in kwargs.keys():
            try:
                parameters[i](kwargs[i])
            except KeyError:
                pass


    ##############################
    # send commands
    ##############################
    def _com(self, cmd):
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
            return "Sent: " + cmd

    def _com_binary(self, cmd):
        if self.verbatim:
            print(cmd)
        if cmd[-1] == '?':
            return self._inst.query_binary_values(cmd, datatype='d', is_big_endian=True)
        else:
            # TODO: Test this section
            self._inst.write_binary_values(cmd, datatype='d', is_big_endian=True)
            return "Waveform sent"


if __name__ == "__main__":
    import matplotlib.pyplot as plt
    import os.path as path
    # import Labber
    import json
    ################
    # Create object/Connect to device.
    ################
    rm = visa.ResourceManager('@py')
    # ip = '192.168.0.204'
    # addr = 'TCPIP::{}::INSTR'.format(ip)
    # addr = 'TCPIP0::K-E5071C-33486.local::inst0::INSTR'
    # addr = 'TCPIP0::192.168.0.100'
    addr = "TCPIP0::K-E5071C-33486.local::inst0::INSTR"
    # addr = 'TCPIP0::10.0.0.15'
    vna = E5071C(addr)
    vna.freq_center(4.0)


    # vna.set_freq_axis(start=1, stop=20, point=10001, bandwidth=1000, sweep_type='lin')
    # vna.set_set_response_axes(trace_formates=['mlog', 'phase'], delay=1, phase_offset=180, Spar='S12')
    # vna.set_averaging(state='off', count=0)
    # vna.set_trigger(source='bus', averaging=0, initiate=True)

    # vna.trigger_initiate(True)
    # vna.trigger_now()

    # file_path = r'C:\\Users\\hqdteam\\Documents\\Maser_Data_E59\\2023\\12\\Data_1214'
    # file_name = 'WiringTest_C2toO2_cavity2'
    # file_path = path.join(file_path,file_name)

    ## Save csv 
    # data = vna.read_all_traces()
    # print(data)
    # data = pd.DataFrame(data).T
    # data.to_csv(file_path+'.csv', index=False)

    ## plot fig.
    # freqs = data.iloc[:,0]

    # trace1 = data.iloc[:,1]
    # trace2 = data.iloc[:,3]

    # freqs = data[0]
    # trace1 = data[1]
    # trace2 = data[3]
    # export = np.hstack((freqs[:,None],trace1[:,None],trace2[:,None]))
    
    # lStep = [dict(name='Frequency', unit='Hz', values=freqs),]
    # lLog = [dict(name='Amplitude', unit='dB', vector=False,),
    #         dict(name='Phase', unit='deg', vector=False,),]
    
    # #exp_name = 'S21_12mK_Port1(A2)_to_Port2(O)_2'
    # # exp_name = 'Port1(B2)_0.5mm-gap-cavity-sapphire_CryoSwitch-ON_HEMT-6-20C-sn2222Z_Port2(O1)_Tmxc-11mK'
    # # exp_name = 'Test_Tmxc_5.8K_(A2)_HEMT_0.3_14A_sn1103Z(Vd_1.229V_10mA)_4Kplate_(O)'
    # # exp_name = 'Test_Tmxc_5.8K_B1_C2'
    # # exp_name = 'Test_B1_MXC'
    # # exp_name = 'Test_Port1(right_before_HEMT_on_A2)_Port2(A2)'
    # exp_name = 'SMA-male2male-adapter_8GHz-Cavity(v2)_1-loop(v2)_zoom'
    # # exp_name = 'SMA-male2male-adapter_0.5mm-gap-cavity-with-sapphire_1loop-antenna_(zoom)'
    # # exp_name = '0.5mm-gap-cavity-backcover_loop4.0'
    # # exp_name = '4GHz-Cavity_circuit-S11'
    # ############################################    
    # f = Labber.createLogFile_ForData(exp_name, lLog, lStep)
    # f.setUser('IvanKostylev')
    # f.setProject('Cavity Measurements')
    # # f.setProject('Test for repaired HEMT')
    # # f.setProject('NTN CPW Ruby maser')
    # f.setTags(['Transmission', 'RT', 'VNA', 'Lab1'])
    # comment = {"Temperature": " RT",
    #              'Line': "Port 1 (in) to Port 2 (Out)",
    #             #'Line': "Port 1 (in)",
    #             "Cable": "SMA-male2male-adapter",
    #             # "Cable": "Totoku 3.0mx2",
    #            # "HEMT": "LNC_6_20C_s/n 2222Z",
    #            #"HEMT": "LNC_0p3_14A s/n 1103Z",
    #            #"HEMT": "LNC_4_8C s/n 3037H",
    #            "Misc": "N/A"}
    # f.setComment(json.dumps(dict(**comment, **vna.get_parameters()), indent=2, separators=(",",":")))

    # data = {'Amplitude': trace2, 'Phase': trace1,}
    # f.addEntry(data)

    # # fig = plt.figure(figsize=(10,8))
    # # fig.suptitle(file_path.split('\\')[-1])


    # # ax1 = fig.add_subplot(2, 1, 1)
    # # ax1.plot(freqs/1e9, trace1, label='Phase',color='orange')
    # # ax1.set_xlabel("Frequency [GHz]")
    # # ax1.set_ylabel("phase [deg.]")

    # # ax2 = fig.add_subplot(2, 1, 2)
    # # ax2.plot(freqs/1e9, trace2, label='Amp')
    # # ax2.set_xlabel("Frequency [GHz]")
    # # ax2.set_ylabel("Amp [dB]")


    # # fig.tight_layout()
    # # # plt.savefig(file_path+'.png')
    # # plt.show()

    # # ################
    # # # Set up parameters related to frequency scan.
    # # ################
    # # vna.freq_start(1)
    # # vna.freq_stop(2)
    # # vna.points(1001)
    # # vna.bandwidth(1000)
    # # vna.sweep_type('lin')
    # # ################
    # # # Set up trace related commands. Channel related commands are similar.
    # # ################
    # # vna.traces_number(3)
    # # vna.active_trace(1)
    # # vna.Spar('S12')
    # # print(vna.Format('mlog'))
    # # vna.delay(1)
    # # vna.phase_offset(180)
    # # print(vna.active_trace(2))
    # # vna.Spar('S12')
    # # vna.delay(1)
    # # vna.phase_offset(180)
    # # print(vna.Format('phase'))
    # # print(vna.active_trace(3))
    # # vna.Spar('S12')
    # # vna.delay(1)
    # # vna.phase_offset(180)
    # # print(vna.Format('Plog'))
    # # ################
    # # # Set up averaging parameters. Don't forget to set the "vna.trigger_averaging(True)" when using averaging
    # # ################
    # # print(vna.average_state(False))
    # # print(vna.average_count(0))
    # # ################
    # # # Set up averaging parameters.
    # # ################
    # # print(vna.trigger_source('bus'))
    # # print(vna.trigger_averaging(0))
    # # print(vna.trigger_initiate(True))
    # # print(vna.trigger_now())
    # # ################
    # # # Read the data on the screen
    # # ################
    # # print(vna.freq_read())
    # # print(vna.trace_read(1)[0])
    # # print(vna.trace_read(2)[0])
    # # data = vna.trace_read(3)
    # # print(data[0])
    # # print(data[1])
    # # data = vna.read()  # This command gets values for x axis and the primary and secondary data for all the traces.

