##########################################
# 2022/Aug./1st Write ver.1
# Need to be tested
# Tatsuki Hamamoto
##########################################
import time

import numpy as np
import pyvisa as visa


class KeysightPSG:
    def __init__(self, address):
        self._inst = visa.ResourceManager("@py").open_resource(address)

        self._name = self._query("*IDN?").split(",")[1]
        self.config = {
            "name": self._name,
            "address": address,
        }

    ##############################
    # Method
    ##############################
    def saveState(self, name):
        """
        Save the instrument state. Just returns a dictionary with all relevant parameters.
        """
        return self.parameters()

    def get_config(self):
        """
        Returns all relevant parameters of the instrument.
        """
        self.config["params"] = {
            "frequency": self.freqInGHz,
            "power": self.power_dBm,
            "mwIsOn": self.mwIsOn,
        }

        return self.config

    def restoreState(self, state):
        """
        Restores a previously saved state.
        """
        print(state)
        self.setFrequency(state["frequency"])
        self.setPower(state["power"])
        if state["output"]:
            self.turnOn()
        elif state["output"] == False:
            self.turnOff()

    def loadFreqSweep(self, startFreq, stopFreq, dwellTime, numPoints):
        self.setStartFreq(startFreq)
        self.setStopFreq(stopFreq)
        self.setDwell(dwellTime)
        self.setSweepPoints(numPoints)

    ##############################
    # Methods that send commands
    ##############################
    def _write(self, cmd):
        self._instr.write(cmd)

    def _read(self):
        val = self._instr.read()
        return val

    def _query(self, cmd):
        val = self._instr.query(cmd)
        return val[:-1]

    ##############################
    # Attributes
    ##############################
    @property
    def freqInGHz(self):
        return float(self._query("FREQ:FIXED?")) / 1e9

    @freqInGHz.setter
    def freqInGHz(self, freq):
        self._write("FREQ:FIXED %f" % (freq * 1e9))

    @property
    def power_dBm(self):
        return float(self._query("POW?"))

    @power_dBm.setter
    def power_dBm(self, power):
        _power = str(power)
        self._write("POW %s" % (_power))

    @property
    def phaseInDeg(self):
        return float(self._query("PHAS?")) / np.pi * 180

    @phaseInDeg.setter
    def PhaseInDeg(self, phase):
        self._write("PHAS %f" % (np.pi * phase / 180))

    def setPhaseRef(self):
        """
        Turn on the microwave.
        """
        self._write("PHAS:REF")
        return self.output()

    @property
    def mwIsOn(self):
        state = int(self._query("OUTP?"))
        if state != 0:
            state = True
        else:
            state = False
        return state

    @mwIsOn.setter
    def mwIsOn(self, on):
        if on:
            self._write("OUTP ON")
        else:
            self._write("OUTP OFF")

    @property
    def mode(self):
        return self._query("FREQ:MODE?")

    @mode.setter
    def mode(self, mode):
        self._write("FREQ:MODE %s" % mode)
        return self.getMode()

    @property
    def sweepPoints(self):
        return self._query("SWE:POIN?")

    @sweepPoints.setter
    def sweepPoints(self, numPoints):
        self._write("SWE:POIN %f" % numPoints)

    @property
    def startFreqInGHz(self):
        return self._query("FREQ:STAR?")

    @startFreqInGHz.setter
    def startFreqInGHz(self, startFreq):
        self._write("FREQ:STAR %f GHz" % startFreq)

    @property
    def StopFreqInGHz(self):
        return self._query("FREQ:STOP?")

    @StopFreqInGHz.setter
    def StopFreqInGHz(self, stopFreq):
        self._write("FREQ:STOP %f GHz" % stopFreq)

    @property
    def sweepDirection(self):
        return self._query("LIST:DIR?")

    @sweepDirection.setter
    def sweepDirection(self, Direc):
        self._write("LIST:DIR %s" % Direc)

    def setDwell(self, dwellTime):
        self._write("SWE:DWEL %f" % dwellTime)

    def startSweep(self):  # assuming trigger is set to be "FreeRun"
        self._write("INIT")

    def getStat(self):
        return self._query("STAT:OPER:COND?")

    def StartandCheckSweep(self):
        """
        Launch a sweep and keep watching the status until finishing.
        useful to implement in experiment codes
        """
        self.startSweep()
        while True:  # check sweep status until finishing
            try:
                stat = self.getStat()  # get MW source status
                print(stat)
                if not (
                    stat == "+10" or stat == "+40"
                ):  # True if the state is "+10" or "+40" (one of the two is the sweep status)
                    break
                time.sleep(0.5)

            except:
                print("error?try again...")


if __name__ == "__main__":
    rm = visa.ResourceManager()
    # pprint(rm.list_resources())
    ip = "192.168.0.11"
    # ip = '192.168.0.13'
    visa_cmd = "TCPIP::" + ip + "::INSTR"
    dic_connect = {
        "rm": rm,
        "visa_cmd": visa_cmd,
    }

    inst = Keysight_PSG(dic_connect)
    print(inst._query("*IDN?"))

    # print(inst._query('PWR?'))
    # inst._write(":FORM:DATA REAL32")
    # inst.mwIsOn= True
    print(inst.power_dBm)
    inst.power_dBm = -8

    print(inst.mwIsOn)
    inst.mwIsOn = False
    print(inst.mwIsOn)
