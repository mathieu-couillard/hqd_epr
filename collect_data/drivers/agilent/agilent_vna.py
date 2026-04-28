import numpy as np
import pyvisa as visa
import time
import cmath


# This is the VNA instrument.
class AgilentN5230C:
    def __init__(self, address):
        rm = visa.ResourceManager("@py")
        self._instr = rm.open_resource(address)

        self._instr.timeout = 10000

        self._name = "unknown vna?"
        self._name = self._query("*IDN?").split(",")[1]
        self.config = {
            "name": self._name,
        }

        self._channel = 1
        self._port = 1
        self._trace = 1
        # self._write("CALC:PAR:SEL 'CH1_S21_2'")
        self.freq = self.getFreq()

    ##############################
    # Method
    ##############################
    # def clearDevice(self):
    # handle = self.getHandle()
    # handle.timeout = 1
    # vpp43.clear(handle.vi)
    # handle._write('*CLS')
    # try:
    # print 'STB=',self._query('*STB?')
    # return True
    # except visa.VisaIOError:
    # return False

    def clearAverage(self):
        self._write("SENS:AVER:CLE")

    def get_config(self):
        self.config["params"] = {
            "VNA power": self.totalPower_dBm,
            "VNA cwONOFF": self.CW,
            "VNA centerInGHz": self.centerFreqInGHz,
            "VNA spanInGHz": self.spanFreqInGHz,
            "VNA startInGHz": self.startFreqInGHz,
            "VNA stopInGHz": self.stopFreqInGHz,
            "VNA BWInHz": self.BW,
            "VNA numOfPoints": self.numOfPoints,
            "VNA avgCount": self.numOfAve,
            "VNA avgONOFF": self.aveIsOn,
            "VNA electricalDelay": self.electricalDelay,
        }
        return self.config

    def operation_complete(self):
        return self._query("*OPC?")
    
    def getFreq(
        self,
    ):
        self._write("CALC:PAR:SEL 'CH1_S21_2'")
        self._write(":FORM:DATA REAL,32")
        self._write("CALC:X?")
        time.sleep(0.1)
        sData = self._instr.read_raw()
        # sData = self._instr.read()

        i0 = sData.find(b"#")
        nDig = int(sData[i0 + 1 : i0 + 2])  # how many next digit for data length

        nByte = int(sData[i0 + 2 : i0 + 2 + nDig])  # data length
        nData = int(nByte / 4)
        nPts = int(nData / 2)
        # print(sData[:10])
        # get data to numpy array
        vData = np.frombuffer(
            sData[(i0 + 2 + nDig) : (i0 + 2 + nDig + nByte)], dtype="<f", count=nData
        ).byteswap()
        # This is returning in big endian format

        return vData

    def getTrace(self, dB=True):
        self._write("CALC:PAR:SEL 'CH1_S21_2'")
        self._write(":FORM REAL,32")
        self._write("CALC:DATA? SDATA")
        time.sleep(0.1)
        sData = self._instr.read_raw()

        ###################################################################
        # strip header to find # of points
        # ex. sData = b'#44008\xc2\xa7\x08= ...'
        # sData = #, 4, 4008, I[0],Q[0],I[1],Q[1], ...
        ###################################################################
        i0 = sData.find(b"#")
        nDig = int(sData[i0 + 1 : i0 + 2])  # how many next digit for data length

        nByte = int(sData[i0 + 2 : i0 + 2 + nDig])  # data length
        nData = int(nByte / 4)
        nPts = int(nData / 2)
        # print(sData[:10])
        # get data to numpy array
        vData = np.frombuffer(
            sData[(i0 + 2 + nDig) : (i0 + 2 + nDig + nByte)], dtype="<f", count=nData
        ).byteswap()

        # data is in I0,Q0,I1,Q1,I2,Q2,.. format, convert to complex
        mC = vData.reshape((nPts, 2))
        vComplex = mC[:, 0] + 1j * mC[:, 1]
        phase = [cmath.phase(c_num) for c_num in vComplex]
        amp = abs(vComplex)

        freqs = self.getFreq()
        delay_sec = self.electricalDelay  # *1e-12

        delta_phase = delay_sec * freqs * 2 * np.pi
        phase = (phase + delta_phase - self.phaseOffset * (np.pi / 180) - np.pi) % (
            2 * np.pi
        ) - np.pi

        if dB:
            amp_dB = 20 * np.log10(amp)
            return amp_dB, phase
        else:
            return amp, phase

    def trigger(self, channel=1):
        self._write("TRIG:SOUR MAN")
        self._write("INIT" + str(self._channel) + ":IMM")

    def waitFullSweep(self, channel=1, restore=False):
        mode = self._query("TRIG:SOUR?")
        self.trigger(channel=channel)
        sweep_start = time.time()
        self._write("*OPC")
        while True:
            time.sleep(0.1)
            esr = int(self._query("*ESR?"))
            if (esr & 1) == 1:
                break
        if restore:
            self._write("TRIG:SOUR " + mode)

        sweep_end = time.time()
        wait_time = self.sweepTime
        sweep_time_here = sweep_end - sweep_start
        if sweep_time_here < wait_time:
            print(f"Waiting full sweep... {wait_time} sec")
            time.sleep(wait_time - sweep_time_here)

    ##############################
    # Methods that send commands
    ##############################
    def _write(self, cmd):
        # time.sleep(0.2) #<-----added
        self._instr.write(cmd)

    def _read(self):
        # time.sleep(0.2) #<-----added
        val = self._instr.read()
        return val

    def _query(self, cmd):
        val = self._instr.query(cmd)
        # time.sleep(0.2) #<-----added
        return val

    ##############################
    # Attributes
    ##############################
    @property
    def channel(self):
        return self._channel

    @channel.setter
    def channel(self, ch):
        self._channel = ch

    @property
    def port(self):
        return self._port

    @port.setter
    def port(self, port):
        self._port = port

    @property
    def trace(self):
        return self._trace

    @trace.setter
    def trace(self, trace):
        self._trace = trace

    @property
    def sweepMode(self):
        return self._query("SENS" + str(self._channel) + ":SWEEP:MODE?")

    @sweepMode.setter
    def sweepMode(self, Mode):  # Mode is 'CONT' or 'SINGLE' or 'HOLD'
        self._write("SENS" + str(self._channel) + ":SWEEP:MODE " + Mode)

    @property
    def outputIsOn(self):
        return self._query("OUTP:STAT?")

    @outputIsOn.setter
    def outputIsOn(self, tf):
        if tf:
            self._write("OUTP:STAT ON")
        else:
            self._write("OUTP:STAT OFF")

    @property
    def totalPower_dBm(self):
        return float(self._query("SOUR" + str(int(self._port)) + ":POW?"))

    @totalPower_dBm.setter
    def totalPower_dBm(self, powerIndBm):
        self._write("SOUR" + str(int(self._port)) + ":POW " + str(powerIndBm))

    @property
    def attenuation_dB(self):
        return float(self._query("SOUR:POW:ATT?"))

    @attenuation_dB.setter
    def attenuation_dB(self, attenIndB="AUTO"):
        str1 = "SOUR" + str(self._channel) + ":POW" + str(int(self._port))
        if isinstance(attenIndB, (int, float)):
            str1 += ":ATT " + str(attenIndB)
        else:
            str1 += ":ATT:AUTO ON"
        self._write(str1)

    @property
    def mode(self):
        return self._query("SENS:SWE:TYPE?")

    @mode.setter
    def mode(self, mode):
        self._write("SENS:SWE:TYPE " + mode)

    @property
    def CW(self):
        return self.mode == "CW"

    @CW.setter
    def CW(self, on=True):
        if on:
            return self.setMode("CW")
        else:
            return self.setMode("LIN")

    @property
    def startFreqInGHz(self):
        return float(self._query("SENS" + str(self._channel) + ":FREQ:START?")) / 1e9

    @startFreqInGHz.setter
    def startFreqInGHz(self, freq):
        freq = freq * 1e9
        self._write("SENS" + str(self._channel) + ":FREQ:START " + str(freq))

    @property
    def stopFreqInGHz(self):
        return float(self._query("SENS" + str(self._channel) + ":FREQ:STOP?")) / 1e9

    @stopFreqInGHz.setter
    def stopFreqInGHz(self, freq):
        freq = freq * 1e9
        self._write("SENS" + str(self._channel) + ":FREQ:STOP " + str(freq))

    @property
    def centerFreqInGHz(self):
        return float(self._query("SENS" + str(self._channel) + ":FREQ:CENT?")) / 1e9

    @centerFreqInGHz.setter
    def centerFreqInGHz(self, freq):
        freq = freq * 1e9
        self._write("SENS" + str(self._channel) + ":FREQ:CENT " + str(freq))

    @property
    def spanFreqInGHz(self):
        return float(self._query("SENS" + str(self._channel) + ":FREQ:SPAN?")) / 1e9

    @spanFreqInGHz.setter
    def spanFreqInGHz(self, span):
        span = span * 1e9
        self._write("SENS" + str(self._channel) + ":FREQ:SPAN " + str(span))

    @property
    def numOfPoints(self):
        return int(self._query("SENS" + str(self._channel) + ":SWEEP:POINTS?"))

    @numOfPoints.setter
    def numOfPoints(self, nOfPoints):
        self._write("SENS" + str(self._channel) + ":SWEEP:POINTS " + str(nOfPoints))

    # confirm Unit
    @property
    def BW(self):
        return float(self._query("SENS" + str(self._channel) + ":BAND?"))

    @BW.setter
    def BW(self, bandwidth):
        self._write("SENS" + str(self._channel) + ":BAND " + str(bandwidth))

    @property
    def aveIsOn(self):
        return bool(int(self._query("SENS:AVER?")))

    @aveIsOn.setter
    def aveIsOn(self, on=True):
        if on:
            self._write("SENS:AVER ON")
        else:
            self._write("SENS:AVER OFF")

    @property
    def averageMode(self):
        return self._query("SENS:AVER:MODE?")

    @averageMode.setter
    def averageMode(self, mode="SWEEP"):  # use 'SWEEP' or 'POINT'
        self._write("SENS:AVER:MODE " + mode)

    @property
    def numOfAve(self):
        return int(self._query("SENS:AVER:COUN?"))

    @numOfAve.setter
    def numOfAve(self, count):
        self._write("SENS:AVER:COUN " + str(int(count)))

    @property
    def electricalLength(self):
        self.selectTrace(channel=self._channel, trace=self._trace)
        return float(self._query("CALC" + str(self._channel) + ":CORR:EDEL:DIST?"))

    @electricalLength.setter
    def electricalLength(self, dist):
        self.selectTrace(channel=self._channel, trace=self._trace)
        self._write("CALC" + str(self._channel) + ":CORR:EDEL:DIST " + str(dist))
        return self.electricalLength()

    @property
    def electricalDelay(self):
        self.selectTrace(channel=self._channel, trace=1)
        return float(self._query("SENSe:CORRection:COLLect:CKIT:STANdard:DELay?"))
        # return float(self._query("CALCulate:CORRection:EDELay:TIME?"))

    @electricalDelay.setter
    def electricalDelay(self, delay):  # delay is second, not ps
        # self.selectTrace(channel=self._channel, trace=1)
        self._write("SENSe:CORRection:COLLect:CKIT:STANdard:DELay " + str(delay))
        # self._write("CALCulate:CORRection:EDELay:TIME " + str(delay))

    @property
    def phaseOffset(self):
        # self.selectTrace(channel=self._channel, trace=1)
        return float(self._query("CALCulate:CORRection:OFFSet:PHASe?"))

    @phaseOffset.setter
    def phaseOffset(self, offset, trace=1):
        self.selectTrace(channel=self._channel, trace=trace)
        self._write("CALCulate:CORRection:OFFSet:PHASe " + str(offset))

    @property
    def sweepTime(self):
        return float(self._query(":SENS:SWE:TIME?"))

    @sweepTime.setter
    def sweepTime(self, time):
        self._write(":SENS:SWE:TIME {}".format(str(time)))

    def measurements(
        self, channel=1
    ):  # measurement number = tr# (and mont the trace) on the PNA
        # print(self._query('SYST:MEAS:CAT? '+str(channel))[1:-2])
        return [
            int(u)
            for u in self._query("SYST:MEAS:CAT? " + str(channel))[1:-2].split(",")
        ]

    def selectTrace(
        self, channel=1, trace=1
    ):  # trace also called measurement in the documentation
        if trace in self.measurements(channel=channel):
            self._write("CALC" + str(self._channel) + ":PAR:MNUM " + str(trace))
        trace2 = int(self._query("CALC" + str(self._channel) + ":PAR:MNUM?"))
        if trace2 != trace:
            raise NameError(
                "Can't select trace " + str() + " of channel " + str(self._channel)
            )
        return trace2

    def getFormat(self, _channel, trace):
        success, trace = self.selectTrace(_channel=_channel, trace=trace)
        if success:
            self._query("CALC" + str(self._channel) + ":FORM?")
        else:
            # print '_channel '+_channel+':measurement '+trace+' does not exist.'
            pass

    def setFormat(
        self, _channel, trace, format
    ):  # format is MLINear,MLOGarithmic,PHASe,UPHase,IMAGinary,REAL,POLar
        success, trace = self.selectTrace(_channel=_channel, trace=trace)
        if success:
            self._write("CALC" + str(self._channel) + ":FORM " + format)
            return self.getFormat(_channel, trace)

    ##############################
    # Markers
    ##############################

    def checkMarkerIndex(self, index):
        if index >= 10:
            raise NameError("Marker index should be lower than 10.")

    def markerState(self, _channel=1, trace=1, marker=1):
        self.checkMarkerIndex(marker)
        self.selectTrace(channel=_channel, trace=trace)
        return int(
            self._query("CALC" + str(self._channel) + ":MARK" + str(marker) + "?")
        )

    def markerOn(self, _channel=1, trace=1, marker=1):
        self.checkMarkerIndex(marker)
        self.selectTrace(_channel=_channel, trace=trace)
        self._write("CALC" + str(self._channel) + ":MARK" + str(marker) + " ON")
        return self.markerState(_channel=_channel, marker=marker)

    def markerOff(self, _channel=1, trace=1, marker=1):
        self.checkMarkerIndex(marker)
        self.selectTrace(_channel=_channel, trace=trace)
        self._write("CALC" + str(self._channel) + ":MARK" + str(marker) + " OFF")
        return self.markerState(_channel=_channel, marker=marker)

    def markerState2(self, _channel=1, trace=1, marker=1, forceOn=False):
        state = self.markerState(_channel=_channel, trace=trace, marker=marker)
        if not state:
            if forceOn:
                return self.markerOn(_channel=_channel, trace=trace, marker=marker)
            else:
                raise NameError(
                    "Marker is off. Switch it on or use kwarg forceOn=True in your calls."
                )
        else:
            return state

    def markerPosition(
        self, _channel=1, trace=1, marker=1, forceOn=False
    ):  # position in number of points
        self.markerState2(
            _channel=_channel, trace=trace, marker=marker, forceOn=forceOn
        )
        return int(
            self._query("CALC" + str(self._channel) + ":MARK" + str(marker) + ":BUCK?")
        )

    def markerSetPosition(
        self, position, _channel=1, trace=1, marker=1, forceOn=True
    ):  # position in number of points
        self.markerState2(
            _channel=_channel, trace=trace, marker=marker, forceOn=forceOn
        )
        self._write(
            "CALC"
            + str(self._channel)
            + ":MARK"
            + str(marker)
            + ":BUCK "
            + str(position)
        )
        return self.markerPosition(_channel=_channel, marker=marker)

    def markerX(
        self, _channel=1, trace=1, marker=1, forceOn=True
    ):  # position X the unit of the X axis (frequency, power or time )
        self.markerState2(
            _channel=_channel, trace=trace, marker=marker, forceOn=forceOn
        )
        return float(
            self._query("CALC" + str(self._channel) + ":MARK" + str(marker) + ":X?")
        )

    def markerSetX(
        self, x, _channel=1, trace=1, marker=1, forceOn=True
    ):  # position in number of points
        self.markerState2(
            _channel=_channel, trace=trace, marker=marker, forceOn=forceOn
        )
        self._write(
            "CALC" + str(self._channel) + ":MARK" + str(marker) + ":X " + str(x)
        )
        return self.markerX(_channel=_channel, marker=marker)

    def markerY(self, _channel=1, marker=1, trace=1, forceOn=True):
        self.markerState2(
            _channel=_channel, trace=trace, marker=marker, forceOn=forceOn
        )
        return [
            float(y)
            for y in self._query(
                "CALC" + str(self._channel) + ":MARK" + str(marker) + ":Y?"
            ).split(",")
        ]

        # -----------------------------------------------------------------------
        # Set center frequency or marker to Max or Min
        # -----------------------------------------------------------------------

    def extremum(
        self, target="max", _channel=1, trace=1, waitFullSweep=False, **kwargs
    ):
        x, y = self.getTrace(
            _channel=_channel, trace=trace, waitFullSweep=waitFullSweep
        )
        if target == "max":
            target = max(y)
        else:
            target = min(y)
        pos = np.where(y == target)[0][0]
        return (trace, (x[pos], y[pos]), pos)

    def centerAtExtremum(self, _channel=1, **kwargs):
        (trace, (x0, y0), pos) = self.extremum(_channel=_channel, **kwargs)
        self.setCenterFrequency(x0, _channel=_channel)
        return (trace, (x0, y0), pos)

    def centerAtMax(self, **kwargs):
        return self.centerAtExtremum(target="max", **kwargs)

    def centerAtMin(self, **kwargs):
        return self.centerAtExtremum(target="min", **kwargs)

    def markerAtExtremum(
        self,
        channel=1,
        trace=1,
        marker=1,
        forceOn=False,
        allTraces=True,
        complexOut=False,
        **kwargs,
    ):
        self.markerState2(channel=channel, trace=trace, marker=marker, forceOn=forceOn)
        (trace, (x0, y0), pos) = self.extremum(
            channel=channel, trace=trace, marker=marker, **kwargs
        )
        if allTraces:
            result = []
            traces = self.measurements(channel=channel)
            for tracei in traces:
                self.markerSetPosition(
                    pos, channel=channel, trace=tracei, marker=marker
                )
                xi = self.markerX(
                    channel=channel, trace=trace, marker=marker, forceOn=forceOn
                )
                yi = self.markerY(
                    channel=channel, trace=trace, marker=marker, forceOn=forceOn
                )
                if complexOut == False:
                    yi = yi[0]
                result.append(
                    (tracei, (xi, yi), pos)
                )  # list of tuples [(trace1,(x1,y1),pos1),(trace2,(x2,y2),pos2),...]
        else:
            self.markerSetPosition(pos, channel=channel, trace=trace, marker=marker)
            result = (trace, (x0, y0), pos)  # tuple
        return result

    def markerAtMax(self, **kwargs):
        return self.markerAtExtremum(target="max", **kwargs)

    def markerAtMin(self, **kwargs):
        return self.markerAtExtremum(target="min", **kwargs)


if __name__ == "__main__":
    import matplotlib.pyplot as plt
    import numpy as np
    import pandas as pd
    import datetime

    print("test...")
    print(inst._query("*IDN?"))
    print(inst.markerPosition())
    # print(inst.get_config())
    # print(inst.getFreq())
    # inst.centerFreqInGHz = 6.78763
    # inst.totalPower_dBm = 0
    # inst.waitFullSweep()
    # inst.spanFreqInGHz = 0.03
    # inst.numOfPoints = 1001
    # inst.numOfAve = 100
    # inst.waitFullSweep()
    # inst.totalPower_dBm = -30

    # import timeit
    # start = timeit.timeit()
    # for i in range(10000):
    #     print(i)
    # time.sleep(1)
    # inst.get_config()
    # inst._query("*IDN?")
    # inst = Instrument(dic_connect)
    # inst.waitFullSweep()
    # print(timeit.timeit() - start)

    # import matplotlib.pyplot as plt
    # plt.plot(delta)
    # plt.show()
    # print(inst._query('*IDN?'))
    # freq = inst.getFreq()

    # print(len(freq))
    # print(freq)
    # inst._write(":FORM:DATA REAL32")
    # print(inst.totalPower_dBm)
    # inst._write(':FORM REAL,32')
    # channel = 1
    # inst._instr.write(':FORM REAL,64;CALC:DATA? SDATA')

    # inst.spanFreqInGHz = 0.2

    # inst.numOfPoints = 601
    # inst.centerFreqInGHz(4)
    # inst.spanFreqInGHz(1)

    # cf = inst.centerFreqInGHz
    # span = inst.spanFreqInGHz
    # # span_ = 0.2
    # # print(inst.spanFreqInGHz, inst.numOfPoints)
    # # inst.spanFreqInGHz = 0.2

    # start = time.time()
    # # inst.waitFullSweep()
    # amp,phase = inst.getTrace(dBm=True)
    # end = time.time()
    # print(end-start)

    # # inst.electricalDelay = 64.437251e-9
    # # delay_sec = inst.electricalDelay
    # # # print(delay_sec)

    # x = np.linspace(cf-span/2,cf+span/2,len(amp))

    # fig = plt.figure(figsize=(8, 6))
    # ax1 = fig.add_subplot(2, 1, 1)
    # ax1.plot(x, amp)
    # ax1.set_xlabel("Frequency [Hz]")
    # ax1.set_ylabel("Amp [dB]")
    # #ax1.set_xlim(0, 110)
    # #ax1.set_ylim(0, 190)

    # ax2 = fig.add_subplot(2, 1, 2)
    # ax2.plot(x, phase)
    # ax2.set_xlabel("Frequency [Hz]")
    # ax2.set_ylabel("Phase")
    # ax2.set_ylim([-np.pi, np.pi])
    # plt.show()

    # now = datetime.datetime.now()
    # columns = ['Frequency [GHz]', 'Amp [dB]', 'Phase [deg.]']
    # df = pd.DataFrame(np.array((x,amp,phase)).T,columns=columns)
    # #print(df)
    # # path='D:\\Data\\QuickSave\\vna_'+now.strftime('%y%m%d_%H%M%S')+'.csv'
    # path='D:\\Data\\Maser_data_E59\\2024\\02\\Data_0214\\vna_'+now.strftime('%y%m%d_%H%M%S')+'.csv'
    # df.to_csv(path)

    # print(inst.get_config())
