import pyvisa as visa

class KeysightN9010A():

    def __init__(self,addr):
        self._instr = visa.ResourceManager('@py').open_resource(addr)
        self._instr.timeout = 30000
        self._name = 'unknown spa?'
        self._name = self._query('*IDN?').split(',')[1]
        self.config = {
            'name':self._name,
            'cmd':addr,
            }

    def restart(self):
        self.write("INIT:REST;*OPC")


    def get_config(self):
        """ """
        self.config['params'] = {
            'attenuation':self.attenuation_dB,
            'centerInGHz':self.centerFreqInGHz,
            'spanInGHz':self.spanInGHz,
            'startInGHz':self.startFreqInGHz,
            'stopInGHz':self.stopFreqInGHz,
            'vidBWInHz':self.videoBWInHz,
            'ResBWInHz':self.resBWInHz,
            'numOfPoints':self.numOfPoints,
            'avgCount':self.sweepAveCounts,
            'Marker1_Hz':self.x_Marker1,
            'Marker2_Hz':self.x_Marker2,
            'Marker3_Hz':self.x_Marker3,
            }
        return self.config


    ##############################
    # Methods that send commands
    ##############################
    def _write(self, cmd):
        self._instr.write(cmd)

    def _read(self):
        val = self._instr.read()
        return val

    def _query(self, cmd):
        val =  self._instr.query(cmd).split('\n')[0]
        return val

    ##############################
    # Attributes
    ##############################
    @property
    def refLevel_dBm(self): 
        val = self._query("DISP:WIND:TRAC1:Y:RLEV?")
        return val

    @refLevel_dBm.setter
    def refLevel_dBm(self,level):
        self._write("DISP:WIND:TRAC1:Y:RLEV %f dBm" %level)

    @property
    def centerFreqInGHz(self):
        return float(self._query("FREQ:CENT?"))/1e9

    @centerFreqInGHz.setter
    def centerFreqInGHz(self,freq):
        self._write("FREQ:CENT %f GHZ" %freq)

    @property
    def spanInGHz(self):
        return float(self._query("FREQ:SPAN?"))/1e9

    @spanInGHz.setter
    def spanInGHz(self,span):
        self._write("FREQ:SPAN %f GHZ" %span)

    @property
    def startFreqInGHz(self):
        """Gets the start frequency in GHz."""
        return float(self._query("FREQ:STAR?"))/1e9
    
    @startFreqInGHz.setter
    def startFreqInGHz(self,starf):
        """Sets the start frequency in GHz."""
        self._write("FREQ:STAR %f GHz" %starf)

    @property
    def stopFreqInGHz(self): 
        """Gets the stop frequency in GHz."""
        return float(self._query("FREQ:STOP?"))/1e9

    @stopFreqInGHz.setter
    def stopFreqInGHz(self,stopf): 
        self._write("FREQ:STOP %f GHZ" %stopf)

    @property
    def resBWInHz(self):
        """ """
        return float(self._query("BAND:RES?"))

    @resBWInHz.setter
    def resBWInHz(self,resBandwidth='auto'):
        if type(resBandwidth)!= type(str):
            resBandwidth=str(resBandwidth)+'HZ'
        self._write("BAND:RES "+resBandwidth)

    @property
    def videoBWInHz(self):
        """ """
        return float(self._query("BAND:VID?")) 

    @videoBWInHz.setter
    def videoBWInHz(self,videoBandwidth='auto'):
        if type(videoBandwidth)!= type(str):
            videoBandwidth=str(videoBandwidth)+'HZ'
        self._write("BAND:VID "+videoBandwidth)
        
    @property
    def sweepTimeInSec(self):
        """ """
        return float(self._query("SWE:TIME?"))

    @sweepTimeInSec.setter
    def sweepTimeInSec(self,st='AUTO'):
        """ """
        if type(st) != type(str):
            st = str(st)
            cmd="SWE:TIME "+st
            self._write(cmd)

        if st=='AUTO' or st=='auto':
            st2=str(st2)+' ON'
            cmd="SWE:TIME:"+st2
            self._write(cmd)

    @property
    def sweepAveCounts(self):
        """ """
        return int(self._query("AVER:COUN?"))

    @sweepAveCounts.setter
    def sweepAveCounts(self,sweepCounts=1):
        """ """
        self._write("AVER:COUN %i" %sweepCounts)

    @property
    def attenuation_dB(self):
        """ """
        return float(self._query("POW:ATT?"))

    @attenuation_dB.setter
    def attenuation_dB(self,level):
        """ """
        self._write("POW:ATT %d" %level)

    @property
    def x_Marker1(self): #done
        """ """
        return float(self._query("CALC:MARK1:X?"))
    
    @x_Marker1.setter
    def x_Marker1(self,x_Hz): #done
        """ """
        self._write("CALC:MARK1:X %e"%x_Hz)

    @property
    def x_Marker2(self): #done
        """ """
        return float(self._query("CALC:MARK2:X?"))
    
    @x_Marker2.setter
    def x_Marker2(self,x_Hz): #done
        """ """
        self._write("CALC:MARK2:X %e"%x_Hz)

    @property
    def x_Marker3(self): #done
        """ """
        return float(self._query("CALC:MARK3:X?"))
    
    @x_Marker3.setter
    def x_Marker3(self,x_Hz): #done
        """ """
        self._write("CALC:MARK3:X %e"%x_Hz)

    @property
    def valueAtMarker1(self): #done
        """ """
        return float(self._query("CALC:MARK1:Y?"))

    @property
    def valueAtMarker2(self): #done
        """ """
        return float(self._query("CALC:MARK2:Y?"))

    @property
    def valueAtMarker3(self): #done
        """ """
        return float(self._query("CALC:MARK3:Y?"))

    @property
    def numOfPoints(self):
        """ """
        return int(self._query("SWE:POIN?"))

    @numOfPoints.setter
    def numOfPoints(self,n):
        """ """
        self._write("SWE:POIN "+str(n))

    @property
    def triggerType(self):
        return self._query("TRIG:SOUR?")

    @triggerType.setter
    def triggerType(self, typ):
        self._write("TRIG:SOUR "+str(typ))

   

    ######################
    #  GET TRACES BELOW  #
    ######################
    def manual_trigger(self):
        """
        Send a trigger to SPA.  
        Use this in Single mode or when you want to make sure the SPA returns data
        of each measurement
        """
        self._write("*TRG")    

    def getTrace(self,traceno = 1):
        """
        Transfers immeditaly a trace from the FSP.
        Returns the trace as a list of two lists.
        For internal use only. USE getTrace() OR getTraceCube  INSTEAD.
        """
        freq_mode = float(self._query("FREQ:SPAN?"))
        timedomain = False  
        sweeptime = 0
        freqStart = 0
        freqStop = 0
        if freq_mode == 0:
            #This is a time domain measurement.
            timedomain = True
            sweeptime = float(self._query("SWE:TIME?"))
        else:
            #This is a frequency domain measurement.
            freqStart = float(self._query("FREQ:STAR?"))
            freqStop = float(self._query("FREQ:STOP?"))

        trace = self._query("TRAC:DATA? TRACE"+str(traceno))
        # self.write("INIT:CONT ON")# 20/03/2012 VS recoved Denis 30/01/2013
        
        values = trace.split(',')
        values = [float(x) for x in values]
        # map(lambda x:float(x),values)
        if timedomain:
            times=[i * sweeptime / len(values) for i in range(0,len(values))]
            result = [times,values]
        else:
            frequencies=[ freqStart+ i * (freqStop-freqStart) / len(values) for i in range(0,len(values))]
            result = [frequencies,values]

        return result


    ## Under testing ##
    def getChannelPower(self):
        """
        Get rms power in in the measurement BW.
        The SPA should be in Channel Power Measurement Mode
        """
        return float(self.ask("FETCH:CHP:CHP?")) #done

    ## Under testing ##
    def getChannelPowerDensity(self):
        """
        Get rms power density.
        The SPA should be in Channel power measurement mode.
        """
        return float(self.ask("FETCH:CHP:DENS?")) #done



if __name__== "__main__":
    import matplotlib.pyplot as plt
    import datetime, os
    import numpy as np
    spa = SPA_N9010A()
    print(spa._query('*IDN?'))


#     # pprint(rm.list_resources())

#     dic_connect = {
#         "rm" : rm,
#         "visa_cmd" : "TCPIP::192.168.0.61::INSTR"
#     }
#     inst = Instrument(dic_connect)
#     print(inst._query("*IDN?")[:-1])
#     inst.x_Marker1=6.0e9

#     config = inst.get_config()
#     today = datetime.date.today()
#     now = datetime.datetime.now()
#     path='D:\\Data\\QuickSave'
#     file_name = 'spa_{0:%Y%m%d}_{1:%H%M%S}'.format(today, now)

#     path_SPA = os.path.join(path, file_name+'.txt')
#     con_path = os.path.join(path, 'config_'+file_name+'.txt')

#     trace = inst.getTrace()

#     np.savetxt(path_SPA, trace, fmt="%1.10f")
#     with open(con_path,'w') as fp:
#         json.dump(config,fp,sort_keys=True, indent=4)

#     print(config)
#     plt.plot(trace[0],trace[1])
#     plt.show()
