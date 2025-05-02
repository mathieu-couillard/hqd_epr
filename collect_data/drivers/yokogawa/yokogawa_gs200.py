"""
June 2022
@author: Mathieu Couillard

Driver for Yokogawa GS200 DC source
"""

import pyvisa as visa

def format_num(arg, units=1, limits=(-float('inf'),float('inf')), function_name='') -> str:
    if arg == None or arg == '?':
        return '?'
    else:
        # TODO: Make dictionary of units
        arg = float(arg)*units
        if limits[0]<=arg<=limits[1]:
            return ' ' + str(arg)
        else:
            raise Exception("OutOfRangeException: {} value must be between {} and {}. arg = {}".format(function_name, limits[0], limits[1], arg), '?')

def format_from_dict(arg, arg_dict, function_name='') -> str:
    if arg == None:
        arg = '?'
    arg = str(arg).lower()
    try:
        return arg_dict[arg]
    except:
        print("InvalidInputError: {} argument must be : {}. Argument values is {}".format(function_name, list(arg_dict.keys()), arg))
        return '?' # FIXME: There should be a better way to handle this error with querying the device.


class YokogawaGS200:
    def __init__(self, address, verbatim=False, visa_backend=None):
        if visa_backend==None:
            self._inst = visa.ResourceManager().open_resource(address)
        else:
            self._inst = visa.ResourceManager(visa_backend).open_resource(address)
        # self._inst.timeout = 2500
        self._inst.write_termination = '\r'
        self._inst.read_termination = '\n'
        # self._inst.inst.chunk_size=1024
        self.verbatim = verbatim
        identity = self.identify()
        print("Identity: {}".format(identity))
        if "YOKOGAWA,GS210" not in identity or"YOKOGAWA,GS211" not in identity :
            Exception("WARNING: The device: {} is not a Yokogawa GS200 DC source."
                      "\nSome commands may not work.".format(address))

        self.verbatim = verbatim  # Print every command before sending
#################
# Common Commands
#################


    def close(self):
        self._inst.close()

    def identify(self):
        return self._com("*IDN?")

    def idn(self):
        return self._com("*IDN?")

    def operation_complete(self):
        return self._com("*OPC?")
#################
# Output Command
#################
    def output(self, state=None):
        states = {'true': ' on',
                  'on' : ' on',
                  '1' : ' on',
                  'false': ' off',
                  'off': ' off',
                  '0' : ' off',
                  '?': '?'
                  }
        state = format_from_dict(state, states, function_name="output(arg)")
        return self._com(':OUTPut{}'.format(state))

#################
# Source Commands
#################

    def function(self, function=None):
        functions={'curr': ' current',
                   'current': ' current',
                   'volt':' voltage',
                   'voltage': ' voltage',
                   '?':'?'
                   }
        function = format_from_dict(function, functions, function_name='function(arg)')
        return self._com('source:function{}'.format(function))


    def source_range(self, source_range=None):
        ranges_v = {'0.01':' 0.01', '0.1':' 0.1', '1':' 1', '10':' 10', '30':' 30', '?':'?'}
        ranges_i = {'0.001':' 0.001', '0.01':' 0.01', '0.1': ' 0.1', '0.2':' 0.2', '?':'?'}
        if self.function()=='CURR':
            ranges = ranges_i
        else:
            ranges = ranges_v
        source_range = format_from_dict(source_range, ranges, function_name='source_range(arg)')
        return self._com('source:range{}'.format(source_range))
            

    def level(self, level=None):
        if self.function() == 'CURR':
            limit = 0.2
        else:
            limit = 32
        level = format_num(level, limits=(-limit, limit), function_name='level(arg)')        
        return self._com('source:level:auto{}'.format(level))
 
            
    def protection_voltage(self, voltage=None):
        voltage = format_num(voltage, limits=(-32,32), function_name='protection_voltage(arg)')
        return self._com(':SOURce:PROTection:VOLTage{}'.format(voltage))
            
    def protection_current(self, current=None):
        current = format_num(current, limits=(-0.2, 0.2), function_name='protection_current(arg)')
        return self._com(':SOURce:PROTection:CURRent{}'.format(current))
###############
# Program Commands
###############


###############
# Sense Commands
###############


###############
# Read Commands
###############
    def initiate(self):
        return self._com(':INITiate')

    def fetch(self):
         return self._com(':FETCh?')

    def read(self):
        return self._com(':READ?')

    def measure(self):
        return self._com(':MEASure?')
    
###############
# Trace Commands
###############

###############
# Route Commands (BNC I/O)
###############
    def bnc_out(self, option=None):
        options ={'trig':'trigger', 'output':'outp', 'read':'ready'}
        option = format_from_dict(option, options, function_name="bnc_out(arg)")        
        return self._com(':ROUTe:BNCO{}'.format(option))

    
    def bnc_in(self, option=None):
        options ={'trig':'trigger', 'output':'outp'}
        option = format_from_dict(option,options, function_name="bnc_in(arg)")
        return self._com(':ROUTe:BNCI{}'.format(option))
    
###############
# System Commands
###############

    def error(self):
        return self._com(':SYSTem:ERRor')
        
    def local(self):
        return self._com(':SYSTem:LOCal')
    
    def remote(self):
        return self._com(':SYSTem:REMote')


    def line_frequency(self):
        # The GS200 automatically measures the line frequency
        return self._com(':SYSTem:LFRequency?')

        
###############
# Status Commands
###############
    def condition(self):
        return self._com(':STATus:CONDition?')
        
    def event(self):
        return self._com(':STATus:EVENt?')
    
    def status_enable(self, register=None):
        register = format_num(register, limits=(0,2**16), function_name='status_enable(arg)')
        return self._com(':STATus:ENABle{}'.format(register))
        
    def status_error(self):
        # Same as error()
        return self._com(':STATus:ERRor?')

###############
# Communication Command
###############
    def _com(self, cmd):
        if self.verbatim:
            print(cmd)
        if cmd[-1] == '?':
            value = self._inst.query(cmd)
            if value.isnumeric():
                return float(value)
            else:
                return value
        else:
            self._inst.write(cmd)
            return "Sent: " + cmd




if __name__ == '__main__':
    addr='TCPIP::192.168.0.125::INSTR'
    source = gs200(addr, visa_backend='@py')
    source.function('current') # Set to constant current
    print(source.function())
    source.source_range('0.2')
    # source.level(0)  # Set level to 150 mA
    # source.protection_voltage(1) # Set protection voltage to 1 V
    # source.output(True) # turn on output
    
    # print(source.level()) # Get the set level and print value
    # source.output(False)
    
